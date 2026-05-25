#!/usr/bin/env python3
#
# Copyright (c) 2026, TurtleBot3 Simulations Contributors
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
# Author: Qwen Code AI Assistant

"""
碰撞检测与安全停止节点 (Collision Safety Node)

功能说明：
- 实时订阅激光雷达数据 (/scan)
- 检测前方障碍物距离是否低于安全阈值
- 当检测到碰撞风险时，自动发布停止指令到 /cmd_vel
- 覆盖键盘控制的速度指令，防止小车持续撞击障碍物
- 距离恢复安全后，自动解除停止状态

使用场景：
- 键盘控制时防止碰撞障碍物
- SLAM 建图时保护小车安全
- DQN 训练时的额外安全层

启动方式：
  ros2 run turtlebot3_teleop collision_safety

参数：
  --ros-args -p safety_distance:=0.15  (安全距离阈值，单位：米)
  --ros-args -p front_angle_range:=30  (前方检测角度范围，单位：度)
"""

import os
import sys

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import Twist
from rclpy.clock import Clock
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy


class CollisionSafetyNode(Node):
    """
    碰撞检测与安全停止 ROS2 节点

    订阅 /scan 话题，检测前方障碍物距离。当距离低于安全阈值时，
    自动发布零速度指令到 /cmd_vel，防止小车碰撞。
    """

    def __init__(self):
        super().__init__('collision_safety')

        # ==================== 参数声明与获取 ====================
        # 安全距离阈值（米）- 低于此距离触发停止
        self.declare_parameter('safety_distance', 0.15)
        self.safety_distance = self.get_parameter('safety_distance').value

        # 警告距离阈值（米）- 低于此距离打印警告（安全距离的 1.5 倍）
        self.warning_distance = self.safety_distance * 1.5

        # 前方检测角度范围（度）- 检测正前方 ± 这个角度
        self.declare_parameter('front_angle_range', 30.0)
        self.front_angle_range = self.get_parameter('front_angle_range').value

        # 是否启用日志输出
        self.declare_parameter('enable_logging', True)
        self.enable_logging = self.get_parameter('enable_logging').value

        # 紧急停止状态下是否持续发布停止指令
        self.declare_parameter('continuous_stop', True)
        self.continuous_stop = self.get_parameter('continuous_stop').value

        # ==================== 状态变量 ====================
        self.emergency_stop_active = False  # 紧急停止状态标志
        self.last_stop_time = self.get_clock().now()  # 上次发布停止指令的时间
        self.stop_publish_interval = 0.1  # 停止指令发布间隔（秒），避免高频发布

        # ==================== 订阅激光雷达数据 ====================
        # 使用 SensorData QoS 配置，与激光雷达发布者匹配
        scan_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            scan_qos
        )

        # ==================== 发布速度指令 ====================
        # 检测 ROS2 发行版，选择正确的消息类型
        ROS_DISTRO = os.environ.get('ROS_DISTRO', 'jazzy')
        self.use_twist_stamped = (ROS_DISTRO != 'humble')

        if self.use_twist_stamped:
            self.cmd_vel_pub = self.create_publisher(
                TwistStamped, '/cmd_vel', 10
            )
        else:
            self.cmd_vel_pub = self.create_publisher(
                Twist, '/cmd_vel', 10
            )

        # ==================== 日志输出 ====================
        self.get_logger().info('=' * 60)
        self.get_logger().info('碰撞安全节点已启动 (Collision Safety Node)')
        self.get_logger().info(f'  安全距离阈值: {self.safety_distance:.2f} m')
        self.get_logger().info(f'  警告距离阈值: {self.warning_distance:.2f} m')
        self.get_logger().info(f'  前方检测角度: ±{self.front_angle_range:.0f}°')
        self.get_logger().info(f'  消息类型: {"TwistStamped" if self.use_twist_stamped else "Twist"}')
        self.get_logger().info('  状态: 监控中 (Monitoring)')
        self.get_logger().info('=' * 60)

    def scan_callback(self, msg: LaserScan):
        """
        激光雷达数据回调函数

        检测前方扇形区域内的最小距离，判断是否触发紧急停止。

        参数:
            msg: LaserScan 消息，包含 360° 距离数据
        """
        # 获取激光雷达数据
        ranges = msg.ranges
        num_samples = len(ranges)

        if num_samples == 0:
            return

        # ==================== 计算前方检测区域 ====================
        # 激光雷达角度范围
        angle_min = msg.angle_min  # 通常为 0.0
        angle_max = msg.angle_max  # 通常为 2π (360°)
        angle_increment = msg.angle_increment

        # 将角度范围转换为索引
        front_angle_rad = self.front_angle_range * 3.14159 / 180.0

        # 计算正前方（0° 或 angle_min + angle_max / 2）的索引
        # Gazebo 中激光雷达通常从 0° 开始，正前方是角度范围的中间
        center_angle = (angle_min + angle_max) / 2.0
        center_idx = int((center_angle - angle_min) / angle_increment)

        # 计算前方 ±front_angle_range 的索引范围
        angle_range_idx = int(front_angle_rad / angle_increment)
        start_idx = max(0, center_idx - angle_range_idx)
        end_idx = min(num_samples, center_idx + angle_range_idx)

        # ==================== 检测最小距离 ====================
        # 提取前方区域的距离数据，过滤无效值（0 或 inf）
        front_ranges = [
            d for d in ranges[start_idx:end_idx]
            if d > msg.range_min and d < msg.range_max
        ]

        if not front_ranges:
            # 没有有效数据，不触发停止
            return

        min_distance = min(front_ranges)

        # ==================== 碰撞检测逻辑 ====================
        if min_distance < self.safety_distance:
            # 距离过近，触发紧急停止
            if not self.emergency_stop_active:
                # 首次触发，打印警告
                self.get_logger().warn(
                    f'⚠️  碰撞风险！前方距离: {min_distance:.2f}m < {self.safety_distance:.2f}m '
                    f'(安全阈值) - 触发紧急停止!'
                )
                self.emergency_stop_active = True
                self.last_stop_time = self.get_clock().now()

            # 发布停止指令
            if self.continuous_stop:
                now = self.get_clock().now()
                elapsed = (now - self.last_stop_time).nanoseconds / 1e9
                if elapsed >= self.stop_publish_interval:
                    self.publish_stop_command()
                    self.last_stop_time = now
            else:
                # 仅发布一次停止指令
                if self.emergency_stop_active:
                    self.publish_stop_command()
                    self.emergency_stop_active = False  # 重置状态

        elif min_distance < self.warning_distance:
            # 距离较近，打印警告但不触发停止
            if self.enable_logging:
                self.get_logger().info(
                    f'⚡ 接近障碍物: {min_distance:.2f}m '
                    f'(警告阈值: {self.warning_distance:.2f}m)'
                )

            # 如果之前在紧急停止状态，现在解除
            if self.emergency_stop_active:
                self.get_logger().info(
                    f'✅ 安全距离恢复: {min_distance:.2f}m > {self.safety_distance:.2f}m '
                    f'- 解除紧急停止'
                )
                self.emergency_stop_active = False

        else:
            # 安全距离，解除紧急停止
            if self.emergency_stop_active:
                if self.enable_logging:
                    self.get_logger().info(
                        f'✅ 安全距离恢复: {min_distance:.2f}m - 解除紧急停止，可继续控制'
                    )
                self.emergency_stop_active = False

    def publish_stop_command(self):
        """
        发布零速度停止指令到 /cmd_vel
        """
        if self.use_twist_stamped:
            stop_msg = TwistStamped()
            stop_msg.header.stamp = Clock().now().to_msg()
            stop_msg.header.frame_id = 'base_footprint'
            stop_msg.twist.linear.x = 0.0
            stop_msg.twist.linear.y = 0.0
            stop_msg.twist.linear.z = 0.0
            stop_msg.twist.angular.x = 0.0
            stop_msg.twist.angular.y = 0.0
            stop_msg.twist.angular.z = 0.0
        else:
            stop_msg = Twist()
            stop_msg.linear.x = 0.0
            stop_msg.linear.y = 0.0
            stop_msg.linear.z = 0.0
            stop_msg.angular.x = 0.0
            stop_msg.angular.y = 0.0
            stop_msg.angular.z = 0.0

        self.cmd_vel_pub.publish(stop_msg)


def main(args=None):
    """
    碰撞安全节点入口函数
    """
    rclpy.init(args=args)
    node = CollisionSafetyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('碰撞安全节点已停止 (KeyboardInterrupt)')
    except Exception as e:
        node.get_logger().error(f'节点异常: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
