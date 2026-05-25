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

#### 键盘控制 SLAM 建图详细指南

本章节介绍如何使用键盘手动控制 TurtleBot3，配合 slam_toolbox 进行实时建图。

##### 系统架构

```
键盘输入 → teleop_twiststamped_keyboard → /cmd_vel (TwistStamped) → ros_gz_bridge → Gazebo DiffDrive
                                                                    ↓
                                                            TurtleBot3 运动
                                                                    ↓
joint_states / scan / odom / tf → ros_gz_bridge → slam_toolbox → /map (OccupancyGrid) → rviz2
```

##### 启动步骤（4 个节点）

> **提示**: 以下每一步都可以在新终端中使用 `./turtlebot3_simulations.sh` 快捷命令启动，无需手动进入容器执行 `ros2 launch`。

**第一步：启动 Gazebo 仿真世界**

```bash
./turtlebot3_simulations.sh turtlebot3_world   # 带障碍物场景
# 或
./turtlebot3_simulations.sh empty_world        # 空世界
# 或
./turtlebot3_simulations.sh turtlebot3_house   # 室内房屋场景
```

> 如需在容器内手动启动，可执行：
> ```bash
> ./turtlebot3_simulations.sh shell
> source /root/turtlebot3_ws/install/setup.bash
> export TURTLEBOT3_MODEL=burger
> ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
> ```

**启动内容：**
- Gazebo Sim 服务器（gzserver）
- Gazebo 客户端 GUI（gzclient）
- robot_state_publisher
- ros_gz_bridge（Gazebo ↔ ROS2 消息桥接）
- spawn_turtlebot3（机器人模型生成）

**发布/订阅的 Topic：**
| Topic | 类型 | 方向 |
|-------|------|------|
| /clock | rosgraph_msgs/msg/Clock | GZ → ROS |
| /joint_states | sensor_msgs/msg/JointState | GZ → ROS |
| /odom | nav_msgs/msg/Odometry | GZ → ROS |
| /tf | tf2_msgs/msg/TFMessage | GZ → ROS |
| /scan | sensor_msgs/msg/LaserScan | GZ → ROS |
| /imu | sensor_msgs/msg/Imu | GZ → ROS |
| /cmd_vel | geometry_msgs/msg/TwistStamped | ROS → GZ |

**第二步：启动 RViz2 可视化**

新开终端：
```bash
./turtlebot3_simulations.sh rviz_slam
```

> 如需在容器内手动启动，可执行：
> ```bash
> ./turtlebot3_simulations.sh shell
> source /root/turtlebot3_ws/install/setup.bash
> ros2 launch turtlebot3_bringup rviz2.launch.py
> ```

**功能：** 实时显示激光雷达扫描、里程计、TF 树和 SLAM 构建的地图。

**第三步：启动 SLAM Toolbox**

新开终端：
```bash
./turtlebot3_simulations.sh slam_toolbox
```

> 如需在容器内手动启动，可执行：
> ```bash
> ./turtlebot3_simulations.sh shell
> source /root/turtlebot3_ws/install/setup.bash
> ros2 launch slam_toolbox online_sync_launch.py
> ```

**功能：** 实时接收激光雷达和里程计数据，构建 2D 栅格地图。

**节点名称：** `/slam_toolbox`

**订阅的 Topic：**
| Topic | 类型 | 用途 |
|-------|------|------|
| /scan | sensor_msgs/msg/LaserScan | 激光雷达数据 |
| /tf | tf2_msgs/msg/TFMessage | 坐标变换 |
| /clock | rosgraph_msgs/msg/Clock | 仿真时间 |

**发布的 Topic：**
| Topic | 类型 | 用途 |
|-------|------|------|
| /map | nav_msgs/msg/OccupancyGrid | 构建的地图 |
| /map_metadata | nav_msgs/msg/MapMetaData | 地图元数据 |
| /slam_toolbox/feedback | slam_toolbox/msg/Feedback | SLAM 状态反馈 |

**第四步：启动键盘控制**

新开终端：
```bash
./turtlebot3_simulations.sh teleop_slam
```

> 如需在容器内手动启动，可执行：
> ```bash
> ./turtlebot3_simulations.sh shell
> source /root/turtlebot3_ws/install/setup.bash
> ros2 run turtlebot3_teleop teleop_twiststamped_keyboard
> ```

**功能：** 读取键盘输入，发布 TwistStamped 速度指令到 `/cmd_vel`。

**节点名称：** `/teleop_twiststamped_keyboard`

##### 键盘控制方法

**布局说明**

采用与 `teleop_twist_keyboard` 相同的直观控制方式：

```
移动方向控制：
   u    i    o
   j    k    l
   m    ,    .

全向移动（按住 Shift）：
   U    I    O
   J    K    L
   M    <    >

Z轴升降：
   t : 上升 (+z)
   b : 下降 (-z)

速度调节：
   q/z : 同时增减线速度和角速度 ±10%
   w/x : 只增减线速度 ±10%
   e/c : 只增减角速度 ±10%

其他：
   任意非方向键 : 停止
   CTRL-C : 退出
```

**按键含义**

| 按键 | 线性速度 X | 角速度 Z | 运动方向 |
|------|-----------|---------|---------|
| `i` | + | 0 | 前进 |
| `,` | - | 0 | 后退 |
| `j` | 0 | + | 左转 |
| `l` | 0 | - | 右转 |
| `u` | + | + | 前进+左转 |
| `o` | + | - | 前进+右转 |
| `m` | - | - | 后退+右转 |
| `.` | - | + | 后退+左转 |
| `k` | 0 | 0 | 停止 |

**速度调节说明**

- 初始速度：线性 0.5 m/s，角速度 1.0 rad/s
- `w` 键每次增加线速度 10%
- `x` 键每次减少线速度 10%
- `e` 键每次增加角速度 10%
- `c` 键每次减少角速度 10%
- `q` / `z` 同时调整两者

##### 建图操作建议

1. **启动顺序**：严格按照上述 1→2→3→4 的顺序启动节点
2. **初始建图**：原地旋转 360° 建立初始地图
3. **探索环境**：使用 `i` 前进、`j`/`l` 转向，逐步探索整个环境
4. **避免过快**：建图时建议保持较低速度，使用 `x`/`c` 降低速度
5. **回环检测**：尽量回到已探索过的区域，帮助 slam_toolbox 进行回环检测
6. **保存地图**：

```bash
# 方法一：使用服务调用
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '/path/to/map'}}"

# 方法二：使用 slam_toolbox 插件
ros2 run slam_toolbox map_saver_cli --map /path/to/map
```

##### 验证 Topic 数据流

建图过程中可以使用以下命令验证数据流：

```bash
# 查看所有节点
ros2 node list

# 查看 /cmd_vel 是否有消息发布
ros2 topic hz /cmd_vel

# 查看 /cmd_vel 消息类型和内容
ros2 topic echo /cmd_vel

# 查看激光雷达数据
ros2 topic echo /scan

# 查看地图
ros2 topic echo /map

# 查看 TF 树
ros2 run tf2_tools view_frames
```

##### 常见问题

**键盘无法控制小车**

**原因：** `teleop_twist_keyboard` 发布的是 `Twist` 类型，而 ros_gz_bridge 订阅的是 `TwistStamped`，类型不匹配。

**解决：** 使用本项目提供的 `teleop_twiststamped_keyboard` 节点：

```bash
ros2 run turtlebot3_teleop teleop_twiststamped_keyboard
```

**地图不更新**

- 检查 `/scan` topic 是否有数据：`ros2 topic hz /scan`
- 检查 slam_toolbox 节点是否正常运行：`ros2 node info /slam_toolbox`
- 确认 `use_sim_time` 参数一致

**RViz 中地图显示异常**

- 确认 Fixed Frame 设置为 `map`
- 检查 TF 树是否完整：`map` → `odom` → `base_footprint` → `base_scan`

##### 停止顺序

完成建图后，按以下顺序停止节点（反向）：

1. 停止键盘控制（Ctrl+C）
2. 停止 SLAM Toolbox
3. 停止 RViz2
4. 停止 Gazebo

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
./turtlebot3_simulations.sh teleop             # 键盘控制节点 (turtlebot3_teleop, WASD 布局)
./turtlebot3_simulations.sh teleop_twist       # 键盘控制节点 (teleop_twist_keyboard, TwistStamped 类型)
./turtlebot3_simulations.sh respawn            # 重新生成小车 (Gazebo reset 后使用)
./turtlebot3_simulations.sh turtlebot3_drive   # 自动避障演示
```

#### 碰撞安全防护（防止撞障碍物失控）

**问题背景：** 键盘控制小车时，如果不小心撞到障碍物，由于物理引擎碰撞响应与持续的速度指令冲突，小车会出现抖动、旋转或"失控"现象。

**解决方案：** 启动碰撞安全节点，实时监测激光雷达数据，当检测到前方障碍物距离过近时自动发送停止指令。

##### 快速使用

```bash
# 方式 1: 默认参数启动（安全距离 0.15m，检测角度 ±30°）
./turtlebot3_simulations.sh collision_safety

# 方式 2: 保守参数启动（安全距离 0.25m，检测角度 ±45°，推荐新手使用）
./turtlebot3_simulations.sh collision_safety_safe

# 方式 3: 自定义参数启动（安全距离 0.20m，检测角度 ±40°）
./turtlebot3_simulations.sh collision_safety 0.20 40.0

# 停止碰撞安全节点
./turtlebot3_simulations.sh collision_safety_off
```

##### 完整使用示例

**场景 1: 键盘控制 + 碰撞保护（推荐）**

```bash
# 终端 1: 启动 Gazebo 仿真
./turtlebot3_simulations.sh turtlebot3_world

# 终端 2: 启动碰撞安全节点（默认参数）
./turtlebot3_simulations.sh collision_safety

# 终端 3: 启动键盘控制
./turtlebot3_simulations.sh teleop
```

**场景 2: SLAM 建图 + 碰撞保护**

```bash
# 终端 1: 启动仿真
./turtlebot3_simulations.sh turtlebot3_world

# 终端 2: 启动 RViz
./turtlebot3_simulations.sh rviz_slam

# 终端 3: 启动 SLAM Toolbox
./turtlebot3_simulations.sh slam_toolbox

# 终端 4: 启动碰撞安全节点（保守参数）
./turtlebot3_simulations.sh collision_safety_safe

# 终端 5: 启动键盘控制建图
./turtlebot3_simulations.sh teleop_slam
```

**场景 3: DQN 训练 + 额外安全层**

```bash
# 终端 1: 启动 DQN 训练
./turtlebot3_simulations.sh dqn_train_1

# 终端 2: 启动碰撞安全节点（防止训练过程中频繁碰撞损坏模型）
./turtlebot3_simulations.sh collision_safety 0.20 30.0
```

##### 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    碰撞安全防护架构                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  键盘控制终端                                                 │
│  ┌─────────────────┐                                        │
│  │ teleop_keyboard │ ── 发布 /cmd_vel (TwistStamped) ──┐    │
│  └─────────────────┘                                    │    │
│                                                         ↓    │
│  碰撞安全节点                                         ┌─────────────┐
│  ┌──────────────────┐    检测距离    │  ros_gz_bridge  │
│  │ collision_safety │ ←─────────────→ │                 │
│  │                  │   /scan        └─────────────┘
```

##### 参数配置说明

| 参数 | 默认值 | 说明 | 推荐值 |
|------|--------|------|--------|
| `safety_distance` | 0.15m | 安全距离阈值，低于此距离触发紧急停止 | 新手: 0.25m<br>熟练: 0.15m |
| `front_angle_range` | 30.0° | 前方检测角度范围（正前方 ± 角度） | 开阔环境: 20°<br>复杂环境: 45° |
| `enable_logging` | true | 是否启用日志输出 | 调试: true<br>生产: false |
| `continuous_stop` | true | 紧急停止状态下是否持续发布停止指令 | 推荐: true |

**参数调整建议：**

| 场景 | safety_distance | front_angle_range | 说明 |
|------|----------------|-------------------|------|
| 空旷环境快速建图 | 0.10m | 20° | 减少误触发，提高建图效率 |
| 标准障碍物环境 | 0.15m | 30° | 默认配置，平衡安全与效率 |
| 复杂密集障碍物 | 0.25m | 45° | 更早触发停止，保护小车 |
| 新手学习阶段 | 0.30m | 60° | 最大安全裕度，避免碰撞 |

##### 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    碰撞检测工作流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 节点启动                                                 │
│     • 订阅 /scan 话题（激光雷达数据）                         │
│     • 准备发布 /cmd_vel（速度指令）                           │
│     • 输出初始化信息（安全距离、检测角度）                     │
│                                                             │
│  2. 实时监控（循环执行）                                      │
│     • 接收 LaserScan 消息                                    │
│     • 提取前方 ±front_angle_range 范围内的距离数据            │
│     • 计算最小距离 min_distance                               │
│                                                             │
│  3. 碰撞判断                                                 │
│     ├─ min_distance < safety_distance                        │
│     │   → 触发紧急停止                                        │
│     │   → 发布零速度指令到 /cmd_vel                           │
│     │   → 覆盖键盘控制的速度指令                              │
│     │   → 打印警告日志                                        │
│     │                                                        │
│     ├─ safety_distance <= min_distance < warning_distance    │
│     │   → 打印警告信息（不触发停止）                           │
│     │   → 如之前在紧急停止状态，解除停止                       │
│     │                                                        │
│     └─ min_distance >= warning_distance                      │
│         → 安全状态，正常监控                                   │
│         → 如之前在紧急停止状态，打印恢复日志                    │
│                                                             │
│  4. 停止指令发布                                             │
│     • 使用 TwistStamped 消息类型（兼容 ROS2 Jazzy）           │
│     • 设置 linear.x = 0.0, angular.z = 0.0                   │
│     • 根据 continuous_stop 参数决定发布频率                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**辅助工具详细说明：**

| 命令 | 功能描述 | 依赖节点/包 | 使用场景 | 注意事项 |
|------|----------|------------|----------|----------|
| `rviz` | 启动 RViz2 可视化工具，加载预配置的 RViz 布局文件，显示机器人状态、传感器数据、地图等 | `rviz2`（ROS2 可视化工具）<br>`turtlebot3_gazebo`（RViz 配置文件） | • 实时查看 LaserScan 点云数据 | • 观察 TF 坐标变换树 | • 监控地图构建进度 | • 调试导航路径规划 | 需先启动仿真或建图节点，否则 RViz 无数据可显示 |
| `rviz_slam` | 启动 SLAM 建图专用 RViz2，使用 `turtlebot3_bringup rviz2.launch.py`，预配置 SLAM 相关显示 | `rviz2`（ROS2 可视化工具）<br>`turtlebot3_bringup`（RViz 启动文件） | • SLAM 建图时实时显示地图 | • 查看激光雷达和里程计数据 | • 监控 TF 树 | 需先启动 Gazebo 和 SLAM 节点 |
| `teleop` | 启动键盘控制节点（`turtlebot3_teleop`），将 `WASD` 和箭头键转换为 `/cmd_vel` **TwistStamped** 速度指令发送给机器人 | `turtlebot3_teleop`（TurtleBot3 官方包） | • 手动控制小车移动 | • 建图时人工探索环境 | • 测试控制响应 | **需在新终端中运行**，焦点需在终端窗口内；发布 `TwistStamped` 类型（参数 `stamped:=True`） |
| `teleop_twist` | 启动键盘控制节点（`teleop_twist_keyboard`），将键盘输入转换为 `/cmd_vel` **TwistStamped** 速度指令。使用小键盘 `u/i/o/j/k/l` 布局 | `teleop_twist_keyboard`（ROS2 Jazzy 自带） | • 手动控制小车移动 | • 建图时人工探索环境 | • 与 `ros_gz_bridge` 等需要 `TwistStamped` 的节点配合 | **需在新终端中运行**；发布 `TwistStamped` 类型；如其他节点使用 `Twist`，可加参数 `-p stamped:=False` |
| `teleop_slam` | 启动 SLAM 建图专用键盘控制（`turtlebot3_teleop teleop_twiststamped_keyboard`），发布 `TwistStamped` 类型，uio/jkl 布局 | `turtlebot3_teleop`（TurtleBot3 官方包） | • SLAM 建图时精细控制小车 | • 需要速度调节功能 | • 与 ros_gz_bridge 的 TwistStamped 订阅兼容 | **需在新终端中运行**；专为 SLAM 建图设计；与 `teleop_twist` 使用不同的底层实现 |
| `respawn` | 在 Gazebo reset 或小车卡住后，重新生成小车到初始位置（默认坐标：x=-2.0, y=-0.5） | `turtlebot3_gazebo/spawn_turtlebot3.launch.py` | • Gazebo 重置后恢复小车位置 | • 小车陷入障碍物 | • 测试重新开始 | 会杀掉当前 teleop 进程，需重新启动键盘控制 |
| `turtlebot3_drive` | 启动自动避障演示节点，小车基于 LaserScan 数据自主移动，检测到障碍物时自动转向 | `turtlebot3_node/turtlebot3_drive`（自动避障节点） | • 演示自主导航能力 | • 无需键盘控制的自动探索 | • 验证传感器数据 | 避障策略较简单，仅基于距离阈值，复杂环境可能碰撞 |
| `collision_safety` | **启动碰撞检测与安全停止节点**，实时监测 `/scan` 数据，当障碍物距离 < 安全阈值时自动发送停止指令到 `/cmd_vel` | `turtlebot3_teleop/collision_safety`（新增安全节点） | • 键盘控制时防止碰撞障碍物 | • SLAM 建图时保护小车安全 | • DQN 训练时的额外安全层 | **需在新终端中运行**；与键盘控制节点同时运行；可自定义安全距离和检测角度参数 |
| `collision_safety_safe` | 使用保守参数启动碰撞安全节点（安全距离 0.25m，检测角度 ±45°） | 同上 | • 新手推荐配置 | • 复杂障碍物环境 | • 需要更大安全裕度的场景 | 更保守的参数，更早触发停止 |
| `collision_safety_off` | 停止碰撞安全节点 | - | • 临时关闭安全防护 | • 测试碰撞行为 | • 调试物理引擎 | 停止后不再有自动保护 |

**键盘控制键位说明：**

`teleop`（turtlebot3_teleop，WASD 布局）：

```
        W
      A S D
        X

W/A/S/D : 前进/左转/后退/右转
X        : 停止运动
其他键   : 退出控制节点
```

`teleop_twist`（teleop_twist_keyboard，小键盘布局）：

```
   u    i    o
   j    k    l
   m    ,    .

I        : 前进
J        : 左转
L        : 右转
,        : 后退
K        : 停止运动

t/b      : 上升/下降（z 轴）
q/z      : 增加/减少最大速度
w/x      : 仅增加/减少线速度
e/c      : 仅增加/减少角速度
其他键   : 退出控制节点
```

`teleop_slam`（turtlebot3_teleop teleop_twiststamped_keyboard，小键盘布局）：

```
   u    i    o
   j    k    l
   m    ,    .

I        : 前进
J        : 左转
L        : 右转
,        : 后退
K        : 停止运动

t/b      : 上升/下降（z 轴）
q/z      : 增加/减少最大速度
w/x      : 仅增加/减少线速度
e/c      : 仅增加/减少角速度
其他键   : 退出控制节点
```

> **注意**：`teleop_slam` 与 `teleop_twist` 键位布局相同，但使用不同的底层包实现（`turtlebot3_teleop` vs `teleop_twist_keyboard`）。

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

- 预装 VSCode 扩展：
  - `ms-python.python`, `ms-python.vscode-pylance` (Python 开发)
  - `ms-vscode.cpptools` (C++ 开发)
  - `redhat.vscode-yaml`, `redhat.vscode-xml` (ROS2 launch/参数文件)
  - `qwenlm.qwen-code-vscode-ide-companion`, `tencent-cloud.coding-copilot` (AI 助手)
- `postCreateCommand`: 自动执行环境初始化脚本
- `shutdownAction: stopContainer`: 关闭 VSCode 时停止容器（非删除）

> **注意**: 原 `ms-iot.vscode-ros` 扩展已于 2025-09 被归档废弃，已替换为上述扩展组合。

### `.devcontainer/post-create.sh`

首次创建容器时自动执行：
1. 安装常用开发工具（gdb, vim, git）
2. 安装 ROS-Gazebo 桥接包
3. 配置 `.bashrc` 环境变量
4. 创建符号链接并编译项目

## 六、常见问题

### Q: 键盘控制小车撞到障碍物后失控（抖动/旋转/卡住）

**A**: 这是由于物理引擎碰撞响应与持续的速度指令冲突导致的。推荐使用碰撞安全节点：

```bash
# 在新终端启动碰撞安全节点（与键盘控制同时运行）
./turtlebot3_simulations.sh collision_safety        # 默认参数
# 或
./turtlebot3_simulations.sh collision_safety_safe   # 保守参数（推荐新手）
```

**工作原理：**
- 实时订阅 `/scan` 激光雷达数据
- 检测前方 ±30° 范围内的障碍物距离
- 当距离 < 0.15m（默认）时，自动发送停止指令到 `/cmd_vel`
- 覆盖键盘控制的速度指令，防止持续撞击
- 距离恢复安全后，自动解除停止状态

**如果已经失控，如何恢复正常：**

| 场景 | 操作 | 效果 |
|------|------|------|
| 轻微碰撞，小车卡住 | 在键盘控制终端按 `k` 键（停止） | 停止速度指令，物理引擎会恢复 |
| 严重碰撞，小车翻转 | `./turtlebot3_simulations.sh respawn` | 重新生成小车到初始位置 |
| 小车陷入障碍物 | 在 Gazebo GUI 中右键小车 → Reset | 重置小车物理状态 |
| 完全失控，Gazebo 崩溃 | Ctrl+C 停止仿真 → 重新启动 | 完全重启仿真环境 |

**参数调整：**
```bash
# 自定义安全距离和检测角度
./turtlebot3_simulations.sh collision_safety 0.20 40.0
# 安全距离 0.20m，检测前方 ±40° 范围

# 停止碰撞安全节点
./turtlebot3_simulations.sh collision_safety_off
```

**替代方案（不推荐）：** 修改 `model.sdf` 中的车轮摩擦系数（从 100000.0 降低到 1.0），但会影响正常行驶手感。

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

## 九、碰撞安全节点详细文档

> 本节提供碰撞安全节点的完整技术文档，包括技术实现、日志示例、验证方法和高级用法。

### 9.1 技术实现

**节点名称：** `/collision_safety`

**节点类型：** Python ROS2 节点

**源码位置：** `turtlebot3_ws/src/turtlebot3/turtlebot3/turtlebot3_teleop/turtlebot3_teleop/script/collision_safety.py`

**Launch 文件：** `turtlebot3_ws/src/turtlebot3/turtlebot3/turtlebot3_bringup/launch/collision_safety.launch.py`

**消息接口：**

| 接口 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `/scan` | `sensor_msgs/msg/LaserScan` | 订阅 | 激光雷达数据（360° 扫描） |
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | 发布 | 速度指令（紧急停止时发布零速度） |

**核心算法：**

```python
1. 订阅 /scan 话题，接收 LaserScan 消息
2. 提取前方 ±front_angle_range 范围内的距离数据
3. 过滤无效值（0 或 inf）
4. 计算最小距离 min_distance
5. 碰撞判断：
   - min_distance < safety_distance → 触发紧急停止
   - safety_distance <= min_distance < warning_distance → 打印警告
   - min_distance >= warning_distance → 安全状态
6. 触发停止时，发布 TwistStamped 零速度指令到 /cmd_vel
```

### 9.2 日志输出示例

**正常启动日志：**

```
[INFO] [collision_safety]: ============================================================
[INFO] [collision_safety]: 碰撞安全节点已启动 (Collision Safety Node)
[INFO] [collision_safety]:   安全距离阈值: 0.15 m
[INFO] [collision_safety]:   警告距离阈值: 0.22 m
[INFO] [collision_safety]:   前方检测角度: ±30°
[INFO] [collision_safety]:   消息类型: TwistStamped
[INFO] [collision_safety]:   状态: 监控中 (Monitoring)
[INFO] [collision_safety]: ============================================================
```

**触发紧急停止日志：**

```
[WARN] [collision_safety]: ⚠️  碰撞风险！前方距离: 0.12m < 0.15m (安全阈值) - 触发紧急停止!
[INFO] [collision_safety]: ✅ 安全距离恢复: 0.25m > 0.15m - 解除紧急停止，可继续控制
```

**接近障碍物警告日志：**

```
[INFO] [collision_safety]: ⚡ 接近障碍物: 0.18m (警告阈值: 0.22m)
```

### 9.3 验证方法

**验证节点是否正常运行：**

```bash
# 方法 1: 查看节点列表
docker exec turtlebot3-sim ros2 node list | grep collision
# 应输出: /collision_safety

# 方法 2: 查看节点信息
docker exec turtlebot3-sim ros2 node info /collision_safety
# 应显示订阅和发布的 topic

# 方法 3: 查看节点日志
docker exec turtlebot3-sim ros2 topic echo /rosout | grep collision_safety

# 方法 4: 验证 /cmd_vel 是否有停止指令发布
docker exec turtlebot3-sim ros2 topic hz /cmd_vel
# 触发停止时应看到消息发布频率
```

**验证数据流：**

```bash
# 查看激光雷达数据
docker exec turtlebot3-sim ros2 topic echo /scan --once

# 查看速度指令
docker exec turtlebot3-sim ros2 topic echo /cmd_vel

# 查看所有活跃节点
docker exec turtlebot3-sim ros2 node list
```

### 9.4 常见问题

**Q1: 碰撞安全节点启动后立即停止小车**

**原因：** 安全距离设置过大，或激光雷达数据异常。

**解决：**
```bash
# 检查激光雷达数据是否正常
docker exec turtlebot3-sim ros2 topic echo /scan --once

# 增大安全距离阈值
./turtlebot3_simulations.sh collision_safety 0.30 20.0

# 或暂时关闭节点
./turtlebot3_simulations.sh collision_safety_off
```

**Q2: 节点未触发停止（碰撞无反应）**

**原因：** /scan 话题无数据，或节点未正确订阅。

**解决：**
```bash
# 检查 /scan 是否有数据
docker exec turtlebot3-sim ros2 topic hz /scan

# 检查节点是否订阅 /scan
docker exec turtlebot3-sim ros2 node info /collision_safety

# 重新启动节点
./turtlebot3_simulations.sh collision_safety_off
./turtlebot3_simulations.sh collision_safety
```

**Q3: 节点频繁触发停止（过于敏感）**

**原因：** 安全距离过小，或检测角度过大。

**解决：**
```bash
# 减小检测角度，增大安全距离
./turtlebot3_simulations.sh collision_safety 0.20 15.0

# 或使用保守配置
./turtlebot3_simulations.sh collision_safety_safe
```

**Q4: 与键盘控制冲突（小车无法移动）**

**原因：** 多个节点同时发布 /cmd_vel，优先级问题。

**解决：**
```bash
# 确保碰撞安全节点使用 continuous_stop:=false
docker exec turtlebot3-sim ros2 launch turtlebot3_bringup collision_safety.launch.py continuous_stop:=false

# 或仅在有碰撞风险时手动启动节点
./turtlebot3_simulations.sh collision_safety_off  # 正常控制时关闭
./turtlebot3_simulations.sh collision_safety      # 需要保护时启动
```

### 9.5 高级用法

**自定义 Launch 文件：**

创建自定义 launch 文件 `my_collision_safety.launch.py`：

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlebot3_teleop',
            executable='collision_safety',
            name='collision_safety',
            output='screen',
            parameters=[{
                'safety_distance': 0.20,
                'front_angle_range': 40.0,
                'enable_logging': True,
                'continuous_stop': True,
            }],
            remappings=[
                ('/scan', '/custom_scan'),  # 如需使用自定义话题
            ],
        ),
    ])
```

**与 Nav2 集成：**

在 Navigation2 中使用碰撞安全节点作为额外安全层：

```bash
# 启动 Nav2 导航
ros2 launch turtlebot3_navigation2 navigation2.launch.py

# 同时启动碰撞安全节点
./turtlebot3_simulations.sh collision_safety 0.25 30.0
```

**DQN 训练安全层：**

在 DQN 训练时添加碰撞保护，防止训练过程中频繁碰撞损坏模型：

```bash
# 终端 1: 启动 DQN 训练
./turtlebot3_simulations.sh dqn_train_1

# 终端 2: 启动碰撞安全节点（保守参数）
./turtlebot3_simulations.sh collision_safety 0.20 30.0
```

**多机器人场景：**

在多机器人仿真中，为每个机器人启动独立的碰撞安全节点：

```bash
# 机器人 1
docker exec turtlebot3-sim ros2 run turtlebot3_teleop collision_safety \
  --ros-args -p safety_distance:=0.15 \
  --remap /scan:=/robot1/scan \
  --remap /cmd_vel:=/robot1/cmd_vel

# 机器人 2
docker exec turtlebot3-sim ros2 run turtlebot3_teleop collision_safety \
  --ros-args -p safety_distance:=0.15 \
  --remap /scan:=/robot2/scan \
  --remap /cmd_vel:=/robot2/cmd_vel
```

---

> 📌 **提示**: 所有命令均在项目根目录执行。如遇问题，先执行 `./turtlebot3_simulations.sh shell` 进入容器排查。
