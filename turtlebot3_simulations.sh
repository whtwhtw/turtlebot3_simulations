#!/bin/bash
# TurtleBot3 Simulations Docker 管理脚本
# 参考 ROS2-start 项目改造

CONTAINER_NAME="turtlebot3-sim"
IMAGE_NAME="osrf/ros:jazzy-desktop-full"
WORKSPACE="/root/turtlebot3_ws"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

start_container() {
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
            log_info "容器 $CONTAINER_NAME 已在运行"
        else
            log_info "启动容器 $CONTAINER_NAME..."
            xhost +local:docker 2>/dev/null || true
            docker start $CONTAINER_NAME
        fi
    else
        log_info "创建并启动容器 $CONTAINER_NAME..."
        xhost +local:docker 2>/dev/null || true
        docker run -d \
            --name $CONTAINER_NAME \
            --privileged \
            --gpus all \
            -e DISPLAY=$DISPLAY \
            -e QT_X11_NO_MITSHM=1 \
            -e TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL:-burger} \
            -e ROS_DOMAIN_ID=0 \
            -e NVIDIA_DRIVER_CAPABILITIES=all \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -v $PROJECT_DIR:/workspace \
            -v $PROJECT_DIR/turtlebot3_ws:/root/turtlebot3_ws \
            -w $WORKSPACE \
            --network host \
            $IMAGE_NAME \
            tail -f /dev/null
    fi
}

stop_container() {
    log_info "停止容器 $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME 2>/dev/null
}

remove_container() {
    log_warn "删除容器 $CONTAINER_NAME..."
    docker rm -f $CONTAINER_NAME 2>/dev/null
}

shell() {
    log_info "进入容器 $CONTAINER_NAME 的bash..."
    docker exec -it $CONTAINER_NAME bash
}

build() {
    log_info "编译 TurtleBot3 项目..."
    docker exec $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash &&
        cd /root/turtlebot3_ws &&
        mkdir -p src &&
        # 只 symlink 仿真包，避免整个项目路径重复
        rm -f /root/turtlebot3_ws/src/turtlebot3_simulations &&
        rm -f /root/turtlebot3_ws/src/turtlebot3_fake_node &&
        rm -f /root/turtlebot3_ws/src/turtlebot3_gazebo &&
        ln -sf /workspace/turtlebot3_fake_node /root/turtlebot3_ws/src/turtlebot3_fake_node &&
        ln -sf /workspace/turtlebot3_gazebo /root/turtlebot3_ws/src/turtlebot3_gazebo &&
        colcon build --symlink-install
    "
}

# 通用执行函数：确保环境正确溯源
exec_in_container() {
    local cmd=$1
    docker exec -it $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash &&
        cd $WORKSPACE &&
        if [ -f install/setup.bash ]; then
            source install/setup.bash
        fi &&
        $cmd
    "
}

# Gazebo 仿真启动函数
launch_gazebo() {
    local world=$1
    log_info "启动 Gazebo 仿真: $world..."
    exec_in_container "ros2 launch turtlebot3_gazebo ${world}.launch.py"
}

# Fake Node 启动函数
launch_fake() {
    log_info "启动 Fake Node (RViz only)..."
    exec_in_container "ros2 launch turtlebot3_fake_node fake_node.launch.py"
}

# RViz2 启动
launch_rviz() {
    log_info "启动 RViz2..."
    exec_in_container "ros2 run rviz2 rviz2 -d \$ROS_DISTRO/share/turtlebot3_gazebo/rviz/tb3_gazebo.rviz"
}

# 键盘控制
launch_teleop() {
    log_info "启动键盘控制..."
    exec_in_container "ros2 run turtlebot3_teleop teleop_keyboard"
}

# 重新生成小车
respawn_robot() {
    log_info "重新生成小车并恢复控制..."
    docker exec -it $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash &&
        cd /root/turtlebot3_ws && source install/setup.bash &&
        pkill -f 'teleop_keyboard' 2>/dev/null || true &&
        ros2 launch turtlebot3_gazebo spawn_turtlebot3.launch.py x_pose:=-2.0 y_pose:=-0.5 &
        sleep 3 &&
        echo 'Respawn complete! Restart teleop if needed.'
    "
}

# 自动避障演示
launch_drive() {
    log_info "启动自动避障演示..."
    exec_in_container "ros2 run turtlebot3_node turtlebot3_drive"
}

# SLAM 建图 - Cartographer
launch_slam_cartographer() {
    log_info "启动 Cartographer SLAM 建图..."
    exec_in_container "ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=true"
}

# SLAM 建图 - slam_toolbox
launch_slam_toolbox() {
    log_info "启动 slam_toolbox SLAM 建图..."
    exec_in_container "ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true"
}

# 自动 SLAM 建图（使用 turtlebot3_drive 自动避障 + Cartographer）
launch_auto_slam() {
    log_info "启动自动 SLAM 建图 (Cartographer + Auto Drive)..."
    exec_in_container "ros2 launch turtlebot3_gazebo auto_slam.launch.py"
}

# 保存地图
save_map() {
    local map_name=${1:-map}
    log_info "保存地图: ${map_name}..."
    exec_in_container "
        cd /root/turtlebot3_ws &&
        mkdir -p maps &&
        ros2 run nav2_map_server map_saver_cli -f maps/${map_name} --fmt png --ros-args -p save_map_timeout:=10000.0
    "
}

# 切换机器人模型
set_model() {
    local model=$1
    if [[ ! "burger burger_cam waffle waffle_pi" =~ $model ]]; then
        log_error "无效的模型: $model"
        echo "可用模型: burger, burger_cam, waffle, waffle_pi"
        return 1
    fi
    export TURTLEBOT3_MODEL=$model
    log_info "设置机器人模型: $model"
    log_warn "注意: 需要重启容器或重新设置环境变量生效"
}

# 诊断工具
diagnose() {
    log_info "运行环境诊断..."
    exec_in_container "
        echo '=== ROS2 环境 ===' &&
        ros2 --help | head -1 &&
        echo 'ROS_DISTRO=' \$ROS_DISTRO &&
        echo '=== 工作空间 ===' &&
        pwd && ls -la &&
        echo '=== install 目录 ===' &&
        ls -la install/ 2>/dev/null | head -5 &&
        echo '=== turtlebot3 包 ===' &&
        ros2 pkg list | grep turtlebot3 &&
        echo '=== 包路径 ===' &&
        ros2 pkg prefix turtlebot3_gazebo 2>/dev/null || echo '未找到 turtlebot3_gazebo'
    "
}

show_help() {
    cat << HELP
TurtleBot3 Simulations 管理脚本

用法: $0 <命令> [参数]

容器管理:
  start              启动/创建 Docker 容器
  stop               停止容器
  rm                 删除容器
  shell              进入容器 Bash

构建与运行:
  build              编译项目 (colcon build)
  empty_world        启动空世界仿真
  turtlebot3_world   启动 World 场景（有障碍物）
  turtlebot3_house   启动 House 室内场景
  fake_node          启动 Fake Node (RViz only, 无需 Gazebo)
  dqn_stage1~4       启动 DQN 强化学习场景 (阶段 1-4)

SLAM 建图:
  slam_cartographer  启动 Cartographer SLAM 建图 + RViz
  slam_toolbox       启动 slam_toolbox SLAM 建图 + RViz
  auto_slam          自动 SLAM 建图 (Cartographer + 自动避障，无需键盘)
  save_map [name]    保存当前地图 (默认名: map)

辅助工具:
  rviz               启动 RViz2 可视化
  gazebo             启动 Gazebo 客户端
  teleop             启动键盘控制节点
  respawn            重新生成小车 (Gazebo reset 后使用)
  turtlebot3_drive   启动自动避障演示

环境配置:
  model <name>       设置机器人模型 (burger|waffle|waffle_pi)

诊断:
  diagnose           运行环境诊断，检查包路径和编译状态

示例:
  $0 start                    # 启动容器
  $0 build                    # 编译项目
  $0 diagnose                 # 诊断环境问题
  $0 turtlebot3_world         # 启动 World 仿真

HELP
}

# 主入口
case "$1" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    rm)
        remove_container
        ;;
    shell|sh)
        shell
        ;;
    build)
        build
        ;;
    empty_world)
        launch_gazebo "empty_world"
        ;;
    turtlebot3_world)
        launch_gazebo "turtlebot3_world"
        ;;
    turtlebot3_house)
        launch_gazebo "turtlebot3_house"
        ;;
    fake_node)
        launch_fake
        ;;
    dqn_stage1|dqn_stage2|dqn_stage3|dqn_stage4)
        launch_gazebo "$1"
        ;;
    rviz)
        launch_rviz
        ;;
    gazebo)
        log_info "启动 Gazebo 客户端..."
        docker exec -it $CONTAINER_NAME bash -c "gzclient"
        ;;
    teleop)
        launch_teleop
        ;;
    respawn)
        respawn_robot
        ;;
    turtlebot3_drive)
        launch_drive
        ;;
    slam_cartographer)
        launch_slam_cartographer
        ;;
    slam_toolbox)
        launch_slam_toolbox
        ;;
    auto_slam)
        launch_auto_slam
        ;;
    save_map)
        save_map "${2:-map}"
        ;;
    model)
        set_model "$2"
        ;;
    diagnose)
        diagnose
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
