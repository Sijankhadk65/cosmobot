#include "welding_movement/weld_controller_node.hpp"
#include <rclcpp/rclcpp.hpp>

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<welding_movement::WeldControllerNode>());
  rclcpp::shutdown();
  return 0;
}