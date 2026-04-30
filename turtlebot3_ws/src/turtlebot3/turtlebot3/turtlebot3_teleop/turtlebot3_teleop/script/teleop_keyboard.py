#!/usr/bin/env python
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

import os
import select
import sys

from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.clock import Clock
from rclpy.qos import QoSProfile

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty

BURGER_MAX_LIN_VEL = 0.22
BURGER_MAX_ANG_VEL = 2.84

WAFFLE_MAX_LIN_VEL = 0.26
WAFFLE_MAX_ANG_VEL = 1.82

LIN_VEL_STEP_SIZE = 0.01
ANG_VEL_STEP_SIZE = 0.1

TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']

msg = """
Control Your TurtleBot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity (Burger : ~ 0.22, Waffle and Waffle Pi : ~ 0.26)
a/d : increase/decrease angular velocity (Burger : ~ 2.84, Waffle and Waffle Pi : ~ 1.82)

space key, s : force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""


def get_key(settings):
    """
    获取用户按键输入
    
    参数:
        settings: 原始终端设置，在非Windows系统上用于恢复终端模式
    
    返回值:
        str: 用户按下的键值，如果没有按键则返回空字符串
    """
    # Windows系统下使用msvcrt.getch()获取按键
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8')
    
    # 设置终端为原始模式，直接读取字符而不需回车
    tty.setraw(sys.stdin.fileno())
    # 使用select等待输入，最多等待0.1秒
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    # 恢复终端到原来的状态
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def print_vels(target_linear_velocity, target_angular_velocity):
    """
    打印当前的目标线速度和角速度
    
    参数:
        target_linear_velocity (float): 目标线速度值
        target_angular_velocity (float): 目标角速度值
    """
    print('currently:\tlinear velocity {0}\t angular velocity {1} '.format(
        target_linear_velocity,
        target_angular_velocity))


def make_simple_profile(output_vel, input_vel, slop):
    """
    根据输入速度和当前输出速度，通过一个容差范围(slop)平滑地调整输出速度值
    
    这个函数用于实现速度变化的平滑过渡，防止速度突然跳变导致机器人运动不稳定。
    
    参数:
    output_vel -- 当前输出的速度值
    input_vel -- 目标输入的速度值
    slop -- 每次调整允许的最大变化量
    
    返回值:
    经过平滑处理后的输出速度值
    """
    if input_vel > output_vel:
        # 如果目标速度大于当前输出速度，则逐步增加速度值
        output_vel = min(input_vel, output_vel + slop)
    elif input_vel < output_vel:
        # 如果目标速度小于当前输出速度，则逐步减小速度值
        output_vel = max(input_vel, output_vel - slop)
    else:
        # 如果目标速度等于当前输出速度，则直接赋值
        output_vel = input_vel

    return output_vel


def constrain(input_vel, low_bound, high_bound):
    """
    将输入的速度值限制在指定的边界范围内。

    参数:
    input_vel: 输入的速度值
    low_bound: 允许的最小值下界
    high_bound: 允许的最大值上界

    返回:
    限制在边界范围内的速度值
    """
    if input_vel < low_bound:
        input_vel = low_bound
    elif input_vel > high_bound:
        input_vel = high_bound
    else:
        input_vel = input_vel

    return input_vel


def check_linear_limit_velocity(velocity):
    '''
    限制线性速度在最大允许范围内，根据不同TurtleBot3模型设置不同的最大线性速度限制

    :param velocity: 输入的线性速度值
    :return: 限制在对应模型最大线性速度范围内的速度值
    '''
    if TURTLEBOT3_MODEL == 'burger':
        return constrain(velocity, -BURGER_MAX_LIN_VEL, BURGER_MAX_LIN_VEL)
    else:
        return constrain(velocity, -WAFFLE_MAX_LIN_VEL, WAFFLE_MAX_LIN_VEL)


def check_angular_limit_velocity(velocity):
    if TURTLEBOT3_MODEL == 'burger':
        return constrain(velocity, -BURGER_MAX_ANG_VEL, BURGER_MAX_ANG_VEL)
    else:
        return constrain(velocity, -WAFFLE_MAX_ANG_VEL, WAFFLE_MAX_ANG_VEL)


def main():
    """
    主函数，实现通过键盘控制TurtleBot3机器人移动的功能
    
    该函数初始化ROS2节点，设置键盘输入监听，并根据按键发布相应的速度指令到/cmd_vel话题。
    支持ROS Humble版本和其他版本，两者在消息类型上有差异。
    按键控制：'w'增加线速度，'x'减少线速度，'a'增加角速度，'d'减少角速度，空格或's'停止。
    """
    settings = None
    # 非Windows系统保存终端设置以便读取键盘输入
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    rclpy.init()
    ROS_DISTRO = os.environ.get('ROS_DISTRO')
    qos = QoSProfile(depth=10)
    node = rclpy.create_node('teleop_keyboard')
    # 根据ROS2发行版选择不同的消息类型
    if ROS_DISTRO == 'humble':
        pub = node.create_publisher(Twist, 'cmd_vel', qos)
    else:
        pub = node.create_publisher(TwistStamped, 'cmd_vel', qos)

    # 初始化速度变量
    status = 0
    target_linear_velocity = 0.0
    target_angular_velocity = 0.0
    control_linear_velocity = 0.0
    control_angular_velocity = 0.0

    try:
        print(msg)
        while (1):
            key = get_key(settings)
            # 处理前进键'w'，增加线性前进速度
            if key == 'w':
                target_linear_velocity =\
                    check_linear_limit_velocity(target_linear_velocity + LIN_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            # 处理后退键'x'，增加线性后退速度
            elif key == 'x':
                target_linear_velocity =\
                    check_linear_limit_velocity(target_linear_velocity - LIN_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            # 处理左转键'a'，增加逆时针角速度
            elif key == 'a':
                target_angular_velocity =\
                    check_angular_limit_velocity(target_angular_velocity + ANG_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            # 处理右转键'd'，增加顺时针角速度
            elif key == 'd':
                target_angular_velocity =\
                    check_angular_limit_velocity(target_angular_velocity - ANG_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            # 处理停止键（空格或's'），重置所有速度为0
            elif key == ' ' or key == 's':
                target_linear_velocity = 0.0
                control_linear_velocity = 0.0
                target_angular_velocity = 0.0
                control_angular_velocity = 0.0
                print_vels(target_linear_velocity, target_angular_velocity)
            else:
                # 处理Ctrl+C退出程序
                if (key == '\x03'):
                    break

            # 每隔20次按键重新打印提示信息
            if status == 20:
                print(msg)
                status = 0

            # 应用平滑配置文件调整实际控制速度
            control_linear_velocity = make_simple_profile(
                control_linear_velocity,
                target_linear_velocity,
                (LIN_VEL_STEP_SIZE / 2.0))

            control_angular_velocity = make_simple_profile(
                control_angular_velocity,
                target_angular_velocity,
                (ANG_VEL_STEP_SIZE / 2.0))

            # 根据ROS2发行版发布适当的消息类型
            if ROS_DISTRO == 'humble':
                twist = Twist()
                twist.linear.x = control_linear_velocity
                twist.linear.y = 0.0
                twist.linear.z = 0.0

                twist.angular.x = 0.0
                twist.angular.y = 0.0
                twist.angular.z = control_angular_velocity

                pub.publish(twist)
            else:
                twist_stamped = TwistStamped()
                twist_stamped.header.stamp = Clock().now().to_msg()
                twist_stamped.header.frame_id = ''
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
        # 程序结束前发送零速度命令以确保机器人停止
        if ROS_DISTRO == 'humble':
            twist = Twist()
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = 0.0
            pub.publish(twist)
        else:
            twist_stamped = TwistStamped()
            twist_stamped.header.stamp = Clock().now().to_msg()
            twist_stamped.header.frame_id = ''
            twist_stamped.twist.linear.x = control_linear_velocity  # 这里应该是0.0，但保持原代码不变
            twist_stamped.twist.linear.y = 0.0
            twist_stamped.twist.linear.z = 0.0
            twist_stamped.twist.angular.x = 0.0
            twist_stamped.twist.angular.y = 0.0
            twist_stamped.twist.angular.z = control_angular_velocity  # 这里应该是0.0，但保持原代码不变
            pub.publish(twist_stamped)

        # 恢复终端设置
        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


if __name__ == '__main__':
    main()
