# /map_metadata

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/map_metadata` |
| 消息类型 | `nav_msgs/msg/MapMetaData` |
| 发布节点 | `/slam_toolbox`, Cartographer |
| 订阅节点 | RViz2, Nav2 |

## 功能说明

**地图元数据话题**：发布地图的尺寸、分辨率和原点等元数据信息。

核心职责：
1. 提供地图的分辨率信息
2. 发布地图的尺寸（宽度、高度）
3. 定义地图原点在世界坐标系中的位姿

## 消息结构

```
MapMetaData
  ├─ map_load_time: time         # 地图加载时间
  ├─ resolution: float           # 地图分辨率 (m/cell)
  ├─ width: uint32               # 地图宽度 (cells)
  ├─ height: uint32              # 地图高度 (cells)
  └─ origin: Pose
      ├─ position: Point
      │   ├─ x: float
      │   ├─ y: float
      │   └─ z: float
      └─ orientation: Quaternion
          ├─ x: float
          ├─ y: float
          ├─ z: float
          └─ w: float
```

## 典型值

| 字段 | 示例值 | 说明 |
|------|--------|------|
| resolution | 0.05 | 5cm/像素 |
| width | 400 | 地图宽度 400 像素 |
| height | 400 | 地图高度 400 像素 |
| origin.position.x | -10.0 | 地图原点 X 坐标 |
| origin.position.y | -10.0 | 地图原点 Y 坐标 |
| origin.orientation.w | 1.0 | 无旋转 |

## 与 /map 的关系

```
/map ────────────→ 占据栅格数据 (data[])
                       ↓
/map_metadata ───→ 栅格如何解释 (分辨率、尺寸、原点)
```

`/map` 话题的消息中包含完整的 `OccupancyGrid`，其中已经嵌入了 `MapMetaData`。
`/map_metadata` 单独发布是为了方便只需要元数据的节点。

## 用途

| 场景 | 说明 |
|------|------|
| RViz 渲染 | 根据分辨率和尺寸正确显示地图 |
| 路径规划 | 计算实际距离（像素坐标 → 米坐标） |
| 坐标转换 | 在世界坐标和栅格坐标之间转换 |
| 地图保存 | 生成正确的 YAML 元数据文件 |

## 坐标转换示例

```python
# 世界坐标 (米) → 栅格坐标 (像素)
def world_to_map(world_x, world_y, metadata):
    map_x = int((world_x - metadata.origin.position.x) / metadata.resolution)
    map_y = int((world_y - metadata.origin.position.y) / metadata.resolution)
    return map_x, map_y

# 栅格坐标 (像素) → 世界坐标 (米)
def map_to_world(map_x, map_y, metadata):
    world_x = map_x * metadata.resolution + metadata.origin.position.x
    world_y = map_y * metadata.resolution + metadata.origin.position.y
    return world_x, world_y
```

## 调试建议

```bash
# 查看地图元数据
ros2 topic echo /map_metadata

# 查看话题信息
ros2 topic info /map_metadata
```
