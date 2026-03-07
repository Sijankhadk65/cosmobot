#include "coordinate_transformer/coordinate_transform_node.hpp"

using namespace std::chrono_literals;

CoordinateTransformNode::CoordinateTransformNode()
: Node("coordinate_transform_node")
{
  publisher_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
    "/target_pose", 10);

  timer_ = this->create_wall_timer(
    500ms,
    std::bind(&CoordinateTransformNode::publish_pose, this));

  RCLCPP_INFO(this->get_logger(), "Coordinate Transform Node Started");
}

void CoordinateTransformNode::publish_pose()
{
  geometry_msgs::msg::PoseStamped msg;

  msg.header.stamp = this->get_clock()->now();
  msg.header.frame_id = "base_link";

  msg.pose.position.x =  0.08;
  msg.pose.position.y = -0.22;
  msg.pose.position.z =  0.18;
  msg.pose.orientation.w = 1.0;

  publisher_->publish(msg);

  RCLCPP_INFO(this->get_logger(), "Publishing target pose");
}