# /tf

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/tf` |
| 消息类型 | `tf2_msgs/msg/TFMessage` |
| 发布节点 | `/robot_state_publisher`, SLAM 节点 |
| 订阅节点 | RViz2, 导航节点, 状态估计节点 |

## 功能说明

**坐标变换话题**：发布随时间变化的动态坐标变换信息。

核心职责：
1. 维护坐标系之间的变换关系（平移 + 旋转）
2. 支持坐标变换的查询和插值
3. 构建完整的坐标变换树（TF Tree）

## 消息结构

```
TFMessage
  └─ transforms: TransformStamped[]  # 变换列表

TransformStamped
  ├─ header: Header
  │   ├─ stamp: time
  │   └─ frame_id: string        # 父坐标系
  ├─ child_frame_id: string      # 子坐标系
  └─ transform: Transform
      ├─ translation: Vector3    # 平移
      │   ├─ x: float
      │   ├─ y: float
      │   └─ z: float
      └─ rotation: Quaternion    # 旋转（四元数）
          ├─ x: float
          ├─ y: float
          ├─ z: float
          └─ w: float
```

## TurtleBot3 坐标系关系

```
                    map
                     │
                     │ (SLAM/AMCL 发布)
                     │ 校正漂移
                     ↓
                   odom
                     │
                     │ (robot_state_publisher 发布)
                     │ 关节运动计算
                     ↓
            base_footprint
                     │
                     │ (固定变换)
                     ↓
               base_link
                ╱     ╲
               ╱       ╲
              ╱         ╲
        base_scan      imu_link
        (LiDAR)        (IMU)
```

## TF 树规则

1. **单父原则**：每个坐标系只能有一个父坐标系
2. **无环原则**：坐标变换不能形成环
3. **树状结构**：所有坐标系形成一棵树

## 典型变换

### 1. odom → base_footprint

```
由里程计积分计算：
translation: (x, y, 0)      # 位置
rotation: (0, 0, sin(θ/2), cos(θ/2))  # 偏航角
```

### 2. base_link → base_scan

```
固定变换（由 URDF 定义）：
translation: (0.0, 0.0, 0.0)  # 传感器位置偏移
rotation: (0, 0, 0, 1)        # 无旋转
```

## 查询坐标变换

### C++

```cpp
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>

tf2_ros::Buffer buffer(node->get_clock());
tf2_ros::TransformListener listener(buffer);

geometry_msgs::msg::TransformStamped transform;
transform = buffer.lookupTransform("map", "base_link", tf2::TimePointZero);
```

### Python

```python
from tf2_ros import Buffer, TransformListener

buffer = Buffer()
listener = TransformListener(buffer, node)

transform = buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
```

## 调试建议

```bash
# 查看 TF 树
ros2 run tf2_tools view_frames

# 查看两个坐标系之间的变换
ros2 run tf2_ros tf2_echo source_frame target_frame

# 查看 /tf 话题数据
ros2 topic echo /tf
```

## /tf 与 /tf_static 的区别

| 特性 | /tf | /tf_static |
|------|-----|------------|
| 内容 | 动态变换 | 静态变换 |
| 发布频率 | 高（10-50Hz） | 低（启动时发布一次） |
| 示例 | odom→base_link | base_link→base_scan |
| 来源 | 里程计、传感器 | URDF 固定关系 |

## 注意事项

- TF 数据是有时间戳的，支持历史查询
- 查询变换时应注意时间同步
- TF 树出现断裂会导致查询失败
- SLAM 回环检测会校正 map→odom 的变换
