from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import os

def generate_launch_description():

    is_sim = LaunchConfiguration("is_sim")
    
    is_sim_arg = DeclareLaunchArgument(
        "is_sim",
        default_value="False"
    )

    # MoveIt Configuration
    moveit_config = (
        MoveItConfigsBuilder("so101_arm", package_name="so_arm_moveit_config")
        .robot_description(file_path="config/so101_arm_hardware.urdf.xacro")
        .robot_description_semantic(file_path="config/so101_arm.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    # Load controllers configuration
    ros2_controllers_path = os.path.join(
        get_package_share_directory("so_arm_moveit_config"),
        "config",
        "ros2_controllers.yaml",
    )

    # ROS2 Control Node
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            moveit_config.robot_description,
            ros2_controllers_path,
        ],
        output="screen",
    )

    # Controller Spawners
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # Node to move the robot to the initial pose
    initial_pose_node = Node(
        package="pymoveit2", # Replace with your package name if different
        executable="initial_pose.py",
        name="initial_pose",
        output="screen",
        # Ensure this node starts after the controllers are spawned
        # You might need to use a lifecycle node or events for strict ordering in a real system,
        # but for this case, placing it after spawner nodes in the list should suffice for basic
        # initialization as the script will wait for MoveIt.
    )

    # MoveIt Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": is_sim},
            {"publish_robot_description_semantic": True}
        ],
        arguments=["--ros-args", "--log-level", "info"],
    )

    # RViz Configuration
    rviz_config_path = os.path.join(
        get_package_share_directory("so_arm_moveit_config"),
        "config",
        "moveit.rviz",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_path],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
        ],
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    # Add Planning Scene Monitor parameters
    planning_scene_monitor_params = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }

    # Merge planning_scene_monitor_params into moveit_config
    moveit_config.planning_scene_monitor.update(planning_scene_monitor_params)

    return LaunchDescription(
        [
            is_sim_arg,
            # Robot state publisher
            robot_state_publisher_node,
            
            # ROS2 controllers
            ros2_control_node,
            joint_state_broadcaster_spawner,
            arm_controller_spawner,
            gripper_controller_spawner,
            initial_pose_node, # Add the initial pose node here

            # MoveIt and visualization
            move_group_node,
            
            # Launch RViz only after the initial pose node finishes
            RegisterEventHandler(
                OnProcessExit(
                    target_action=initial_pose_node,
                    on_exit=[rviz_node]
                )
            )
        ]
    )
