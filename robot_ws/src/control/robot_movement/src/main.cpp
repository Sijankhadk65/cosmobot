#include "rclcpp/rclcpp.hpp"
#include "robot_movement/move_node.hpp"

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  std::shared_ptr<MoveNode> move_node = std::make_shared<MoveNode>();

  rclcpp::executors::MultiThreadedExecutor executor;

  move_node->initialize_planning();

  executor.add_node(move_node);
  executor.spin();

  rclcpp::shutdown();
  return 0;
}