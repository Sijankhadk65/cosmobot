#include "robot_movement/move_node.hpp"

MoveNode::MoveNode()
: Node("move_node")
{
  RCLCPP_INFO(this->get_logger(), "Move Node Started");

  callback_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);

  auto sub_options = rclcpp::SubscriptionOptions();
  sub_options.callback_group = callback_group_;

  coords_sub_ = this->create_subscription<robot_interfaces::msg::TargetCoordinates>(
    "/target_pose", 10,
    std::bind(&MoveNode::callback, this, std::placeholders::_1),
    sub_options);

  RCLCPP_INFO(this->get_logger(), "Subscribed to /target_pose");
}

void MoveNode::initialize_planning(){
  planning_grp_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(shared_from_this(), "arm");
  planning_grp_->setPlanningTime(10.0);
  planning_grp_->setMaxVelocityScalingFactor(0.3);
  planning_grp_->startStateMonitor();

  RCLCPP_INFO(this->get_logger(), "Planning Group initialized");
}

void MoveNode::callback(const std::shared_ptr<robot_interfaces::msg::TargetCoordinates> target)
{  
  bool move_success = false;

  if(is_moving) {
    RCLCPP_INFO(this->get_logger(),"Robot is already moving.");
    return;
  }

  if(target->targets.empty()) {
    RCLCPP_INFO(this->get_logger(),"No target positions recieved.");
    return;
  }

  RCLCPP_INFO(
    this->get_logger(),
    "Target pose received: frame=%s x=%.3f y=%.3f z=%.3f",
    target->header.frame_id.c_str(),
    target->targets[0].pose.position.x,
    target->targets[0].pose.position.y,
    target->targets[0].pose.position.z);

  is_moving = true;

  geometry_msgs::msg::Pose start_point = planning_grp_->getCurrentPose().pose;

  // Tool Pointed downward received: x=0.217 y=0.021 z=0.206, Quartenions X=0.000,Y=-0.002,Z=0.000,W=1.000  
  
  RCLCPP_INFO(
    this->get_logger(),
    "Current pose received: Px=%.3f Py=%.3f Pz=%.3f and Ox=%.3f Oy=%.3f Oz=%.3f Ow=%.3f",
    start_point.position.x,
    start_point.position.y,
    start_point.position.z,
    start_point.orientation.x,
    start_point.orientation.y,
    start_point.orientation.z,
    start_point.orientation.w
  );

  start_point.position.x = 0.130;
  start_point.position.y = 0.021;
  start_point.position.z = 0.162;

  start_point.orientation.x = 0.0;
  start_point.orientation.y = -0.004;
  start_point.orientation.z = 0.0;
  start_point.orientation.w = 1.0;
  move_success = move(start_point);
  sleep(10000);

  if(move_success){
    move_success = move_straight_line();
    sleep(6000);
  }else{
    RCLCPP_INFO(this->get_logger(),"Pose Movement Failed");
  }

  if(!move_success) RCLCPP_INFO(this->get_logger(),"Straight Line Movement Failed");

  is_moving = false;
  rclcpp::shutdown();
}

bool MoveNode::move_straight_line()
{ 
  // Max Distance in X  = 14 cm;
  // Point 1 ->  Px=0.130 Py=0.021 Pz=0.162 and Ox=0.000 Oy=-0.004 Oz=0.000 Ow=1.000;
  // Point 2 ->  Px=0.276 Py=0.021 Pz=0.154 and Ox=0.000 Oy=-0.004 Oz=0.000 Ow=1.000;

  planning_grp_->setStartStateToCurrentState();

  std::vector<geometry_msgs::msg::Pose> waypoints;
  
  geometry_msgs::msg::Pose current_pose = planning_grp_->getCurrentPose().pose;
  geometry_msgs::msg::Pose next_pose = current_pose;
  

  const int steps = 15;
  const double dx = 0.05 / steps;

  next_pose.position.z += 0.0003;

  for (int i = 0; i < steps; ++i)
  {
    next_pose.position.x += dx;
    waypoints.push_back(next_pose);
  }

  moveit_msgs::msg::RobotTrajectory trajectory;

  double fraction = planning_grp_->computeCartesianPath(
      waypoints,
      0.002,
      trajectory
  );

  RCLCPP_INFO(
    this->get_logger(),
    "Cartesian path fraction: %.2f%%",
    fraction * 100.0
  );

  if (fraction < 0.95)
  {
    RCLCPP_WARN(
      this->get_logger(),
      "Cartesian path incomplete. Only %.2f%% achieved.",
      fraction * 100.0
    );
    return false;
  }

  auto result = planning_grp_->execute(trajectory);
  return result == moveit::core::MoveItErrorCode::SUCCESS;
}

bool MoveNode::move(const geometry_msgs::msg::Pose pose)
{
  RCLCPP_INFO(this->get_logger(), "Moving Robot to X:%f, Y:%f, Z:%f",pose.position.x,pose.position.y,pose.position.z);
  planning_grp_->setPoseTarget(pose);
  moveit::planning_interface::MoveGroupInterface::Plan plan;
    if (planning_grp_->plan(plan) == moveit::core::MoveItErrorCode::SUCCESS) {
      return planning_grp_->execute(plan) == moveit::core::MoveItErrorCode::SUCCESS;
  }
  return false;
}

void MoveNode::sleep(int milliseconds){
  rclcpp::sleep_for(std::chrono::milliseconds(milliseconds));
}