# /imu

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/imu` |
| 消息类型 | `sensor_msgs/msg/Imu` |
| 发布节点 | Gazebo 传感器插件 → ros_gz_bridge |
| 订阅节点 | SLAM 节点，导航节点，状态估计节点 |

## 功能说明

**惯性测量单元话题**：发布机器人的姿态、角速度和线加速度信息。

核心职责：
1. 提供机器人的三维姿态信息（四元数）
2. 发布角速度（用于检测旋转）
3. 发布线加速度（用于运动分析）

## 消息结构

```
Imu
  ├─ header: Header
  │   └─ frame_id: string      # 通常为 "imu_link"
  ├─ orientation: Quaternion
  │   ├─ x: float
  │   ├─ y: float
  │   ├─ z: float
  │   └─ w: float              # 四元数表示的姿态
  ├─ angular_velocity: Vector3
  │   ├─ x: float              # 横滚角速度 (rad/s)
  │   ├─ y: float              # 俯仰角速度 (rad/s)
  │   └─ z: float              # 偏航角速度 (rad/s)
  ├─ linear_acceleration: Vector3
  │   ├─ x: float              # X 轴加速度 (m/s²)
  │   ├─ y: float              # Y 轴加速度 (m/s²)
  │   └─ z: float              # Z 轴加速度 (m/s²)
  └─ orientation_covariance: float[9]
     angular_velocity_covariance: float[9]
     linear_acceleration_covariance: float[9]
```

## 传感器配置

在 URDF 文件中定义：

```xml
<!-- turtlebot3_burger.urdf -->
<link name="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>50</update_rate>    <!-- 50Hz 更新频率 -->
    <topic>imu</topic>
  </sensor>
</link>
```

## 在 TurtleBot3 中的应用

| 用途 | 说明 |
|------|------|
| 姿态估计 | 获取机器人的俯仰角（pitch）和横滚角（roll） |
| SLAM 融合 | 与激光雷达、里程计融合，提高定位精度 |
| 运动分析 | 检测机器人是否打滑或异常运动 |

## 典型数值

```
静止状态：
  angular_velocity: (0, 0, 0)        # 无旋转
  linear_acceleration: (0, 0, 9.81)  # 仅重力加速度

转弯时：
  angular_velocity.z: ±1.5 rad/s     # TurtleBot3 最大转弯角速度

倾斜时：
  orientation.w: ~0.707              # 45° 倾斜
  orientation.z: ~0.707
```

## 数据流

```
Gazebo IMU 传感器 ──→ ros_gz_bridge ──→ /imu ──→ SLAM/导航节点
                                                  ↓
                                          姿态估计
                                          运动分析
                                          数据融合
```

## 调试建议

```bash
# 查看 IMU 数据
ros2 topic echo /imu

# 查看发布频率
ros2 topic hz /imu

# 查看话题信息
ros2 topic info /imu
```

## 注意事项

- 仿真中的 IMU 数据是理想化的，无噪声
- 实际机器人的 IMU 会有噪声和漂移，需要滤波
- TurtleBot3 是差速驱动，主要关注 `angular_velocity.z`（偏航角速度）
