#!/bin/bash
# TurtleBot3 Respawn Helper Script
# Usage: After Gazebo reset, run this to respawn the robot and restore teleop

source /opt/ros/jazzy/setup.bash
cd /root/turtlebot3_ws && source install/setup.bash

TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL:-burger}

# Default spawn position (from turtlebot3_house.launch.py)
X_POSE=${1:--2.0}
Y_POSE=${2:--0.5}

echo "========================================="
echo "  TurtleBot3 Respawn Script"
echo "========================================="
echo "Model: $TURTLEBOT3_MODEL"
echo "Position: x=$X_POSE, y=$Y_POSE"
echo "========================================="

# Kill existing bridge and spawn processes
echo "Cleaning up existing nodes..."
pkill -f "parameter_bridge" 2>/dev/null || true
pkill -f "image_bridge" 2>/dev/null || true
pkill -f "spawn_turtlebot3" 2>/dev/null || true
sleep 1

# Remove existing robot from simulation (if any)
echo "Removing existing robot from simulation..."
ros2 service call /world/default/remove_entity gz_msgs.srv.EntityFactory "name: '$TURTLEBOT3_MODEL'" 2>/dev/null || true
sleep 1

# Respawn the robot with all bridges
echo "Respawning TurtleBot3 with bridges..."
ros2 launch turtlebot3_gazebo spawn_turtlebot3.launch.py \
    x_pose:=$X_POSE \
    y_pose:=$Y_POSE &

# Wait for spawn to complete
sleep 3

echo ""
echo "========================================="
echo "  Respawn complete!"
echo "  Teleop should now be functional."
echo "  If not, restart teleop in another terminal:"
echo "    ros2 run turtlebot3_teleop teleop_keyboard"
echo "========================================="
