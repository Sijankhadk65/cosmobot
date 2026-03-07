#ifndef MOVE_NODE_HPP_
#define MOVE_NODE_HPP_

#include <memory>
#include <string>
#include <vector>
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <mutex>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <std_msgs/msg/string.hpp>
#include <robot_interfaces/msg/target_coordinates.hpp>

class MoveNode : public rclcpp::Node
{
public:
  MoveNode();
  void initialize_planning();
  
private:
  void callback(const std::shared_ptr<robot_interfaces::msg::TargetCoordinates> target);
  bool move(const geometry_msgs::msg::Pose pose);
  void sleep(int milliseconds);

  rclcpp::CallbackGroup::SharedPtr callback_group_;
  rclcpp::Subscription<robot_interfaces::msg::TargetCoordinates>::SharedPtr coords_sub_;

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> planning_grp_;

  bool is_moving = false;

  std::mutex move_mutex;
};

#endif