# /robot_description

## 基本信息

| 属性 | 值 |
|------|-----|
| 话题名称 | `/robot_description` |
| 消息类型 | `std_msgs/msg/String` |
| 发布节点 | `/robot_state_publisher` |
| 订阅节点 | RViz2, Gazebo, 其他需要机器人模型的节点 |

## 功能说明

**机器人描述话题**：发布机器人的 URDF 描述文本。

核心职责：
1. 提供完整的 URDF（Unified Robot Description Format）XML 描述
2. 定义机器人的结构（link、joint、传感器等）
3. 供 RViz2 等工具渲染机器人模型

## 消息结构

```
String
  └─ data: string    # URDF XML 文本内容
```

## URDF 内容示例

```xml
<?xml version="1.0" ?>
<robot name="turtlebot3_burger">
  <!-- Link 定义 -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.140 0.140 0.100"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="0.140 0.140 0.100"/>
      </geometry>
    </collision>
  </link>

  <!-- Joint 定义 -->
  <joint name="wheel_left_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left_link"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- 传感器插件 -->
  <gazebo>
    <plugin name="differential_drive_controller" ...>
      ...
    </plugin>
  </gazebo>
</robot>
```

## TurtleBot3 机器人模型

| 模型 | 特点 | 传感器 |
|------|------|--------|
| burger | 基础款 | LiDAR + IMU |
| burger_cam | 视觉增强款 | LiDAR + IMU + RGB 相机 |
| waffle | 高级款 | LiDAR + IMU + 深度相机 |
| waffle_pi | 视觉导航款 | LiDAR + IMU + RGB 相机 |

## 数据流

```
URDF 文件 ──→ robot_state_publisher ──→ /robot_description
                                               ↓
                                       RViz2 加载模型
                                       Gazebo 加载模型
                                       其他节点使用
```

## 切换机器人模型

```bash
# 设置环境变量
export TURTLEBOT3_MODEL=waffle

# 重新启动仿真
./turtlebot3_simulations.sh turtlebot3_world
```

## 在 RViz2 中显示

1. 打开 RViz2
2. 添加 "RobotModel" 显示插件
3. 设置 "Robot Description" 话题为 `/robot_description`
4. 机器人模型将自动显示

## 调试建议

```bash
# 查看机器人描述
ros2 topic echo /robot_description

# 查看话题信息
ros2 topic info /robot_description

# 保存 URDF 到文件
ros2 topic echo /robot_description --once > robot.urdf
```

## 注意事项

- URDF 描述通常是不变的（启动后不会更改）
- RViz2 启动时会等待 `/robot_description` 话题有数据
- 可以通过 `robot_state_publisher` 的参数指定 URDF 文件路径
- 仿真中切换模型需要重启容器或重新设置环境变量
