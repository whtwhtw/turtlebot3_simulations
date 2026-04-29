# /ros_gz_bridge

## 基本信息

| 属性 | 值 |
|------|-----|
| 节点名称 | `/ros_gz_bridge` |
| 节点类型 | 桥接节点 |
| 所属包 | `ros_gz_bridge` |

## 功能说明

**ROS 2 ↔ Gazebo 消息桥**：负责在 ROS 2 和 Gazebo 仿真器之间转换和转发消息。

核心职责：
1. 将 Gazebo 仿真器的消息（传感器数据、仿真状态）转换为 ROS 2 消息
2. 将 ROS 2 控制命令转发给 Gazebo 执行
3. 根据 YAML 配置文件定义话题映射关系

## 桥接方向

| 方向 | 说明 |
|------|------|
| GZ_TO_ROS | Gazebo → ROS 2（传感器数据） |
| ROS_TO_GZ | ROS 2 → Gazebo（控制命令） |
| BIDIRECTIONAL | 双向转发 |

## 典型桥接配置

```yaml
# params/turtlebot3_burger_bridge.yaml 示例
- ros_topic_name: "scan"
  gz_topic_name: "scan"
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS        # 激光雷达：Gazebo → ROS

- ros_topic_name: "cmd_vel"
  gz_topic_name: "cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ        # 速度控制：ROS → Gazebo
```

## 在 TurtleBot3 中的桥接话题

| ROS 话题 | Gazebo 话题 | 方向 | 消息类型 |
|----------|-------------|------|---------|
| `/scan` | `/scan` | GZ→ROS | LaserScan |
| `/cmd_vel` | `/cmd_vel` | ROS→GZ | Twist |
| `/joint_states` | `/joint_states` | GZ→ROS | JointState |
| `/tf` | `/tf` | GZ→ROS | TFMessage |
| `/clock` | `/clock` | GZ→ROS | Clock |
| `/imu` | `/imu` | GZ→ROS | Imu |

## 数据流

```
Gazebo 仿真 ──→ ros_gz_bridge ──→ ROS 2 节点
    ↓                                  ↓
传感器数据                    /scan, /imu, /joint_states
物理引擎                       /clock, /tf
                                     ↓
                              ROS 2 处理/决策
                                     ↓
                              /cmd_vel 控制指令
                                     ↓
ros_gz_bridge ──→ Gazebo 执行器
                     ↓
              驱动机器人运动
```

## 调试建议

```bash
# 查看桥接状态
ros2 node info /ros_gz_bridge

# 查看桥接的话题映射
ros2 param get /ros_gz_bridge config_file

# 检查话题是否有数据
ros2 topic hz /scan
```
