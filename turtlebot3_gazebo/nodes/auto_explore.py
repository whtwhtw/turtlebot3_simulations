#!/usr/bin/env python3
"""
Auto-exploration node for TurtleBot3 SLAM.
Drives the robot in a spiral/circle pattern to explore and map the environment.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import time


class AutoExplore(Node):
    def __init__(self):
        super().__init__('auto_explore')
        
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)
        
        self.scan_ranges = []
        self.min_obstacle_dist = 0.8  # minimum distance before turning
        
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.linear_speed = 0.15
        self.angular_speed = 0.5
        self.state = 'forward'  # forward, turn
        self.turn_direction = 1.0  # 1.0 = left, -1.0 = right
        self.forward_time = 0
        self.last_scan_time = time.time()
        
        self.get_logger().info('Auto Explore node started!')
        self.get_logger().info('State: FORWARD - moving forward and mapping...')
    
    def scan_callback(self, msg):
        self.scan_ranges = msg.ranges
    
    def check_obstacles(self):
        """Check if there are obstacles in front."""
        if not self.scan_ranges:
            return False
        
        # Check front sector (±30 degrees)
        center = len(self.scan_ranges) // 2
        sector = 60  # ±30 degrees
        start = max(0, center - sector)
        end = min(len(self.scan_ranges), center + sector)
        
        for i in range(start, end):
            dist = self.scan_ranges[i]
            if 0.1 < dist < self.min_obstacle_dist:
                return True
        return False
    
    def timer_callback(self):
        twist = Twist()
        
        if self.check_obstacles():
            # Obstacle detected, turn
            self.state = 'turn'
            self.get_logger().info('State: TURN - obstacle detected, turning...')
        
        if self.state == 'forward':
            twist.linear.x = self.linear_speed
            twist.angular.z = 0.0
            self.forward_time += 0.1
            
            # Every 5 seconds, do a small rotation to scan more area
            if self.forward_time > 5.0:
                twist.angular.z = 0.15
                if self.forward_time > 7.0:
                    self.forward_time = 0
                    
        elif self.state == 'turn':
            twist.linear.x = 0.0
            twist.angular.z = self.angular_speed * self.turn_direction
            self.forward_time = 0
            
            # Check if path is clear
            if not self.check_obstacles():
                self.state = 'forward'
                self.turn_direction *= -1  # alternate turn direction
                self.get_logger().info('State: FORWARD - path clear, continuing...')
        
        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = AutoExplore()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Auto Explore stopped by user')
    finally:
        # Send stop command
        twist = Twist()
        node.publisher.publish(twist)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
