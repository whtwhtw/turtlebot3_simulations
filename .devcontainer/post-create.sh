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
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-image

# 安装 Python 扩展
echo "检查 colcon-common-extensions 安装状态..."
if ! dpkg -l | grep -q python3-colcon-common-extensions; then
    echo "正在安装 colcon-common-extensions..."
    sudo apt-get install -y python3-colcon-common-extensions
else
    echo "colcon-common-extensions 已安装"
fi

# 配置 ROS2 环境
if ! grep -q "source /opt/ros/jazzy/setup.bash" ~/.bashrc; then
    echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
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
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install 2>&1 | tail -20

echo "=== 初始化完成 ==="
echo "提示: 运行 'source install/setup.bash' 加载环境"
