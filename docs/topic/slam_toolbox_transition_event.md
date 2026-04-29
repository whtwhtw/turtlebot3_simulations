# /slam_toolbox/transition_event

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/transition_event` |
| 消息类型 | `slam_toolbox/msg/Transition` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | 调试工具，监控系统 |

## 功能说明

**状态转换事件话题**：当 slam_toolbox 内部状态发生变化时发布通知消息。

核心职责：
1. 通知其他模块建图状态的转换
2. 提供状态转换的详细信息
3. 用于监控建图过程

## 消息结构

```
Transition
  ├─ header: Header
  ├─ from_state: string          # 转换前状态
  ├─ to_state: string            # 转换后状态
  └─ reason: string              # 转换原因
```

## 可能的状态

| 状态 | 说明 |
|------|------|
| INITIALIZING | 初始化中 |
| LOCALIZING | 定位模式 |
| MAPPING | 建图模式 |
| PAUSED | 暂停 |
| ERROR | 错误状态 |

## 典型事件

```
初始化完成 → 开始建图：
  from_state: "INITIALIZING"
  to_state: "MAPPING"
  reason: "Initialization complete"

建图 → 暂停：
  from_state: "MAPPING"
  to_state: "PAUSED"
  reason: "Service call"

定位 → 建图：
  from_state: "LOCALIZING"
  to_state: "MAPPING"
  reason: "New map started"
```

## 调试建议

```bash
# 查看状态转换事件
ros2 topic echo /slam_toolbox/transition_event
```

## 用途

- 监控 slam_toolbox 的运行状态
- 了解建图过程中的状态变化
- 诊断建图失败的原因

## 相关服务

```bash
# 暂停建图
ros2 service call /slam_toolbox/pause slam_toolbox/srv/Pause

# 恢复建图
ros2 service call /slam_toolbox/serialize slam_toolbox/srv/Resume

# 保存地图
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: 'my_map'}"
```
