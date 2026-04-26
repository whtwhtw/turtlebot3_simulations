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

"""Unified entry point for TurtleBot3 simulation launches."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_world(context, *args, **kwargs):
    """Include the appropriate world launch file based on parameter."""
    world_name = LaunchConfiguration('world').perform(context)
    launch_file_dir = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'), 'launch'
    )
    
    world_map = {
        'empty': 'empty_world.launch.py',
        'world': 'turtlebot3_world.launch.py',
        'house': 'turtlebot3_house.launch.py',
        'dqn_stage1': 'turtlebot3_dqn_stage1.launch.py',
        'dqn_stage2': 'turtlebot3_dqn_stage2.launch.py',
        'dqn_stage3': 'turtlebot3_dqn_stage3.launch.py',
        'dqn_stage4': 'turtlebot3_dqn_stage4.launch.py',
    }
    
    if world_name not in world_map:
        raise ValueError(f"Unknown world: {world_name}. Available: {list(world_map.keys())}")
    
    return [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, world_map[world_name])
        )
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='empty',
            description='World to launch: empty|world|house|dqn_stage1|dqn_stage2|dqn_stage3|dqn_stage4'
        ),
        
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        
        DeclareLaunchArgument(
            'x_pose',
            default_value='0.0',
            description='Initial X position of robot'
        ),
        
        DeclareLaunchArgument(
            'y_pose',
            default_value='0.0',
            description='Initial Y position of robot'
        ),
        
        OpaqueFunction(function=launch_world),
    ])
