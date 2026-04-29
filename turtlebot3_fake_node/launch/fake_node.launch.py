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

"""Launch TurtleBot3 fake node for RViz-only simulation (no Gazebo)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directories
    fake_node_share = get_package_share_directory('turtlebot3_fake_node')
    gazebo_share = get_package_share_directory('turtlebot3_gazebo')

    # Environment variable for robot model
    turtlebot3_model = os.environ.get('TURTLEBOT3_MODEL', 'burger')

    # ROS distribution
    ros_distro = os.environ.get('ROS_DISTRO', 'humble').lower()
    enable_stamped = ros_distro != 'humble'
    
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    param_dir = LaunchConfiguration(
        'param_dir',
        default=os.path.join(fake_node_share, 'param', f'{turtlebot3_model}.yaml')
    )
    
    # URDF file
    urdf_file_name = f'turtlebot3_{turtlebot3_model}.urdf'
    urdf = os.path.join(gazebo_share, 'urdf', urdf_file_name)
    
    return LaunchDescription([
        LogInfo(msg=['=== TurtleBot3 Fake Node (RViz Only) ===']),
        LogInfo(msg=[f'Robot Model: {turtlebot3_model}']),
        
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        
        DeclareLaunchArgument(
            'param_dir',
            default_value=param_dir,
            description='Path to parameter file'
        ),
        
        # Fake node for simulating odometry and sensors
        Node(
            package='turtlebot3_fake_node',
            executable='turtlebot3_fake_node',
            name='turtlebot3_fake_node',
            parameters=[
                param_dir,
                {'enable_stamped_cmd_vel': enable_stamped}
            ],
            output='screen',
            remappings=[
                ('cmd_vel', '/cmd_vel'),
                ('odom', '/odom'),
                ('joint_states', '/joint_states'),
            ]
        ),
        
        # Robot state publisher for TF transforms
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=[urdf]
        ),
        
        # RViz2 for visualization
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(fake_node_share, 'launch', 'rviz2.launch.py')
            ),
            launch_arguments={'use_sim_time': use_sim_time}.items()
        ),
    ])
