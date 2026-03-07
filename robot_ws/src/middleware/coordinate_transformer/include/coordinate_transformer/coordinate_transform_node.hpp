#ifndef COORDINATE_TRANSFORMER__COORDINATE_TRANSFORM_NODE_HPP_
#define COORDINATE_TRANSFORMER__COORDINATE_TRANSFORM_NODE_HPP_

#include "rclcpp/rclcpp.hpp"
#include "robot_interfaces/msg/target_coordinates.hpp"
#include "robot_interfaces/msg/target_coordinate.hpp"

class CoordinateTransformNode : public rclcpp::Node
{
public:
  CoordinateTransformNode();

private:
  void publish_pose();

  rclcpp::Publisher<robot_interfaces::msg::TargetCoordinates>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

#endif