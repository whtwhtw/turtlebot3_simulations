# /slam_toolbox/new_node_event

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/new_node_event` |
| 消息类型 | `slam_toolbox/msg/NewNode` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | 调试工具，监控系统 |

## 功能说明

**新节点添加事件话题**：当 slam_toolbox 在位姿图中添加新节点时发布通知消息。

核心职责：
1. 通知其他模块新节点已添加
2. 提供新节点的信息（ID、位置等）
3. 用于监控建图进度

## 消息结构

```
NewNode
  ├─ header: Header
  ├─ node_id: int32              # 新添加的节点 ID
  ├─ position_x: float           # 节点 X 坐标
  ├─ position_y: float           # 节点 Y 坐标
  └─ position_theta: float       # 节点朝向
```

## 节点添加时机

```
机器人运动 ──→ 激光扫描 ──→ 特征提取
                                ↓
                          与历史数据对比
                                ↓
                          判断是否有足够新信息
                                ↓
                          添加新节点到位姿图
                                ↓
                          发布 /slam_toolbox/new_node_event
```

## 典型事件

```
添加新节点：
  node_id: 127
  position_x: 3.45
  position_y: -1.23
  position_theta: 0.52
```

## 节点频率

| 条件 | 节点添加频率 |
|------|------------|
| 快速移动 | 高（频繁添加） |
| 慢速移动 | 低 |
| 原地旋转 | 中 |
| 静止不动 | 无 |

## 调试建议

```bash
# 查看新节点事件
ros2 topic echo /slam_toolbox/new_node_event

# 监控节点添加频率
ros2 topic hz /slam_toolbox/new_node_event
```

## 用途

- 监控建图进度
- 评估机器人运动轨迹的覆盖程度
- 发现建图异常（长时间不添加节点）

## 与 /slam_toolbox/feedback 的关系

- `/slam_toolbox/new_node_event`：仅在添加新节点时发布
- `/slam_toolbox/feedback`：持续发布，包含更全面的统计信息
- 两者可以配合使用，获得完整的建图状态
