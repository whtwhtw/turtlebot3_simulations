# /slam_toolbox/update

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/update` |
| 消息类型 | `slam_toolbox/msg/Update` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | 监控系统，其他节点 |

## 功能说明

**建图更新话题**：发布 SLAM 建图过程中的更新信息。

核心职责：
1. 提供建图过程中的增量更新信息
2. 通知其他模块位姿图的变化
3. 用于实时监控建图进度

## 消息结构

```
Update
  ├─ header: Header
  ├─ update_type: uint8          # 更新类型
  ├─ node_id: int32              # 相关节点 ID
  └─ ...                         # 其他更新数据
```

## 更新类型

| 类型 | 说明 |
|------|------|
| NODE_ADDED | 新节点添加 |
| NODE_UPDATED | 节点更新 |
| NODE_REMOVED | 节点删除 |
| EDGE_ADDED | 新边添加 |
| EDGE_REMOVED | 边删除 |
| MAP_UPDATED | 地图更新 |

## 调试建议

```bash
# 查看建图更新
ros2 topic echo /slam_toolbox/update

# 查看发布频率
ros2 topic hz /slam_toolbox/update
```

## 用途

- 实时监控建图过程
- 了解位姿图的变化情况
- 调试建图算法和参数

## 与 feedback 的关系

| 话题 | 内容 | 频率 |
|------|------|------|
| `/slam_toolbox/update` | 具体更新事件 | 按需发布 |
| `/slam_toolbox/feedback` | 整体状态反馈 | 持续发布 |
