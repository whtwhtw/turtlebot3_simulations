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

# ==========================================
# VS Code 扩展配置说明
# 以下扩展通过 devcontainer.json 自动安装:
#   - ms-python.python / ms-python.vscode-pylance (Python 开发)
#   - ms-vscode.cpptools (C++ 开发)
#   - redhat.vscode-yaml / redhat.vscode-xml (ROS2 launch/参数文件)
#   - qwenlm.qwen-code-vscode-ide-companion (Qwen AI 助手)
#   - tencent-cloud.coding-copilot (腾讯 Codebuddy)
#   - Alibaba-Cloud.tongyi-lingma (通义灵码)
# 注意: ms-iot.vscode-ros 已于 2025-09 归档废弃，不再使用
# ==========================================

echo "=== VS Code 扩展配置检查 ==="

# 确保 VS Code Server 扩展目录存在且有正确权限
mkdir -p /root/.vscode-server/extensions
chmod 755 /root/.vscode-server/extensions

echo "✓ 扩展已配置为自动安装:"
echo "  - Python + Pylance, C/C++, YAML, XML"
echo "  - Qwen Code Companion, Tencent Cloud Codebuddy"
echo "  容器重建后会自动恢复"
