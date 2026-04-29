# /slam_toolbox/graph_visualization

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/graph_visualization` |
| 消息类型 | `visualization_msgs/msg/MarkerArray` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | RViz2 |

## 功能说明

**位姿图可视化话题**：发布 SLAM 位姿图的可视化标记，用于在 RViz 中显示。

核心职责：
1. 在 RViz 中显示所有位姿节点
2. 显示节点之间的约束关系
3. 帮助理解建图过程和回环检测效果

## 消息结构

```
MarkerArray
  └─ markers: Marker[]           # 标记列表
      ├─ id: int32               # 标记 ID
      ├─ type: uint8             # 标记类型 (SPHERE, LINE, TEXT 等)
      ├─ action: uint8           # 操作 (ADD, DELETE)
      ├─ pose: Pose              # 标记位姿
      ├─ scale: Vector3          # 标记尺寸
      ├─ color: ColorRGBA        # 颜色
      └─ ...
```

## 在 RViz 中显示

1. 打开 RViz2
2. 添加 "MarkerArray" 显示插件
3. 设置话题为 `/slam_toolbox/graph_visualization`
4. 位姿图将以图形方式显示

## 可视化内容

| 元素 | 类型 | 说明 |
|------|------|------|
| 位姿节点 | 球体/圆点 | 每个扫描位置 |
| 约束边 | 线段 | 节点之间的关联 |
| 回环边 | 不同颜色线段 | 检测到的回环约束 |

## 调试建议

```bash
# 查看话题信息
ros2 topic info /slam_toolbox/graph_visualization

# 查看标记数据
ros2 topic echo /slam_toolbox/graph_visualization
```

## 用途

- 直观了解 SLAM 建图质量
- 检查回环检测是否正确
- 发现建图中的异常节点或约束
