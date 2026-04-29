#!/usr/bin/env python3
"""Auto SLAM: slam_toolbox + turtlebot3_drive (no keyboard needed)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    turtlebot3_slam_toolbox = get_package_share_directory('turtlebot3_slam_toolbox')
    turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    # 1. 启动 slam_toolbox SLAM（不启动 RViz，避免重复打开）
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_slam_toolbox, 'launch', 'slam_toolbox.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'use_rviz': 'false',
        }.items(),
    )

    # 2. 延迟 3 秒后启动自动避障节点
    auto_drive = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(turtlebot3_gazebo, 'launch', 'turtlebot3_drive.launch.py')
                ),
                launch_arguments={
                    'use_sim_time': 'true',
                }.items(),
            )
        ],
    )

    return LaunchDescription([
        slam,
        auto_drive,
    ])
