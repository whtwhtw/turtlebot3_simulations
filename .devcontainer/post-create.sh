#!/bin/bash
set -e

echo "=== TurtleBot3 Simulations 环境初始化 ==="

# 更新系统包
sudo apt-get update

# 安装常用开发工具
sudo apt-get install -y \
    gdb \
    vim \
    curl \
    git \
    python3-pip \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-image

# 安装 Python 扩展
pip3 install --user colcon-common-extensions

# 配置 ROS2 环境
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
fi

if ! grep -q "TURTLEBOT3_MODEL" ~/.bashrc; then
    echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
fi

# 创建工作空间目录（如果不存在）
mkdir -p /root/turtlebot3_ws/src

# 如果源码未链接，创建符号链接
if [ ! -L /root/turtlebot3_ws/src/turtlebot3_simulations ]; then
    ln -sf /workspace /root/turtlebot3_ws/src/turtlebot3_simulations
fi

# 编译项目
cd /root/turtlebot3_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install 2>&1 | tail -20

echo "=== 初始化完成 ==="
echo "提示: 运行 'source install/setup.bash' 加载环境"
