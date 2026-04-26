// Copyright 2019 ROBOTIS CO., LTD.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Authors: Taehun Lim (Darby), Ryan Shim

#include "turtlebot3_gazebo/turtlebot3_drive.hpp"

#include <memory>

using namespace std::chrono_literals;

Turtlebot3Drive::Turtlebot3Drive()
: Node("turtlebot3_drive_node")
{
  /************************************************************
  ** Initialise variables
  ************************************************************/
  scan_data_[0] = 0.0;
  scan_data_[1] = 0.0;
  scan_data_[2] = 0.0;
  front_avg_dist_ = 3.5;  // range_max 初始值
  left_avg_dist_ = 3.5;
  right_avg_dist_ = 3.5;
  front_inf_count_ = 0;
  front_total_ = 0;
  left_count_ = 0;
  right_count_ = 0;

  robot_pose_ = 0.0;
  prev_robot_pose_ = 0.0;

  /************************************************************
  ** Initialise ROS publishers and subscribers
  ************************************************************/
  auto qos = rclcpp::QoS(rclcpp::KeepLast(10));

  // Initialise publishers
  cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", qos);

  // Initialise subscribers
  scan_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
    "scan", \
    rclcpp::SensorDataQoS(), \
    std::bind(
      &Turtlebot3Drive::scan_callback, \
      this, \
      std::placeholders::_1));
  odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
    "odom", qos, std::bind(&Turtlebot3Drive::odom_callback, this, std::placeholders::_1));

  /************************************************************
  ** Initialise ROS timers
  ************************************************************/
  update_timer_ = this->create_wall_timer(10ms, std::bind(&Turtlebot3Drive::update_callback, this));

  RCLCPP_INFO(this->get_logger(), "Turtlebot3 simulation node has been initialised");
}

Turtlebot3Drive::~Turtlebot3Drive()
{
  RCLCPP_INFO(this->get_logger(), "Turtlebot3 simulation node has been terminated");
}

/********************************************************************************
** Callback functions for ROS subscribers
********************************************************************************/
void Turtlebot3Drive::odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
{
  tf2::Quaternion q(
    msg->pose.pose.orientation.x,
    msg->pose.pose.orientation.y,
    msg->pose.pose.orientation.z,
    msg->pose.pose.orientation.w);
  tf2::Matrix3x3 m(q);
  double roll, pitch, yaw;
  m.getRPY(roll, pitch, yaw);

  robot_pose_ = yaw;
}

void Turtlebot3Drive::scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
{
  uint16_t scan_angle[3] = {0, 30, 330};

  for (int num = 0; num < 3; num++) {
    if (std::isinf(msg->ranges.at(scan_angle[num]))) {
      scan_data_[num] = msg->range_max;
    } else {
      scan_data_[num] = msg->ranges.at(scan_angle[num]);
    }
  }

  // 计算前方扇形区域的平均距离
  // 注意：angle_min=0, angle_max=2π，index 0 = 正前方
  // 重置计数器
  double front_sum = 0.0;
  int front_count = 0;
  int front_inf_count = 0;
  left_avg_dist_ = 3.5;   // range_max 默认值
  right_avg_dist_ = 3.5;
  left_count_ = 0;
  right_count_ = 0;

  // 前方：-60° 到 +60°（由于 angle_min=0，对应 index 0~60 和末尾部分）
  // 简化：取 index 0~60 和末尾 index (size-60)~(size-1)
  size_t num_rays = msg->ranges.size();
  for (size_t i = 0; i < num_rays; i++) {
    double angle = msg->angle_min + i * msg->angle_increment;
    // 归一化到 -π ~ +π
    while (angle > M_PI) angle -= 2 * M_PI;
    while (angle < -M_PI) angle += 2 * M_PI;

    // 前方 -60° ~ +60°
    if (std::abs(angle) <= 60.0 * DEG2RAD) {
      if (std::isinf(msg->ranges[i])) {
        front_inf_count++;
      } else if (msg->ranges[i] > msg->range_min) {
        front_sum += msg->ranges[i];
        front_count++;
      }
    }

    // 左侧 +60° ~ +120°
    if (angle > 60.0 * DEG2RAD && angle <= 120.0 * DEG2RAD) {
      if (!std::isinf(msg->ranges[i]) && msg->ranges[i] > msg->range_min) {
        left_avg_dist_ += msg->ranges[i];
        left_count_++;
      }
    }

    // 右侧 -120° ~ -60°
    if (angle < -60.0 * DEG2RAD && angle >= -120.0 * DEG2RAD) {
      if (!std::isinf(msg->ranges[i]) && msg->ranges[i] > msg->range_min) {
        right_avg_dist_ += msg->ranges[i];
        right_count_++;
      }
    }
  }

  front_inf_count_ = front_inf_count;
  front_total_ = front_count + front_inf_count;
  front_avg_dist_ = (front_count > 0) ? (front_sum / front_count) : msg->range_max;
  left_avg_dist_ = (left_count_ > 0) ? (left_avg_dist_ / left_count_) : msg->range_max;
  right_avg_dist_ = (right_count_ > 0) ? (right_avg_dist_ / right_count_) : msg->range_max;
}

void Turtlebot3Drive::update_cmd_vel(double linear, double angular)
{
  geometry_msgs::msg::Twist cmd_vel;
  cmd_vel.linear.x = linear;
  cmd_vel.angular.z = angular;

  cmd_vel_pub_->publish(cmd_vel);
}

/********************************************************************************
** Update functions
********************************************************************************/
void Turtlebot3Drive::update_callback()
{
  static uint8_t turtlebot3_state_num = 0;
  static int forward_count = 0;
  double escape_range = 30.0 * DEG2RAD;
  double check_forward_dist = 1.2;   // 前方安全距离
  double check_side_dist = 1.0;      // 侧方安全距离

  switch (turtlebot3_state_num) {
    case GET_TB3_DIRECTION: {
      // 计算前方 .inf 比例
      double inf_ratio = (front_total_ > 0) ?
        (static_cast<double>(front_inf_count_) / front_total_) : 0.0;

      if (inf_ratio > 0.7) {
        // 大部分射线检测不到障碍 → 前方开阔，但需要主动探索转向
        forward_count++;
        if (forward_count > 30) {
          // 直行 30 次后主动转向探索
          prev_robot_pose_ = robot_pose_;
          if (left_avg_dist_ > right_avg_dist_) {
            turtlebot3_state_num = TB3_LEFT_TURN;
          } else {
            turtlebot3_state_num = TB3_RIGHT_TURN;
          }
          forward_count = 0;
        } else {
          turtlebot3_state_num = TB3_DRIVE_FORWARD;
        }
      } else if (front_avg_dist_ > check_forward_dist) {
        // 前方安全，检查侧方
        forward_count = 0;
        if (left_avg_dist_ < check_side_dist && left_count_ > 0) {
          prev_robot_pose_ = robot_pose_;
          turtlebot3_state_num = TB3_RIGHT_TURN;
        } else if (right_avg_dist_ < check_side_dist && right_count_ > 0) {
          prev_robot_pose_ = robot_pose_;
          turtlebot3_state_num = TB3_LEFT_TURN;
        } else {
          turtlebot3_state_num = TB3_DRIVE_FORWARD;
        }
      } else {
        // 前方有障碍，转向
        prev_robot_pose_ = robot_pose_;
        forward_count = 0;
        if (left_avg_dist_ > right_avg_dist_) {
          turtlebot3_state_num = TB3_LEFT_TURN;
        } else {
          turtlebot3_state_num = TB3_RIGHT_TURN;
        }
      }
      break;
    }

    case TB3_DRIVE_FORWARD:
      update_cmd_vel(LINEAR_VELOCITY, 0.0);
      turtlebot3_state_num = GET_TB3_DIRECTION;
      break;

    case TB3_RIGHT_TURN:
      if (fabs(prev_robot_pose_ - robot_pose_) >= escape_range) {
        turtlebot3_state_num = GET_TB3_DIRECTION;
        forward_count = 0;
      } else {
        update_cmd_vel(0.0, -1 * ANGULAR_VELOCITY);
      }
      break;

    case TB3_LEFT_TURN:
      if (fabs(prev_robot_pose_ - robot_pose_) >= escape_range) {
        turtlebot3_state_num = GET_TB3_DIRECTION;
        forward_count = 0;
      } else {
        update_cmd_vel(0.0, ANGULAR_VELOCITY);
      }
      break;

    default:
      turtlebot3_state_num = GET_TB3_DIRECTION;
      break;
  }
}

/*******************************************************************************
** Main
*******************************************************************************/
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Turtlebot3Drive>());
  rclcpp::shutdown();

  return 0;
}
