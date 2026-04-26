# TurtleBot3 Simulations 学习指南

> 本项目是 ROBOTIS 官方的 ROS 2 仿真包，提供 Gazebo 物理仿真和轻量级 Fake Node 两套环境，
> 适合学习 SLAM、导航、强化学习和机器人运动学。

---

## 一、项目架构总览

```
turtlebot3_simulations/
├── turtlebot3_gazebo/          # 核心包：Gazebo 仿真
│   ├── src/                    # C++ 源码（驱动、插件）
│   ├── include/                # 头文件
│   ├── launch/                 # Python 启动文件
│   ├── params/                 # ros_gz_bridge 桥接 YAML
│   ├── worlds/                 # Gazebo 世界文件 (.world)
│   ├── models/                 # Gazebo 模型（机器人、场景）
│   ├── urdf/                   # URDF 机器人描述
│   ├── rviz/                   # RViz 可视化配置
│   └── nodes/                  # Python 节点
├── turtlebot3_fake_node/       # 轻量仿真（无物理引擎）
│   ├── src/                    # C++ 源码
│   ├── launch/                 # 启动文件
│   └── param/                  # 参数 YAML
└── turtlebot3_simulations/     # meta-package（仅声明依赖）
```

### 三大模块关系

```
turtlebot3_simulations (meta)
    ├── turtlebot3_gazebo       ← 完整物理仿真（Gazebo + 传感器 + 插件）
    └── turtlebot3_fake_node    ← 轻量仿真（仅运动学 + RViz 可视化）
```

---

## 二、各模块详解

### 模块 1：turtlebot3_gazebo — Gazebo 仿真环境

**定位**：核心模块，提供完整的物理仿真世界。

#### 1.1 Gazebo 插件（C++）

| 源文件 | 头文件 | 功能 |
|--------|--------|------|
| `src/obstacles.cpp` | `include/obstacles.hpp` | 360° 旋转障碍物，80秒/圈，用于 DQN 场景 |
| `src/obstacle1.cpp` | `include/obstacle1.hpp` | 移动障碍物，沿 7 个路径点以 0.1 m/s 循环运动 |
| `src/obstacle2.cpp` | `include/obstacle2.hpp` | 移动障碍物，沿 11 个路径点以 0.1 m/s 循环运动 |
| `src/traffic_light_plugin.cpp` | `include/traffic_light_plugin.hpp` | 交通灯纹理切换（绿5s→黄1s→红5s），用于 Autorace |
| `src/traffic_bar_plugin.cpp` | `include/traffic_bar_plugin.hpp` | 栏杆臂升降，每 10 秒切换，用于 Autorace |

**关键知识点**：
- 使用 GZ Sim (Gazebo Garden) 的 `gz::sim::System` 插件体系
- `GZ_ADD_PLUGIN` 宏注册系统，实现 `ISystemConfigure` + `ISystemPreUpdate`
- 通过 `Model::SetWorldPoseCmd()` 控制模型位姿

#### 1.2 ROS 节点（C++）

**`turtlebot3_drive` — 自动避障节点**

- 源码：`src/turtlebot3_drive.cpp`
- 原理：订阅 `/scan`（激光雷达）→ 状态机决策 → 发布 `/cmd_vel`

```
状态机：
GET_TB3_DIRECTION ──┬── 前方开阔 → TB3_DRIVE_FORWARD（前进 0.3 m/s）
                    ├── 左侧近   → TB3_RIGHT_TURN（右转 1.5 rad/s，转 30°）
                    └── 右侧近   → TB3_LEFT_TURN（左转 1.5 rad/s，转 30°）

主动探索：直行 30 次后自动转向更开阔的一侧
```

- 前方安全距离：1.2m
- 侧方安全距离：1.0m
- 探索转向角度：30°（`escape_range`）

#### 1.3 世界文件（.world）

| 世界文件 | 场景特点 | 用途 |
|----------|---------|------|
| `empty_world.world` | 空场地 | 基础功能测试 |
| `turtlebot3_world.world` | 六边形墙壁 + 障碍 | SLAM 建图、路径规划 |
| `turtlebot3_house.world` | 多房间 + 家具 | 复杂室内导航 |
| `turtlebot3_dqn_stage[1-4].world` | 渐进难度障碍 | 强化学习训练 |
| `turtlebot3_autorace_2020.world` | 赛道 + 交通设施 | 自动驾驶竞赛 |

#### 1.4 URDF 机器人描述

| URDF 文件 | 传感器配置 | 适用场景 |
|-----------|-----------|---------|
| `turtlebot3_burger.urdf` | LiDAR + IMU | 2D SLAM、基础导航 |
| `turtlebot3_burger_cam.urdf` | LiDAR + IMU + RGB 相机 | 视觉 SLAM |
| `turtlebot3_waffle.urdf` | LiDAR + IMU + 深度相机 | 3D 感知、导航 |
| `turtlebot3_waffle_pi.urdf` | LiDAR + IMU + RGB 相机 | 视觉导航 |

#### 1.5 桥接配置（params/）

Gazebo 和 ROS 2 之间通过 `ros_gz_bridge` 通信，YAML 文件定义话题映射：

```yaml
- ros_topic_name: "scan"          # ROS 话题
  gz_topic_name: "scan"           # Gazebo 话题
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS            # 数据流向
```

#### 1.6 Python 工具脚本

- **`nodes/auto_explore.py`**：自动探索节点，订阅激光雷达，遇障碍转向，适合快速建图
- **`launch/auto_slam.launch.py`**：Cartographer + turtlebot3_drive 一键自动建图
- **`launch/gazebo_reset_handler.py`**：Gazebo 状态复位处理

#### 1.7 启动文件（launch/）

| 入口 | 说明 |
|------|------|
| `main.launch.py` | 统一入口，通过 `world:=empty|world|house|dqn_stage*` 选择场景 |
| `empty_world.launch.py` | 空世界 |
| `turtlebot3_world.launch.py` | World 场景 |
| `turtlebot3_house.launch.py` | House 室内场景 |
| `turtlebot3_dqn_stage*.launch.py` | DQN 训练场景 |
| `turtlebot3_drive.launch.py` | 自动避障演示 |
| `teleop_keyboard.launch.py` | 键盘控制 |
| `rviz.launch.py` | RViz 可视化 |
| `auto_slam.launch.py` | 自动 SLAM 建图 |

---

### 模块 2：turtlebot3_fake_node — 轻量级仿真

**定位**：无 Gazebo 物理引擎的纯运动学仿真，启动快、资源占用低。

#### 2.1 工作原理

```
/cmd_vel (输入)
    │
    ▼
┌─────────────────────────────────────────┐
│          TurtleBot3 Fake Node            │
│                                          │
│  1. 差速运动学：                          │
│     v_left  = v - ω·L/2                  │
│     v_right = v + ω·L/2                  │
│                                          │
│  2. 轮速→角度：w = v / r                  │
│                                          │
│  3. 位姿积分：                            │
│     Δs = r·(w_r + w_l)·dt / 2           │
│     Δθ = r·(w_r - w_l)·dt / L           │
│     x += Δs·cos(θ + Δθ/2)               │
│     y += Δs·sin(θ + Δθ/2)               │
│     θ += Δθ                              │
│                                          │
│  4. 超时保护：1秒无 cmd_vel 自动停止      │
└─────────────────────────────────────────┘
    │
    ├──► /odom           (nav_msgs/Odometry)
    ├──► /joint_states   (sensor_msgs/JointState)
    └──► /tf             (tf2_msgs/TFMessage)
```

#### 2.2 关键源码

- `src/turtlebot3_fake_node.cpp`：主节点，100Hz 更新频率
- `param/burger.yaml` 等：轮距、轮半径等参数配置

#### 2.3 使用场景

| 场景 | 推荐原因 |
|------|---------|
| 算法快速验证 | 无需启动 Gazebo，秒级启动 |
| CI/CD 测试 | 资源占用低，适合自动化测试 |
| RViz 可视化调试 | TF 变换 + 里程计 + 关节状态 |
| 运动学控制算法 | 纯数学模型，无噪声干扰 |

#### 2.4 限制

- 无碰撞检测
- 无激光雷达/相机传感器数据
- 无物理引擎（摩擦力、惯性等）

---

### 模块 3：turtlebot3_simulations — meta-package

**定位**：聚合包，无任何代码，仅声明对 `turtlebot3_gazebo` 和 `turtlebot3_fake_node` 的依赖。
**学习重点**：无需单独学习，了解 ROS package 依赖组织方式即可。

---

## 三、推荐学习流程

### 阶段 1：环境搭建与初步体验（1-2 天）

```
1. 学习 Docker 环境配置
   → 阅读 docs/Docker启动指南.md
   → ./turtlebot3_simulations.sh start && build

2. 启动空世界，认识基本组件
   → ./turtlebot3_simulations.sh empty_world
   → 观察 Gazebo GUI，熟悉机器人模型

3. 启动 World 场景，体验键盘控制
   → ./turtlebot3_simulations.sh turtlebot3_world
   → 另开终端 ./turtlebot3_simulations.sh teleop
   → 手动驾驶机器人

4. 观察 ROS 话题和节点
   → ros2 node list
   → ros2 topic list
   → ros2 topic echo /scan
   → ros2 topic echo /odom
```

**关键概念理解**：
- Gazebo 是什么（物理仿真引擎）
- ROS 2 的话题通信模型
- `/cmd_vel` → Gazebo → `/odom` 的闭环

---

### 阶段 2：理解 URDF 和机器人模型（1-2 天）

```
1. 阅读 urdf/turtlebot3_burger.urdf
   → 理解 <link>、<joint>、<sensor> 标签
   → 查看传感器插件配置（LiDAR、IMU）

2. 阅读 params/turtlebot3_burger_bridge.yaml
   → 理解 ros_gz_bridge 的话题映射机制

3. 切换不同机器人模型
   → export TURTLEBOT3_MODEL=waffle
   → 对比 Burger vs Waffle 传感器差异
```

**关键概念理解**：
- URDF（Unified Robot Description Format）
- 传感器插件（Gazebo 插件如何发布传感器数据）
- 差速驱动运动学模型

---

### 阶段 3：深入 Gazebo 插件开发（2-3 天）

```
1. 阅读 src/obstacles.cpp
   → 理解 ObstaclesPlugin::Configure() 和 PreUpdate()
   → 理解 GZ_ADD_PLUGIN 宏

2. 阅读 src/traffic_light_plugin.cpp
   → 理解纹理切换的实现

3. 尝试修改插件参数
   → 修改旋转障碍物速度
   → 修改交通灯周期

4. 编写自定义 Gazebo 插件
   → 参考现有插件模板
   → 实现一个简单的追踪/跟随模型
```

**关键概念理解**：
- GZ Sim 插件系统架构（System、ISystemConfigure、ISystemPreUpdate）
- `EntityComponentManager` 和 `EventManager`
- `Model::SetWorldPoseCmd()` 控制位姿

---

### 阶段 4：理解 ROS 节点与运动学（2-3 天）

```
1. 精读 src/turtlebot3_drive.cpp
   → 理解状态机设计
   → 理解激光雷达数据处理（扇形分区、INF 处理、平均值计算）
   → 修改安全距离参数，观察行为变化

2. 精读 turtlebot3_fake_node/src/turtlebot3_fake_node.cpp
   → 理解差速运动学数学推导
   → 理解里程计位姿积分
   → 理解 TF 变换发布

3. 阅读 nodes/auto_explore.py
   → 理解 Python 节点的编写方式
   → 对比 auto_explore 和 turtlebot3_drive 的策略差异
```

**关键概念理解**：
- ROS 2 节点生命周期（init → spin → shutdown）
- 订阅/发布模式
- 差速运动学公式推导
- 坐标变换（TF2）
- 四元数 ↔ 欧拉角

---

### 阶段 5：SLAM 与导航实践（3-5 天）

```
1. 自动建图
   → ./turtlebot3_simulations.sh turtlebot3_house
   → ros2 launch turtlebot3_gazebo auto_slam.launch.py
   → 观察 Cartographer 建图过程

2. 手动建图
   → 启动 house 场景 + Cartographer
   → 用键盘控制完成建图
   → 保存地图：ros2 run nav2_map_server map_saver_cli

3. 导航测试
   → 使用保存的地图
   → 启动 Nav2 导航栈
   → 设置目标点，观察路径规划

4. 对比不同场景的建图效果
   → empty_world（无特征，建图困难）
   → turtlebot3_world（六边形墙壁，特征明显）
   → turtlebot3_house（复杂室内，适合完整测试）
```

**关键概念理解**：
- SLAM 基本原理（Cartographer、Gmapping）
- 2D 地图格式（Occupancy Grid）
- Nav2 导航栈（全局规划 + 局部规划 + 恢复行为）
- AMCL 定位

---

### 阶段 6：进阶与扩展（持续）

```
1. 强化学习方向
   → 研究 DQN 场景设计（stage1-4 的渐进难度）
   → 结合 turtlebot3_machine_learning 项目
   → 训练自定义避障策略

2. 传感器扩展
   → 在 URDF 中添加新传感器
   → 配置对应的 bridge YAML
   → 测试新传感器数据流

3. 自定义世界
   → 使用 Gazebo 编辑器创建 .world
   → 添加自定义模型
   → 编写对应的 launch 文件

4. 多机器人仿真
   → 在 Gazebo 中生成多个机器人
   → 配置独立的命名空间和话题
   → 实现协同导航

5. 真实机器人迁移
   → 理解仿真与实机的差异
   → 将仿真中验证的算法部署到实体 TurtleBot3
```

---

## 四、常用调试命令速查

```bash
# 查看所有运行中的节点
ros2 node list

# 查看所有话题
ros2 topic list

# 查看话题消息类型
ros2 topic info /scan

# 实时查看激光数据
ros2 topic echo /scan

# 查看机器人发布的 TF 树
ros2 run tf2_tools view_frames

# 查看节点日志
ros2 run rqt_console rqt_console

# 录制话题数据
ros2 bag record -a

# 回放录制数据
ros2 bag play <bag_folder>

# 查看 Gazebo 话题（仿真侧）
gz topic -l

# 查看 Gazebo 话题数据
gz topic -e -t /scan
```

---

## 五、核心概念总结

| 概念 | 说明 | 对应代码 |
|------|------|---------|
| 差速驱动 | 两轮差速运动学模型 | `turtlebot3_fake_node.cpp:181-244` |
| 状态机 | 避障决策状态流转 | `turtlebot3_drive.cpp:178-250` |
| Gazebo 插件 | C++ 系统插件控制物理模型 | `obstacles.cpp:30-66` |
| 话题桥接 | Gazebo ↔ ROS 2 消息映射 | `params/turtlebot3_burger_bridge.yaml` |
| URDF | 机器人结构描述（link + joint） | `urdf/turtlebot3_burger.urdf` |
| TF 变换 | 坐标系之间的关系 | `turtlebot3_fake_node.cpp:255-263` |
| Launch 文件 | Python 启动脚本，组织节点 | `launch/main.launch.py` |
