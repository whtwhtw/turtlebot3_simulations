# /slam_toolbox/pose_graph

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/pose_graph` |
| 消息类型 | `visualization_msgs/msg/MarkerArray` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | RViz2 |

## 功能说明

**位姿图可视化话题**：发布完整的 SLAM 位姿图可视化标记。

核心职责：
1. 在 RViz 中显示所有位姿节点和约束
2. 展示回环检测的效果
3. 帮助理解建图质量和优化过程

## 消息结构

```
MarkerArray
  └─ markers: Marker[]           # 标记列表
      ├─ id: int32               # 标记 ID
      ├─ type: uint8             # 标记类型
      ├─ action: uint8           # 操作
      ├─ pose: Pose              # 标记位姿
      ├─ scale: Vector3          # 标记尺寸
      ├─ color: ColorRGBA        # 颜色
      └─ ...
```

## 位姿图概念

位姿图（Pose Graph）是 SLAM 的核心数据结构：

```
节点 (Node) ──→ 机器人在某时刻的位姿 (x, y, θ)
     │
     ├── 边 (Edge) ──→ 节点之间的约束关系
     │
     ├── 里程计边 ──→ 相邻节点的运动估计
     │
     └── 回环边 ──→ 非相邻节点的关联（消除漂移）
```

## 可视化元素

| 元素 | 颜色 | 说明 |
|------|------|------|
| 位姿节点 | 蓝色/绿色 | 每个扫描位置 |
| 里程计边 | 蓝色细线 | 相邻节点的运动关系 |
| 回环边 | 红色粗线 | 检测到的回环约束 |
| 当前位姿 | 大圆点/箭头 | 机器人当前位置 |

## 在 RViz 中显示

1. 打开 RViz2
2. 添加 "MarkerArray" 显示插件
3. 设置话题为 `/slam_toolbox/pose_graph`
4. 位姿图将完整显示

## 调试建议

```bash
# 查看位姿图数据
ros2 topic echo /slam_toolbox/pose_graph

# 查看话题信息
ros2 topic info /slam_toolbox/pose_graph
```

## 用途

- 直观展示建图质量
- 检查回环是否正确连接
- 发现位姿图中的异常节点或约束
- 评估全局优化效果

## 与 graph_visualization 的关系

| 话题 | 内容 | 区别 |
|------|------|------|
| `/slam_toolbox/pose_graph` | 完整位姿图 | 包含所有节点和约束 |
| `/slam_toolbox/graph_visualization` | 图可视化 | 可能包含额外的可视化元素 |
