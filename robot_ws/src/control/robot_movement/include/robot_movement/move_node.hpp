#ifndef MOVE_NODE_HPP_
#define MOVE_NODE_HPP_

#include <memory>
#include <string>
#include <vector>
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include "geometry_msgs/msg/pose_stamped.hpp"

class MoveNode : public rclcpp::Node
{
public:
  MoveNode();
  void initialize_planning();
  
private:
  void callback(const geometry_msgs::msg::PoseStamped::SharedPtr pose);
  bool move(const geometry_msgs::msg::Pose pose);
  void sleep(int milliseconds);

  rclcpp::CallbackGroup::SharedPtr callback_group_;
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr coords_sub_;

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> planning_grp_;

  bool is_moving = false;
};

#endif