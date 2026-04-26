# TurtleBot3
<img src="https://raw.githubusercontent.com/ROBOTIS-GIT/emanual/master/assets/images/platform/turtlebot3/logo_turtlebot3.png" width="300">

- Active Branches: noetic, jazzy, main
- Legacy Branches: humble, *-devel

## Open Source Projects Related to TurtleBot3
- [turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3)
- [turtlebot3_msgs](https://github.com/ROBOTIS-GIT/turtlebot3_msgs)
- [turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations)
- [turtlebot3_manipulation](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation)
- [turtlebot3_manipulation_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation_simulations)
- [turtlebot3_applications](https://github.com/ROBOTIS-GIT/turtlebot3_applications)
- [turtlebot3_applications_msgs](https://github.com/ROBOTIS-GIT/turtlebot3_applications_msgs)
- [turtlebot3_machine_learning](https://github.com/ROBOTIS-GIT/turtlebot3_machine_learning)
- [turtlebot3_autorace](https://github.com/ROBOTIS-GIT/turtlebot3_autorace)
- [turtlebot3_home_service_challenge](https://github.com/ROBOTIS-GIT/turtlebot3_home_service_challenge)
- [hls_lfcd_lds_driver](https://github.com/ROBOTIS-GIT/hls_lfcd_lds_driver)
- [ld08_driver](https://github.com/ROBOTIS-GIT/ld08_driver)
- [open_manipulator](https://github.com/ROBOTIS-GIT/open_manipulator)
- [dynamixel_sdk](https://github.com/ROBOTIS-GIT/DynamixelSDK)
- [OpenCR-Hardware](https://github.com/ROBOTIS-GIT/OpenCR-Hardware)
- [OpenCR](https://github.com/ROBOTIS-GIT/OpenCR)

## Documentation, Videos, and Community

### Official Documentation
- ⚙️ **[ROBOTIS DYNAMIXEL](https://dynamixel.com/)** – Official website for DYNAMIXEL
- 📚 **[ROBOTIS e-Manual for Dynamixel SDK](http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)** – Official guide for Dynamixel SDK
- 📚 **[ROBOTIS e-Manual for TurtleBot3](http://turtlebot3.robotis.com/)** – Official guide for TurtleBot3
- 📚 **[ROBOTIS e-Manual for OpenMANIPULATOR-X](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/overview/)** – Official guide for OpenMANIPULATOR-X

### Learning Resources
- 🎥 **[ROBOTIS YouTube Channel](https://www.youtube.com/@ROBOTISCHANNEL)**
- 🎥 **[ROBOTIS Open Source YouTube Channel](https://www.youtube.com/@ROBOTISOpenSourceTeam)**
- 🎥 **[ROBOTIS TurtleBot3 YouTube Playlist](https://www.youtube.com/playlist?list=PLRG6WP3c31_XI3wlvHlx2Mp8BYqgqDURU)** – Video tutorials for TurtleBot3
- 🎥 **[ROBOTIS OpenMANIPULATOR YouTube Playlist](https://www.youtube.com/playlist?list=PLRG6WP3c31_WpEsB6_Rdt3KhiopXQlUkb)** – Video tutorials for OpenMANIPULATOR

### Community & Support
- 💬 **[ROBOTIS Community Forum](https://forum.robotis.com/)** – Get help and discuss with other users

## 🐳 Docker 快速启动（推荐）

本项目已集成 Docker 容器化开发支持，参考 ROS2-start 项目架构。

### 一键启动

```bash
# 1. 授权 X11 显示
xhost +local:docker

# 2. 启动容器并运行
cd turtlebot3_simulations
./turtlebot3_simulations.sh start
./turtlebot3_simulations.sh build
./turtlebot3_simulations.sh turtlebot3_world  # 启动仿真
```

### 完整文档

- 📖 [启动方式说明](docs/启动方式说明.md) - 两种启动方式详解
- 🐳 [Docker启动指南](docs/Docker启动指南.md) - 容器化开发完整指南
- 🔧 [开发指南](docs/开发指南.md) - 代码开发与调试

### VSCode 支持

使用 [Dev Containers](.devcontainer/) 配置，一键进入集成开发环境：
`Ctrl+Shift+P` → `Dev Containers: Reopen in Container`
