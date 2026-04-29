# /map

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/map` |
| 消息类型 | `nav_msgs/msg/OccupancyGrid` |
| 发布节点 | `/slam_toolbox`, Cartographer |
| 订阅节点 | RViz2, Nav2, 地图保存节点 |

## 功能说明

**2D 占据栅格地图话题**：发布由激光雷达数据构建的环境地图。

核心职责：
1. 表示环境中每个栅格单元的状态（空闲、占据、未知）
2. 提供地图的元数据（分辨率、尺寸、原点等）
3. 用于机器人定位和路径规划

## 消息结构

```
OccupancyGrid
  ├─ header: Header
  │   ├─ stamp: time
  │   └─ frame_id: string        # 通常为 "map"
  ├─ info: MapMetaData
  │   ├─ map_load_time: time
  │   ├─ resolution: float       # 地图分辨率 (m/cell)，默认 0.05
  │   ├─ width: uint32           # 地图宽度 (cells)
  │   ├─ height: uint32          # 地图高度 (cells)
  │   └─ origin: Pose            # 地图原点在世界坐标系中的位姿
  └─ data: int8[]                # 占据栅格数据
      # 值含义：
      #   -1: 未知 (unknown)
      #    0: 空闲/可通行 (free)
      #   100: 占据/障碍物 (occupied)
```

## 栅格值说明

| 值 | 含义 | 颜色 (RViz) | 说明 |
|----|------|------------|------|
| -1 | 未知 | 灰色 | 传感器未探测到的区域 |
| 0 | 空闲 | 白色 | 可通行的区域 |
| 1~99 | 概率 | 灰色渐变 | 占据概率（中间值） |
| 100 | 占据 | 黑色 | 障碍物或墙壁 |

## 典型参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 分辨率 | 0.05 m/cell | 每个栅格代表 5cm |
| 地图尺寸 | 动态增长 | 随建图进行自动扩展 |
| 原点 | (0, 0, 0) | 建图起始点 |

## 数据流

```
激光雷达 (/scan) ──→ SLAM 节点 ──→ 特征提取
                                      ↓
里程计 (/odom) ──→ 位姿估计 ──→ 栅格更新
                                      ↓
                               发布 /map
                                      ↓
                          RViz 可视化 / 保存 / 导航
```

## 地图格式对比

| 格式 | 发布方式 | 用途 |
|------|---------|------|
| OccupancyGrid (话题) | 实时发布 | RViz 显示，导航使用 |
| PNG + YAML (文件) | map_saver 保存 | 持久存储，后续导航加载 |
| slam_toolbox 格式 | 服务调用保存 | 包含位姿图，可继续优化 |

## 保存地图

```bash
# 保存为 PNG + YAML 格式
ros2 run nav2_map_server map_saver_cli -f maps/my_map --fmt png

# 通过 slam_toolbox 服务保存
ros2 service call /slam_toolbox/save_map \
  slam_toolbox/srv/SaveMap "{name: 'my_map'}"
```

## 调试建议

```bash
# 查看地图话题
ros2 topic echo /map

# 查看地图发布频率
ros2 topic hz /map

# 查看地图信息
ros2 topic info /map

# RViz 可视化
rviz2  # 添加 Map 显示插件
```

## 在 TurtleBot3 中的应用

- 由 `slam_toolbox` 或 Cartographer 实时构建
- 用于 Nav2 导航栈的路径规划
- 建图完成后可保存用于后续的定位和导航
- 分辨率影响建图精度和计算量，需权衡选择
