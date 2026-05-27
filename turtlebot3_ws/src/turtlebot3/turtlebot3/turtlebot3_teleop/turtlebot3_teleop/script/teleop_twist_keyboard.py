#!/usr/bin/env python3
#
# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
#
# Software License Agreement (BSD 2-Clause Simplified License)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Darby Lim

"""
Teleoperation node for TurtleBot3 using keyboard.
Similar to teleop_twist_keyboard, publishes TwistStamped messages.

Keyboard layout (numpad style):
       u       i       o
       j               k
       m       ,       .

i/, : increase/decrease linear velocity
j/k : increase/decrease angular velocity
u/o : diagonal movement (linear + angular)
space key, key 's' : force stop
"""

import os
import select
import sys
import math
import termios
import tty
import threading

from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
import rclpy
from rclpy.clock import Clock
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

# TurtleBot3 速度限制
BURGER_MAX_LIN_VEL = 0.22
BURGER_MAX_ANG_VEL = 2.84

WAFFLE_MAX_LIN_VEL = 0.26
WAFFLE_MAX_ANG_VEL = 1.82

TURTLEBOT3_MODEL = os.environ.get('TURTLEBOT3_MODEL', 'burger')

# 固定速度值（按键直接设置，参考原版 teleop_twist_keyboard 默认参数）
LIN_VEL_FIXED = 0.2
ANG_VEL_FIXED = 1.0

# === 防撞安全参数 ===
SAFETY_DISTANCE = 0.2  # 安全距离（米）
FRONT_ANGLE_DEG = 60   # 前方检测区域角度范围（±）— 扩大前方检测范围
SIDE_ANGLE_DEG = 60    # 侧方检测区域角度范围（±）

msg = """
Control Your TurtleBot3!
---------------------------
Moving around (numpad layout):
        u       i       o
        j       k       l
        m       ,       .

i     : forward (fixed speed {0} m/s)
,     : backward (fixed speed {0} m/s)
j     : turn left (fixed speed {1} rad/s)
l     : turn right (fixed speed {1} rad/s)
k     : stop
u     : forward + left (diagonal)
o     : forward + right (diagonal)
m     : backward + left (diagonal)
.     : backward + right (diagonal)
space : emergency stop

[Collision avoidance enabled: will stop if obstacle < {2}m]

CTRL-C to quit
""".format(LIN_VEL_FIXED, ANG_VEL_FIXED, SAFETY_DISTANCE)


def get_key(settings):
    """
    获取用户按键输入

    Args:
        settings: 原始终端设置

    Returns:
        str: 用户按下的键值
    """
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8')

    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def print_vels(target_linear_velocity, target_angular_velocity):
    """打印当前速度"""
    print(
        'currently:\tlinear velocity {0:.2f}\t angular velocity {1:.2f}'.format(
            target_linear_velocity, target_angular_velocity
        )
    )


def constrain(input_vel, low_bound, high_bound):
    """限制速度在指定范围内"""
    return max(low_bound, min(input_vel, high_bound))


def check_linear_limit_velocity(velocity):
    """限制线性速度"""
    if TURTLEBOT3_MODEL == 'burger':
        return constrain(velocity, -BURGER_MAX_LIN_VEL, BURGER_MAX_LIN_VEL)
    else:
        return constrain(velocity, -WAFFLE_MAX_LIN_VEL, WAFFLE_MAX_LIN_VEL)


def check_angular_limit_velocity(velocity):
    """限制角速度"""
    if TURTLEBOT3_MODEL == 'burger':
        return constrain(velocity, -BURGER_MAX_ANG_VEL, BURGER_MAX_ANG_VEL)
    else:
        return constrain(velocity, -WAFFLE_MAX_ANG_VEL, WAFFLE_MAX_ANG_VEL)


def make_simple_profile(output_vel, input_vel, slop):
    """速度平滑过渡"""
    if input_vel > output_vel:
        output_vel = min(input_vel, output_vel + slop)
    elif input_vel < output_vel:
        output_vel = max(input_vel, output_vel - slop)
    else:
        output_vel = input_vel
    return output_vel


class ObstacleDetector:
    """激光雷达障碍物检测器"""

    def __init__(self, safety_distance, front_angle_deg, side_angle_deg):
        self.safety_distance = safety_distance
        self.front_angle = math.radians(front_angle_deg)
        self.side_angle = math.radians(side_angle_deg)

        self.front_clear = True
        self.back_clear = True
        self.left_clear = True
        self.right_clear = True
        self._lock = threading.Lock()

    def scan_callback(self, msg: LaserScan):
        """处理激光雷达扫描数据，更新各方向障碍物状态

        Gazebo 激光雷达映射：
        - ranges[0] = 0° = 前方（x 轴正方向）
        - ranges[90] = 90° = 左方
        - ranges[180] = 180° = 后方
        - ranges[270] = 270° = 右方
        """
        n = len(msg.ranges)
        if n == 0:
            return

        # 过滤无效数据
        ranges = []
        for r in msg.ranges:
            if msg.range_min <= r <= msg.range_max:
                ranges.append(r)
            else:
                ranges.append(float('inf'))

        front_span = int(self.front_angle / (2 * math.pi) * n)
        side_span = int(self.side_angle / (2 * math.pi) * n)

        # === 前方区域：ranges[0] 附近（跨越 0° 边界）===
        front_start = n - front_span  # 从末尾开始
        front_end = front_span        # 到开头结束
        front_min = min(ranges[front_start:] + ranges[:front_end])

        # === 后方区域：ranges[n//2] 附近 ===
        back_center = n // 2
        back_start = back_center - front_span
        back_end = back_center + front_span
        back_min = min(ranges[back_start:back_end])

        # === 左侧区域：ranges[n//4] 附近（90°）===
        left_center = n // 4
        left_start = left_center - side_span
        left_end = left_center + side_span
        left_min = min(ranges[left_start:left_end])

        # === 右侧区域：ranges[3n//4] 附近（270°）===
        right_center = (3 * n) // 4
        right_start = right_center - side_span
        right_end = right_center + side_span
        right_min = min(ranges[right_start:right_end])

        with self._lock:
            self.front_clear = front_min >= self.safety_distance
            self.back_clear = back_min >= self.safety_distance
            self.left_clear = left_min >= self.safety_distance
            self.right_clear = right_min >= self.safety_distance

    def check_and_clamp(self, vx, wz):
        """
        根据障碍物位置检查并限制速度命令。

        策略（方向感知模式）：
        - 前进(vx>0)：前方有障碍 → 停止前进
        - 后退(vx<0)：后方有障碍 → 停止后退
        - 左转(wz>0)：左方有障碍 → 停止左转
        - 右转(wz<0)：右方有障碍 → 停止右转
        - 只阻止冲突方向，不锁死其他方向
        """
        with self._lock:
            if vx > 0 and not self.front_clear:
                vx = 0.0
            if vx < 0 and not self.back_clear:
                vx = 0.0
            if wz > 0 and not self.left_clear:
                wz = 0.0
            if wz < 0 and not self.right_clear:
                wz = 0.0

            return vx, wz


def main():
    """
    主函数，实现键盘控制 TurtleBot3 机器人
    发布 TwistStamped 类型的消息到 cmd_vel 话题
    集成防撞功能：订阅激光雷达，障碍物过近时阻止靠近
    """
    settings = None
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    rclpy.init()

    qos = QoSProfile(depth=10)
    node = rclpy.create_node('teleop_twist_keyboard')

    # === 防撞检测器 ===
    detector = ObstacleDetector(SAFETY_DISTANCE, FRONT_ANGLE_DEG, SIDE_ANGLE_DEG)

    # 订阅激光雷达
    scan_qos = QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=10
    )
    node.create_subscription(LaserScan, 'scan', detector.scan_callback, scan_qos)

    # 启动后台 spin 线程处理回调
    spin_executor = rclpy.executors.SingleThreadedExecutor()
    spin_executor.add_node(node)
    spin_thread = threading.Thread(target=spin_executor.spin, daemon=True)
    spin_thread.start()

    # 始终发布 TwistStamped 类型
    pub = node.create_publisher(TwistStamped, 'cmd_vel', qos)

    status = 0
    target_linear_velocity = 0.0
    target_angular_velocity = 0.0
    control_linear_velocity = 0.0
    control_angular_velocity = 0.0

    try:
        print(msg)
        while True:
            key = get_key(settings)

            # 前进
            if key == 'i':
                target_linear_velocity = LIN_VEL_FIXED
                target_angular_velocity = 0.0
                print_vels(target_linear_velocity, target_angular_velocity)
            # 后退
            elif key == ',':
                target_linear_velocity = -LIN_VEL_FIXED
                target_angular_velocity = 0.0
                print_vels(target_linear_velocity, target_angular_velocity)
            # 逆时针旋转
            elif key == 'j':
                target_linear_velocity = 0.0
                target_angular_velocity = ANG_VEL_FIXED
                print_vels(target_linear_velocity, target_angular_velocity)
            # 停止
            elif key == 'k':
                target_linear_velocity = 0.0
                target_angular_velocity = 0.0
                print_vels(target_linear_velocity, target_angular_velocity)
            # 顺时针旋转
            elif key == 'l':
                target_linear_velocity = 0.0
                target_angular_velocity = -ANG_VEL_FIXED
                print_vels(target_linear_velocity, target_angular_velocity)
            # 左前方向（前进 + 逆时针）
            elif key == 'u':
                target_linear_velocity = LIN_VEL_FIXED
                target_angular_velocity = ANG_VEL_FIXED
                print_vels(target_linear_velocity, target_angular_velocity)
            # 右前方向（前进 + 顺时针）
            elif key == 'o':
                target_linear_velocity = LIN_VEL_FIXED
                target_angular_velocity = -ANG_VEL_FIXED
                print_vels(target_linear_velocity, target_angular_velocity)
            # 左后方向（后退 + 逆时针）
            elif key == 'm':
                target_linear_velocity = -LIN_VEL_FIXED
                target_angular_velocity = ANG_VEL_FIXED
                print_vels(target_linear_velocity, target_angular_velocity)
            # 右后方向（后退 + 顺时针）
            elif key == '.':
                target_linear_velocity = -LIN_VEL_FIXED
                target_angular_velocity = -ANG_VEL_FIXED
                print_vels(target_linear_velocity, target_angular_velocity)
            # 停止
            elif key == ' ' or key == 's':
                target_linear_velocity = 0.0
                target_angular_velocity = 0.0
                print_vels(target_linear_velocity, target_angular_velocity)
            # Ctrl+C 退出
            elif key == '\x03':
                break

            # 直接设置控制速度，并限制在机器人允许范围内
            control_linear_velocity = check_linear_limit_velocity(target_linear_velocity)
            control_angular_velocity = check_angular_limit_velocity(target_angular_velocity)

            # === 防撞检查 ===
            control_linear_velocity, control_angular_velocity = detector.check_and_clamp(
                control_linear_velocity, control_angular_velocity
            )

            # 发布 TwistStamped 消息
            twist_stamped = TwistStamped()
            twist_stamped.header.stamp = Clock().now().to_msg()
            twist_stamped.header.frame_id = 'base_link'
            twist_stamped.twist.linear.x = control_linear_velocity
            twist_stamped.twist.linear.y = 0.0
            twist_stamped.twist.linear.z = 0.0
            twist_stamped.twist.angular.x = 0.0
            twist_stamped.twist.angular.y = 0.0
            twist_stamped.twist.angular.z = control_angular_velocity

            pub.publish(twist_stamped)

    except Exception as e:
        print(e)

    finally:
        # 发送零速度命令
        twist_stamped = TwistStamped()
        twist_stamped.header.stamp = Clock().now().to_msg()
        twist_stamped.header.frame_id = 'base_link'
        twist_stamped.twist.linear.x = 0.0
        twist_stamped.twist.linear.y = 0.0
        twist_stamped.twist.linear.z = 0.0
        twist_stamped.twist.angular.x = 0.0
        twist_stamped.twist.angular.y = 0.0
        twist_stamped.twist.angular.z = 0.0
        pub.publish(twist_stamped)

        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

        node.destroy_node()
        rclpy.shutdown()
