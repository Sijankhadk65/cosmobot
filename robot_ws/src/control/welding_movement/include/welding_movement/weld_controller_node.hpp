#pragma once

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <visualization_msgs/msg/marker_array.hpp>

#include "welding_movement/seam_path.hpp"
#include "welding_movement/weave_generator.hpp"

namespace welding_movement
{

class WeldControllerNode : public rclcpp::Node
{
public:
  WeldControllerNode();

private:
  void loadParameters();
  void setupSeam();
  void controlLoop();

  geometry_msgs::msg::Point rotateLocalOffsetToWorld(
    const geometry_msgs::msg::Pose& base_pose,
    const geometry_msgs::msg::Vector3& local_offset) const;

  void publishTargetPose(const geometry_msgs::msg::Pose& pose);
  void publishMarkers(const geometry_msgs::msg::Pose& base_pose,
                      const geometry_msgs::msg::Pose& target_pose);

  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr target_pose_pub_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  SeamPath seam_;
  WeaveGenerator weave_;

  std::string world_frame_;
  std::string ee_frame_;
  double control_rate_hz_;
  double travel_speed_;
  double weave_width_;
  double weave_frequency_;

  geometry_msgs::msg::Pose seam_start_;
  geometry_msgs::msg::Pose seam_end_;

  rclcpp::Time weld_start_time_;
  bool started_{false};

  std::vector<geometry_msgs::msg::Point> base_points_;
  std::vector<geometry_msgs::msg::Point> woven_points_;
};

}  // namespace welding_movement