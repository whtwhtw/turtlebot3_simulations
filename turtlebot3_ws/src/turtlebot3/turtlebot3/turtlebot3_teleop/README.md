# TurtleBot3 Teleoperation Package

## 📋 目录

- [概述](#概述)
- [文件结构](#文件结构)
- [详细文件说明](#详细文件说明)
  - [package.xml](#packagexml)
  - [setup.py](#setuppy)
  - [setup.cfg](#setupcfg)
  - [teleop_keyboard.py](#teleop_keyboardpy)
  - [__init__.py](#__init__py)
  - [CHANGELOG.rst](#changelogrst)
  - [resource/turtlebot3_teleop](#resourceturtlebot3_teleop)
- [使用方法](#使用方法)
- [技术细节](#技术细节)
- [版本历史](#版本历史)

---

## 概述

**turtlebot3_teleop** 是 TurtleBot3 机器人的键盘遥控功能包，允许用户通过键盘按键控制机器人的移动。该包基于 ROS 2 (Robot Operating System 2) 开发，支持多种 TurtleBot3 型号（Burger、Waffle、Waffle Pi）。

### 主要功能
- 🎮 通过键盘实时控制机器人移动
- ⚡ 支持线速度和角速度的增量调节
- 🛡️ 内置速度限制保护机制
- 💻 跨平台支持（Linux、Windows）
- 🔄 支持不同 ROS 2 发行版（Humble、Jazzy 等）

---

## 文件结构

```
turtlebot3_teleop/
├── package.xml                          # ROS 2 包描述文件
├── setup.py                             # Python 包安装配置
├── setup.cfg                            # Python 包安装选项配置
├── CHANGELOG.rst                        # 版本更新日志
├── resource/
│   └── turtlebot3_teleop               # Ament 资源标记文件
└── turtlebot3_teleop/
    ├── __init__.py                      # Python 包初始化文件
    └── script/
        ├── __init__.py                  # 脚本模块初始化文件
        └── teleop_keyboard.py           # 键盘遥控主程序（核心文件）
```

---

## 详细文件说明

### package.xml

**文件路径**: `turtlebot3_teleop/package.xml`

**作用**: ROS 2 包的元数据描述文件，定义包的基本信息和依赖关系。

**关键内容**:
- **包名**: `turtlebot3_teleop`
- **版本**: 2.3.6
- **描述**: 使用键盘控制 TurtleBot3 的遥操作节点
- **许可证**: Apache 2.0
- **维护者**: Pyo (pyo@robotis.com)
- **作者**: Darby Lim, Pyo, Will Son
- **执行依赖**:
  - `geometry_msgs`: 提供 Twist 和 TwistStamped 消息类型
  - `rclpy`: ROS 2 Python 客户端库
- **构建类型**: `ament_python`（Python 包构建系统）

**重要性**: 此文件是 ROS 2 包的核心配置文件，rosdep 和 colcon 构建系统依赖此文件来解析依赖关系和构建包。

---

### setup.py

**文件路径**: `turtlebot3_teleop/setup.py`

**作用**: Python 包的安装配置文件，定义如何打包和安装 Python 代码。

**关键配置**:

1. **包信息**:
   ```python
   name='turtlebot3_teleop'
   version='2.3.6'
   ```

2. **数据文件安装**:
   - 将 `resource/turtlebot3_teleop` 安装到 ament 索引
   - 将 `package.xml` 安装到共享目录

3. **入口点配置** (最重要):
   ```python
   entry_points={
       'console_scripts': [
           'teleop_keyboard = turtlebot3_teleop.script.teleop_keyboard:main'
       ],
   }
   ```
   - 定义了可执行命令 `teleop_keyboard`
   - 映射到 `turtlebot3_teleop.script.teleop_keyboard` 模块的 `main()` 函数
   - 安装后可通过 `ros2 run turtlebot3_teleop teleop_keyboard` 运行

4. **元数据**:
   - 作者、维护者信息
   - 分类器（Classifier）：定义包的属性
   - 关键词：ROS

**重要性**: 此文件决定了 Python 包如何被构建、安装和执行，特别是 `entry_points` 部分使得脚本可以作为 ROS 2 节点运行。

---

### setup.cfg

**文件路径**: `turtlebot3_teleop/setup.cfg`

**作用**: Python 包安装的附加配置，指定脚本文件的安装位置。

**配置内容**:
```ini
[develop]
script_dir=$base/lib/turtlebot3_teleop

[install]
install_scripts=$base/lib/turtlebot3_teleop
```

**解释**:
- **开发模式** (`[develop]`): 在开发模式下，脚本安装在 `$base/lib/turtlebot3_teleop` 目录
- **安装模式** (`[install]`): 在正式安装时，脚本也安装在相同位置
- `$base` 通常是 ROS 2 工作空间的 install 目录

**重要性**: 确保可执行脚本被安装到正确的位置，使 ROS 2 能够找到并执行它们。

---

### teleop_keyboard.py

**文件路径**: `turtlebot3_teleop/turtlebot3_teleop/script/teleop_keyboard.py`

**作用**: ⭐ **核心文件** - 键盘遥控的主要实现代码，包含所有控制逻辑。

#### 详细功能分解

##### 1. **导入模块** (第 35-42 行)
```python
import os
import select
import sys
from geometry_msgs.msg import Twist, TwistStamped
import rclpy
from rclpy.clock import Clock
from rclpy.qos import QoSProfile
```
- 标准库：操作系统接口、I/O 多路复用、系统参数
- ROS 2 消息：Twist（基础速度指令）、TwistStamped（带时间戳的速度指令）
- ROS 2 核心：rclpy 客户端库、时钟、QoS 配置

##### 2. **平台兼容性处理** (第 44-48 行)
```python
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Linux/Mac
    import termios
    import tty
```
- **Windows**: 使用 `msvcrt` 进行键盘输入
- **Linux/Mac**: 使用 `termios` 和 `tty` 进行原始键盘输入

##### 3. **速度参数定义** (第 50-57 行)

**Burger 型号**:
```python
BURGER_MAX_LIN_VEL = 0.22   # 最大线速度 0.22 m/s
BURGER_MAX_ANG_VEL = 2.84   # 最大角速度 2.84 rad/s
```

**Waffle/Waffle Pi 型号**:
```python
WAFFLE_MAX_LIN_VEL = 0.26   # 最大线速度 0.26 m/s
WAFFLE_MAX_ANG_VEL = 1.82   # 最大角速度 1.82 rad/s
```

**步进值**:
```python
LIN_VEL_STEP_SIZE = 0.01    # 线速度每次增减 0.01 m/s
ANG_VEL_STEP_SIZE = 0.1     # 角速度每次增减 0.1 rad/s
```

**型号检测**:
```python
TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']
```
从环境变量获取机器人型号，自动适配不同的速度限制。

##### 4. **用户界面消息** (第 59-73 行)
```python
msg = """
Control Your TurtleBot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity
a/d : increase/decrease angular velocity
space key, s : force stop
CTRL-C to quit
"""
```
显示控制说明和操作提示。

##### 5. **核心函数**

###### `get_key(settings)` (第 79-89 行)
**功能**: 非阻塞式读取键盘输入

**实现**:
- **Windows**: 使用 `msvcrt.getch()` 直接读取
- **Linux**: 
  - 设置终端为原始模式（`tty.setraw`）
  - 使用 `select.select` 实现 0.1 秒超时
  - 读取后恢复终端设置（`termios.tcsetattr`）

**返回值**: 单个字符或空字符串

###### `print_vels(target_linear_velocity, target_angular_velocity)` (第 92-96 行)
**功能**: 打印当前目标速度值

###### `make_simple_profile(output_vel, input_vel, slop)` (第 99-107 行)
**功能**: 实现平滑的速度过渡（加速度限制）

**算法**:
```python
if input_vel > output_vel:
    output_vel = min(input_vel, output_vel + slop)  # 缓慢加速
elif input_vel < output_vel:
    output_vel = max(input_vel, output_vel - slop)  # 缓慢减速
```
- 防止速度突变，使运动更平滑
- `slop` 参数控制变化速率

###### `constrain(input_vel, low_bound, high_bound)` (第 110-118 行)
**功能**: 限制速度在指定范围内

**实现**: 简单的边界检查，确保速度不超过最小值和最大值。

###### `check_linear_limit_velocity(velocity)` (第 121-126 行)
**功能**: 根据机器人型号检查线速度限制

###### `check_angular_limit_velocity(velocity)` (第 129-134 行)
**功能**: 根据机器人型号检查角速度限制

##### 6. **主函数 `main()`** (第 137-258 行)

这是整个程序的核心，包含完整的控制循环。

###### **初始化阶段** (第 138-152 行)
```python
# 保存终端设置（用于退出时恢复）
settings = None
if os.name != 'nt':
    settings = termios.tcgetattr(sys.stdin)

# 初始化 ROS 2
rclpy.init()
ROS_DISTRO = os.environ.get('ROS_DISTRO')
qos = QoSProfile(depth=10)
node = rclpy.create_node('teleop_keyboard')

# 根据 ROS 版本选择消息类型
if ROS_DISTRO == 'humble':
    pub = node.create_publisher(Twist, 'cmd_vel', qos)
else:
    pub = node.create_publisher(TwistStamped, 'cmd_vel', qos)
```

**关键点**:
- 检测 ROS 2 发行版
- **Humble**: 使用 `Twist` 消息
- **其他版本（如 Jazzy）**: 使用 `TwistStamped` 消息（带时间戳）

###### **变量初始化** (第 154-158 行)
```python
status = 0                              # 状态计数器
target_linear_velocity = 0.0            # 目标线速度
target_angular_velocity = 0.0           # 目标角速度
control_linear_velocity = 0.0           # 实际控制线速度（平滑后）
control_angular_velocity = 0.0          # 实际控制角速度（平滑后）
```

###### **主控制循环** (第 161-232 行)

**按键处理逻辑**:

| 按键 | 功能 | 影响变量 |
|------|------|---------|
| `w` | 增加线速度 | `target_linear_velocity += 0.01` |
| `x` | 减小线速度 | `target_linear_velocity -= 0.01` |
| `a` | 增加角速度（左转） | `target_angular_velocity += 0.1` |
| `d` | 减小角速度（右转） | `target_angular_velocity -= 0.1` |
| `空格` 或 `s` | 紧急停止 | 所有速度归零 |
| `Ctrl+C` | 退出程序 | 跳出循环 |

**速度平滑处理** (第 208-217 行):
```python
# 对线速度应用平滑滤波
control_linear_velocity = make_simple_profile(
    control_linear_velocity,
    target_linear_velocity,
    (LIN_VEL_STEP_SIZE / 2.0))

# 对角速度应用平滑滤波
control_angular_velocity = make_simple_profile(
    control_angular_velocity,
    target_angular_velocity,
    (ANG_VEL_STEP_SIZE / 2.0))
```

**消息发布** (第 219-238 行):

对于 **Humble**:
```python
twist = Twist()
twist.linear.x = control_linear_velocity
twist.angular.z = control_angular_velocity
pub.publish(twist)
```

对于 **其他版本**:
```python
twist_stamped = TwistStamped()
twist_stamped.header.stamp = Clock().now().to_msg()
twist_stamped.twist.linear.x = control_linear_velocity
twist_stamped.twist.angular.z = control_angular_velocity
pub.publish(twist_stamped)
```

###### **清理阶段** (第 240-258 行)
```python
finally:
    # 发布零速度命令，确保机器人停止
    if ROS_DISTRO == 'humble':
        twist = Twist()
        # ... 设置为零
    else:
        twist_stamped = TwistStamped()
        # ... 设置为零
    pub.publish(twist)
    
    # 恢复终端设置
    if os.name != 'nt':
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
```

**重要性**: 确保程序退出时机器人安全停止，终端恢复正常状态。

---

### __init__.py

**文件路径**: 
- `turtlebot3_teleop/turtlebot3_teleop/__init__.py`
- `turtlebot3_teleop/turtlebot3_teleop/script/__init__.py`

**作用**: Python 包初始化文件，标识目录为 Python 包。

**内容**: 空文件或仅包含注释

**重要性**: 
- 使 Python 能够将目录识别为模块包
- 允许使用 `import turtlebot3_teleop` 导入
- 符合 Python 包规范

---

### CHANGELOG.rst

**文件路径**: `turtlebot3_teleop/CHANGELOG.rst`

**作用**: 记录包的版本历史和变更内容。

**重要版本**:

- **2.2.6 (2025-03-24)**: 
  - ✨ 添加 Jazzy 支持
  - 🔄 将 `cmd_vel` 消息类型从 `Twist` 改为 `TwistStamped`

- **2.1.5 (2022-05-26)**: 
  - ✨ 支持 ROS 2 Humble Hawksbill

- **2.1.0 (2020-06-22)**: 
  - ✨ 支持 ROS 2 Foxy Fitzroy 和 Eloquent Elusor
  - 🪟 启用 Windows 键盘遥控

- **1.0.0 (2018-05-29)**: 
  - 🛡️ 添加速度限制约束
  - 🔧 修改初始值、剖面函数和速度限制

**重要性**: 帮助开发者了解包的演进历史和兼容性变化。

---

### resource/turtlebot3_teleop

**文件路径**: `turtlebot3_teleop/resource/turtlebot3_teleop`

**作用**: Ament 构建系统的资源标记文件。

**内容**: 通常为空或包含简单的标识符

**重要性**: 
- 告诉 ament 构建系统这是一个有效的 ROS 2 包
- 使包能被 `ament_index` 索引和发现
- 支持 `ros2 pkg list` 等命令识别该包

---

## 使用方法

### 1. 环境准备

```bash
# 设置 TurtleBot3 型号（根据实际硬件选择）
export TURTLEBOT3_MODEL=burger
# 或
export TURTLEBOT3_MODEL=waffle
# 或
export TURTLEBOT3_MODEL=waffle_pi

# 设置 ROS 2 环境
source ~/turtlebot3_ws/install/setup.bash
```

### 2. 启动遥控节点

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

### 3. 控制操作

启动后会显示控制说明：

```
Control Your TurtleBot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity
a/d : increase/decrease angular velocity
space key, s : force stop
CTRL-C to quit
```

**操作步骤**:
1. 按 `w` 增加前进速度
2. 按 `x` 减小前进速度（或后退）
3. 按 `a` 增加左转角度速度
4. 按 `d` 增加右转角度速度
5. 按 `空格键` 或 `s` 紧急停止
6. 按 `Ctrl+C` 退出程序

### 4. 查看当前速度

每次按键后，终端会显示当前的目标线速度和角速度：
```
currently:	linear velocity 0.05	 angular velocity 0.0
```

---

## 技术细节

### 架构设计

```
用户键盘输入
    ↓
get_key() 读取按键
    ↓
更新 target_velocity
    ↓
make_simple_profile() 平滑处理
    ↓
生成 control_velocity
    ↓
创建 Twist/TwistStamped 消息
    ↓
发布到 /cmd_vel 话题
    ↓
TurtleBot3 底层控制器接收并执行
```

### 关键特性

1. **速度平滑**
   - 使用渐进式速度变化，避免突变
   - 步长为设定值的一半（`STEP_SIZE / 2.0`）
   - 提供更自然的运动体验

2. **速度限制**
   - 根据机器人型号自动应用不同的限制
   - Burger: 线速度 ±0.22 m/s，角速度 ±2.84 rad/s
   - Waffle: 线速度 ±0.26 m/s，角速度 ±1.82 rad/s

3. **跨版本兼容**
   - 自动检测 ROS 2 发行版
   - Humble 使用 `Twist` 消息
   - Jazzy 及以后使用 `TwistStamped` 消息

4. **安全性**
   - 程序退出时自动发送零速度命令
   - 紧急停止功能（空格键或 s 键）
   - 终端状态恢复

### 消息类型对比

| 特性 | Twist | TwistStamped |
|------|-------|--------------|
| 时间戳 | ❌ 无 | ✅ 有 |
| 坐标系 | ❌ 无 | ✅ 有 |
| 适用版本 | Humble 及之前 | Jazzy 及之后 |
| 精度 | 一般 | 更高（同步性更好） |

---

## 版本历史

详见 [CHANGELOG.rst](#changelogrst) 部分。

**最新稳定版**: 2.3.6 (2025-12-15)

**主要里程碑**:
- 2017: 初始版本（ROS 1）
- 2019: ROS 2 支持（Dashing）
- 2020: Windows 支持
- 2022: Humble 支持
- 2025: Jazzy 支持，TwistStamped 消息

---

## 常见问题

### Q1: 为什么按下按键后机器人没有反应？

**可能原因**:
1. 未设置 `TURTLEBOT3_MODEL` 环境变量
2. TurtleBot3 底层节点未启动
3. ROS 2 网络配置问题

**解决方法**:
```bash
# 检查环境变量
echo $TURTLEBOT3_MODEL

# 确认底层节点运行
ros2 node list

# 检查话题通信
ros2 topic echo /cmd_vel
```

### Q2: 速度变化不平滑怎么办？

调整 `LIN_VEL_STEP_SIZE` 和 `ANG_VEL_STEP_SIZE` 参数，或修改 `make_simple_profile()` 中的斜率参数。

### Q3: 如何在远程计算机上控制？

确保两台计算机的 ROS 2 DDS 配置正确：
```bash
# 设置相同的 DOMAIN ID
export ROS_DOMAIN_ID=30

# 或使用 CycloneDDS/FastDDS 配置
```

---

## 贡献指南

如需贡献代码或报告问题，请访问：
- 📝 Issues: https://github.com/ROBOTIS-GIT/turtlebot3/issues
- 🔗 Repository: https://github.com/ROBOTIS-GIT/turtlebot3

---

## 许可证

Apache License, Version 2.0

版权所有 (c) 2011-2025, ROBOTIS Co., Ltd.

---

## 联系方式

- **维护者**: Pyo <pyo@robotis.com>
- **网站**: http://turtlebot3.robotis.com
- **技术支持**: https://github.com/ROBOTIS-GIT/turtlebot3/issues
