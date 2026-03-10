#include "welding_movement/seam_path.hpp"

#include <algorithm>
#include <cmath>

namespace welding_movement
{

void SeamPath::setStraightLine(const geometry_msgs::msg::Pose& start,
                               const geometry_msgs::msg::Pose& end)
{
  start_ = start;
  end_ = end;

  const double dx = end.position.x - start.position.x;
  const double dy = end.position.y - start.position.y;
  const double dz = end.position.z - start.position.z;

  length_ = std::sqrt(dx * dx + dy * dy + dz * dz);
}

double SeamPath::getLength() const
{
  return length_;
}

geometry_msgs::msg::Pose SeamPath::getPoseAtDistance(double s) const
{
  geometry_msgs::msg::Pose pose = start_;

  if (length_ <= 1e-9) {
    return pose;
  }

  const double alpha = std::clamp(s / length_, 0.0, 1.0);

  pose.position.x = start_.position.x + alpha * (end_.position.x - start_.position.x);
  pose.position.y = start_.position.y + alpha * (end_.position.y - start_.position.y);
  pose.position.z = start_.position.z + alpha * (end_.position.z - start_.position.z);

  // Phase 1: constant orientation = start orientation
  pose.orientation = start_.orientation;

  return pose;
}

}