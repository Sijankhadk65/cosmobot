#include "robot_movement/move_node.hpp"

MoveNode::MoveNode()
: Node("move_node")
{
  RCLCPP_INFO(this->get_logger(), "Move Node Started");

  callback_group_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

  auto sub_options = rclcpp::SubscriptionOptions();
  sub_options.callback_group = callback_group_;

  coords_sub_ = this->create_subscription<robot_interfaces::msg::TargetCoordinates>(
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

void MoveNode::callback(const std::shared_ptr<robot_interfaces::msg::TargetCoordinates> target)
{
  {
    std::lock_guard<std::mutex> lock(move_mutex);
  }
  
  if(is_moving || target->targets.empty()) {
    std::lock_guard<std::mutex> lock(move_mutex);
    return;
  }

  RCLCPP_INFO(
    this->get_logger(),
    "Target pose received: frame=%s x=%.3f y=%.3f z=%.3f",
    target->header.frame_id.c_str(),
    target->targets[0].pose.position.x,
    target->targets[0].pose.position.y,
    target->targets[0].pose.position.z);

  is_moving = true;

  bool success = move(target->targets[0].pose);
  sleep(6000);

  if(!success) RCLCPP_INFO(this->get_logger(),"Movement Failed");
  
  {
    std::lock_guard<std::mutex> lock(move_mutex);
    is_moving = false;
  }

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