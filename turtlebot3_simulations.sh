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
            # 等待容器完全启动
            sleep 2
            setup_devcontainer_support
        fi
    else
        log_info "创建并启动容器 $CONTAINER_NAME..."
        xhost +local:docker 2>/dev/null || true
        docker run -d \
            --name $CONTAINER_NAME \
            --privileged \
            --gpus all \
            --runtime=nvidia \
            -e DISPLAY=$DISPLAY \
            -e QT_X11_NO_MITSHM=1 \
            -e TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL:-burger} \
            -e ROS_DOMAIN_ID=0 \
            -e NVIDIA_DRIVER_CAPABILITIES=all \
            -e NVIDIA_VISIBLE_DEVICES=all \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -v $PROJECT_DIR:/workspace \
            -v $PROJECT_DIR/turtlebot3_ws:/root/turtlebot3_ws \
            -w $WORKSPACE \
            --network host \
            $IMAGE_NAME \
            tail -f /dev/null
        
        # 等待容器完全启动
        sleep 3
        setup_devcontainer_support
    fi
}

# 为脚本创建的容器添加 Dev Container 支持
setup_devcontainer_support() {
    log_info "配置 Dev Container 支持..."
    
    # 1. 创建 .devcontainer 标记文件，让 VS Code 能识别
    docker exec $CONTAINER_NAME bash -c "
        mkdir -p /root/.vscode-server /root/.vscode-server/bin
        # 创建 devcontainer.json 标记
        mkdir -p /workspace/.devcontainer
        if [ ! -f /workspace/.devcontainer/devcontainer.json ]; then
            cp /workspace/.devcontainer/devcontainer.json.example /workspace/.devcontainer/devcontainer.json 2>/dev/null || true
        fi
    "
    
    # 2. 安装 VS Code Server（如果尚未安装）
    local vscode_installed
    vscode_installed=$(docker exec $CONTAINER_NAME bash -c "
        [ -f /root/.vscode-server/bin/code-server ] && echo 'yes' || echo 'no'
    " 2>/dev/null)
    
    if [ "$vscode_installed" = "no" ]; then
        log_info "安装 VS Code Server..."
        # 获取 VS Code 最新版本
        local vscode_version
        vscode_version=$(curl -s https://api.github.com/repos/microsoft/vscode/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
        
        if [ -n "$vscode_version" ]; then
            docker exec $CONTAINER_NAME bash -c "
                # 下载并安装 VS Code Server
                cd /root/.vscode-server
                curl -sL "https://update.code.visualstudio.com/${vscode_version#v}/server-linux-x64/stable" -o vscode-server.tar.gz
                tar -xf vscode-server.tar.gz --strip-components=1
                rm vscode-server.tar.gz
                # 创建启动脚本
                cat > /root/.vscode-server/bin/code-server << 'EOF'
#!/bin/bash
exec /root/.vscode-server/node /root/.vscode-server/out/server-main.js \"\$@\"
EOF
                chmod +x /root/.vscode-server/bin/code-server
                echo 'VS Code Server 安装完成'
            "
        else
            log_warn "无法获取 VS Code 最新版本，跳过安装"
            log_warn "你仍然可以通过 Dev Container 扩展重新打开项目来安装"
        fi
    else
        log_info "VS Code Server 已安装"
    fi
    
    log_info "Dev Container 支持配置完成"
    log_info "现在可以在 VS Code 中使用 'Dev Containers: Attach to Running Container' 连接到此容器"
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
    docker exec -it $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash &&
        cd /root/turtlebot3_ws &&
        exec bash
    "
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
        rm -f /root/turtlebot3_ws/src/slam_toolbox &&
        rm -f /root/turtlebot3_ws/src/turtlebot3_dqn &&
        ln -sf /workspace/turtlebot3_fake_node /root/turtlebot3_ws/src/turtlebot3_fake_node &&
        ln -sf /workspace/turtlebot3_gazebo /root/turtlebot3_ws/src/turtlebot3_gazebo &&
        ln -sf /workspace/slam_toolbox /root/turtlebot3_ws/src/slam_toolbox &&
        ln -sf /workspace/turtlebot3_machine_learning/turtlebot3_dqn /root/turtlebot3_ws/src/turtlebot3_dqn &&
        colcon build --symlink-install &&
        # 检查 DQN 依赖
        if ! python3 -c 'import tensorflow' 2>/dev/null; then
            echo '[WARN] TensorFlow 未安装，DQN 训练功能不可用'
            echo '[WARN] 执行以下命令安装: docker exec turtlebot3-sim bash /workspace/turtlebot3_machine_learning/install_dqn_deps.sh'
        fi
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

# 键盘控制（原版 turtlebot3_teleop，WASD 布局）
launch_teleop() {
    log_info "启动键盘控制 (turtlebot3_teleop, WASD 布局)..."
    exec_in_container "ros2 run turtlebot3_teleop teleop_keyboard --ros-args -p stamped:=True"
}

# 键盘控制（teleop_twist_keyboard，小键盘布局，发布 TwistStamped 类型）
launch_teleop_twist() {
    log_info "启动键盘控制 (teleop_twist_keyboard, uio/jkl 布局, TwistStamped 类型)..."
    exec_in_container "ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=True"
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

# DQN 强化学习训练
launch_dqn_train() {
    local stage=$1
    log_info "启动 DQN 训练: Stage ${stage} (GPU 加速)..."
    docker exec -it $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash
        cd ${WORKSPACE}
        [ -f install/setup.bash ] && source install/setup.bash
        ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage${stage}.launch.py &
        sleep 3
        ros2 run turtlebot3_dqn dqn_gazebo ${stage} &
        sleep 2
        ros2 run turtlebot3_dqn dqn_environment &
        sleep 2
        ros2 run turtlebot3_dqn dqn_agent --ros-args \
            -p max_training_episodes:=1000 \
            -p use_gpu:=true
    "
}

# DQN 训练（后台运行，不阻塞终端）
launch_dqn_train_bg() {
    local stage=$1
    log_info "后台启动 DQN 训练: Stage ${stage} (GPU 加速)..."
    docker exec $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash
        cd ${WORKSPACE}
        [ -f install/setup.bash ] && source install/setup.bash
        ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage${stage}.launch.py &
        sleep 3
        ros2 run turtlebot3_dqn dqn_gazebo ${stage} &
        sleep 2
        ros2 run turtlebot3_dqn dqn_environment &
        sleep 2
        ros2 run turtlebot3_dqn dqn_agent --ros-args \
            -p max_training_episodes:=1000 \
            -p use_gpu:=true &
        echo 'DQN Stage ${stage} training started in background (GPU enabled)'
        echo 'Use: docker exec turtlebot3-sim ros2 node list 查看节点'
    "
}

# DQN 模型测试
launch_dqn_test() {
    local model_file=$1
    if [ -z "$model_file" ]; then
        log_error "请指定模型文件路径 (相对于 saved_model 目录)"
        echo "示例: $0 dqn_test model1.h5"
        return 1
    fi
    log_info "启动 DQN 测试，使用模型: ${model_file}..."
    docker exec -it $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash
        cd ${WORKSPACE}
        [ -f install/setup.bash ] && source install/setup.bash
        ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage1.launch.py &
        sleep 3
        ros2 run turtlebot3_dqn dqn_gazebo 1 &
        sleep 2
        ros2 run turtlebot3_dqn dqn_environment &
        sleep 2
        ros2 run turtlebot3_dqn dqn_test --ros-args -p model_file:=${model_file}
    "
}

# DQN 动作可视化
launch_dqn_action_graph() {
    log_info "启动 DQN 动作可视化 (需要 X11 转发)..."
    docker exec -it $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash
        cd ${WORKSPACE}
        [ -f install/setup.bash ] && source install/setup.bash
        ros2 run turtlebot3_dqn action_graph
    "
}

# 安装 DQN 依赖
install_dqn_deps() {
    log_info "安装 DQN 训练依赖 (TensorFlow + PyQt5)..."
    docker exec -it $CONTAINER_NAME bash /workspace/turtlebot3_machine_learning/install_dqn_deps.sh
}

# 验证 GPU 可用性
check_gpu() {
    log_info "检查 GPU 配置..."
    echo ""
    echo "=== 宿主机 GPU ==="
    nvidia-smi 2>/dev/null || echo "❌ nvidia-smi 不可用"
    echo ""
    echo "=== 容器内 GPU ==="
    docker exec $CONTAINER_NAME bash -c "
        source /opt/ros/jazzy/setup.bash
        cd ${WORKSPACE}
        [ -f install/setup.bash ] && source install/setup.bash
        echo '--- NVIDIA Container ---'
        nvidia-smi 2>/dev/null || echo '❌ nvidia-smi 不可用'
        echo ''
        echo '--- TensorFlow GPU ---'
        python3 -c \"
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f'✅ 发现 {len(gpus)} 个 GPU:')
    for gpu in gpus:
        print(f'   - {gpu}')
else:
    print('❌ TensorFlow 未发现 GPU')
\"
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
  start              启动/创建 Docker 容器（支持 Dev Container）
  stop               停止容器
  rm                 删除容器
  shell              进入容器 Bash
  vscode             在 VS Code 中打开容器（推荐）

构建与运行:
  build              编译项目 (colcon build)
  empty_world        启动空世界仿真
  turtlebot3_world   启动 World 场景（有障碍物）
  turtlebot3_house   启动 House 室内场景
  fake_node          启动 Fake Node (RViz only, 无需 Gazebo)
  dqn_stage1~4       启动 DQN 强化学习场景 (阶段 1-4，仅 Gazebo)

DQN 强化学习训练:
  dqn_train_1~4      启动 DQN 训练 (Stage 1-4，完整训练流程)
  dqn_train_bg_1~4   后台启动 DQN 训练 (不阻塞终端)
  dqn_test <model>   使用训练好的模型进行测试 (例: dqn_test model1.h5)
  dqn_action_graph   启动 DQN 动作可视化界面 (需要 X11)
  dqn_install_deps   安装 DQN 训练依赖 (TensorFlow + PyQt5)

SLAM 建图:
  slam_cartographer  启动 Cartographer SLAM 建图 + RViz
  slam_toolbox       启动 slam_toolbox SLAM 建图 + RViz
  auto_slam          自动 SLAM 建图 (Cartographer + 自动避障，无需键盘)
  save_map [name]    保存当前地图 (默认名: map)

辅助工具:
  rviz               启动 RViz2 可视化
  gazebo             启动 Gazebo 客户端
  teleop             启动键盘控制节点 (turtlebot3_teleop, WASD 布局)
  teleop_twist       启动键盘控制节点 (teleop_twist_keyboard, TwistStamped 类型)
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
    vscode|code)
        if command -v code &> /dev/null; then
            log_info "在 VS Code 中打开容器 $CONTAINER_NAME..."
            # 检查 VS Code 是否支持 Dev Containers
            code --folder-uri "vscode-remote://attached-container+$(echo -n $CONTAINER_NAME | xxd -p)" /workspace 2>/dev/null &
            log_info "VS Code 正在启动..."
        else
            log_info "请在 VS Code 中执行以下步骤："
            log_info "1. 按 Ctrl+Shift+P (或 Cmd+Shift+P on Mac)"
            log_info "2. 输入并选择: 'Dev Containers: Attach to Running Container'"
            log_info "3. 选择容器: $CONTAINER_NAME"
            log_info ""
            log_info "提示: 安装 'code' 命令到 PATH 可以自动打开 VS Code"
            log_info "  https://code.visualstudio.com/docs/setup/setup-overview"
        fi
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
        # 保持兼容：原来只启动 Gazebo 场景
        launch_gazebo "$1"
        ;;
    dqn_train_1|dqn_train_2|dqn_train_3|dqn_train_4)
        stage_num=${1##*_}
        launch_dqn_train "$stage_num"
        ;;
    dqn_train_bg_1|dqn_train_bg_2|dqn_train_bg_3|dqn_train_bg_4)
        stage_num=${1##*_}
        launch_dqn_train_bg "$stage_num"
        ;;
    dqn_test)
        launch_dqn_test "$2"
        ;;
    dqn_action_graph)
        launch_dqn_action_graph
        ;;
    dqn_install_deps)
        install_dqn_deps
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
    teleop_twist)
        launch_teleop_twist
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
