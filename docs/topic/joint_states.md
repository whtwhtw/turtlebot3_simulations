# /joint_states

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/joint_states` |
| 消息类型 | `sensor_msgs/msg/JointState` |
| 发布节点 | Gazebo 插件 → ros_gz_bridge |
| 订阅节点 | `/robot_state_publisher` |

## 功能说明

**关节状态话题**：发布机器人各个关节的当前位置、速度和力矩信息。

核心职责：
1. 实时报告机器人关节的角度位置
2. 提供关节的速度信息
3. 为 `robot_state_publisher` 提供数据以计算 TF 变换

## 消息结构

```
JointState
  ├─ header: Header
  │   └─ stamp: time
  ├─ name: string[]              # 关节名称列表
  │   ├─ "wheel_left_joint"
  │   └─ "wheel_right_joint"
  ├─ position: float[]           # 关节位置（弧度）
  │   ├─ wheel_left_position
  │   └─ wheel_right_position
  ├─ velocity: float[]           # 关节速度（rad/s）
  │   ├─ wheel_left_velocity
  │   └─ wheel_right_velocity
  └─ effort: float[]             # 关节力矩（N·m）
      ├─ wheel_left_effort
      └─ wheel_right_effort
```

## TurtleBot3 关节

| 关节名称 | 类型 | 范围 | 说明 |
|---------|------|------|------|
| `wheel_left_joint` | 连续旋转 | 无限制 | 左轮关节 |
| `wheel_right_joint` | 连续旋转 | 无限制 | 右轮关节 |

注意：差速驱动机器人的轮子是连续旋转的，没有位置限制。

## 数据流

```
Gazebo 物理引擎 ──→ 获取关节状态 ──→ ros_gz_bridge
                                              ↓
                                       发布 /joint_states
                                              ↓
                                robot_state_publisher
                                              ↓
                                计算并发布 /tf 变换
                                              ↓
                                   RViz 渲染模型
```

## 与里程计的区别

| 特性 | /joint_states | /odom |
|------|---------------|-------|
| 内容 | 关节角度 | 位姿（x, y, θ） |
| 用途 | TF 变换计算 | 运动控制和导航 |
| 坐标系 | 相对关系 | 世界坐标系 |
| 累积误差 | 无 | 有（随时间增加） |

## 调试建议

```bash
# 查看关节状态
ros2 topic echo /joint_states

# 查看发布频率
ros2 topic hz /joint_states

# 查看特定关节
ros2 topic echo /joint_states | grep -A 2 wheel_left
```

## 注意事项

- 仿真中关节状态是精确的，无噪声
- 实际机器人可能有编码器噪声和丢步
- 轮子的 position 值会随旋转无限增长（非 0~2π）
- `robot_state_publisher` 依赖此话题来更新 TF 树
