#include "rclcpp/rclcpp.hpp"
#include "coordinate_transformer/coordinate_transform_node.hpp"

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CoordinateTransformNode>());
  rclcpp::shutdown();
  return 0;
}