#include <memory>
#include <string>
#include <vector>
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/pose.hpp>

class FollowLineNode : public rclcpp::Node
{
public:
  FollowLineNode() : Node("follow_line_hardware_node")
  {
    RCLCPP_INFO(this->get_logger(), "Line Follower Node Started");
  }

  void initialize()
  {
    // Cgroup for non-blocking execution
    callback_group_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

    // Init MoveIt
    arm_group_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(shared_from_this(), "arm");
    arm_group_->setPlanningTime(10.0);
    arm_group_->setMaxVelocityScalingFactor(0.3);
    arm_group_->startStateMonitor();

    // Subscribe to coordinates
    auto sub_options = rclcpp::SubscriptionOptions();
    sub_options.callback_group = callback_group_;

    coords_sub_ = this->create_subscription<std_msgs::msg::String>(
        "/robot_line_coordinates", 10,
        std::bind(&FollowLineNode::lineCallback, this, std::placeholders::_1),
        sub_options);

    RCLCPP_INFO(this->get_logger(), "Waiting for line data on /robot_line_coordinates...");
  }

private:
  void lineCallback(const std_msgs::msg::String::SharedPtr msg)
  {
    if (is_busy_) return;
    
    // Parse format: Line: P1=(x, y, z), P2=(x, y, z), Length=Lm
    double x1, y1, z1, x2, y2, z2;
    if (sscanf(msg->data.c_str(), "Line: P1=(%lf, %lf, %lf), P2=(%lf, %lf, %lf)", &x1, &y1, &z1, &x2, &y2, &z2) == 6) {
        RCLCPP_INFO(this->get_logger(), "Line detected from (%.2f, %.2f) to (%.2f, %.2f)", x1, y1, x2, y2);
        is_busy_ = true;
        
        // Sequence: Home -> P1_Up -> P1 -> P2 -> P2_Up -> Home
        RCLCPP_INFO(this->get_logger(), "Moving to Approach P1...");
        moveToPose(x1, y1, z1 + 0.01); // Approach P1
        sleep(6000); // 5 sec delay

        RCLCPP_INFO(this->get_logger(), "Moving to P1...");
        moveToPose(x1, y1, z1);        // Touch P1
        sleep(6000); 

        RCLCPP_INFO(this->get_logger(), "Tracing to P2...");
        moveToPose(x2, y2, z2);        // Trace to P2
        sleep(6000);

        RCLCPP_INFO(this->get_logger(), "Lifting from P2...");
        moveToPose(x2, y2, z2 + 0.01); // Lift from P2
        sleep(6000);
        
        // Return to Home
        RCLCPP_INFO(this->get_logger(), "Returning Home...");
        arm_group_->setJointValueTarget(std::vector<double>{1.57, 0.0, 0.0, 0.0, 0.0});
        arm_group_->move();

        RCLCPP_INFO(this->get_logger(), "Sequence complete.");
        is_busy_ = false;
        rclcpp::shutdown();
    }
  }

  void sleep(int milliseconds)
  {
    rclcpp::sleep_for(std::chrono::milliseconds(milliseconds));
  }

  bool moveToPose(double x, double y, double z)
  {
    geometry_msgs::msg::Pose pose;
    pose.position.x = x;
    pose.position.y = y;
    pose.position.z = z;
    pose.orientation.w = 1.0; // Minimal orientation (pointing down/neutral)

    arm_group_->setPoseTarget(pose);
    moveit::planning_interface::MoveGroupInterface::Plan plan;
    if (arm_group_->plan(plan) == moveit::core::MoveItErrorCode::SUCCESS) {
      return arm_group_->execute(plan) == moveit::core::MoveItErrorCode::SUCCESS;
    }
    return false;
  }

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> arm_group_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr coords_sub_;
  rclcpp::CallbackGroup::SharedPtr callback_group_;
  bool is_busy_{false};
};

int main(int argc, char* argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<FollowLineNode>();
  node->initialize();
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  executor.spin();
  rclcpp::shutdown();
  return 0;
}
