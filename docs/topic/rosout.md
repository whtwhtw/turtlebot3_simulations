# /rosout

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/rosout` |
| 消息类型 | `rcl_interfaces/msg/Log` |
| 发布节点 | 所有 ROS 2 节点 |
| 订阅节点 | `/rosout_agg`（汇总节点），rqt_console |

## 功能说明

**日志话题**：集中收集和发布所有 ROS 2 节点的日志信息。

核心职责：
1. 收集所有节点的日志消息（INFO、WARN、ERROR 等）
2. 提供统一的日志查看接口
3. 支持日志过滤和持久化

## 消息结构

```
Log
  ├─ stamp: time                 # 日志时间戳
  ├─ level: int8                 # 日志级别
  ├─ name: string                # 节点名称
  ├─ msg: string                 # 日志消息内容
  ├─ file: string                # 源文件名
  ├─ function: string            # 源函数名
  └─ line: uint32                # 源文件行号
```

## 日志级别

| 级别 | 值 | 说明 | 颜色 |
|------|-----|------|------|
| DEBUG | 10 | 调试信息 | 灰色 |
| INFO | 20 | 一般信息 | 白色/绿色 |
| WARN | 30 | 警告信息 | 黄色 |
| ERROR | 40 | 错误信息 | 红色 |
| FATAL | 50 | 致命错误 | 红色 |

## 使用示例

### C++

```cpp
#include <rclcpp/rclcpp.hpp>

RCLCPP_INFO(node->get_logger(), "Robot started moving");
RCLCPP_WARN(node->get_logger(), "Laser reading is INF");
RCLCPP_ERROR(node->get_logger(), "Failed to connect to sensor");
```

### Python

```python
import rclpy
from rclpy.node import Node

node.get_logger().info("Robot started moving")
node.get_logger().warn("Laser reading is INF")
node.get_logger().error("Failed to connect to sensor")
```

## 查看日志

```bash
# 通过 rosout 话题查看
ros2 topic echo /rosout

# 使用 ros2 命令查看节点日志
ros2 node list

# 使用 rqt_console 图形界面
ros2 run rqt_console rqt_console

# 使用 ros2 log 命令
ros2 log list          # 列出日志文件
ros2 log get /node_name  # 获取节点日志
```

## 在 TurtleBot3 中的应用

| 节点 | 典型日志 |
|------|---------|
| `/turtlebot3_drive` | "Forward!", "Turn Right!", "Obstacle detected" |
| `/slam_toolbox` | "New node added", "Loop closure detected" |
| `/ros_gz_bridge` | "Bridge configured", "Topic mapped" |

## 数据流

```
节点 A ──→ RCLCPP_INFO/WARN/ERROR ──→ /rosout ──→ rqt_console
节点 B ──→ 日志消息 ──→ /rosout ──→ ros2 topic echo
节点 C ──→ 日志消息 ──→ /rosout ──→ rosout_agg → 日志文件
```

## 日志过滤

```bash
# 仅查看 ERROR 级别日志
ros2 topic echo /rosout --filter 'm.level >= 40'

# 仅查看特定节点的日志
ros2 topic echo /rosout --filter 'm.name == "/turtlebot3_drive"'
```

## 注意事项

- `/rosout` 是 ROS 2 的标准日志机制
- 大量日志可能影响性能，应合理使用日志级别
- 仿真中的日志频率可能比实际机器人高
- 可以使用 `--log-level` 参数调整节点日志输出级别
