# /cmd_vel

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/cmd_vel` |
| 消息类型 | `geometry_msgs/msg/Twist` |
| 发布节点 | `/turtlebot3_drive`, 键盘控制，Nav2 等 |
| 订阅节点 | `/ros_gz_bridge` → Gazebo |

## 功能说明

**速度指令话题**：用于向机器人发布运动控制指令（线速度和角速度）。

核心职责：
1. 接收来自控制节点的运动指令
2. 通过 ros_gz_bridge 转发给 Gazebo 执行
3. 驱动机器人的差速驱动轮运动

## 消息结构

```
Twist
  ├─ linear: Vector3
  │   ├─ x: float    # 前后线速度 (m/s)，正值为前进
  │   ├─ y: float    # 左右线速度 (m/s)，通常差速驱动不使用
  │   └─ z: float    # 上下线速度 (m/s)，地面机器人通常为 0
  └─ angular: Vector3
      ├─ x: float    # 横滚角速度 (rad/s)，通常不使用
      ├─ y: float    # 俯仰角速度 (rad/s)，通常不使用
      └─ z: float    # 偏航角速度 (rad/s)，正值为左转
```

## 典型使用场景

| 场景 | linear.x | angular.z | 说明 |
|------|----------|-----------|------|
| 直线前进 | 0.3 m/s | 0 rad/s | 慢速前进 |
| 快速前进 | 0.5 m/s | 0 rad/s | 快速前进 |
| 左转 | 0 m/s | 1.5 rad/s | 原地左转 |
| 右转 | 0 m/s | -1.5 rad/s | 原地右转 |
| 左前转弯 | 0.3 m/s | 0.5 rad/s | 前进+左转 |
| 停止 | 0 m/s | 0 rad/s | 停止运动 |

## 发布者

| 节点 | 说明 |
|------|------|
| `/turtlebot3_drive` | 自动避障节点，基于激光雷达决策 |
| `teleop_keyboard` | 键盘手动控制 |
| Nav2 局部规划器 | 导航时的路径跟踪 |
| `auto_explore.py` | 自动探索建图 |

## 数据流

```
控制节点 (turtlebot3_drive/teleop/Nav2)
         ↓
    发布 /cmd_vel
         ↓
   ros_gz_bridge (ROS→GZ)
         ↓
   Gazebo 物理引擎
         ↓
   差速驱动运动
```

## TurtleBot3 运动学参数

```
差速驱动公式：
v_left  = (v - ω * L/2) / R_wheel
v_right = (v + ω * L/2) / R_wheel

其中：
v = linear.x (线速度)
ω = angular.z (角速度)
L = 轮距 (TurtleBot3 Burger: 0.16m)
R_wheel = 轮半径 (0.033m)
```

## 调试建议

```bash
# 查看发布的速度指令
ros2 topic echo /cmd_vel

# 查看发布频率
ros2 topic hz /cmd_vel

# 手动发布速度指令
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## 安全注意事项

- 默认最大线速度：约 0.5 m/s
- 急转弯时可能导致打滑或翻倒
- 在仿真中可以安全测试，实机需要注意物理限制
