#include "welding_movement/weld_controller_node.hpp"

#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

#include <algorithm>
#include <cmath>

namespace welding_movement
{

WeldControllerNode::WeldControllerNode()
: Node("weld_controller_node")
{
  loadParameters();
  setupSeam();

  weave_.configure(weave_width_, weave_frequency_);

  target_pose_pub_ =
    this->create_publisher<geometry_msgs::msg::PoseStamped>(
      "/welding/target_pose", 10);

  marker_pub_ =
    this->create_publisher<visualization_msgs::msg::MarkerArray>(
      "/welding/markers", 10);

  const auto period = std::chrono::duration<double>(1.0 / control_rate_hz_);
  timer_ = this->create_wall_timer(
    std::chrono::duration_cast<std::chrono::milliseconds>(period),
    std::bind(&WeldControllerNode::controlLoop, this));

  RCLCPP_INFO(this->get_logger(), "WeldControllerNode started.");
}

void WeldControllerNode::loadParameters()
{
  this->declare_parameter<std::string>("world_frame", "world");
  this->declare_parameter<std::string>("ee_frame", "gripper");
  this->declare_parameter<double>("control_rate_hz", 100.0);
  this->declare_parameter<double>("travel_speed", 0.01);
  this->declare_parameter<double>("weave_width", 0.006);
  this->declare_parameter<double>("weave_frequency", 3.0);

  this->declare_parameter<std::vector<double>>(
    "seam_start.position", {0.20, 0.00, 0.20});
  this->declare_parameter<std::vector<double>>(
    "seam_end.position", {0.30, 0.00, 0.20});
  this->declare_parameter<std::vector<double>>(
    "seam_orientation_rpy", {0.0, M_PI, 0.0});

  world_frame_ = this->get_parameter("world_frame").as_string();
  ee_frame_ = this->get_parameter("ee_frame").as_string();
  control_rate_hz_ = this->get_parameter("control_rate_hz").as_double();
  travel_speed_ = this->get_parameter("travel_speed").as_double();
  weave_width_ = this->get_parameter("weave_width").as_double();
  weave_frequency_ = this->get_parameter("weave_frequency").as_double();

  const auto start_pos = this->get_parameter("seam_start.position").as_double_array();
  const auto end_pos = this->get_parameter("seam_end.position").as_double_array();
  const auto rpy = this->get_parameter("seam_orientation_rpy").as_double_array();

  seam_start_.position.x = start_pos.at(0);
  seam_start_.position.y = start_pos.at(1);
  seam_start_.position.z = start_pos.at(2);

  seam_end_.position.x = end_pos.at(0);
  seam_end_.position.y = end_pos.at(1);
  seam_end_.position.z = end_pos.at(2);

  tf2::Quaternion q;
  q.setRPY(rpy.at(0), rpy.at(1), rpy.at(2));
  q.normalize();

  seam_start_.orientation = tf2::toMsg(q);
  seam_end_.orientation = tf2::toMsg(q);
}

void WeldControllerNode::setupSeam()
{
  seam_.setStraightLine(seam_start_, seam_end_);

  RCLCPP_INFO(this->get_logger(),
              "Seam length: %.4f m",
              seam_.getLength());
}

geometry_msgs::msg::Point WeldControllerNode::rotateLocalOffsetToWorld(
  const geometry_msgs::msg::Pose& base_pose,
  const geometry_msgs::msg::Vector3& local_offset) const
{
  tf2::Quaternion q;
  tf2::fromMsg(base_pose.orientation, q);

  tf2::Matrix3x3 R(q);
  tf2::Vector3 local(local_offset.x, local_offset.y, local_offset.z);
  tf2::Vector3 world = R * local;

  geometry_msgs::msg::Point p;
  p.x = world.x();
  p.y = world.y();
  p.z = world.z();
  return p;
}

void WeldControllerNode::publishTargetPose(const geometry_msgs::msg::Pose& pose)
{
  geometry_msgs::msg::PoseStamped msg;
  msg.header.stamp = this->now();
  msg.header.frame_id = world_frame_;
  msg.pose = pose;
  target_pose_pub_->publish(msg);
}

void WeldControllerNode::publishMarkers(const geometry_msgs::msg::Pose& base_pose,
                                        const geometry_msgs::msg::Pose& target_pose)
{
  base_points_.push_back(base_pose.position);
  woven_points_.push_back(target_pose.position);

  visualization_msgs::msg::MarkerArray array;

  visualization_msgs::msg::Marker base_line;
  base_line.header.frame_id = world_frame_;
  base_line.header.stamp = this->now();
  base_line.ns = "welding";
  base_line.id = 0;
  base_line.type = visualization_msgs::msg::Marker::LINE_STRIP;
  base_line.action = visualization_msgs::msg::Marker::ADD;
  base_line.scale.x = 0.002;
  base_line.color.r = 0.0f;
  base_line.color.g = 1.0f;
  base_line.color.b = 0.0f;
  base_line.color.a = 1.0f;
  base_line.points = base_points_;

  visualization_msgs::msg::Marker weave_line;
  weave_line.header.frame_id = world_frame_;
  weave_line.header.stamp = this->now();
  weave_line.ns = "welding";
  weave_line.id = 1;
  weave_line.type = visualization_msgs::msg::Marker::LINE_STRIP;
  weave_line.action = visualization_msgs::msg::Marker::ADD;
  weave_line.scale.x = 0.002;
  weave_line.color.r = 1.0f;
  weave_line.color.g = 0.0f;
  weave_line.color.b = 0.0f;
  weave_line.color.a = 1.0f;
  weave_line.points = woven_points_;

  visualization_msgs::msg::Marker tcp_sphere;
  tcp_sphere.header.frame_id = world_frame_;
  tcp_sphere.header.stamp = this->now();
  tcp_sphere.ns = "welding";
  tcp_sphere.id = 2;
  tcp_sphere.type = visualization_msgs::msg::Marker::SPHERE;
  tcp_sphere.action = visualization_msgs::msg::Marker::ADD;
  tcp_sphere.pose = target_pose;
  tcp_sphere.scale.x = 0.01;
  tcp_sphere.scale.y = 0.01;
  tcp_sphere.scale.z = 0.01;
  tcp_sphere.color.r = 1.0f;
  tcp_sphere.color.g = 1.0f;
  tcp_sphere.color.b = 0.0f;
  tcp_sphere.color.a = 1.0f;

  array.markers.push_back(base_line);
  array.markers.push_back(weave_line);
  array.markers.push_back(tcp_sphere);

  marker_pub_->publish(array);
}

void WeldControllerNode::controlLoop()
{
  if (!started_) {
    weld_start_time_ = this->now();
    started_ = true;
  }

  const double t = (this->now() - weld_start_time_).seconds();
  const double s = travel_speed_ * t;
  const double seam_length = seam_.getLength();

  const double s_clamped = std::clamp(s, 0.0, seam_length);
  const auto base_pose = seam_.getPoseAtDistance(s_clamped);

  const auto local_offset = weave_.compute(t);
  const auto world_offset = rotateLocalOffsetToWorld(base_pose, local_offset);

  geometry_msgs::msg::Pose target_pose = base_pose;
  target_pose.position.x += world_offset.x;
  target_pose.position.y += world_offset.y;
  target_pose.position.z += world_offset.z;

  publishTargetPose(target_pose);
  publishMarkers(base_pose, target_pose);

  if (s >= seam_length) {
    RCLCPP_INFO_THROTTLE(
      this->get_logger(), *this->get_clock(), 2000,
      "Reached seam end. Holding final pose.");
  }
}

}  // namespace welding_movement