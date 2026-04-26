#!/usr/bin/env python3
#
# TurtleBot3 Gazebo Reset Handler
# Listens for Gazebo reset events and restarts bridge/spawn nodes
#

import os
import signal
import subprocess
import time

import rclpy
from rclpy.node import Node
from rosgraph_msgs.msg import Clock


class GazeboResetHandler(Node):
    """
    Monitors simulation clock for reset events (time going backwards).
    When detected, kills and restarts the bridge and spawn processes.
    """

    def __init__(self):
        super().__init__('gazebo_reset_handler')
        
        self.last_sim_time = 0.0
        self.reset_cooldown = 5.0  # Minimum seconds between resets
        self.last_reset_time = 0.0
        self.restart_in_progress = False
        
        self.declare_parameter('x_pose', -2.0)
        self.declare_parameter('y_pose', -0.5)
        self.declare_parameter('respawn_delay', 2.0)

        self.x_pose = str(self.get_parameter('x_pose').get_parameter_value().double_value)
        self.y_pose = str(self.get_parameter('y_pose').get_parameter_value().double_value)
        self.respawn_delay = self.get_parameter('respawn_delay').get_parameter_value().double_value
        
        self.clock_sub = self.create_subscription(
            Clock,
            '/clock',
            self.clock_callback,
            10
        )
        
        self.bridge_pids = []
        self.spawn_proc = None
        
        self.get_logger().info('Gazebo Reset Handler initialized')
        self.get_logger().info(f'Watching for reset events on /clock topic...')
        self.get_logger().info(f'Respawn position: x={self.x_pose}, y={self.y_pose}')

    def clock_callback(self, msg):
        """Detect reset by checking if simulation time goes backwards."""
        sim_time = msg.clock.sec + msg.clock.nanosec / 1e9
        now = time.time()
        
        # Check if time went backwards (reset detected)
        if sim_time < self.last_sim_time - 1.0:  # 1 second tolerance
            if now - self.last_reset_time > self.reset_cooldown:
                self.get_logger().warn(
                    f'Gazebo reset detected! Sim time jumped from '
                    f'{self.last_sim_time:.2f}s to {sim_time:.2f}s'
                )
                self.last_reset_time = now
                self.handle_reset()
        
        self.last_sim_time = sim_time

    def handle_reset(self):
        """Kill old processes and restart spawn + bridges."""
        if self.restart_in_progress:
            return
        
        self.restart_in_progress = True
        
        try:
            self.get_logger().info('Stopping existing bridge and spawn processes...')
            
            # Kill bridge processes
            subprocess.run(['pkill', '-f', 'parameter_bridge'], 
                         capture_output=True, timeout=5)
            subprocess.run(['pkill', '-f', 'image_bridge'], 
                         capture_output=True, timeout=5)
            
            time.sleep(1)
            
            self.get_logger().info(f'Respawning TurtleBot3 at ({self.x_pose}, {self.y_pose})...')
            
            # Start new spawn process
            cmd = [
                'ros2', 'launch', 'turtlebot3_gazebo', 'spawn_turtlebot3.launch.py',
                f'x_pose:={self.x_pose}',
                f'y_pose:={self.y_pose}'
            ]
            
            self.spawn_proc = subprocess.Popen(cmd)
            
            self.get_logger().info('Respawn initiated. Bridges will restart automatically.')
            
        except Exception as e:
            self.get_logger().error(f'Reset handling failed: {e}')
        finally:
            self.restart_in_progress = False


def main(args=None):
    rclpy.init(args=args)
    node = GazeboResetHandler()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.spawn_proc:
            node.spawn_proc.terminate()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
