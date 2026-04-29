# /turtlebot3_drive

## 基本信息

| 属性 | 值 |
|------|-----|
| 节点名称 | `/turtlebot3_drive` |
| 节点类型 | 应用节点 |
| 所属包 | `turtlebot3_gazebo` |
| 源码位置 | `turtlebot3_gazebo/src/turtlebot3_drive.cpp` |
| 编程语言 | C++ |

## 功能说明

**自动避障演示节点**：实现基于激光雷达的自主避障和主动探索功能。

核心职责：
1. 订阅激光雷达扫描数据（`/scan`）
2. 通过状态机进行避障决策
3. 发布速度指令（`/cmd_vel`）控制机器人运动
4. 支持主动探索模式（直行 30 次后自动转向）

## 订阅话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D 激光雷达数据 |

## 发布话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 速度控制指令 |

## 状态机设计

```
                    GET_TB3_DIRECTION
                           │
              ┌────────────┼────────────┐
              │            │            │
         前方开阔       左侧近        右侧近
              │            │            │
              ↓            ↓            ↓
     TB3_DRIVE     TB3_RIGHT     TB3_LEFT
       _FORWARD      _TURN         _TURN
    (0.3 m/s)    (1.5 rad/s)   (1.5 rad/s)
```

### 状态说明

| 状态 | 行为 | 线速度 | 角速度 |
|------|------|--------|--------|
| `GET_TB3_DIRECTION` | 读取激光数据，决策方向 | 0 | 0 |
| `TB3_DRIVE_FORWARD` | 直线前进 | 0.3 m/s | 0 |
| `TB3_RIGHT_TURN` | 右转避障 | 0 | -1.5 rad/s |
| `TB3_LEFT_TURN` | 左转避障 | 0 | 1.5 rad/s |

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `front_distance` | 1.2 m | 前方安全距离阈值 |
| `left_distance` | 1.0 m | 左侧安全距离阈值 |
| `right_distance` | 1.0 m | 右侧安全距离阈值 |
| `escape_range` | 30° (0.524 rad) | 主动探索转向角度 |
| `drive_count` | 30 | 连续直行次数阈值 |

## 激光数据处理

```cpp
// 激光扇区划分
front_sector:  [-10°, +10°]   // 前方区域
left_sector:   [+60°, +120°]  // 左侧区域
right_sector:  [-120°, -60°]  // 右侧区域

// 距离计算
// 过滤 INF（超出量程）值
// 计算扇区内平均距离
```

## 主动探索逻辑

```python
直行计数 = 0
while True:
    如果 直行计数 >= 30:
        如果 左侧距离 > 右侧距离:
            左转 escape_range
        否则:
            右转 escape_range
        直行计数 = 0
    否则:
        直行
        直行计数 += 1
```

## 在 TurtleBot3 中的使用场景

- **演示自动避障**：无需人工干预，机器人自主导航
- **配合 SLAM 建图**：自动探索环境，快速完成建图
- **避障算法学习**：理解基于激光雷达的简单决策逻辑

## 启动方式

```bash
# 通过脚本启动
./turtlebot3_simulations.sh turtlebot3_drive

# 直接启动
ros2 run turtlebot3_gazebo turtlebot3_drive
```

## 调试建议

```bash
# 查看节点日志
ros2 run rqt_console rqt_console

# 实时查看激光数据
ros2 topic echo /scan

# 查看发布的速度指令
ros2 topic echo /cmd_vel
```

## 与其他节点对比

| 节点 | 输入 | 输出 | 复杂度 |
|------|------|------|--------|
| `turtlebot3_drive` | `/scan` | `/cmd_vel` | 简单（状态机） |
| `auto_explore.py` | `/scan` | `/cmd_vel` | 简单（Python） |
| Nav2 | `/scan`, `/odom`, `/map` | `/cmd_vel` | 复杂（完整导航栈） |
