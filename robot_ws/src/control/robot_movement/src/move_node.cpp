#include "robot_movement/move_node.hpp"

MoveNode::MoveNode()
: Node("move_node")
{
  RCLCPP_INFO(this->get_logger(), "Move Node Started");

  callback_group_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

  auto sub_options = rclcpp::SubscriptionOptions();
  sub_options.callback_group = callback_group_;

  coords_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
    "/target_pose", 10,
    std::bind(&MoveNode::callback, this, std::placeholders::_1),
    sub_options);

  RCLCPP_INFO(this->get_logger(), "Subscribed to /target_pose");
}

void MoveNode::initialize_planning(){
  planning_grp_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(shared_from_this(), "arm");
  planning_grp_->setPlanningTime(10.0);
  planning_grp_->setMaxVelocityScalingFactor(0.3);
  planning_grp_->startStateMonitor();

  RCLCPP_INFO(this->get_logger(), "Planning Group initialized");
}

void MoveNode::callback(const geometry_msgs::msg::PoseStamped::SharedPtr pose)
{
  if(is_moving) return;

  RCLCPP_INFO(
    this->get_logger(),
    "Target pose received: frame=%s x=%.3f y=%.3f z=%.3f",
    pose->header.frame_id.c_str(),
    pose->pose.position.x,
    pose->pose.position.y,
    pose->pose.position.z);

  is_moving = true;

  if(!move(pose->pose)) return;
  sleep(6000);

  is_moving = false;
  rclcpp::shutdown();
}

bool MoveNode::move(const geometry_msgs::msg::Pose pose)
{
  RCLCPP_INFO(this->get_logger(), "Moving Robot to X:%f, Y:%f, Z:%f",pose.position.x,pose.position.y,pose.position.z);
  planning_grp_->setPoseTarget(pose);
  moveit::planning_interface::MoveGroupInterface::Plan plan;
    if (planning_grp_->plan(plan) == moveit::core::MoveItErrorCode::SUCCESS) {
      return planning_grp_->execute(plan) == moveit::core::MoveItErrorCode::SUCCESS;
  }
  return false;
}

void MoveNode::sleep(int milliseconds){
  rclcpp::sleep_for(std::chrono::milliseconds(milliseconds));
}