# TurtleBot3 仿真 SLAM 建图指南（SLAMToolbox）

本文档介绍如何在 Gazebo 仿真环境中使用键盘手动控制 TurtleBot3，并通过 slam_toolbox 进行实时建图。

## 系统架构

```
键盘输入 → teleop_twiststamped_keyboard → /cmd_vel (TwistStamped) → ros_gz_bridge → Gazebo DiffDrive
                                                                    ↓
                                                            TurtleBot3 运动
                                                                    ↓
joint_states / scan / odom / tf → ros_gz_bridge → slam_toolbox → /map (OccupancyGrid) → rviz2
```

## 环境要求

- ROS 2 Jazzy
- Gazebo (ros_gz_sim)
- turtlebot3_gazebo
- slam_toolbox
- turtlebot3_teleop（含 TwistStamped 支持）

## 启动步骤（4 个节点）

### 1. 启动 Gazebo 仿真世界

```bash
source /root/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

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

---

### 2. 启动 RViz2 可视化

```bash
ros2 launch turtlebot3_bringup rviz2.launch.py
```

**功能：** 实时显示激光雷达扫描、里程计、TF 树和 SLAM 构建的地图。

**订阅的 Topic：**
| Topic | 类型 |
|-------|------|
| /scan | sensor_msgs/msg/LaserScan |
| /odom | nav_msgs/msg/Odometry |
| /map | nav_msgs/msg/OccupancyGrid |
| /tf, /tf_static | tf2_msgs/msg/TFMessage |

---

### 3. 启动 SLAM Toolbox

```bash
ros2 launch slam_toolbox online_sync_launch.py
```

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

**服务（Services）：**
| Service | 类型 | 用途 |
|---------|------|------|
| /slam_toolbox/deserialize_map | slam_toolbox/srv/DeserializePoseGraph | 加载已有地图 |
| /slam_toolbox/dynamic_map | nav_msgs/srv/GetMap | 获取当前地图 |
| /slam_toolbox/save_map | slam_toolbox/srv/SaveMap | 保存地图 |
| /slam_toolbox/toggle_interactive | std_srvs/srv/Empty | 切换交互模式 |

---

### 4. 启动键盘控制

```bash
ros2 run turtlebot3_teleop teleop_twiststamped_keyboard
```

**功能：** 读取键盘输入，发布 TwistStamped 速度指令到 `/cmd_vel`。

**节点名称：** `/teleop_twiststamped_keyboard`

**发布的 Topic：**
| Topic | 类型 | 说明 |
|-------|------|------|
| /cmd_vel | geometry_msgs/msg/TwistStamped | 速度指令（含时间戳和 frame_id） |

---

## 键盘控制方法

### 布局说明

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

### 按键含义

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

### 速度调节说明

- 初始速度：线性 0.5 m/s，角速度 1.0 rad/s
- `w` 键每次增加线速度 10%
- `x` 键每次减少线速度 10%
- `e` 键每次增加角速度 10%
- `c` 键每次减少角速度 10%
- `q` / `z` 同时调整两者

---

## 建图操作建议

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

---

## 验证 Topic 数据流

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

---

## 常见问题

### 键盘无法控制小车

**原因：** `teleop_twist_keyboard` 发布的是 `Twist` 类型，而 ros_gz_bridge 订阅的是 `TwistStamped`，类型不匹配。

**解决：** 使用本项目提供的 `teleop_twiststamped_keyboard` 节点：

```bash
ros2 run turtlebot3_teleop teleop_twiststamped_keyboard
```

### 地图不更新

- 检查 `/scan` topic 是否有数据：`ros2 topic hz /scan`
- 检查 slam_toolbox 节点是否正常运行：`ros2 node info /slam_toolbox`
- 确认 `use_sim_time` 参数一致

### RViz 中地图显示异常

- 确认 Fixed Frame 设置为 `map`
- 检查 TF 树是否完整：`map` → `odom` → `base_footprint` → `base_scan`

---

## 停止顺序

完成建图后，按以下顺序停止节点（反向）：

1. 停止键盘控制（Ctrl+C）
2. 停止 SLAM Toolbox
3. 停止 RViz2
4. 停止 Gazebo
