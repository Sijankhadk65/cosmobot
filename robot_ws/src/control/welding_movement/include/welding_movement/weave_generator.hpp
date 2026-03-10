#pragma once

#include <geometry_msgs/msg/vector3.hpp>

namespace welding_movement
{

class WeaveGenerator
{
public:
  WeaveGenerator() = default;

  void configure(double width, double frequency);

  geometry_msgs::msg::Vector3 compute(double t) const;

private:
  double width_{0.0};      // total width in meters
  double frequency_{1.0};  // Hz
};

}  // namespace welding_movement