# /odom

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/odom` |
| 消息类型 | `nav_msgs/msg/Odometry` |
| 发布节点 | Gazebo 插件 → ros_gz_bridge, Fake Node |
| 订阅节点 | SLAM 节点, 导航节点, 状态估计节点 |

## 功能说明

**里程计话题**：发布机器人在世界坐标系中的位姿和速度估计。

核心职责：
1. 提供机器人在世界坐标系中的位置（x, y）和姿态（θ）
2. 发布线速度和角速度信息
3. 提供协方差矩阵表示估计的不确定性

## 消息结构

```
Odometry
  ├─ header: Header
  │   ├─ stamp: time
  │   └─ frame_id: string        # 通常为 "odom"
  ├─ child_frame_id: string      # 通常为 "base_footprint" 或 "base_link"
  ├─ pose: PoseWithCovariance
  │   ├─ pose: Pose
  │   │   ├─ position: Point     # 位置 (x, y, z)
  │   │   │   ├─ x: float
  │   │   │   ├─ y: float
  │   │   │   └─ z: float
  │   │   └─ orientation: Quaternion  # 姿态（四元数）
  │   └─ covariance: float[36]   # 位姿协方差
  └─ twist: TwistWithCovariance
      ├─ twist: Twist
      │   ├─ linear: Vector3     # 线速度 (m/s)
      │   └─ angular: Vector3    # 角速度 (rad/s)
      └─ covariance: float[36]   # 速度协方差
```

## 坐标系关系

```
map ──→ odom ──→ base_footprint/base_link
  │        │              │
  │        │              └─ 机器人本体
  │        │
  │        └─ 里程计坐标系（有漂移）
  │
  └─ 地图坐标系（全局固定）
```

- `map` → `odom`：由 SLAM 或 AMCL 发布（校正漂移）
- `odom` → `base_link`：由里程计发布（积分计算）

## 在 TurtleBot3 中的发布方式

### Gazebo 仿真

通过 Gazebo 的差速驱动插件计算并发布：

```xml
<!-- turtlebot3_burger.urdf -->
<gazebo>
  <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <odom_frame>odom</odom_frame>
    <robot_base_frame>base_footprint</robot_base_frame>
  </plugin>
</gazebo>
```

### Fake Node

通过差速运动学积分计算位姿：

```cpp
// 根据 cmd_vel 积分计算
x += v * cos(theta) * dt
y += v * sin(theta) * dt
theta += omega * dt
```

## 典型数值

```
初始状态：
  position: (0, 0, 0)
  orientation: (0, 0, 0, 1)  # 四元数，表示无旋转

前进 1 米后：
  position: (1, 0, 0)

左转 90° 后：
  position: (0, 0, 0)
  orientation: (0, 0, 0.707, 0.707)  # z=0.707, w=0.707 表示 90°
```

## 里程计漂移

| 原因 | 说明 |
|------|------|
| 轮子打滑 | 地面摩擦不足 |
| 轮径误差 | 实际轮径与标称值不符 |
| 编码器误差 | 脉冲计数不精确 |
| 地不平 | 倾斜地面导致轮子空转 |

**仿真中的里程计是理想的，无漂移。**

## 数据流

```
Gazebo 物理引擎 ──→ 计算机器位姿 ──→ ros_gz_bridge
                                          ↓
                                    发布 /odom
                                          ↓
                              SLAM/导航/状态估计
```

## 调试建议

```bash
# 查看里程计数据
ros2 topic echo /odom

# 查看发布频率
ros2 topic hz /odom

# 查看 TF 变换
ros2 run tf2_ros tf2_echo odom base_footprint
```

## 注意事项

- 仿真中的 `/odom` 是理想的，实际机器人会有漂移
- SLAM 使用 `/odom` 作为初始位姿估计，然后通过回环检测校正
- Nav2 需要 `/odom` 来进行局部路径规划
