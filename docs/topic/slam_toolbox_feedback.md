# /slam_toolbox/feedback

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/feedback` |
| 消息类型 | `slam_toolbox/msg/Feedback` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | 调试工具，监控系统 |

## 功能说明

**SLAM 建图反馈话题**：发布 slam_toolbox 的实时运行状态和反馈信息。

核心职责：
1. 提供当前建图的节点数量
2. 报告回环检测状态
3. 反馈处理器使用情况和性能指标

## 消息结构

```
Feedback
  ├─ header: Header
  ├─ total_nodes: uint32         # 总位姿节点数
  ├─ total_submaps: uint32       # 总子地图数
  ├─ processing_ms: uint32       # 处理耗时 (ms)
  ├─ status: string              # 当前状态描述
  └─ ...
```

## 典型反馈内容

| 字段 | 示例值 | 说明 |
|------|--------|------|
| total_nodes | 150 | 已添加 150 个位姿节点 |
| total_submaps | 3 | 创建了 3 个子地图 |
| processing_ms | 25 | 本次处理耗时 25ms |
| status | "Adding node" | 正在添加新节点 |

## 调试建议

```bash
# 查看建图反馈
ros2 topic echo /slam_toolbox/feedback

# 监控建图进度
ros2 topic echo /slam_toolbox/feedback --once
```

## 用途

- **性能监控**：观察处理时间是否正常
- **进度跟踪**：了解建图过程中节点的增长情况
- **异常诊断**：发现处理延迟或状态异常
