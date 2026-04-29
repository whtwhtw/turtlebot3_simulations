# /scan

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/scan` |
| 消息类型 | `sensor_msgs/msg/LaserScan` |
| 发布节点 | Gazebo LiDAR 传感器插件 → ros_gz_bridge |
| 订阅节点 | `/turtlebot3_drive`, SLAM 节点, 避障节点 |

## 功能说明

**2D 激光雷达扫描话题**：发布激光雷达在 360° 范围内扫描得到的距离数据。

核心职责：
1. 提供机器人周围环境的距离信息
2. 用于障碍物检测、避障决策和地图构建
3. 是 TurtleBot3 最重要的传感器数据

## 消息结构

```
LaserScan
  ├─ header: Header
  │   ├─ stamp: time
  │   └─ frame_id: string        # 通常为 "base_scan" 或 "laser_frame"
  ├─ angle_min: float            # 起始角度 (rad)
  ├─ angle_max: float            # 结束角度 (rad)
  ├─ angle_increment: float      # 角度增量 (rad)
  ├─ time_increment: float       # 时间增量 (s)
  ├─ scan_time: float            # 扫描周期时间 (s)
  ├─ range_min: float            # 最小测量距离 (m)
  ├─ range_max: float            # 最大测量距离 (m)
  └─ ranges: float[]             # 距离数据数组 (m)
      └─ intensities: float[]    # 反射强度数据 (可选)
```

## TurtleBot3 LiDAR 参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 型号 | LDS-01 (Hokuyo UTM-30LX 仿真) | 2D LiDAR |
| 扫描角度 | -180° ~ +180° (360°) | 全周扫描 |
| 角度分辨率 | 1° (0.017 rad) | 360 个数据点 |
| 测量范围 | 0.12m ~ 3.5m | 有效距离范围 |
| 更新频率 | 10Hz | 每秒 10 次扫描 |

## 数据解释

```python
# 索引与角度的关系
angle[i] = angle_min + i * angle_increment

# 示例：索引 180 对应的角度
angle[180] = -π + 180 * (2π/360) = 0°  # 正前方

# 距离值解释
ranges[i] = distance  # 单位：米
ranges[i] = inf       # 超出量程（无障碍物）
ranges[i] = nan       # 无效数据
```

## 典型应用场景

### 1. 避障决策

```cpp
// 检查前方 1.2m 内是否有障碍物
float front_min = *std::min_element(ranges.begin() + 170, ranges.begin() + 190);
if (front_min < 1.2) {
    // 需要避障
}
```

### 2. SLAM 建图

```
/scan ──→ slam_toolbox ──→ 提取特征点（墙角、边缘）
                           ↓
                    与历史数据匹配
                           ↓
                    更新地图
```

### 3. 扇区分析

```
前方扇区：[-10°, +10°]  →  ranges[170:190]
左侧扇区：[+60°, +120°] →  ranges[210:270]
右侧扇区：[-120°, -60°] →  ranges[90:150]
```

## 数据流

```
Gazebo LiDAR 传感器 ──→ 射线检测 ──→ ros_gz_bridge
                                              ↓
                                       发布 /scan
                                              ↓
                          ┌───────────────┬───────────────┐
                          ↓               ↓               ↓
                    turtlebot3_drive  slam_toolbox     RViz2
                    (避障决策)        (建图)         (可视化)
```

## 调试建议

```bash
# 查看激光数据
ros2 topic echo /scan

# 查看发布频率
ros2 topic hz /scan

# 查看话题信息
ros2 topic info /scan

# 在 RViz 中可视化
rviz2  # 添加 LaserScan 显示插件
```

## 注意事项

- 仿真中的 LiDAR 数据是理想的，无噪声
- 实际 LiDAR 会有测量噪声和丢包
- `inf` 值表示超出测量范围（正前方无障碍物）
- 障碍物距离越近，数值越小
- SLAM 和避障算法需要正确处理 `inf` 和 `nan` 值
