# /parameter_events

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/parameter_events` |
| 消息类型 | `rcl_interfaces/msg/ParameterEvent` |
| 发布节点 | ROS 2 参数服务器（所有节点） |
| 订阅节点 | 需要监听参数变化的节点 |

## 功能说明

**参数事件话题**：当 ROS 2 节点的参数发生变化时，自动发布参数变更通知。

核心职责：
1. 通知其他节点参数已更改
2. 提供参数名称、旧值和新值
3. 支持运行时动态配置

## 消息结构

```
ParameterEvent
  ├─ stamp: time                 # 事件时间戳
  ├─ node: string                # 参数变更的节点名称
  ├─ new_parameters: Parameter[] # 新增或更新的参数列表
  ├─ changed_parameters: Parameter[] # 变更的参数列表
  └─ deleted_parameters: string[]    # 删除的参数名称列表
```

### Parameter 结构

```
Parameter
  ├─ name: string                # 参数名称
  └─ value: ParameterValue
      └─ type: byte              # 参数类型
      └─ bool_value: boolean
      └─ integer_value: int64
      └─ double_value: float64
      └─ string_value: string
      └─ ...
```

## 使用场景

| 场景 | 说明 |
|------|------|
| 动态配置 | 运行时调整参数，无需重启节点 |
| 参数同步 | 多个节点共享同一参数配置 |
| 调试监控 | 观察参数变化对系统的影响 |
| 故障排查 | 追踪异常参数变更的来源 |

## 典型事件

```bash
# 当执行以下命令时会产生 parameter_events：
ros2 param set /node_name param_name value

# 查看参数事件
ros2 topic echo /parameter_events
```

## 在 TurtleBot3 中的应用

| 节点 | 可配置参数 |
|------|-----------|
| `/slam_toolbox` | 地图分辨率、回环检测阈值等 |
| `/turtlebot3_drive` | 安全距离、转向角度等 |
| 导航栈 | 规划器参数、恢复行为等 |

## 调试建议

```bash
# 监听所有参数事件
ros2 topic echo /parameter_events

# 查看节点的参数
ros2 param list /node_name

# 获取参数值
ros2 param get /node_name param_name

# 设置参数值
ros2 param set /node_name param_name value
```

## 参数类型

| 类型 | 说明 | 示例 |
|------|------|------|
| bool | 布尔值 | true/false |
| integer | 整数 | 1, 100, -5 |
| double | 浮点数 | 0.05, 1.5 |
| string | 字符串 | "map", "odom" |
| array | 数组 | [1, 2, 3] |
| dict | 字典 | {"key": "value"} |

## 注意事项

- 所有使用参数的节点都会收到 `/parameter_events` 通知
- 参数变更是异步的，可能需要时间生效
- 某些参数变更后需要重新初始化相关模块才能生效
