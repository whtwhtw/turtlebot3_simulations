#!/bin/bash
# 测试自动导航建图流程 (slam_toolbox)

echo "===== 步骤 0: 清理旧进程 ====="
docker exec turtlebot3-sim bash -c "
    # 收集所有 Gazebo 和相关进程的 PID
    PIDS=\$(ps aux | grep -E 'gz sim|gz server|gz client|ign gazebo|robot_state_pub|ros_gz_bridge|turtlebot3_drive|slam_toolbox|sync_slam_tool' | grep -v grep | awk '{print \$2}' | tr '\n' ' ')
    if [ -n \"\$PIDS\" ]; then
        echo \"正在清理旧进程 (PIDs: \$PIDS)...\"
        kill -9 \$PIDS 2>/dev/null || true
        sleep 3
        echo '旧进程已清理'
    else
        echo '无残留进程'
    fi
"
sleep 2

echo "===== 步骤 1: 启动 Gazebo 仿真 ====="
docker exec -d turtlebot3-sim bash -c "
    source /opt/ros/jazzy/setup.bash
    cd /root/turtlebot3_ws
    source install/setup.bash
    export TURTLEBOT3_MODEL=\${TURTLEBOT3_MODEL:-burger}
    ros2 launch turtlebot3_gazebo empty_world.launch.py
"
echo "等待 Gazebo 启动..."
sleep 15

echo "===== 步骤 2: 验证 Gazebo 已启动 ====="
docker exec turtlebot3-sim bash -c "source /opt/ros/jazzy/setup.bash && ros2 topic echo /clock --once 2>/dev/null | head -3"
echo ""

echo "===== 步骤 3: 启动 slam_toolbox SLAM ====="
docker exec -d turtlebot3-sim bash -c "
    source /opt/ros/jazzy/setup.bash
    cd /root/turtlebot3_ws
    source install/setup.bash
    ros2 launch turtlebot3_slam_toolbox slam_toolbox.launch.py use_sim_time:=true use_rviz:=false
"
echo "等待 slam_toolbox 启动..."
sleep 5

echo "===== 步骤 4: 验证 slam_toolbox ====="
docker exec turtlebot3-sim bash -c "source /opt/ros/jazzy/setup.bash && ros2 node list | grep slam_toolbox"
echo ""

echo "===== 步骤 5: 启动 turtlebot3_drive 自动导航 ====="
docker exec -d turtlebot3-sim bash -c "
    source /opt/ros/jazzy/setup.bash
    cd /root/turtlebot3_ws
    source install/setup.bash
    ros2 launch turtlebot3_gazebo turtlebot3_drive.launch.py use_sim_time:=true
"
echo "等待导航节点启动..."
sleep 3

echo "===== 步骤 6: 检查所有节点 ====="
echo "--- ROS2 Nodes ---"
docker exec turtlebot3-sim bash -c "source /opt/ros/jazzy/setup.bash && ros2 node list"
echo ""

echo "===== 步骤 7: 监控 cmd_vel (10秒) ====="
for i in 1 2 3 4 5; do
    echo "--- cmd_vel sample \$i ---"
    docker exec turtlebot3-sim bash -c "source /opt/ros/jazzy/setup.bash && ros2 topic echo /cmd_vel --once 2>/dev/null | head -8"
    sleep 2
done

echo ""
echo "===== 步骤 8: 检查 map 话题 ====="
docker exec turtlebot3-sim bash -c "source /opt/ros/jazzy/setup.bash && ros2 topic echo /map --once 2>/dev/null | head -10"

echo ""
echo "===== 测试完成 ====="
echo "如果 cmd_vel 有非零值，说明自动导航正常工作"
echo "如果 /map 有数据，说明 SLAM 建图正常"
