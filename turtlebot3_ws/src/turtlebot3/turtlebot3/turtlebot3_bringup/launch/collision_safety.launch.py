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

"""
碰撞安全节点 Launch 文件

启动碰撞检测与安全停止节点，用于防止 TurtleBot3 碰撞障碍物。

使用方式：
  ros2 launch turtlebot3_bringup collision_safety.launch.py

参数：
  safety_distance: 安全距离阈值（米），默认 0.15
  front_angle_range: 前方检测角度范围（度），默认 30.0
  enable_logging: 是否启用日志输出，默认 True
  continuous_stop: 是否持续发布停止指令，默认 True
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ==================== 参数声明 ====================
    safety_distance_arg = DeclareLaunchArgument(
        'safety_distance',
        default_value='0.15',
        description='安全距离阈值（米），低于此距离触发紧急停止'
    )

    front_angle_range_arg = DeclareLaunchArgument(
        'front_angle_range',
        default_value='30.0',
        description='前方检测角度范围（度），检测正前方 ± 这个角度'
    )

    enable_logging_arg = DeclareLaunchArgument(
        'enable_logging',
        default_value='true',
        description='是否启用日志输出'
    )

    continuous_stop_arg = DeclareLaunchArgument(
        'continuous_stop',
        default_value='true',
        description='紧急停止状态下是否持续发布停止指令'
    )

    # ==================== 节点配置 ====================
    collision_safety_node = Node(
        package='turtlebot3_teleop',
        executable='collision_safety',
        name='collision_safety',
        output='screen',
        parameters=[{
            'safety_distance': LaunchConfiguration('safety_distance'),
            'front_angle_range': LaunchConfiguration('front_angle_range'),
            'enable_logging': LaunchConfiguration('enable_logging'),
            'continuous_stop': LaunchConfiguration('continuous_stop'),
        }],
        remappings=[
            # 可根据需要重映射话题
            # ('/scan', '/custom_scan'),
            # ('/cmd_vel', '/custom_cmd_vel'),
        ],
    )

    return LaunchDescription([
        safety_distance_arg,
        front_angle_range_arg,
        enable_logging_arg,
        continuous_stop_arg,
        collision_safety_node,
    ])
