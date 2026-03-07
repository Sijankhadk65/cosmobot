#include "coordinate_transformer/coordinate_transform_node.hpp"

using namespace std::chrono_literals;

CoordinateTransformNode::CoordinateTransformNode()
: Node("coordinate_transform_node")
{
  publisher_ = this->create_publisher<robot_interfaces::msg::TargetCoordinates>(
    "/target_pose", 10);

  timer_ = this->create_wall_timer(
    500ms,
    std::bind(&CoordinateTransformNode::publish_pose, this));

  RCLCPP_INFO(this->get_logger(), "Coordinate Transform Node Started");
}

void CoordinateTransformNode::publish_pose()
{
  robot_interfaces::msg::TargetCoordinates msg;
  robot_interfaces::msg::TargetCoordinate target;

  msg.header.stamp = this->get_clock()->now();
  msg.header.frame_id = "base_link";

  target.pose.position.x =  0.08;
  target.pose.position.y = -0.22;
  target.pose.position.z =  0.18;
  target.pose.orientation.w = 1.0;

  msg.targets.push_back(target);

  publisher_->publish(msg);

  RCLCPP_INFO(this->get_logger(), "Publishing target pose");
}