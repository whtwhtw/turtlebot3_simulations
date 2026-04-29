#!/bin/bash
# DQN 训练依赖安装脚本
# 用法：在容器内执行 bash install_dqn_deps.sh
# 或使用宿主机脚本：./turtlebot3_simulations.sh dqn_install_deps

set -e

PROXY_HOST="127.0.0.1"
PROXY_PORT="7897"
PROXY_URL="http://${PROXY_HOST}:${PROXY_PORT}"

PIP_MIRROR="-i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    --proxy=${PROXY_URL}"

APT_PROXY_CONF="/etc/apt/apt.conf.d/99proxy.conf"

echo "[DQN] 配置 apt 代理: ${PROXY_URL}..."
echo "Acquire::http::Proxy \"${PROXY_URL}\";" > ${APT_PROXY_CONF}

echo "[DQN] 安装 TensorFlow 和相关依赖 (使用清华镜像源 + 代理)..."

# 安装系统依赖
# 安装系统依赖和 Python
apt-get update
apt-get install -y python3-pip

# 移除系统自带的 scipy (由 debian 安装，会导致 RECORD 冲突)
apt-get remove -y python3-scipy || true

# 安装 Python 依赖（使用清华镜像源 + 代理加速）
# 注意：Ubuntu 24.04 (Noble) 默认 Python 3.12，需使用兼容版本
# 使用 --ignore-installed 覆盖系统自带的 scipy
# 使用 tensorflow[and-cuda] 自带 CUDA 库
pip3 install --break-system-packages --ignore-installed $PIP_MIRROR \
    "tensorflow[and-cuda]==2.18.0" \
    "scipy>=1.12" \
    "numpy>=1.26,<2" \
    "keras>=3.0" \
    pyqt5 \
    pyqtgraph

# 设置环境变量避免 oneDNN 警告
echo 'export TF_ENABLE_ONEDNN_OPTS=0' >> /root/.bashrc

# 安装 NVIDIA Container Toolkit 支持（确保 GPU 可用）
# TensorFlow 2.x 默认包含 GPU 支持，需要确保 NVIDIA 驱动正确

# 安装 PyQt5 系统依赖（用于 action_graph 可视化）
apt-get install -y python3-pyqt5 python3-pyqtgraph 
# 安装 Ceres 库依赖（用于slam-toolbox）
apt-get install -y libsuitesparse-dev libceres-dev libgoogle-glog-dev libopenblas-dev liblapack-dev

# 清理代理配置
rm -f ${APT_PROXY_CONF}

echo "[DQN] 依赖安装完成！"
echo "[DQN] 验证安装..."
python3 -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} 已安装')" 2>/dev/null || {
    echo "⚠️ TensorFlow 验证失败，尝试降级安装..."
    pip3 install --break-system-packages $PIP_MIRROR "tensorflow[and-cuda]==2.17.0" 2>&1 | tail -5
}
python3 -c "import PyQt5; print('PyQt5 已安装')"
python3 -c "import numpy; print(f'NumPy {numpy.__version__} 已安装')"

echo ""
echo "[DQN] 验证 GPU 可用性..."
python3 << 'PYEOF'
import sys
try:
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f'✅ 发现 {len(gpus)} 个 GPU:')
        for gpu in gpus:
            print(f'   - {gpu}')
        print('GPU 训练可用')
    else:
        print('⚠️ TensorFlow 未发现 GPU，将使用 CPU 训练')
        print('如需 GPU 训练，请检查:')
        print('  1. 容器启动时添加 --gpus all')
        print('  2. NVIDIA Container Toolkit 已安装')
        print('  3. 宿主机 nvidia-smi 正常')
except Exception as e:
    print(f'❌ GPU 验证失败: {e}')
PYEOF
