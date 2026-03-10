#pragma once

#include <geometry_msgs/msg/pose.hpp>

namespace welding_movement
{

class SeamPath
{
public:
  SeamPath() = default;

  void setStraightLine(const geometry_msgs::msg::Pose& start,
                       const geometry_msgs::msg::Pose& end);

  double getLength() const;

  geometry_msgs::msg::Pose getPoseAtDistance(double s) const;

private:
  geometry_msgs::msg::Pose start_;
  geometry_msgs::msg::Pose end_;
  double length_{0.0};
};

}