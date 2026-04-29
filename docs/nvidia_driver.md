# NVIDIA GPU 配置指南

> 本文档记录 Docker 容器内 NVIDIA GPU 配置的问题排查与解决方案，用于 DQN 强化学习训练的 GPU 加速。

## 一、环境要求

| 组件 | 要求 | 说明 |
|------|------|------|
| **GPU** | NVIDIA RTX 3090 等 | 支持 CUDA 的 NVIDIA 显卡 |
| **NVIDIA Driver** | 535+ | 宿主机驱动 |
| **CUDA Version** | 12.2+ | 驱动支持的 CUDA 版本 |
| **NVIDIA Container Toolkit** | 必需 | Docker GPU 支持 |
| **Docker** | 20.10+ | 容器运行时 |

## 二、问题描述

### 症状

在容器内执行 `nvidia-smi` 报错：

```bash
bash: nvidia-smi: command not found
```

TensorFlow 安装后验证失败：

```
I0000 00:00:1777338991.471531 cudart_stub.cc:31] Could not find cuda drivers on your machine, GPU will not be used.
Segmentation fault (core dumped)
```

### 原因分析

1. **容器缺少 `--runtime=nvidia`**：虽然 Docker 脚本有 `--gpus all`，但缺少 runtime 参数
2. **缺少环境变量**：`NVIDIA_VISIBLE_DEVICES` 未设置
3. **NVIDIA Container Toolkit 未安装或未配置**

## 三、解决方案

### 步骤 1：安装 NVIDIA Container Toolkit（宿主机）

```bash
# 检查是否已安装
nvidia-ctk --version

# 如未安装，执行以下命令：
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 验证
docker info | grep -i nvidia
# 应输出: Runtimes: io.containerd.runc.v2 nvidia runc
```

### 步骤 2：修改 `turtlebot3_simulations.sh` 脚本

在 `start_container()` 函数的 `docker run` 命令中添加 GPU 参数：

```bash
docker run -d \
    --name $CONTAINER_NAME \
    --privileged \
    --gpus all \
    --runtime=nvidia \                        # 新增
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -e TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL:-burger} \
    -e ROS_DOMAIN_ID=0 \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e NVIDIA_VISIBLE_DEVICES=all \           # 新增
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $PROJECT_DIR:/workspace \
    -v $PROJECT_DIR/turtlebot3_ws:/root/turtlebot3_ws \
    -w $WORKSPACE \
    --network host \
    $IMAGE_NAME \
    tail -f /dev/null
```

**关键参数说明：**

| 参数 | 作用 |
|------|------|
| `--gpus all` | 挂载所有 GPU |
| `--runtime=nvidia` | 使用 NVIDIA 容器运行时 |
| `NVIDIA_DRIVER_CAPABILITIES=all` | 启用所有 NVIDIA 驱动能力 |
| `NVIDIA_VISIBLE_DEVICES=all` | 显示所有 GPU 设备 |

### 步骤 3：修改 `.devcontainer/docker-compose.yml`

如果使用 VSCode Dev Container，需要同步更新 compose 配置：

```yaml
version: '3.8'
services:
  turtlebot3-sim:
    image: osrf/ros:jazzy-desktop-full
    container_name: turtlebot3-sim
    privileged: true
    runtime: nvidia                           # 新增
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
      - TURTLEBOT3_MODEL=burger
      - ROS_DOMAIN_ID=0
      - NVIDIA_DRIVER_CAPABILITIES=all        # 新增
      - NVIDIA_VISIBLE_DEVICES=all            # 新增
    deploy:                                   # 新增
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
      - ..:/workspace
      - ../turtlebot3_ws:/root/turtlebot3_ws
    working_dir: /root/turtlebot3_ws
    network_mode: host
    command: tail -f /dev/null
```

### 步骤 4：重建容器

**必须重建容器**，因为 GPU 参数在 `docker run` 时设置，无法动态修改：

```bash
# 停止并删除旧容器
./turtlebot3_simulations.sh stop
./turtlebot3_simulations.sh rm

# 创建新容器（会应用新的 GPU 参数）
./turtlebot3_simulations.sh start

# 进入容器
./turtlebot3_simulations.sh shell
```

### 步骤 5：验证 GPU 可用性

```bash
# 容器内执行 - 检查 nvidia-smi
nvidia-smi

# 预期输出：
# +---------------------------------------------------------------------------------------+
# | NVIDIA-SMI 535.247.01             Driver Version: 535.247.01   CUDA Version: 12.2     |
# |-----------------------------------------+----------------------+----------------------+
# |   0  NVIDIA GeForce RTX 3090        Off | 00000000:01:00.0  On |                  N/A |
# | 58%   47C    P8              46W / 370W |    494MiB / 24576MiB |      8%      Default |
# +-----------------------------------------+----------------------+----------------------+
```

## 四、安装 TensorFlow GPU 支持

### 安装脚本

项目提供自动化安装脚本 `turtlebot3_machine_learning/install_dqn_deps.sh`，包含：

- 配置代理（apt + pip）
- 使用清华镜像源加速
- 安装 `tensorflow[and-cuda]`（自带 CUDA 运行库）
- 验证 GPU 可用性

```bash
# 容器内执行
bash /workspace/turtlebot3_machine_learning/install_dqn_deps.sh

# 或宿主机执行
./turtlebot3_simulations.sh dqn_install_deps
```

### 验证 TensorFlow GPU

```python
import tensorflow as tf

# 查看 GPU 设备
gpus = tf.config.list_physical_devices('GPU')
print(f'发现 {len(gpus)} 个 GPU')
for gpu in gpus:
    print(f'  - {gpu}')

# 测试 GPU 计算
with tf.device('/GPU:0'):
    a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
    b = tf.constant([[1.0, 1.0], [1.0, 1.0]])
    c = tf.matmul(a, b)
    print(c)
```

## 五、启动 DQN GPU 训练

脚本已默认启用 GPU 训练（`-p use_gpu:=true`）：

```bash
# 前台训练（实时查看日志）
./turtlebot3_simulations.sh dqn_train_1

# 后台训练（不阻塞终端）
./turtlebot3_simulations.sh dqn_train_bg_1
```

训练启动时会显示：

```
[INFO] 启动 DQN 训练: Stage 1 (GPU 加速)...
```

## 六、常见问题排查

### Q1: `nvidia-smi` 命令不存在

**原因**：容器内未挂载 GPU

**解决**：
1. 确认 `--runtime=nvidia` 已添加到 `docker run`
2. 确认 NVIDIA Container Toolkit 已安装并配置
3. 重建容器（`stop → rm → start`）

### Q2: TensorFlow 报 `Could not find cuda drivers`

**原因**：TensorFlow 未安装 GPU 版本

**解决**：
```bash
pip3 install --break-system-packages "tensorflow[and-cuda]>=2.16"
```

### Q3: Segmentation fault

**原因**：CUDA 库与宿主机驱动版本不匹配

**解决**：
1. 检查驱动 CUDA 版本：`nvidia-smi` → `CUDA Version: 12.2`
2. 安装兼容的 TensorFlow 版本：
   ```bash
   # CUDA 12.2 对应 TensorFlow 2.17-2.18
   pip3 install --break-system-packages "tensorflow[and-cuda]==2.18.0"
   ```

### Q4: `docker info` 没有 nvidia runtime

**原因**：NVIDIA Container Toolkit 未配置

**解决**：
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
docker info | grep -i nvidia
```

### Q5: 只删除 Docker 缓存，不删除镜像和容器

```bash
# 删除构建缓存
docker builder prune -f

# 删除未使用的缓存（限制保留大小）
docker builder prune --keep-storage 10g -f
```

## 七、配置检查清单

使用以下命令快速检查配置是否正确：

```bash
# 宿主机检查
nvidia-smi                              # ✅ 应显示 GPU 信息
docker info | grep -i nvidia            # ✅ 应显示 nvidia runtime

# 容器内检查
./turtlebot3_simulations.sh shell
nvidia-smi                              # ✅ 应显示 GPU 信息
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
                                        # ✅ 应显示 [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

## 八、参考

- [NVIDIA Container Toolkit 官方文档](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [TensorFlow GPU 支持](https://www.tensorflow.org/install/gpu)
- [Docker GPU 文档](https://docs.docker.com/config/containers/resource_constraints/#gpu)
