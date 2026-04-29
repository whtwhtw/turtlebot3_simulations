# /slam_toolbox

## 基本信息

| 属性 | 值 |
|------|-----|
| 节点名称 | `/slam_toolbox` |
| 节点类型 | SLAM 节点 |
| 所属包 | `slam_toolbox` |

## 功能说明

**2D 激光 SLAM 建图工具**：使用 2D 激光雷达数据进行同步定位与建图（SLAM）。

核心职责：
1. 订阅激光雷达扫描数据（`/scan`）
2. 订阅里程计数据（`/odom`）
3. 实时构建 2D 占据栅格地图（Occupancy Grid Map）
4. 进行回环检测（Loop Closure）以消除累积误差
5. 发布地图（`/map`）和机器人位姿估计

## 订阅话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D 激光雷达数据 |
| `/odom` | `nav_msgs/msg/Odometry` | 里程计数据（可选，提高精度） |
| `/tf` | `tf2_msgs/msg/TFMessage` | 坐标变换 |
| `/slam_toolbox/update` | `slam_toolbox/msg/Update` | 建图更新请求 |

## 发布话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/map` | `nav_msgs/msg/OccupancyGrid` | 2D 占据栅格地图 |
| `/map_metadata` | `nav_msgs/msg/MapMetaData` | 地图元数据（尺寸、分辨率等） |
| `/slam_toolbox/pose_graph` | `visualization_msgs/msg/MarkerArray` | 位姿图可视化 |
| `/slam_toolbox/graph_visualization` | `visualization_msgs/msg/MarkerArray` | 图优化可视化 |
| `/slam_toolbox/loop_closure_event` | `slam_toolbox/msg/LoopClosure` | 回环检测事件 |
| `/slam_toolbox/new_node_event` | `slam_toolbox/msg/NewNode` | 新节点添加事件 |
| `/slam_toolbox/scan_visualization` | `visualization_msgs/msg/MarkerArray` | 扫描数据可视化 |
| `/slam_toolbox/feedback` | `slam_toolbox/msg/Feedback` | 建图反馈信息 |
| `/slam_toolbox/transition_event` | `slam_toolbox/msg/Transition` | 状态转换事件 |

## SLAM 模式

| 模式 | 启动命令 | 说明 |
|------|---------|------|
| 在线异步 | `online_async_launch.py` | 最常用，建图与定位同时进行 |
| 在线同步 | `online_sync_launch.py` | 同步模式，精度更高但更慢 |
| 离线 | `offline_launch.py` | 使用录制的 bag 数据建图 |
| 定位 | `localization_launch.py` | 使用已有地图进行定位 |

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `map_resolution` | 0.05 | 地图分辨率（米/像素） |
| `max_laser_range` | 20.0 | 激光雷达最大使用距离 |
| `loop_search_maximum_distance` | 5.0 | 回环检测最大搜索距离 |
| `publish_map_tf` | true | 是否发布 map→odom 的 TF 变换 |
| `use_sim_time` | false | 是否使用仿真时钟 |

## 工作流程

```
/scan (LiDAR) ──→ slam_toolbox ──→ 特征提取
                                    ↓
/odom (里程计) ──→ 位姿估计 ──→ 图优化
                                    ↓
回环检测 ──→ 全局优化 ──→ /map 发布
```

## 地图保存

```bash
# 保存地图为 pgm + yaml
ros2 run nav2_map_server map_saver_cli -f maps/my_map --fmt png

# 保存为 slam_toolbox 格式（包含位姿图）
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: 'my_map'}"
```

## 在 TurtleBot3 中的使用

- 常与 Cartographer 二选一使用
- 适合室内 2D 环境建图
- 配合键盘控制或自动避障节点完成建图
- 建图完成后可将地图用于 Nav2 导航

## 调试建议

```bash
# 查看建图状态
ros2 topic echo /slam_toolbox/feedback

# 查看回环检测事件
ros2 topic echo /slam_toolbox/loop_closure_event

# 查看地图发布频率
ros2 topic hz /map
```
