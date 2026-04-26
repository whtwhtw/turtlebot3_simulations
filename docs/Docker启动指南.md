# TurtleBot3 Simulations Docker 启动指南

> 本文档介绍如何使用 Docker 容器化方式运行 TurtleBot3 仿真项目，参考 ROS2-start 项目架构改造。

## 一、环境要求

### 宿主机要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **操作系统** | Ubuntu 24.04 LTS | 推荐，其他发行版需自行验证 |
| **Docker** | 20.10+ | 容器运行时 |
| **NVIDIA Container Toolkit** | 必需 | GPU 硬件加速仿真（RTX 3090 等） |
| **X11 Server** | 任意 | 用于显示 Gazebo/RViz GUI |

> **重要**: 本项目基于 ROS2 **Jazzy** (非 Humble)，使用 Gazebo Harmonic/Ionic 新版。

### 检查环境

```bash
# 检查 Docker
docker --version

# 检查 NVIDIA Container Toolkit
nvidia-smi

# 检查 X11 转发
echo $DISPLAY  # 应输出 :0 或类似值
```

## 二、快速开始

### 1. 授权 X11 访问

```bash
# 允许 Docker 容器访问宿主机的 X11 显示
xhost +local:docker
```

### 2. 启动容器

```bash
cd /media/wht/J/Auto-driving/slam/仿真SLAM/turtlebot3_simulations
./turtlebot3_simulations.sh start
```

### 3. 编译项目

```bash
./turtlebot3_simulations.sh build
```

### 4. 启动仿真

```bash
# 选择任一场景启动
./turtlebot3_simulations.sh empty_world        # 空世界
./turtlebot3_simulations.sh turtlebot3_world   # 带障碍物场景
./turtlebot3_simulations.sh turtlebot3_house   # 室内房屋场景
./turtlebot3_simulations.sh fake_node          # 仅 RViz（无 Gazebo）
```

### 5. 控制机器人

新开终端执行：
```bash
./turtlebot3_simulations.sh teleop
```
使用键盘 `WASD` 或 `箭头键` 控制机器人移动。

## 三、VSCode Dev Container 集成

### 一键进入开发环境

1. 在 VSCode 中打开项目目录
2. 按 `Ctrl+Shift+P` → 输入 `Dev Containers: Reopen in Container`
3. 等待容器启动和扩展安装完成

### 开发体验

- ✅ 代码编辑与容器内执行无缝同步
- ✅ 内置 ROS2 扩展支持（代码补全、跳转）
- ✅ 集成终端直接运行 ROS2 命令
- ✅ 调试配置预置（F5 启动调试）

### 常用 VSCode 任务

按 `Ctrl+Shift+P` → `Tasks: Run Task`：

| 任务名 | 功能 |
|--------|------|
| `build` | 编译工作空间 |
| `run:empty_world` | 启动空世界仿真 |
| `run:fake_node` | 启动 RViz 仿真 |
| `rviz2` | 单独启动 RViz |

## 四、命令参考

### 容器管理

```bash
./turtlebot3_simulations.sh start    # 启动/创建容器
./turtlebot3_simulations.sh stop     # 停止容器
./turtlebot3_simulations.sh rm       # 删除容器
./turtlebot3_simulations.sh shell    # 进入容器 Bash
```

### 仿真场景

```bash
./turtlebot3_simulations.sh empty_world        # Gazebo 空世界
./turtlebot3_simulations.sh turtlebot3_world   # World 场景（有障碍）
./turtlebot3_simulations.sh turtlebot3_house   # House 室内场景
./turtlebot3_simulations.sh dqn_stage1         # DQN 强化学习 Stage 1
./turtlebot3_simulations.sh dqn_stage2         # DQN Stage 2
./turtlebot3_simulations.sh dqn_stage3         # DQN Stage 3
./turtlebot3_simulations.sh dqn_stage4         # DQN Stage 4
./turtlebot3_simulations.sh fake_node          # Fake Node（RViz only）
```

### 辅助工具

```bash
./turtlebot3_simulations.sh rviz               # 启动 RViz2
./turtlebot3_simulations.sh teleop             # 键盘控制
./turtlebot3_simulations.sh turtlebot3_drive   # 自动避障演示
```

### 环境配置

```bash
# 切换机器人模型
./turtlebot3_simulations.sh model waffle
./turtlebot3_simulations.sh start  # 重启容器使配置生效

# 可用模型: burger | burger_cam | waffle | waffle_pi
```

## 五、配置文件说明

### `.devcontainer/docker-compose.yml`

```yaml
services:
  turtlebot3-sim:
    image: osrf/ros:jazzy-desktop-full  # ROS2 Jazzy + Gazebo 完整镜像
    environment:
      - TURTLEBOT3_MODEL=burger          # 默认机器人模型
      - ROS_DOMAIN_ID=0                  # ROS2 域 ID，避免多实例冲突
      - NVIDIA_DRIVER_CAPABILITIES=all   # GPU 加速支持
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]        # 启用 GPU
    volumes:
      - ..:/workspace                     # 项目源码挂载
      - ../turtlebot3_ws:/root/turtlebot3_ws  # 工作空间持久化
    network_mode: host                    # 使用宿主机网络，便于 ROS2 通信
```

### 依赖管理

编译前需要导入 TurtleBot3 依赖包：

```bash
# 容器内执行，使用代理（如有需要）
cd /root/turtlebot3_ws/src
mkdir -p turtlebot3 && cd turtlebot3
git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone https://github.com/ROBOTIS-GIT/turtlebot3.git
cd ../utils
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone https://github.com/ROBOTIS-GIT/hls_lfcd_lds_driver.git
```

> 网络受限环境下，宿主机需配置 `verge-mihomo` 代理（端口 **7897**）。

### `.devcontainer/devcontainer.json`

- 预装 VSCode 扩展：`ms-iot.vscode-ros`, `ms-python.python`
- `postCreateCommand`: 自动执行环境初始化脚本
- `shutdownAction: stopContainer`: 关闭 VSCode 时停止容器（非删除）

### `.devcontainer/post-create.sh`

首次创建容器时自动执行：
1. 安装常用开发工具（gdb, vim, git）
2. 安装 ROS-Gazebo 桥接包
3. 配置 `.bashrc` 环境变量
4. 创建符号链接并编译项目

## 六、常见问题

### Q: Gazebo 黑屏或无法显示

**A**: 检查 X11 转发配置：
```bash
# 宿主机执行
xhost +local:docker
echo $DISPLAY  # 确认不为空

# 如使用 SSH，添加 -X 或 -Y 参数
ssh -X user@host
```

### Q: 容器内无法访问网络

**A**: 脚本已配置 `network_mode: host`，如遇问题检查：
```bash
# 宿主机防火墙
sudo ufw status

# Docker 网络
docker network ls
```

### Q: 编译失败，缺少依赖

**A**: 确保依赖已正确克隆到 `/root/turtlebot3_ws/src/`：
```bash
./turtlebot3_simulations.sh shell
# 容器内执行
ls /root/turtlebot3_ws/src/turtlebot3/turtlebot3_msgs
ls /root/turtlebot3_ws/src/turtlebot3/turtlebot3
# 如目录为空，重新克隆（参考上方「依赖管理」章节）
```

### Q: Gazebo 渲染失败（黑屏/无法创建 drawable）

**A**: 确认 NVIDIA Container Toolkit 已安装并配置：
```bash
# 宿主机检查
nvidia-smi
docker info | grep -i runtime  # 应显示 nvidia

# 容器内检查 GPU
docker exec turtlebot3-sim nvidia-smi
# 如报错，重建容器: docker rm -f turtlebot3-sim && ./turtlebot3_simulations.sh start
```

### Q: 如何切换 ROS2 域（多机器人仿真）

**A**: 修改环境变量：
```bash
# 方法 1: 启动前设置
export ROS_DOMAIN_ID=1
./turtlebot3_simulations.sh start

# 方法 2: 容器内临时设置
./turtlebot3_simulations.sh shell
export ROS_DOMAIN_ID=1
source /root/turtlebot3_ws/install/setup.bash
```

### Q: 容器磁盘空间不足

**A**: 清理无用镜像和卷：
```bash
# 查看磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a  # 谨慎使用，会删除未运行容器的镜像
```

## 七、与原生启动对比

| 特性 | Docker 方式 | 原生安装 |
|------|-----------|----------|
| **环境隔离** | ✅ 完全隔离，不污染宿主机 | ❌ 直接安装到系统 |
| **版本管理** | ✅ 镜像版本锁定，可回滚 | ❌ 依赖系统包管理器 |
| **团队共享** | ✅ 配置即代码，一键复现 | ❌ 需手动同步环境 |
| **启动速度** | ⚠️ 首次拉取镜像较慢 | ✅ 直接运行 |
| **GUI 支持** | ⚠️ 需配置 X11 转发 | ✅ 原生支持 |
| **GPU 加速** | ✅ 支持 NVIDIA Container Toolkit | ✅ 原生支持 |

## 八、进阶使用

### 自定义镜像

如需预装额外依赖，创建 `.devcontainer/Dockerfile`：

```dockerfile
FROM osrf/ros:jazzy-desktop-full

# 安装项目特定依赖
RUN apt-get update && apt-get install -y \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /root/turtlebot3_ws
```

修改 `devcontainer.json` 的 `build` 字段引用该 Dockerfile。

### 持久化数据卷

如需持久化 `~/.ros` 等运行时数据：

```yaml
# docker-compose.yml 中添加
volumes:
  - ros-data:/root/.ros

volumes:
  ros-data:
```

### 多容器协作

如需分离仿真与算法开发：

```yaml
# 添加第二个服务
services:
  turtlebot3-sim:  # 仿真容器
    # ... 现有配置

  turtlebot3-dev:  # 开发容器
    image: osrf/ros:jazzy-desktop
    volumes:
      - ..:/workspace
    command: sleep infinity
```

---

> 📌 **提示**: 所有命令均在项目根目录执行。如遇问题，先执行 `./turtlebot3_simulations.sh shell` 进入容器排查。
