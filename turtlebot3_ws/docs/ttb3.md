# src/turtlebot3/ 目录深度解析

`src/turtlebot3/` 实际上包含两个 git 子仓库：

```
turtlebot3/          ← ROS 2 主包集合 (8个子包)
turtlebot3_msgs/     ← 自定义消息/服务/动作定义
```

---

## 一、`turtlebot3_msgs/` — 接口定义包

| 类型 | 名称 | 字段 | 用途 |
|------|------|------|------|
| **msg** | `SensorState` | bumper, cliff, sonar, illumination, battery, encoder 等 | 传感器综合状态 |
| **msg** | `Sound` | value (uint8) | 蜂鸣器模式 (OFF/ON/LOW_BATTERY/ERROR) |
| **msg** | `VersionInfo` | hardware, firmware, software | 硬件/固件/软件版本 |
| **srv** | `Sound` | req: value → resp: success, message | 控制蜂鸣器 |
| **srv** | `Dqn` | req: action, init → resp: state, reward, done | DQN 强化学习接口 |
| **srv** | `Goal` | req: 无 → resp: pose_x, pose_y, success | 查询目标位置 |
| **action** | `Patrol` | Goal: Vector3(x=模式, y=边长, z=迭代) → Result: string → Feedback: string | 自动巡逻 |

---

## 二、`turtlebot3/` — 9 个子包详解

### 1. `turtlebot3` (元包 meta package)

- **作用**：什么都不编译，仅声明对其他 8 个子包的依赖
- **依赖子包**：
  - `turtlebot3_bringup`, `turtlebot3_cartographer`, `turtlebot3_description`
  - `turtlebot3_example`, `turtlebot3_navigation2`, `turtlebot3_node`
  - `turtlebot3_teleop`, `turtlebot3_slam_toolbox`（新增）
- **用途**：`apt install ros-$ROS_DISTRO-turtlebot3` 一键安装全部

---

### 2. `turtlebot3_node` — 核心硬件驱动节点 ⭐ 重点

| 属性 | 值 |
|------|---|
| 语言 | C++17 |
| 可执行文件 | `turtlebot3_ros` |
| 通信方式 | USB 串口 ↔ OpenCR 控制器 (Dynamixel SDK) |

**源文件架构**：

```
src/
  node_main.cpp               # 入口：创建 TurtleBot3 + DiffDriveController 节点
  turtlebot3.cpp              # 主节点类：初始化 SDK、传感器轮询、cmd_vel 处理
  dynamixel_sdk_wrapper.cpp   # OpenCR 串口通信封装 (同步读写、线程安全)
  diff_drive_controller.cpp   # 差速运动学封装
  odometry.cpp                # 里程计计算 (编码器 / 编码器+IMU 时间同步融合)
  devices/
    motor_power.cpp           # /motor_power 服务 (电机电源开关)
    reset.cpp                 # /reset 服务 (IMU 校准 + 里程计重置)
    sound.cpp                 # /sound 服务 (蜂鸣器)
  sensors/
    battery_state.cpp         # → /battery_state
    imu.cpp                   # → /imu + /magnetic_field
    joint_state.cpp           # → /joint_states
    sensor_state.cpp          # → /sensor_state (自定义 msg)
```

**关键概念 — OpenCR 控制表**：

| 地址范围 | 内容 |
|---------|------|
| 26-46 | 按钮、碰撞、光照、IR、声呐、电池 |
| 60-108 | IMU: 角速度、加速度、磁力、四元数 |
| 120-140 | 左右轮编码器位置/速度 |
| 150-170 | 速度指令 (线速度/角速度) |

**学习要点**：
- 理解节点如何订阅 `cmd_vel` → 写入控制表 → OpenCR 驱动电机
- 里程计两种模式：纯编码器 vs 编码器+IMU 时间同步融合
- 50ms 传感器轮询 + 100ms 心跳机制

---

### 3. `turtlebot3_bringup` — 启动脚本

```
launch/
  robot.launch.py              # ⭐ 主启动文件 (启动驱动 + LDS + state_publisher)
  turtlebot3_state_publisher.launch.py  # robot_state_publisher
  camera.launch.py             # 摄像头 (camera_ros)
  rviz2.launch.py              # 可视化
param/
  burger.yaml / waffle.yaml / waffle_pi.yaml  # 节点参数
```

**学习要点**：
- 理解 launch.py 如何组合多个节点
- 通过环境变量 `TURTLEBOT3_MODEL` 动态选择模型
- Humble 用 `Twist`，其他发行版用 `TwistStamped`

---

### 4. `turtlebot3_description` — URDF 模型

```
urdf/
  turtlebot3_burger.urdf       # Burger: 最小巧，差速 + 单万向轮
  turtlebot3_waffle.urdf       # Waffle: 带 RealSense R200 相机
  turtlebot3_waffle_pi.urdf    # Waffle Pi: 不同相机模块
  common_properties.urdf       # 共享颜色材质
meshes/
  bases/ wheels/ sensors/      # STL/DAE 三维模型
```

**TF 树结构**：
```
base_footprint → base_link → wheel_left/right, caster_back, imu_link, base_scan
```

---

### 5. `turtlebot3_teleop` — 键盘遥控

```
turtlebot3_teleop/script/teleop_keyboard.py
```

| 按键 | 功能 |
|------|------|
| w/x | 增减线速度 |
| a/d | 增减角速度 |
| s/空格 | 紧急停止 |

不同模型有不同速度上限（Burger: 0.22 m/s, Waffle: 0.26 m/s）

---

### 6. `turtlebot3_example` — Python 示例

| 可执行文件 | 功能 |
|-----------|------|
| `turtlebot3_interactive_marker` | RViz 交互式标记控制 |
| `turtlebot3_obstacle_detection` | 激光雷达障碍物检测停 |
| `turtlebot3_patrol_server` | 巡逻 action 服务端 (方形/三角形路径) |
| `turtlebot3_patrol_client` | 巡逻 action 客户端 (终端交互) |
| `turtlebot3_absolute_move` | 绝对坐标导航 (odom 坐标系) |
| `turtlebot3_relative_move` | 相对位姿移动 (转向→前进→调朝向) |

---

### 7. `turtlebot3_cartographer` — SLAM 建图

```
launch/
  cartographer.launch.py       # cartographer_node + occupancy_grid + rviz
  occupancy_grid.launch.py     # 单独启动 occupancy_grid_node
config/
  turtlebot3_lds_2d.lua        # 2D 建图配置 (激光 0.12-3.5m, 用里程计不用 IMU)
rviz/
  tb3_cartographer.rviz        # SLAM 可视化配置
```

**`turtlebot3_lds_2d.lua` 关键参数**：

| 参数 | 值 | 说明 |
|------|-----|------|
| `tracking_frame` | `imu_link` | 跟踪帧 |
| `published_frame` | `odom` | 发布帧 |
| `use_odometry` | `true` | 使用里程计 |
| `use_imu_data` | `false` | 不使用 IMU 数据 |
| `min_range` / `max_range` | `0.12` / `3.5` | 激光雷达范围 |
| `use_online_correlative_scan_matching` | `true` | 在线扫描匹配 |

---

### 8. `turtlebot3_slam_toolbox` — SLAM Toolbox 替代方案

> 自定义扩展包，提供与 Cartographer 可选的 SLAM Toolbox 实现。

```
launch/
  slam_toolbox.launch.py       # sync_slam_toolbox_node + rviz
config/
  turtlebot3_lds_2d.yaml       # SLAM Toolbox 参数配置（对标 cartographer 的 lua）
rviz/
  tb3_slam_toolbox.rviz        # SLAM Toolbox 可视化配置
```

**与 Cartographer 对比**：

| 对比维度 | Cartographer | SLAM Toolbox |
|---------|-------------|-------------|
| 内存占用 | 较高（全局子图优化） | 较低（稀疏 pose graph） |
| 建图速度 | 较慢（分支定界匹配） | 较快（局部增量优化） |
| 长期运行 | 可能内存膨胀 | 支持地图持久化/在线离线切换 |
| 配置格式 | Lua 文件 | YAML 文件 |
| ROS 2 集成 | 需单独安装 | Humble/Jazzy 默认包含 |
| 适用场景 | 学术/教程/论文复现 | 实际项目部署/长期运行 |

**`turtlebot3_lds_2d.yaml` 关键参数**：

| 参数 | 值 | 说明 |
|------|-----|------|
| `mode` | `mapping` | SLAM 模式（`localization` 加载已有地图） |
| `odom_frame` | `odom` | 里程计帧 |
| `map_frame` | `map` | 地图帧 |
| `base_frame` | `base_footprint` | 机器人基座帧 |
| `max_laser_range` | `3.5` | 最大激光范围 |
| `resolution` | `0.05` | 地图分辨率 (m/像素) |
| `loop_closure_enabled` | `true` | 启用回环检测 |

---

### 9. `turtlebot3_navigation2` — Nav2 自主导航

```
launch/
  navigation2.launch.py        # Nav2 bringup + rviz
map/
  map.yaml + map.pgm           # 默认 20x20m 地图
param/
  burger.yaml (等)             # AMCL, DWB, Navfn, 代价地图, 行为树等
```

**Nav2 参数模块**：

| 模块 | 作用 |
|------|------|
| `amcl` | 自适应蒙特卡洛定位 |
| `controller_server` | DWB 局部规划器 |
| `planner_server` | Navfn 全局规划器 |
| `global/local_costmap` | 代价地图 |
| `behavior_server` | 旋转/后退等行为 |
| `collision_monitor` | 碰撞监控 |

---

## 三、学习路径建议

```
第1步: turtlebot3_teleop/       ← 最简单，理解 topic 通信
第2步: turtlebot3_description/   ← 理解 URDF/TF
第3步: turtlebot3_bringup/       ← 理解 launch 文件组织
第4步: turtlebot3_node/          ← 核心节点，理解硬件通信 ⭐
第5步: turtlebot3_msgs/          ← 理解自定义接口
第6步: turtlebot3_example/       ← 学习 action/service 示例
第7步: turtlebot3_cartographer/  ← SLAM 建图 (Cartographer)
第8步: turtlebot3_slam_toolbox/  ← SLAM 建图 (SLAM Toolbox, 推荐部署)
第9步: turtlebot3_navigation2/   ← 完整自主导航
```

---

## 四、SLAM 引擎切换功能

### `robot.launch.py` 修改内容

在 `turtlebot3_bringup/launch/robot.launch.py` 中新增了 SLAM 引擎选择和条件启动逻辑：

**新增参数**：

| 参数 | 默认值 | 可选值 | 说明 |
|------|--------|--------|------|
| `slam_engine` | `slam_toolbox` | `cartographer`, `slam_toolbox` | 选择 SLAM 引擎 |
| `use_slam` | `false` | `true`, `false` | 是否启用 SLAM |
| `use_rviz` | `true` | `true`, `false` | 是否启动 RViz 可视化 |

**条件启动逻辑**：

```python
# Cartographer SLAM (conditional)
IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        get_package_share_directory('turtlebot3_cartographer'),
        '/launch/cartographer.launch.py']),
    launch_arguments={
        'use_sim_time': use_sim_time,
        'use_rviz': use_rviz}.items(),
    condition=IfCondition(PythonExpression([
        "'", slam_engine, "' == 'cartographer' and '", use_slam, "' == 'true'"]))),

# SLAM Toolbox (conditional)
IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        get_package_share_directory('turtlebot3_slam_toolbox'),
        '/launch/slam_toolbox.launch.py']),
    launch_arguments={
        'use_sim_time': use_sim_time,
        'use_rviz': use_rviz}.items(),
    condition=IfCondition(PythonExpression([
        "'", slam_engine, "' == 'slam_toolbox' and '", use_slam, "' == 'true'"]))),
```

### 使用方式

```bash
source /opt/ros/jazzy/setup.bash
source /root/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
export LDS_MODEL=LDS-01

# 仅启动机器人（无 SLAM）
ros2 launch turtlebot3_bringup robot.launch.py

# 启动机器人 + SLAM Toolbox（默认）
ros2 launch turtlebot3_bringup robot.launch.py use_slam:=true

# 启动机器人 + Cartographer SLAM
ros2 launch turtlebot3_bringup robot.launch.py use_slam:=true slam_engine:=cartographer

# 启动 SLAM 但不启动 RViz（已有其他 RViz 终端时）
ros2 launch turtlebot3_bringup robot.launch.py use_slam:=true slam_engine:=slam_toolbox use_rviz:=false
```

### SLAM 模式切换架构图

```
                    robot.launch.py
                         |
           +-------------+-------------+
           |                           |
     基础节点                   SLAM 引擎 (条件启动)
     - turtlebot3_ros              |
     - LDS 驱动                    +-- cartographer
     - state_publisher             |   cartographer_node + occupancy_grid
                                   |
                                   +-- slam_toolbox (default)
                                       sync_slam_toolbox_node
```

### 保存地图

**Cartographer**：
```bash
# 调用服务保存
rosservice call /finish_trajectory 0
rosservice call /write_state "{filename: '/tmp/tb3_map.pbstream'}"
```

**SLAM Toolbox**：
```bash
# 调用服务保存
ros2 service call /slam_toolbox/save_map nav2_msgs/SaveMap "{name: {data: '/tmp/tb3_map'}}"
```

---

## 五、ROS2 Jazzy 兼容性修复

### 背景问题

ROS2 Jazzy 使用 `geometry_msgs/msg/TwistStamped` 作为 `cmd_vel` 的标准消息格式，而 Humble 使用 `geometry_msgs/msg/Twist`。消息格式不兼容会导致节点间无法通信。

### 修复内容

#### 1. 示例节点 Twist/TwistStamped 兼容

修复了 3 个始终发布 `Twist` 的示例节点：

| 文件 | 修复方式 |
|------|---------|
| `turtlebot3_interactive_marker.py` | 根据 `ROS_DISTRO` 选择消息类型，非 Humble 时发布 `TwistStamped` |
| `turtlebot3_obstacle_detection.py` | 同上 |
| `turtlebot3_patrol_server.py` | 同上，所有 `cmd_vel` 发布点均更新 |

**代码模式**：
```python
ros_distro = os.environ.get('ROS_DISTRO', 'humble').lower()
if ros_distro == 'humble':
    from geometry_msgs.msg import Twist as CmdVelMsg
else:
    from geometry_msgs.msg import TwistStamped as CmdVelMsg
# 发布时：
if ros_distro != 'humble':
    stamped = CmdVelMsg()
    stamped.header.stamp = self.get_clock().now().to_msg()
    stamped.twist = twist
    self.cmd_vel_pub.publish(stamped)
else:
    self.cmd_vel_pub.publish(twist)
```

#### 2. Gazebo 桥接 YAML 更新

更新 4 个桥接配置文件的 `cmd_vel` 映射：

| 文件 | 修改前 | 修改后 |
|------|--------|--------|
| `turtlebot3_burger_bridge.yaml` | `geometry_msgs/msg/Twist` | `geometry_msgs/msg/TwistStamped` |
| `turtlebot3_waffle_bridge.yaml` | 同上 | 同上 |
| `turtlebot3_waffle_pi_bridge.yaml` | 同上 | 同上 |
| `turtlebot3_burger_cam_bridge.yaml` | 同上 | 同上 |

#### 3. turtlebot3_fake_node 兼容 TwistStamped

**C++ 修改**：
- 新增 `TwistStamped` 订阅支持
- 新增 `enable_stamped_cmd_vel` 参数
- 新增 `command_velocity_stamped_callback` 回调函数

**Launch 修改**：
- 根据 `ROS_DISTRO` 自动设置 `enable_stamped_cmd_vel`（Humble=false，Jazzy=true）

### 编译验证

```bash
source /opt/ros/jazzy/setup.bash
cd /root/turtlebot3_ws
colcon build --packages-select turtlebot3_example turtlebot3_fake_node turtlebot3_gazebo turtlebot3_bringup
```

所有 4 个包编译通过 ✅
