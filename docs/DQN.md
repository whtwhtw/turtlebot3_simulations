# DQN 强化学习训练文档

## 概述

TurtleBot3 DQN（Deep Q-Network）强化学习训练系统，用于在 Gazebo 仿真环境中训练机器人自主导航和避障能力。

## 目录结构

```
turtlebot3_machine_learning/
└── turtlebot3_dqn/
    ├── turtlebot3_dqn/
    │   ├── __init__.py
    │   ├── dqn_agent.py          # DQN 智能体（神经网络、训练、推理）
    │   ├── dqn_environment.py    # RL 环境节点（传感器数据、状态/奖励计算）
    │   ├── dqn_gazebo.py         # Gazebo 接口节点（目标点生成、环境重置）
    │   ├── dqn_test.py           # 训练模型测试节点
    │   ├── action_graph.py       # 动作空间可视化工具
    │   └── result_graph.py       # 训练结果可视化工具
    ├── launch/                   # Launch 文件
    ├── saved_model/              # 训练保存的模型 (.h5 + .json)
    └── setup.py
```

## ROS 2 节点

DQN 训练系统由 **三个独立节点** 组成，通过 ROS 2 话题和服务通信：

### 1. `dqn_gazebo`（节点名: `/gazebo_interface`）

| 属性 | 值 |
|------|-----|
| 功能 | Gazebo 环境接口，负责目标点生成、环境初始化、重置 |
| 启动 | `ros2 run turtlebot3_dqn dqn_gazebo <stage>` |

**提供的服务：**
- `/initialize_env` (Goal) — 初始化环境，生成随机目标点
- `/task_succeed` (Goal) — 任务成功回调，返回新目标点
- `/task_failed` (Goal) — 任务失败回调，返回新目标点

### 2. `dqn_environment`（节点名: `/rl_environment`）

| 属性 | 值 |
|------|-----|
| 功能 | RL 环境核心，处理传感器数据、状态构建、奖励计算、碰撞检测 |
| 启动 | `ros2 run turtlebot3_dqn dqn_environment` |

**提供的服务：**
- `/make_environment` (Empty) — 触发环境初始化
- `/reset_environment` (Dqn) — 重置环境，返回初始状态
- `/rl_agent_interface` (Dqn) — 接收动作，返回 (state, reward, done)

**订阅的话题：**
- `/odom` (Odometry) — 里程计数据
- `/scan` (LaserScan) — LiDAR 扫描数据

**发布的话题：**
- `/cmd_vel` (TwistStamped) — 速度控制指令

**状态向量 (26 维)：**
```
[goal_distance, goal_angle, lidar_0, lidar_1, ..., lidar_23]
```
- `goal_distance`: 到目标点的距离（标量）
- `goal_angle`: 到目标点的相对角度（标量）
- `lidar_0~23`: 前方 LiDAR 射线的均匀下采样值（24 个标量）

**奖励函数：**
- 朝向奖励: `1 - 2*|goal_angle|/π`
- 障碍物奖励: 基于前方障碍物距离的加权指数衰减
- 到达目标: `+100`
- 碰撞: `-50`
- 超时: `-50`

### 3. `dqn_agent`（节点名: `/dqn_agent`）

| 属性 | 值 |
|------|-----|
| 功能 | DQN 智能体核心，包含 Q 网络、经验回放、训练循环 |
| 启动 | `ros2 run turtlebot3_dqn dqn_agent --ros-args -p max_training_episodes:=1000 -p use_gpu:=true` |

**发布的话题：**
- `/get_action` (Float32MultiArray) — `[action, score, reward]`
- `/result` (Float32MultiArray) — 训练结果

**动作空间 (5 个离散动作)：**

| 动作 | 角速度 (rad/s) | 线速度 (m/s) | 描述 |
|------|----------------|--------------|------|
| 0 | +1.50 | 0.2 | 大角度左转 |
| 1 | +0.75 | 0.2 | 小角度左转 |
| 2 | 0.00 | 0.2 | 直行 |
| 3 | -0.75 | 0.2 | 小角度右转 |
| 4 | -1.50 | 0.2 | 大角度右转 |

**神经网络结构：**
```
Input(26) → Dense(512, relu) → Dense(256, relu) → Dense(128, relu) → Dense(5, linear)
```
- 总参数量: 178,693 (698 KB)
- 优化器: Adam (lr=0.0007)
- 损失函数: MSE

**训练参数：**
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_training_episodes` | 1000 | 最大训练轮次 |
| `use_gpu` | false | 是否使用 GPU 加速 |
| `model_file` | '' | 预训练模型路径 |
| `verbose` | true | 是否打印推理日志 |

**内部超参数：**
| 参数 | 值 |
|------|-----|
| 折扣因子 (γ) | 0.99 |
| 学习率 | 0.0007 |
| 初始 ε | 1.0 |
| 最小 ε | 0.05 |
| ε 衰减率 | 2000 |
| 经验回放容量 | 500,000 |
| 最小回放样本 | 5,000 |
| Batch size | 128 |
| 最大步数/回合 | 800 |
| 目标网络更新间隔 | 5000 步 |

## Gazebo 训练场景

| 场景 | Launch 文件 | 描述 |
|------|-------------|------|
| Stage 1 | `turtlebot3_dqn_stage1.launch.py` | 简单空旷环境 |
| Stage 2 | `turtlebot3_dqn_stage2.launch.py` | 少量障碍物 |
| Stage 3 | `turtlebot3_dqn_stage3.launch.py` | 中等复杂度 |
| Stage 4 | `turtlebot3_dqn_stage4.launch.py` | 复杂迷宫环境 |

## 训练启动流程

### 完整训练（推荐）

```bash
# 1. 启动容器
./turtlebot3_simulations.sh start

# 2. 安装 DQN 依赖（仅首次）
./turtlebot3_simulations.sh dqn_install_deps

# 3. 启动后台训练（Stage 1）
./turtlebot3_simulations.sh dqn_train_bg_1

# 或 Stage 2~4
./turtlebot3_simulations.sh dqn_train_bg_2
./turtlebot3_simulations.sh dqn_train_bg_3
./turtlebot3_simulations.sh dqn_train_bg_4
```

### 手动分步启动

```bash
# 在容器内执行：
source /opt/ros/jazzy/setup.bash
cd /root/turtlebot3_ws && source install/setup.bash

# 终端 1: 启动 Gazebo 仿真
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage1.launch.py

# 终端 2: 启动 dqn_gazebo
ros2 run turtlebot3_dqn dqn_gazebo 1

# 终端 3: 启动 dqn_environment
ros2 run turtlebot3_dqn dqn_environment

# 终端 4: 启动 dqn_agent
ros2 run turtlebot3_dqn dqn_agent --ros-args \
    -p max_training_episodes:=1000 \
    -p use_gpu:=true
```

### 后台训练 vs 前台训练

| 命令 | 说明 |
|------|------|
| `dqn_train_1` | 前台启动，阻塞终端，可实时查看日志 |
| `dqn_train_bg_1` | 后台启动，不阻塞终端 |

## 模型测试

```bash
# 使用保存的模型测试
./turtlebot3_simulations.sh dqn_test model1.h5
```

## 模型保存

训练过程中模型会自动保存到：
```
turtlebot3_machine_learning/turtlebot3_dqn/turtlebot3_dqn/saved_model/
```
- `*.h5` — 模型权重
- `*.json` — 训练参数（epsilon、step_counter、trained_episodes）

## 已知问题和修复记录

### Bug 1: Executor 嵌套旋转冲突

**现象：**
```
RuntimeError: Executor is already spinning
```

**原因：** `dqn_environment.py` 的服务回调函数中调用了 `rclpy.spin_until_future_complete()`，
而该回调本身已经在 executor 的 spin 循环中被调用，导致嵌套旋转冲突。

**修复：** 将同步等待改为异步回调模式。

```python
# 修复前（错误）
def make_environment_callback(self, request, response):
    future = self.initialize_environment_client.call_async(Goal.Request())
    rclpy.spin_until_future_complete(self, future)  # ❌ 在回调中调用 spin
    response_goal = future.result()
    return response

# 修复后（正确）
def make_environment_callback(self, request, response):
    future = self.initialize_environment_client.call_async(Goal.Request())
    future.add_done_callback(self._make_environment_done_cb)  # ✅ 异步回调
    return response

def _make_environment_done_cb(self, future):
    response_goal = future.result()
    # ... 处理结果
```

**受影响函数：**
- `make_environment_callback`
- `call_task_succeed`
- `call_task_failed`

**修复文件：** `turtlebot3_dqn/dqn_environment.py`

### Bug 2: NumPy 版本冲突

**现象：**
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.0.2
ImportError: ...
```

**原因：** Ubuntu 24.04 通过 apt 安装的 `python3-matplotlib` 是用 NumPy 1.x 编译的，
但 `pip install numpy>=2.0` 安装了 NumPy 2.x，导致 ABI 不兼容。

**修复：** 降级 NumPy 到 1.x 系列。

```bash
pip3 install --break-system-packages "numpy<2"
# 实际安装版本: numpy==1.26.4
```

### Bug 3: 状态维度不匹配

**现象：**
```
ValueError: cannot reshape array of size 182 into shape (1,26)
```

**原因：** LiDAR 有 360 个采样点，`front_ranges` 包含前方约 180 个射线数据。
环境返回的状态 = `goal_distance(1) + goal_angle(1) + front_ranges(180) = 182 维`，
但 DQN Agent 期望 `state_size = 26` 维（1 + 1 + 24）。

**修复：** 在 `calculate_state()` 中对 `front_ranges` 进行均匀下采样到 24 个值。

```python
# 修复前
def calculate_state(self):
    for var in self.front_ranges:  # ❌ 所有射线都加入状态
        state.append(float(var))

# 修复后
def calculate_state(self):
    num_lidar_bins = 24
    if len(self.front_ranges) > 0:
        front_array = numpy.array(self.front_ranges)
        indices = numpy.linspace(0, len(front_array) - 1, num_lidar_bins, dtype=int)
        sampled = front_array[indices].tolist()
    else:
        sampled = [3.5] * num_lidar_bins
    for var in sampled:  # ✅ 只取 24 个均匀采样的值
        state.append(float(var))
```

### Bug 4: ROS 2 上下文污染

**现象：**
```
rclpy._rclpy_pybind11.RCLError: failed to initialize wait set: the given context is not valid
rclpy._rclpy_pybind11.RCLError: failed to shutdown: rcl_shutdown already called
```

**原因：** 多次异常退出导致 `rclpy.shutdown()` 被重复调用，或 `rclpy.init()` 在已关闭的上下文上调用。

**修复：**
1. 完全重启 Docker 容器：`docker restart turtlebot3-sim`
2. 重置 ROS 2 daemon：`ros2 daemon stop && ros2 daemon start`
3. 避免在代码中多次调用 `rclpy.shutdown()`

## 训练监控

```bash
# 查看运行中的节点
docker exec turtlebot3-sim ros2 node list

# 查看 cmd_vel 速度指令
docker exec turtlebot3-sim ros2 topic echo /cmd_vel

# 查看训练进度
docker exec turtlebot3-sim ros2 topic echo /get_action

# 查看进程状态
docker exec turtlebot3-sim ps aux | grep dqn_ | grep -v grep
```

**正常训练进程（5 个）：**
```
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage1.launch.py  # Gazebo 仿真
gz sim -r -s -v4 ...                                            # Gazebo Server
gz sim -g -v4                                                   # Gazebo GUI
ros2 run turtlebot3_dqn dqn_gazebo 1                            # /gazebo_interface
ros2 run turtlebot3_dqn dqn_environment                         # /rl_environment
ros2 run turtlebot3_dqn dqn_agent                               # /dqn_agent
```

## GPU 训练

### 前提条件
- 容器启动时包含 `--gpus all --runtime=nvidia`
- NVIDIA Container Toolkit 已安装
- 宿主机 `nvidia-smi` 正常

### 验证 GPU 可用性
```bash
./turtlebot3_simulations.sh check_gpu
```

### TensorFlow GPU 警告说明
```
Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
```
这些是 TensorFlow 内部的重复注册警告，**不影响训练**，可以忽略。

```
XLA is disabling parallel compilation...
```
当 CUDA 驱动版本 (12.2) 低于 PTX 编译器版本 (12.5) 时出现，影响训练速度但不影响正确性。
