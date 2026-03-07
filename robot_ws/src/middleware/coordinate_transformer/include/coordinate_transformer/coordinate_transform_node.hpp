#ifndef COORDINATE_TRANSFORMER__COORDINATE_TRANSFORM_NODE_HPP_
#define COORDINATE_TRANSFORMER__COORDINATE_TRANSFORM_NODE_HPP_

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

class CoordinateTransformNode : public rclcpp::Node
{
public:
  CoordinateTransformNode();

private:
  void publish_pose();

  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

#endif