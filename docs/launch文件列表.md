# TurtleBot3 启动文件列表

> 本项目所有 ROS2 launch 文件 (.launch.py) 的完整清单及使用说明。

## 📁 turtlebot3_gazebo/launch/

### 世界场景启动文件

| 文件名 | 功能 | 命令示例 |
|--------|------|----------|
| `empty_world.launch.py` | 空世界，无障碍物 | `ros2 launch turtlebot3_gazebo empty_world.launch.py` |
| `turtlebot3_world.launch.py` | World 场景，带基础障碍物 | `ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py` |
| `turtlebot3_house.launch.py` | House 室内场景，复杂环境 | `ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py` |

### DQN 强化学习场景

| 文件名 | 功能 | 说明 |
|--------|------|--------|
| `turtlebot3_dqn_stage1.launch.py` | DQN Stage 1 | 基础避障训练 |
| `turtlebot3_dqn_stage2.launch.py` | DQN Stage 2 | 增加障碍物复杂度 |
| `turtlebot3_dqn_stage3.launch.py` | DQN Stage 3 | 动态障碍物训练 |
| `turtlebot3_dqn_stage4.launch.py` | DQN Stage 4 | 完整场景训练 |

### 辅助启动文件

| 文件名 | 功能 | 命令示例 |
|--------|------|----------|
| `robot_state_publisher.launch.py` | 发布机器人 TF 变换 | 内部调用，一般不直接使用 |
| `spawn_turtlebot3.launch.py` | 在 Gazebo 中生成机器人 | 内部调用，支持 x/y 位置参数 |
| `rviz.launch.py` | 独立启动 RViz2 | `ros2 launch turtlebot3_gazebo rviz.launch.py` |
| `teleop_keyboard.launch.py` | 键盘控制节点 | `ros2 launch turtlebot3_gazebo teleop_keyboard.launch.py` |
| `turtlebot3_drive.launch.py` | 自动避障演示节点 | `ros2 launch turtlebot3_gazebo turtlebot3_drive.launch.py` |

### 统一入口

| 文件名 | 功能 | 使用方式 |
|--------|------|----------|
| `main.launch.py` | 统一入口，通过参数选择场景 | `ros2 launch turtlebot3_gazebo main.launch.py world:=world` |

**main.launch.py 参数：**
```bash
# world 参数可选值
world:=empty           # 空世界（默认）
world:=world           # World 场景
world:=house           # House 场景
world:=dqn_stage1~4    # DQN 训练场景

# 其他参数
x_pose:=0.0            # 机器人初始 X 坐标
y_pose:=0.0            # 机器人初始 Y 坐标
use_sim_time:=true     # 是否使用仿真时间
```

---

## 📁 turtlebot3_fake_node/launch/

### Fake Node 启动文件（无 Gazebo，仅 RViz）

| 文件名 | 功能 | 命令示例 |
|--------|------|----------|
| `fake_node.launch.py` | **推荐入口**：启动 fake_node + RViz | `ros2 launch turtlebot3_fake_node fake_node.launch.py` |
| `turtlebot3_fake_node.launch.py` | 原始启动文件（含 RViz） | 同 fake_node.launch.py |
| `rviz2.launch.py` | 仅启动 RViz2 | 内部调用 |

**fake_node 特点：**
- ✅ 无需 Gazebo，启动快，资源占用低
- ✅ 适合算法快速验证、CI/CD 测试
- ✅ 模拟 `/odom`、`/scan`、`/joint_states` 等话题
- ❌ 无真实物理仿真，传感器数据为模拟值

---

## 🔧 脚本调用方式

使用 `turtlebot3_simulations.sh` 脚本可简化启动：

```bash
# Gazebo 场景
./turtlebot3_simulations.sh empty_world
./turtlebot3_simulations.sh turtlebot3_world
./turtlebot3_simulations.sh turtlebot3_house
./turtlebot3_simulations.sh dqn_stage1

# Fake Node（RViz only）
./turtlebot3_simulations.sh fake_node

# 辅助工具
./turtlebot3_simulations.sh rviz          # 启动 RViz
./turtlebot3_simulations.sh teleop        # 键盘控制
./turtlebot3_simulations.sh turtlebot3_drive  # 自动避障演示
```

---

## 📋 启动文件参数参考

### 通用参数

```python
# 所有 launch 文件支持的通用参数
use_sim_time: bool      # 是否使用 /clock 仿真时间，默认 true
x_pose: float           # 机器人初始 X 坐标，默认 0.0
y_pose: float           # 机器人初始 Y 坐标，默认 0.0
```

### 使用方式

```bash
# 命令行指定参数
ros2 launch turtlebot3_gazebo empty_world.launch.py \
    x_pose:=2.0 \
    y_pose:=3.0 \
    use_sim_time:=true

# 在 launch 文件中覆盖默认值
from launch.substitutions import LaunchConfiguration
x_pose = LaunchConfiguration('x_pose', default='0.0')
```

---

## 🔄 启动流程依赖图

```
main.launch.py (统一入口)
    │
    ├──► empty_world.launch.py
    │       ├──► gzserver (Gazebo server)
    │       ├──► gzclient (Gazebo GUI)
    │       ├──► robot_state_publisher.launch.py
    │       └──► spawn_turtlebot3.launch.py
    │
    ├──► turtlebot3_world.launch.py  (同上 + 世界文件)
    ├──► turtlebot3_house.launch.py  (同上 + 世界文件)
    └──► turtlebot3_dqn_stage*.launch.py  (同上 + DQN 配置)

fake_node.launch.py (RViz only)
    ├──► turtlebot3_fake_node (模拟节点)
    ├──► robot_state_publisher (TF 发布)
    └──► rviz2.launch.py (可视化)
```

---

## 💡 使用建议

| 场景 | 推荐启动文件 | 理由 |
|------|-------------|------|
| **快速算法验证** | `fake_node.launch.py` | 无需 Gazebo，秒级启动 |
| **物理仿真测试** | `turtlebot3_world.launch.py` | 真实物理引擎，传感器模拟 |
| **SLAM 开发** | `turtlebot3_house.launch.py` | 复杂室内环境，适合建图 |
| **强化学习训练** | `turtlebot3_dqn_stage*.launch.py` | 预置奖励函数和训练配置 |
| **可视化调试** | `rviz.launch.py` | 独立 RViz，可连接任意 ROS2 节点 |
| **手动控制测试** | `teleop_keyboard.launch.py` | 单独启动键盘控制，便于组合 |

---

> 📌 **提示**：所有 launch 文件均支持通过 `ros2 launch --show-args <package> <file>` 查看完整参数列表。
