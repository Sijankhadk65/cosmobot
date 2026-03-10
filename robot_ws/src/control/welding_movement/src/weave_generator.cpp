#include "welding_movement/weave_generator.hpp"

#include <cmath>

namespace welding_movement
{

void WeaveGenerator::configure(double width, double frequency)
{
  width_ = width;
  frequency_ = frequency;
}

geometry_msgs::msg::Vector3 WeaveGenerator::compute(double t) const
{
  geometry_msgs::msg::Vector3 offset;
  const double amplitude = width_ * 0.5;

  // Seam local frame:
  // X = travel direction
  // Y = left/right weave
  // Z = not used in phase 1
  offset.x = 0.0;
  offset.y = amplitude * std::sin(2.0 * M_PI * frequency_ * t);
  offset.z = 0.0;

  return offset;
}

}  // namespace welding_movement