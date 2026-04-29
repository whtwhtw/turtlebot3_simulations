# /slam_toolbox/scan_visualization

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/slam_toolbox/scan_visualization` |
| 消息类型 | `visualization_msgs/msg/MarkerArray` |
| 发布节点 | `/slam_toolbox` |
| 订阅节点 | RViz2 |

## 功能说明

**激光扫描可视化话题**：发布用于 SLAM 建图的激光扫描数据可视化标记。

核心职责：
1. 在 RViz 中显示激光扫描点
2. 显示扫描数据与地图的匹配情况
3. 帮助调试建图算法

## 消息结构

```
MarkerArray
  └─ markers: Marker[]           # 标记列表
      ├─ id: int32               # 标记 ID
      ├─ type: uint8             # 标记类型 (POINTS, LINE_LIST 等)
      ├─ action: uint8           # 操作
      ├─ pose: Pose              # 标记位姿
      ├─ points: Point[]         # 点云数据
      ├─ scale: Vector3          # 标记尺寸
      ├─ color: ColorRGBA        # 颜色
      └─ ...
```

## 可视化内容

| 元素 | 类型 | 说明 |
|------|------|------|
| 当前扫描 | 绿色点 | 最新的激光扫描数据 |
| 历史扫描 | 淡色点 | 之前的扫描数据 |
| 匹配点 | 高亮点 | 与地图匹配的扫描点 |
| 异常点 | 红色点 | 未匹配或异常的扫描点 |

## 在 RViz 中显示

1. 打开 RViz2
2. 添加 "MarkerArray" 显示插件
3. 设置话题为 `/slam_toolbox/scan_visualization`
4. 激光扫描将显示在地图上方

## 调试建议

```bash
# 查看扫描可视化数据
ros2 topic echo /slam_toolbox/scan_visualization

# 查看发布频率
ros2 topic hz /slam_toolbox/scan_visualization
```

## 用途

- 检查激光扫描数据是否正确
- 观察扫描与地图的匹配情况
- 发现传感器数据异常
- 调试建图参数

## 与 /scan 的关系

| 话题 | 内容 | 格式 |
|------|------|------|
| `/scan` | 原始激光数据 | LaserScan 消息 |
| `/slam_toolbox/scan_visualization` | 可视化标记 | MarkerArray，用于 RViz 显示 |

`/scan` 是原始传感器数据，`/slam_toolbox/scan_visualization` 是 slam_toolbox 处理后用于可视化的标记。
