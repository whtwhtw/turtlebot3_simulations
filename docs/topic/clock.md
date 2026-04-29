# /clock

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/clock` |
| 消息类型 | `rosgraph_msgs/msg/Clock` |
| 发布节点 | `/ros_gz_sim` |
| 订阅节点 | `/slam_toolbox`, 其他使用仿真时钟的节点 |

## 功能说明

**仿真时钟话题**：发布 Gazebo 仿真环境的当前仿真时间。

核心职责：
1. 提供仿真环境的时间信息（非真实世界时间）
2. 使 ROS 2 节点能够与仿真时间同步
3. 支持仿真暂停、加速、减速等时间操作

## 消息结构

```
Clock
  └─ clock: time    # 仿真时间（从仿真开始经过的秒数）
```

## 使用场景

| 场景 | 说明 |
|------|------|
| Gazebo 仿真中 | 必须使用 `/clock` 而非系统时钟 |
| SLAM 建图 | slam_toolbox 使用 `/clock` 进行时间戳对齐 |
| 数据录制 | bag 录制时使用 `/clock` 保证时间一致性 |
| 传感器同步 | 多传感器数据基于 `/clock` 进行时间同步 |

## 仿真时间控制

```bash
# 在 Gazebo GUI 中：
# - 点击暂停按钮暂停仿真
# - 调整速度因子（0.1x ~ 10x）

# 通过命令行控制
gz sim -p  # 暂停
gz sim -r  # 恢复
```

## 重要参数

```yaml
# 节点必须设置 use_sim_time 为 true 才能使用仿真时钟
use_sim_time: true
```

## 数据流

```
Gazebo 物理引擎 ──→ ros_gz_sim ──→ /clock ──→ 所有订阅节点
                                              ↓
                                       设置消息时间戳
                                       同步数据处理
```

## 调试建议

```bash
# 查看当前仿真时间
ros2 topic echo /clock

# 查看话题信息
ros2 topic info /clock
```

## 注意事项

- 在 Gazebo 仿真中运行时，所有节点都应设置 `use_sim_time:=true`
- 仿真暂停时，`/clock` 停止更新，依赖时钟的节点也会暂停处理
- 录制 bag 数据时，时间戳基于 `/clock`，回放时需要设置 `--clock`
