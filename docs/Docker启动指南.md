# TurtleBot3 Simulations Docker 启动指南

> 本文档介绍如何使用 Docker 容器化方式运行 TurtleBot3 仿真项目，参考 ROS2-start 项目架构改造。

## 一、环境要求

### 宿主机要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **操作系统** | Ubuntu 24.04 LTS | 推荐，其他发行版需自行验证 |
| **Docker** | 20.10+ | 容器运行时 |
| **NVIDIA Container Toolkit** | 必需（GPU 训练） | DQN 强化学习 GPU 加速 |
| **NVIDIA GPU** | RTX 3090 等 | 支持 CUDA 的显卡（可选） |
| **X11 Server** | 任意 | 用于显示 Gazebo/RViz GUI |

> **重要**: 本项目基于 ROS2 **Jazzy** (非 Humble)，使用 Gazebo Harmonic/Ionic 新版。

### 检查环境

```bash
# 检查 Docker
docker --version

# 检查 NVIDIA GPU（如有）
nvidia-smi

# 检查 NVIDIA Container Toolkit
docker info | grep -i nvidia  # 应显示 nvidia runtime

# 检查 X11 转发
echo $DISPLAY  # 应输出 :0 或类似值
```

> 📖 **GPU 配置详细指南**: 如需使用 GPU 进行 DQN 训练，请参考 [nvidia_driver.md](./nvidia_driver.md) 文档。

## 二、快速开始

### 1. 授权 X11 访问

```bash
# 允许 Docker 容器访问宿主机的 X11 显示
xhost +local:docker
```

### 2. 启动容器

```bash
cd /media/wht/J/Auto-driving/slam/仿真SLAM/turtlebot3_simulations
./turtlebot3_simulations.sh start
```

### 3. 编译项目

```bash
./turtlebot3_simulations.sh build
```

### 4. 启动仿真

```bash
# 选择任一场景启动
./turtlebot3_simulations.sh empty_world        # 空世界
./turtlebot3_simulations.sh turtlebot3_world   # 带障碍物场景
./turtlebot3_simulations.sh turtlebot3_house   # 室内房屋场景
./turtlebot3_simulations.sh fake_node          # 仅 RViz（无 Gazebo）
```

### 5. 控制机器人

新开终端执行：
```bash
./turtlebot3_simulations.sh teleop
```
使用键盘 `WASD` 或 `箭头键` 控制机器人移动。

## 三、VSCode Dev Container 集成

### 一键进入开发环境

1. 在 VSCode 中打开项目目录
2. 按 `Ctrl+Shift+P` → 输入 `Dev Containers: Reopen in Container`
3. 等待容器启动和扩展安装完成

### 开发体验

- ✅ 代码编辑与容器内执行无缝同步
- ✅ 内置 ROS2 扩展支持（代码补全、跳转）
- ✅ 集成终端直接运行 ROS2 命令
- ✅ 调试配置预置（F5 启动调试）

### 常用 VSCode 任务

按 `Ctrl+Shift+P` → `Tasks: Run Task`：

| 任务名 | 功能 |
|--------|------|
| `build` | 编译工作空间 |
| `run:empty_world` | 启动空世界仿真 |
| `run:fake_node` | 启动 RViz 仿真 |
| `rviz2` | 单独启动 RViz |

## 四、命令参考

### 容器管理

```bash
./turtlebot3_simulations.sh start    # 启动/创建容器
./turtlebot3_simulations.sh stop     # 停止容器
./turtlebot3_simulations.sh rm       # 删除容器
./turtlebot3_simulations.sh shell    # 进入容器 Bash
```

### 构建与编译

```bash
./turtlebot3_simulations.sh build    # 编译项目 (colcon build --symlink-install)
```

> `build` 命令会在容器内自动创建符号链接并执行 `colcon build`，无需手动进入容器编译。

### Gazebo 仿真场景

#### 基础仿真场景

```bash
./turtlebot3_simulations.sh empty_world        # Gazebo 空世界
./turtlebot3_simulations.sh turtlebot3_world   # World 场景（有障碍物）
./turtlebot3_simulations.sh turtlebot3_house   # House 室内场景
./turtlebot3_simulations.sh fake_node          # Fake Node（RViz only，无需 Gazebo）
./turtlebot3_simulations.sh gazebo             # 单独启动 Gazebo 客户端
```

**场景详细说明：**

| 命令 | 启动的 Launch 文件 | 功能描述 | 核心依赖节点/包 | 典型用途 |
|------|-------------------|----------|----------------|----------|
| `empty_world` | `turtlebot3_gazebo/empty_world.launch.py` | 启动纯空旷场景，仅包含地面和基础光照，无任何障碍物 | `gazebo_ros`（Gazebo 仿真引擎）<br>`turtlebot3_gazebo`（小车模型和传感器插件）<br>`robot_state_publisher`（发布 TF 坐标变换） | • 验证基础传感器数据（LaserScan、Odometry）<br>• 测试控制算法在无干扰环境的表现 |
| `turtlebot3_world` | `turtlebot3_gazebo/turtlebot3_world.launch.py` | 加载包含墙壁、柱子等障碍物的标准测试场景，适合导航算法验证 | 同上 + `nav2_bringup`（可选，用于 Navigation2 测试） | • 路径规划算法测试（A*、Dijkstra、DWA）<br>• 避障策略验证 |
| `turtlebot3_house` | `turtlebot3_gazebo/turtlebot3_house.launch.py` | 加载室内房屋场景，包含多房间、走廊、门窗等复杂结构 | 同上（需更多 GPU 渲染资源） | • SLAM 建图算法在复杂环境的测试 | • 室内导航和自主探索 |
| `fake_node` | `turtlebot3_fake_node/fake_node.launch.py` | **无需 Gazebo 物理引擎**，仅启动 RViz 并模拟传感器数据发布（虚拟 LaserScan、Odometry） | `turtlebot3_fake_node`（仿真节点）<br>`rviz2`（可视化工具） | • 无 GPU 环境下的算法快速验证 | • 仅测试控制逻辑和消息通信 |

#### DQN 强化学习场景

```bash
./turtlebot3_simulations.sh dqn_stage1         # DQN 强化学习 Stage 1（仅 Gazebo）
./turtlebot3_simulations.sh dqn_stage2         # DQN 强化学习 Stage 2（仅 Gazebo）
./turtlebot3_simulations.sh dqn_stage3         # DQN 强化学习 Stage 3（仅 Gazebo）
./turtlebot3_simulations.sh dqn_stage4         # DQN 强化学习 Stage 4（仅 Gazebo）
```

**场景详细说明：**

| 场景 | 难度递增 | 功能描述 | 依赖 | 典型用途 |
|------|----------|----------|------|----------|
| `dqn_stage1` | 最简单 | 小车处于空旷环境，障碍物极少，适合训练初期策略收敛 | `turtlebot3_gazebo` | 强化学习算法入门验证 |
| `dqn_stage2` | 简单 | 增加少量静态障碍物，需要初步避障能力 | 同上 | DQN 算法基础训练 |
| `dqn_stage3` | 中等 | 复杂障碍物布局，需要更高级的策略 | 同上 | 策略网络调优 |
| `dqn_stage4` | 困难 | 最复杂场景，密集障碍物和狭窄通道 | 同上 | 高级避障策略验证 |

**DQN 场景依赖的外部模块：** 需要配合强化学习训练框架（如 TensorFlow/PyTorch）使用，通过 ROS2 消息接口获取状态和发送动作。

#### DQN 强化学习训练

本项目集成了完整的 DQN（Deep Q-Network）训练流程，基于 `turtlebot3_machine_learning` 包。

##### 训练流程

**首次使用前，需要安装 TensorFlow 依赖：**

```bash
./turtlebot3_simulations.sh dqn_install_deps

# 容器内执行
./turtlebot3_simulations.sh shell
bash /workspace/turtlebot3_machine_learning/install_dqn_deps.sh
```

> ⚠️ TensorFlow 安装约需 500MB 磁盘空间，首次安装约 5-10 分钟。

然后启动训练：

```bash
# 方式 1: 前台启动训练（阻塞终端，可实时查看日志）
./turtlebot3_simulations.sh dqn_train_1         # Stage 1 训练
./turtlebot3_simulations.sh dqn_train_2         # Stage 2 训练
./turtlebot3_simulations.sh dqn_train_3         # Stage 3 训练
./turtlebot3_simulations.sh dqn_train_4         # Stage 4 训练

# 方式 2: 后台启动训练（不阻塞终端）
./turtlebot3_simulations.sh dqn_train_bg_1      # 后台 Stage 1
./turtlebot3_simulations.sh dqn_train_bg_2      # 后台 Stage 2
./turtlebot3_simulations.sh dqn_train_bg_3      # 后台 Stage 3
./turtlebot3_simulations.sh dqn_train_bg_4      # 后台 Stage 4
```

**训练架构说明：**

每个 `dqn_train` 命令会自动启动以下 4 个节点：
1. **Gazebo 仿真** (`turtlebot3_dqn_stage*.launch.py`): 物理仿真环境
2. **dqn_gazebo**: 目标点生成与重置管理
3. **dqn_environment**: 传感器数据处理、奖励计算
4. **dqn_agent**: DQN 神经网络训练（TensorFlow）

##### 训练监控

```bash
# 查看训练进度
docker exec turtlebot3-sim ros2 topic echo /get_action

# 查看训练日志
docker exec turtlebot3-sim ros2 node list | grep dqn

# 查看模型保存情况（训练过程中每 100 episodes 保存一次）
docker exec turtlebot3-sim ls -la /root/turtlebot3_ws/src/turtlebot3_dqn/saved_model/

# 验证 GPU 是否用于训练
docker exec turtlebot3-sim nvidia-smi
# 应看到 Python3 进程使用 GPU
```

**GPU 训练验证：**

```python
# 容器内执行 Python
python3 -c "
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f'✅ GPU 可用: {len(gpus)} 个')
    for gpu in gpus:
        print(f'   - {gpu}')
else:
    print('❌ 使用 CPU 训练，速度会很慢')
"
```

##### 模型测试

训练完成后，使用保存的模型进行测试：

```bash
# 测试训练好的模型（需提供模型文件名）
./turtlebot3_simulations.sh dqn_test model1.h5
```

##### 可视化界面

```bash
# 启动 DQN 动作可视化界面（需要 X11 转发）
./turtlebot3_simulations.sh dqn_action_graph
```

该界面实时显示：
- 5 个动作（左转/右转/直行等）的选择概率
- 当前奖励和累计奖励
- 训练进度

**训练参数配置：**

可通过 ROS2 参数调整训练行为：

```bash
# 自定义训练 episode 数（默认 1000）
ros2 run turtlebot3_dqn dqn_agent --ros-args \
  -p max_training_episodes:=2000 \
  -p epsilon_decay:=5000 \
  -p use_gpu:=true

# 加载已有模型继续训练
ros2 run turtlebot3_dqn dqn_agent --ros-args \
  -p model_file:=model1.h5
```

**DQN 训练工作流程：**

```
┌─────────────────────────────────────────────────────────────┐
│                    DQN 训练流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 启动训练（选择 stage 难度）                               │
│     ./turtlebot3_simulations.sh dqn_train_1                 │
│                                                             │
│  2. 系统自动启动以下组件：                                    │
│     • Gazebo 仿真环境（物理引擎、传感器模拟）                  │
│     • dqn_gazebo（目标点生成/重置）                          │
│     • dqn_environment（状态/奖励计算）                       │
│     • dqn_agent（神经网络训练）                              │
│                                                             │
│  3. 训练过程（自动循环）                                      │
│     • 观察状态（LaserScan + 目标距离/角度）                   │
│     • 选择动作（ε-greedy 策略）                              │
│     • 计算奖励（距离奖励 + 避障惩罚）                         │
│     • 更新 Q-network（经验回放 + 目标网络）                   │
│     • 每 100 episodes 保存模型                               │
│                                                             │
│  4. 监控训练进度                                             │
│     • 终端日志：实时打印 score、epsilon、memory length        │
│     • TensorBoard：~/turtlebot3_dqn_logs/gradient_tape/      │
│     • 可视化界面：dqn_action_graph（动作选择分布）            │
│                                                             │
│  5. 训练完成后测试模型                                       │
│     ./turtlebot3_simulations.sh dqn_test model1.h5          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**DQN 算法核心参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `state_size` | 26 | 状态空间维度（目标距离+角度+前方激光数据） |
| `action_size` | 5 | 动作空间（角速度：1.5, 0.75, 0, -0.75, -1.5） |
| `learning_rate` | 0.0007 | Adam 优化器学习率 |
| `discount_factor` | 0.99 | Q-learning 折扣因子 |
| `epsilon` | 1.0 → 0.05 | 探索率（从随机到贪婪策略） |
| `replay_memory` | 500,000 | 经验回放缓冲区大小 |
| `batch_size` | 128 | 训练批次大小 |
| `target_update` | 5,000 steps | 目标网络更新频率 |

**训练常见问题：**

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 训练不收敛 | epsilon 衰减过快 | 增大 `epsilon_decay` 参数 |
| 碰撞频繁 | 训练 episode 不足 | 增加 `max_training_episodes` |
| 模型未保存 | 目录权限问题 | 检查 `saved_model` 目录是否存在 |
| GPU 未使用 | 未启用 GPU 或配置错误 | 参考 [nvidia_driver.md](./nvidia_driver.md) |
| `nvidia-smi` 不可用 | 容器未挂载 GPU | 重建容器，确认 `--runtime=nvidia` |
| TensorFlow 段错误 | CUDA 版本不匹配 | 安装 `tensorflow[and-cuda]==2.18.0` |

**GPU 训练性能参考：**

| 硬件 | 训练速度（1000 episodes） | 说明 |
|------|--------------------------|------|
| RTX 3090 + GPU | ~2-3 小时 | 推荐配置 |
| CPU (8 核) | ~10-15 小时 | 速度慢 5-7 倍 |

**强化学习与 SLAM 的区别：**

| 特性 | DQN 训练 | SLAM 建图 |
|------|---------|----------|
| **目标** | 学习避障策略 | 构建环境地图 |
| **算法** | 深度强化学习（TensorFlow） | 图优化/粒子滤波 |
| **输出** | 神经网络模型（.h5） | 地图文件（.png + .yaml） |
| **训练时间** | 长（数百至数千 episodes） | 短（单次运行） |
| **实时性** | 训练后推理实时 | 建图过程实时 |
| **适用场景** | 自主导航、避障 | 环境建模、先验地图 |

#### 仿真节点通信架构

所有 Gazebo 仿真场景启动后，节点间通信关系如下：

```
┌─────────────────────────────────────────────────────────┐
│                    ROS2 节点通信拓扑                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  gazebo_ros (仿真引擎)                                   │
│    ↓ 发布 /scan (LaserScan)                              │
│    ↓ 发布 /odom (Odometry)                               │
│    ↓ 订阅 /cmd_vel (Twist) ← 控制指令输入                │
│                                                         │
│  robot_state_publisher                                   │
│    ↓ 发布 /tf 和 /tf_static (坐标变换)                   │
│                                                         │
│  [teleop_keyboard] (可选)                                │
│    → 发布 /cmd_vel ← 键盘输入                            │
│                                                         │
│  [slam_cartographer / slam_toolbox] (可选)               │
│    → 订阅 /scan 和 /odom                                 │
│    → 发布 /map 和更新 /tf                                │
│                                                         │
│  rviz2 (可选)                                            │
│    → 订阅所有话题进行可视化                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### SLAM 建图

#### 手动建图模式

```bash
# 方式 1: Cartographer SLAM
./turtlebot3_simulations.sh slam_cartographer  # Cartographer SLAM 建图 + RViz

# 方式 2: slam_toolbox SLAM
./turtlebot3_simulations.sh slam_toolbox       # slam_toolbox SLAM 建图 + RViz

# 配合键盘控制完成建图
./turtlebot3_simulations.sh teleop             # 新开终端，控制小车移动建图
```

#### 自动建图模式

```bash
# 自动 SLAM 建图（Cartographer + 自动避障，无需键盘控制）
./turtlebot3_simulations.sh auto_slam
```

#### 地图保存

```bash
./turtlebot3_simulations.sh save_map           # 保存地图（默认名: map）
./turtlebot3_simulations.sh save_map my_map    # 保存地图为 maps/my_map.png
```

**SLAM 功能详细说明：**

| 命令 | 启动的 Launch 文件 | 算法特点 | 核心依赖 | 适用场景 |
|------|-------------------|----------|----------|----------|
| `slam_cartographer` | `turtlebot3_cartographer/cartographer.launch.py` | **Google Cartographer**：基于图优化的 2D/3D SLAM 算法，支持回环检测，建图精度高 | `cartographer_ros`（Cartographer ROS 集成）<br>`ceres-solver`（优化求解器） | • 离线建图（事后处理）<br>• 需要高精度地图的场景<br>• 大区域建图 |
| `slam_toolbox` | `slam_toolbox/online_async_launch.py` | **slam_toolbox**：实时 2D SLAM，支持连续建图、地图编辑和序列化，资源占用较低 | `slam_toolbox`（独立 ROS2 包）<br>`liblapack-dev`（线性代数库） | • 实时在线建图 | • 资源受限环境 | • 需要地图持久化和复用 |
| `auto_slam` | `turtlebot3_gazebo/auto_slam.launch.py` | **自动建图**：组合 `turtlebot3_drive`（自动避障）+ Cartographer，小车自主探索环境完成建图 | `turtlebot3_drive`（自动避障节点）<br>`cartographer_ros` | • 无需人工干预的自主建图 | • 快速场景探索 |
| `save_map` | `nav2_map_server map_saver_cli` | 保存当前地图为 PNG 图像 + YAML 配置文件，供 Navigation2 使用 | `nav2_map_server`（地图服务） | • 建图完成后保存 | • 为导航提供先验地图 |

**SLAM 建图工作流程：**

```
┌─────────────────────────────────────────────────────────────┐
│                      SLAM 建图流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 启动仿真场景                                             │
│     ./turtlebot3_simulations.sh turtlebot3_world            │
│                                                             │
│  2. 启动 SLAM 节点（选择一种）                                │
│     ./turtlebot3_simulations.sh slam_cartographer           │
│     或                                                       │
│     ./turtlebot3_simulations.sh slam_toolbox                │
│                                                             │
│  3. 控制小车移动（二选一）                                    │
│     手动：./turtlebot3_simulations.sh teleop                │
│          （键盘 WASD 控制，缓慢移动避免碰撞）                  │
│     自动：./turtlebot3_simulations.sh auto_slam             │
│           （自动避障探索，无需人工）                           │
│                                                             │
│  4. 观察 RViz 中的地图构建进度                               │
│     - 白色区域：已探索的可行走空间                            │
│     - 黑色区域：检测到的障碍物                                │
│     - 灰色区域：未探索区域                                    │
│                                                             │
│  5. 建图完成后保存                                           │
│     ./turtlebot3_simulations.sh save_map [map_name]         │
│     输出：maps/[map_name].png + maps/[map_name].yaml        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Cartographer vs slam_toolbox 对比：**

| 特性 | Cartographer | slam_toolbox |
|------|-------------|--------------|
| **算法类型** | 图优化 SLAM | 基于粒子滤波的在线 SLAM |
| **回环检测** | ✅ 强，支持大规模场景 | ✅ 支持，但精度略低 |
| **实时性** | ⚠️ 计算密集，可能有延迟 | ✅ 轻量，实时性好 |
| **资源占用** | 较高（需 Ceres 求解器） | 较低 |
| **地图编辑** | ❌ 不支持运行时编辑 | ✅ 支持地图序列化和编辑 |
| **适合场景** | 离线高精度建图 | 在线实时建图 |

### 辅助工具

```bash
./turtlebot3_simulations.sh rviz               # 启动 RViz2 可视化
./turtlebot3_simulations.sh teleop             # 键盘控制节点（WASD / 箭头键）
./turtlebot3_simulations.sh respawn            # 重新生成小车（Gazebo reset 后使用）
./turtlebot3_simulations.sh turtlebot3_drive   # 自动避障演示
```

**辅助工具详细说明：**

| 命令 | 功能描述 | 依赖节点/包 | 使用场景 | 注意事项 |
|------|----------|------------|----------|----------|
| `rviz` | 启动 RViz2 可视化工具，加载预配置的 RViz 布局文件，显示机器人状态、传感器数据、地图等 | `rviz2`（ROS2 可视化工具）<br>`turtlebot3_gazebo`（RViz 配置文件） | • 实时查看 LaserScan 点云数据 | • 观察 TF 坐标变换树 | • 监控地图构建进度 | • 调试导航路径规划 | 需先启动仿真或建图节点，否则 RViz 无数据可显示 |
| `teleop` | 启动键盘控制节点，将 `WASD` 和箭头键转换为 `/cmd_vel` 速度指令发送给机器人 | `turtlebot3_teleop`（键盘控制包） | • 手动控制小车移动 | • 建图时人工探索环境 | • 测试控制响应 | **需在新终端中运行**，焦点需在终端窗口内；速度指令频率约 10Hz |
| `respawn` | 在 Gazebo reset 或小车卡住后，重新生成小车到初始位置（默认坐标：x=-2.0, y=-0.5） | `turtlebot3_gazebo/spawn_turtlebot3.launch.py` | • Gazebo 重置后恢复小车位置 | • 小车陷入障碍物 | • 测试重新开始 | 会杀掉当前 teleop 进程，需重新启动键盘控制 |
| `turtlebot3_drive` | 启动自动避障演示节点，小车基于 LaserScan 数据自主移动，检测到障碍物时自动转向 | `turtlebot3_node/turtlebot3_drive`（自动避障节点） | • 演示自主导航能力 | • 无需键盘控制的自动探索 | • 验证传感器数据 | 避障策略较简单，仅基于距离阈值，复杂环境可能碰撞 |

**键盘控制键位说明：**

```
        W
      A S D
        X

W/A/S/D : 前进/左转/后退/右转
X        : 停止运动
其他键   : 退出控制节点
```

### 环境配置

```bash
# 切换机器人模型
./turtlebot3_simulations.sh model burger       # 可选: burger | burger_cam | waffle | waffle_pi
./turtlebot3_simulations.sh start              # 重启容器使配置生效
```

### 诊断工具

```bash
./turtlebot3_simulations.sh diagnose           # 运行环境诊断，检查 ROS2 环境、包路径、编译状态等
```

> `diagnose` 会输出 ROS2 版本、工作空间状态、已安装的 turtlebot3 包及其路径，适合排查环境问题。

### 帮助信息

```bash
./turtlebot3_simulations.sh help               # 显示完整帮助信息
./turtlebot3_simulations.sh -h                 # 同上
./turtlebot3_simulations.sh --help             # 同上
```

## 五、配置文件说明

### `.devcontainer/docker-compose.yml`

```yaml
services:
  turtlebot3-sim:
    image: osrf/ros:jazzy-desktop-full  # ROS2 Jazzy + Gazebo 完整镜像
    environment:
      - TURTLEBOT3_MODEL=burger          # 默认机器人模型
      - ROS_DOMAIN_ID=0                  # ROS2 域 ID，避免多实例冲突
      - NVIDIA_DRIVER_CAPABILITIES=all   # GPU 加速支持
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]        # 启用 GPU
    volumes:
      - ..:/workspace                     # 项目源码挂载
      - ../turtlebot3_ws:/root/turtlebot3_ws  # 工作空间持久化
    network_mode: host                    # 使用宿主机网络，便于 ROS2 通信
```

### 依赖管理

编译前需要导入 TurtleBot3 依赖包：

```bash
# 容器内执行，使用代理（如有需要）
cd /root/turtlebot3_ws/src
mkdir -p turtlebot3 && cd turtlebot3
git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone https://github.com/ROBOTIS-GIT/turtlebot3.git
cd ../utils
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone https://github.com/ROBOTIS-GIT/hls_lfcd_lds_driver.git
```

> 网络受限环境下，宿主机需配置 `verge-mihomo` 代理（端口 **7897**）。

### `.devcontainer/devcontainer.json`

- 预装 VSCode 扩展：`ms-iot.vscode-ros`, `ms-python.python`
- `postCreateCommand`: 自动执行环境初始化脚本
- `shutdownAction: stopContainer`: 关闭 VSCode 时停止容器（非删除）

### `.devcontainer/post-create.sh`

首次创建容器时自动执行：
1. 安装常用开发工具（gdb, vim, git）
2. 安装 ROS-Gazebo 桥接包
3. 配置 `.bashrc` 环境变量
4. 创建符号链接并编译项目

## 六、常见问题

### Q: Gazebo 黑屏或无法显示

**A**: 检查 X11 转发配置：
```bash
# 宿主机执行
xhost +local:docker
echo $DISPLAY  # 确认不为空

# 如使用 SSH，添加 -X 或 -Y 参数
ssh -X user@host
```

### Q: 容器内无法访问网络

**A**: 脚本已配置 `network_mode: host`，如遇问题检查：
```bash
# 宿主机防火墙
sudo ufw status

# Docker 网络
docker network ls
```

### Q: 编译失败，缺少依赖

**A**: 确保依赖已正确克隆到 `/root/turtlebot3_ws/src/`：
```bash
./turtlebot3_simulations.sh shell
# 容器内执行
ls /root/turtlebot3_ws/src/turtlebot3/turtlebot3_msgs
ls /root/turtlebot3_ws/src/turtlebot3/turtlebot3
# 如目录为空，重新克隆（参考上方「依赖管理」章节）
```

### Q: Gazebo 渲染失败（黑屏/无法创建 drawable）

**A**: 确认 NVIDIA Container Toolkit 已安装并配置：
```bash
# 宿主机检查
nvidia-smi
docker info | grep -i runtime  # 应显示 nvidia

# 容器内检查 GPU
docker exec turtlebot3-sim nvidia-smi
# 如报错，重建容器: docker rm -f turtlebot3-sim && ./turtlebot3_simulations.sh start
```

### Q: DQN 训练如何使用 GPU 加速

**A**: 需要完成以下配置：

1. **安装 NVIDIA Container Toolkit**（宿主机）：
   ```bash
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

2. **重建容器**（应用 GPU 参数）：
   ```bash
   ./turtlebot3_simulations.sh stop
   ./turtlebot3_simulations.sh rm
   ./turtlebot3_simulations.sh start
   ```

3. **安装 TensorFlow GPU**：
   ```bash
   ./turtlebot3_simulations.sh dqn_install_deps
   ```

4. **验证 GPU**：
   ```bash
   ./turtlebot3_simulations.sh shell
   nvidia-smi
   ```

详细说明请参考 [nvidia_driver.md](./nvidia_driver.md)。

### Q: 只清理 Docker 缓存（不删除镜像和容器）

**A**: 使用以下命令：
```bash
# 删除构建缓存
docker builder prune -f

# 限制保留缓存大小
docker builder prune --keep-storage 10g -f
```

### Q: 如何切换 ROS2 域（多机器人仿真）

**A**: 修改环境变量：
```bash
# 方法 1: 启动前设置
export ROS_DOMAIN_ID=1
./turtlebot3_simulations.sh start

# 方法 2: 容器内临时设置
./turtlebot3_simulations.sh shell
export ROS_DOMAIN_ID=1
source /root/turtlebot3_ws/install/setup.bash
```

### Q: 容器磁盘空间不足

**A**: 清理无用镜像和卷：
```bash
# 查看磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a  # 谨慎使用，会删除未运行容器的镜像
```

## 七、与原生启动对比

| 特性 | Docker 方式 | 原生安装 |
|------|-----------|----------|
| **环境隔离** | ✅ 完全隔离，不污染宿主机 | ❌ 直接安装到系统 |
| **版本管理** | ✅ 镜像版本锁定，可回滚 | ❌ 依赖系统包管理器 |
| **团队共享** | ✅ 配置即代码，一键复现 | ❌ 需手动同步环境 |
| **启动速度** | ⚠️ 首次拉取镜像较慢 | ✅ 直接运行 |
| **GUI 支持** | ⚠️ 需配置 X11 转发 | ✅ 原生支持 |
| **GPU 加速** | ✅ 支持 NVIDIA Container Toolkit | ✅ 原生支持 |
| **DQN 训练** | ✅ 支持（需配置 GPU） | ✅ 原生支持 |

## 八、进阶使用

### 自定义镜像

如需预装额外依赖，创建 `.devcontainer/Dockerfile`：

```dockerfile
FROM osrf/ros:jazzy-desktop-full

# 安装项目特定依赖
RUN apt-get update && apt-get install -y \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /root/turtlebot3_ws
```

修改 `devcontainer.json` 的 `build` 字段引用该 Dockerfile。

### 持久化数据卷

如需持久化 `~/.ros` 等运行时数据：

```yaml
# docker-compose.yml 中添加
volumes:
  - ros-data:/root/.ros

volumes:
  ros-data:
```

### DQN 模型持久化

训练好的模型保存在容器内，需要复制到宿主机以防丢失：

```bash
# 容器内查看模型
docker exec turtlebot3-sim ls -la /root/turtlebot3_ws/src/turtlebot3_dqn/saved_model/

# 复制模型到宿主机
docker cp turtlebot3-sim:/root/turtlebot3_ws/src/turtlebot3_dqn/saved_model/ ./my_models/

# 重新训练后加载模型继续训练
./turtlebot3_simulations.sh shell
ros2 run turtlebot3_dqn dqn_agent --ros-args -p model_file:=model1.h5
```

### 网络代理配置

如在公司/学校网络下需要配置代理：

```bash
# apt 代理（容器内）
echo "Acquire::http::Proxy \"http://127.0.0.1:7897\";" > /etc/apt/apt.conf.d/99proxy.conf
apt-get update

# pip 代理（容器内）
pip3 install --proxy=http://127.0.0.1:7897 -i https://pypi.tuna.tsinghua.edu.cn/simple/ tensorflow
```

DQN 依赖安装脚本已内置代理配置，直接执行：

```bash
./turtlebot3_simulations.sh dqn_install_deps
```

### 多容器协作

如需分离仿真与算法开发：

```yaml
# 添加第二个服务
services:
  turtlebot3-sim:  # 仿真容器
    # ... 现有配置

  turtlebot3-dev:  # 开发容器
    image: osrf/ros:jazzy-desktop
    volumes:
      - ..:/workspace
    command: sleep infinity
```

---

> 📌 **提示**: 所有命令均在项目根目录执行。如遇问题，先执行 `./turtlebot3_simulations.sh shell` 进入容器排查。
