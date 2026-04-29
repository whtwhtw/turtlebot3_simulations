# /pose

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/pose` |
| 消息类型 | `geometry_msgs/msg/PoseStamped` (推测) |
| 发布节点 | SLAM 节点，定位节点 |
| 订阅节点 | RViz2, 导航节点 |

## 功能说明

**位姿估计话题**：发布机器人在世界坐标系中的位置和姿态估计。

核心职责：
1. 提供机器人的 3D 位置（x, y, z）
2. 提供机器人的 3D 姿态（四元数表示）
3. 用于可视化和导航

## 消息结构

```
PoseStamped
  ├─ header: Header
  │   ├─ stamp: time
  │   └─ frame_id: string        # 通常为 "map" 或 "odom"
  └─ pose: Pose
      ├─ position: Point
      │   ├─ x: float            # X 坐标 (m)
      │   ├─ y: float            # Y 坐标 (m)
      │   └─ z: float            # Z 坐标 (m)，地面机器人通常接近 0
      └─ orientation: Quaternion
          ├─ x: float
          ├─ y: float
          ├─ z: float            # 偏航轴
          └─ w: float
```

## 位姿表示

### 四元数转欧拉角

```python
import math

def quaternion_to_euler(q):
    """四元数转欧拉角（roll, pitch, yaw）"""
    # 偏航角（yaw）- 对地面机器人最重要
    yaw = math.atan2(2 * (q.w * q.z + q.x * q.y),
                     1 - 2 * (q.y * q.y + q.z * q.z))
    return yaw  # 单位：弧度
```

### 典型位姿

```
原点：
  position: (0, 0, 0)
  orientation: (0, 0, 0, 1)  # 四元数，表示朝向为 0°

前进 2 米，左转 90°：
  position: (2, 0, 0)
  orientation: (0, 0, 0.707, 0.707)  # 90° (π/2)
```

## 与 /odom 的区别

| 特性 | /pose | /odom |
|------|-------|-------|
| 内容 | 仅位姿 | 位姿 + 速度 + 协方差 |
| 来源 | SLAM/定位 | 里程计积分 |
| 精度 | 有回环校正 | 有累积漂移 |
| 坐标系 | map | odom |

## 数据流

```
SLAM 节点 ──→ 位姿估计 ──→ /pose ──→ RViz 显示
                                  ──→ Nav2 使用
                                  ──→ 日志记录
```

## 调试建议

```bash
# 查看位姿数据
ros2 topic echo /pose

# 查看发布频率
ros2 topic hz /pose

# RViz 可视化
rviz2  # 添加 Pose 显示插件
```

## 在 RViz 中显示

1. 打开 RViz2
2. 添加 "Pose" 显示插件
3. 设置话题为 `/pose`
4. 调整箭头大小和颜色

## 注意事项

- `/pose` 通常来自 SLAM 或 AMCL 定位
- 与 `/odom` 相比，`/pose` 更准确（有回环检测或地图匹配校正）
- 2D 地面机器人主要关注 position.x、position.y 和 orientation.z/w
