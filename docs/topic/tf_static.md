# /tf_static

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/tf_static` |
| 消息类型 | `tf2_msgs/msg/TFMessage` |
| 发布节点 | `/robot_state_publisher` |
| 订阅节点 | 所有需要坐标变换的节点 |

## 功能说明

**静态坐标变换话题**：发布不随时间变化的坐标变换关系。

核心职责：
1. 发布机器人各部件之间的固定变换关系
2. 减少不必要的重复发布
3. 与 `/tf` 配合构建完整的坐标变换树

## 消息结构

```
TFMessage
  └─ transforms: TransformStamped[]  # 静态变换列表

TransformStamped
  ├─ header: Header
  │   ├─ stamp: time
  │   └─ frame_id: string        # 父坐标系
  ├─ child_frame_id: string      # 子坐标系
  └─ transform: Transform
      ├─ translation: Vector3    # 固定平移
      └─ rotation: Quaternion    # 固定旋转
```

## TurtleBot3 中的静态变换

### URDF 定义的固定关系

```
base_link
    │
    ├──→ base_scan        # LiDAR 传感器位置
    │      translation: (0, 0, 0.0)
    │      rotation: (0, 0, 0, 1)
    │
    ├──→ imu_link          # IMU 传感器位置
    │      translation: (0, 0, 0.0)
    │      rotation: (0, 0, 0, 1)
    │
    ├──→ wheel_left_link   # 左轮关节（连续旋转，非静态）
    └──→ wheel_right_link  # 右轮关节（连续旋转，非静态）
```

### 示例变换

```yaml
# base_link → base_scan
header:
  frame_id: "base_link"
child_frame_id: "base_scan"
transform:
  translation: {x: 0.0, y: 0.0, z: 0.0}
  rotation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
```

## 与 /tf 的区别

| 特性 | /tf | /tf_static |
|------|-----|------------|
| 变换类型 | 动态变化 | 固定不变 |
| 发布频率 | 持续发布（10-50Hz） | 启动时发布一次 |
| 数据来源 | 里程计、传感器 | URDF 定义 |
| 示例 | odom→base_link | base_link→base_scan |
| 带宽占用 | 较高 | 极低 |

## 坐标变换树完整示例

```
map ──→ odom ──→ base_footprint ──→ base_link ──→ base_scan
  │        │           │                          └─→ imu_link
  │        │           │                          └─→ camera_link
  │        │           │
  │        │           └─→ caster_wheel_link
  │        │
  │        └─→ (动态，由里程计发布)
  │
  └─→ (动态，由 SLAM/AMCL 发布)
```

## 调试建议

```bash
# 查看静态变换数据
ros2 topic echo /tf_static

# 查看完整 TF 树
ros2 run tf2_tools view_frames

# 查看特定变换
ros2 run tf2_ros tf2_echo base_link base_scan
```

## 注意事项

- 静态变换在节点启动后不会改变
- URDF 修改后需要重新发布静态变换
- 传感器安装位置变化时需要更新 URDF
- 静态变换也支持时间戳，可以查询历史值
- TF2 库会合并 `/tf` 和 `/tf_static` 进行查询
