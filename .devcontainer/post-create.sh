#!/bin/bash
set -e

ROS_DISTRO="jazzy"

echo "=== TurtleBot3 Simulations 环境初始化 ==="

# ---- apt 源配置 ----
# 修复 NOSPLIT 错误：容器使用 host 网络时，某些代理/防火墙会干扰 HTTPS
# 解决思路：完全替换为清华 HTTPS 镜像源，并清理导致冲突的内置源

# 1. 清理所有内置的 Ubuntu 和 ROS 源
#    Ubuntu 24.04 使用 DEB822 格式 (.sources)，不是传统的 .list
sudo rm -f /etc/apt/sources.list.d/ros*.sources /etc/apt/sources.list.d/ros*.list 2>/dev/null || true
sudo rm -f /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true

# 2. 备份并完全替换 sources.list 为清华镜像
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak 2>/dev/null || true
cat <<'SOURCES' | sudo tee /etc/apt/sources.list > /dev/null
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu noble main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu noble-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu noble-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu noble-security main restricted universe multiverse
SOURCES

# 3. 添加 ROS 2 Jazzy 源
echo ">>> 添加 ROS 2 源..."
sudo apt-get install -y -o Acquire::http::Proxy=false -o Acquire::https::Proxy=false \
    software-properties-common
sudo add-apt-repository -y universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 4. apt-get 更新（绕过代理）
echo ">>> 更新 apt 缓存..."
sudo apt-get update -o Acquire::http::Proxy=false -o Acquire::https::Proxy=false

# 安装常用开发工具
sudo apt-get install -y -o Acquire::http::Proxy=false -o Acquire::https::Proxy=false \
    gdb \
    vim \
    curl \
    git \
    python3-pip \
    ros-${ROS_DISTRO}-ros-gz-sim \
    ros-${ROS_DISTRO}-ros-gz-bridge \
    ros-${ROS_DISTRO}-ros-gz-image

# 安装 Python 扩展
pip3 install --user --break-system-packages colcon-common-extensions

# 配置 ROS2 环境
if ! grep -q "source /opt/ros/${ROS_DISTRO}/setup.bash" ~/.bashrc; then
    echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc
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
source /opt/ros/${ROS_DISTRO}/setup.bash
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
