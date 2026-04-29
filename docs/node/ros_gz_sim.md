# /ros_gz_sim

## 基本信息

| 属性 | 值 |
|------|-----|
| 节点名称 | `/ros_gz_sim` |
| 节点类型 | 仿真器节点 |
| 所属包 | `ros_gz_sim` |

## 功能说明

**Gazebo 仿真器主节点**：负责启动和管理 Gazebo Garden 仿真环境。

核心职责：
1. 加载和运行 Gazebo 物理引擎
2. 加载 `.world` 世界文件（包含环境、模型、灯光等）
3. 加载和运行 Gazebo 插件（如障碍物、交通灯等）
4. 发布仿真时钟（`/clock`）
5. 管理仿真中的传感器和执行器

## 发布话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/clock` | `rosgraph_msgs/msg/Clock` | 仿真时钟（仿真时间，非真实时间） |
| `/robot_description` | `std_msgs/msg/String` | 从世界文件中提取的机器人描述 |

## 订阅话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/clock` | `rosgraph_msgs/msg/Clock` | 时钟同步 |

## 主要功能

| 功能 | 说明 |
|------|------|
| 物理引擎 | 刚体动力学、碰撞检测、重力模拟 |
| 传感器仿真 | LiDAR、IMU、相机、深度相机等 |
| 插件系统 | 支持 C++ 自定义插件（obstacles、traffic_light 等） |
| 渲染引擎 | 3D 可视化、GUI 界面 |
| 时间管理 | 支持实时、加速、减速仿真 |

## 仿真时间控制

```bash
# 暂停仿真
gz sim -p

# 恢复仿真
gz sim -r

# 调整仿真速度因子
gz sim --speed-factor 0.5  # 半速
gz sim --speed-factor 2.0  # 双倍速度
```

## 在 TurtleBot3 中的角色

- 加载 `turtlebot3_world.world` 等世界文件
- 运行 `obstacles.cpp`、`traffic_light_plugin.cpp` 等自定义插件
- 通过传感器发布 `/scan`、`/imu`、`/joint_states` 等数据
- 接收 `/cmd_vel` 控制机器人运动

## 调试建议

```bash
# 查看 Gazebo 中的所有话题
gz topic -l

# 查看 Gazebo 中的话题数据
gz topic -e -t /scan

# 查看仿真状态
gz sim -s
```
