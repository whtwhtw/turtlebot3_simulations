# /robot_state_publisher

## 基本信息

| 属性 | 值 |
|------|-----|
| 节点名称 | `/robot_state_publisher` |
| 节点类型 | 系统节点 |
| 所属包 | `robot_state_publisher` |

## 功能说明

**机器人状态发布器**：负责发布机器人的坐标变换（TF）和机器人描述信息。

核心职责：
1. 读取 URDF 文件中的机器人描述
2. 根据 `joint_states` 话题中的关节角度数据
3. 计算并发布各个 link 之间的 TF 变换（`/tf` 和 `/tf_static`）
4. 发布 `/robot_description` 话题，供 RViz 等工具渲染机器人模型

## 订阅话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/joint_states` | `sensor_msgs/msg/JointState` | 关节角度数据 |

## 发布话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/tf` | `tf2_msgs/msg/TFMessage` | 动态坐标变换（关节运动产生的变化） |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | 静态坐标变换（固定不变的 link 关系） |
| `/robot_description` | `std_msgs/msg/String` | URDF 描述文本 |

## 数据流

```
URDF 文件 ──→ robot_state_publisher ──→ /robot_description
                                               ↓
/joint_states ──→ 计算 TF ──→ /tf + /tf_static ──→ RViz 渲染
```

## 在 TurtleBot3 中的作用

- 发布 `base_link` → `base_scan`、`base_link` → `imu_link`、`base_link` → `wheel_left/right_link` 等坐标变换
- 使 RViz 能够根据实际关节角度正确显示机器人姿态
- 为 SLAM 和导航提供坐标变换基础

## 配置参数

通常在 launch 文件中配置：
- `robot_description`：URDF 内容或文件路径
- `publish_frequency`：TF 发布频率（默认 20Hz）
