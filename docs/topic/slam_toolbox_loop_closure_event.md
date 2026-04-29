# /slam_toolbox/loop_closure_event

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/loop_closure_event` |
| 消息类型 | `slam_toolbox/msg/LoopClosure` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | 调试工具，监控系统 |

## 功能说明

**回环检测事件话题**：当 slam_toolbox 检测到回环时发布通知消息。

核心职责：
1. 通知其他模块回环检测已成功
2. 提供回环的相关信息（节点 ID、得分等）
3. 用于调试和建图质量评估

## 消息结构

```
LoopClosure
  ├─ header: Header
  ├─ node_id_a: int32            # 回环中第一个节点的 ID
  ├─ node_id_b: int32            # 回环中第二个节点的 ID
  ├─ score: float                # 回环匹配得分
  └─ success: bool               # 回环校正是否成功
```

## 什么是回环检测

回环检测（Loop Closure）是 SLAM 中的关键技术：

```
场景示例：

起点 A ──→ ... ──→ B ──→ ... ──→ A'
                            │
                            └─ 回到起点附近
                                 ↓
                          检测到回环
                                 ↓
                    全局优化，消除累积误差
                                 ↓
                          地图校正完成
```

- 机器人从 A 点出发
- 经过一段时间后回到 A 点附近（A'）
- SLAM 系统通过激光匹配检测到回环
- 执行全局优化，消除累积误差

## 典型事件

```
检测到回环：
  node_id_a: 42      # 起始节点
  node_id_b: 156     # 当前节点
  score: 0.85        # 匹配得分高
  success: true      # 校正成功

回环失败：
  node_id_a: 42
  node_id_b: 156
  score: 0.32        # 匹配得分低
  success: false     # 校正失败
```

## 调试建议

```bash
# 查看回环事件
ros2 topic echo /slam_toolbox/loop_closure_event

# 观察回环频率
ros2 topic hz /slam_toolbox/loop_closure_event
```

## 用途

- 监控回环检测的正确性
- 评估建图质量（回环越多，地图越精确）
- 发现回环检测异常（误匹配或漏匹配）

## 相关参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| loop_search_maximum_distance | 5.0 | 回环搜索最大距离 |
| loop_match_minimum_score | 0.5 | 回环匹配最小得分阈值 |
