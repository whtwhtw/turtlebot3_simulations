#!/usr/bin/env python3
#
# Copyright 2024 TurtleBot3 Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Launch RViz2 with TurtleBot3 configuration."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directories
    gazebo_share_dir = get_package_share_directory('turtlebot3_gazebo')
    
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    rviz_config = LaunchConfiguration(
        'rviz_config',
        default=os.path.join(gazebo_share_dir, 'rviz', 'tb3_gazebo.rviz')
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time if true'
        ),
        
        DeclareLaunchArgument(
            'rviz_config',
            default_value=rviz_config,
            description='Path to RViz configuration file'
        ),
        
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}]
        ),
    ])
