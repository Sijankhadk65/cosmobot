from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import FindExecutable
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import os

def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_name = LaunchConfiguration('robot_name')
    use_camera = LaunchConfiguration("use_camera")
    
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_name",
            default_value="so101",
            description="Name of the robot",
        )
    )
    use_camera_arg = DeclareLaunchArgument(
        name='use_camera',
        default_value='true',
        description='Flag to enable the RGBD camera for Gazebo point cloud simulation'
    )

    # Get URDF via xacro with Gazebo configurations
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("so_arm_description"), "urdf", "robots", "so101.urdf.xacro"]
            ),
            " ",
            "use_gazebo:=true",
            " ",
            "robot_name:=",
            robot_name,
            " ",
            " use_camera:=",
                use_camera,
            " ",
            "add_world:=true",
        ]
    )

    robot_description = {"robot_description": ParameterValue(robot_description_content, value_type=str)}
    # Declare argument for world file
    default_world = os.path.join(
        get_package_share_directory('so_arm_gazebo'),
        'worlds',
        'cube.world'
    )    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='World to load'
    )
    world = LaunchConfiguration('world') # Define LaunchConfiguration after DeclareLaunchArgument

    # Include the Gazebo launch file, provided by the ros_gz_sim package
    gz_sim_share = get_package_share_directory('ros_gz_sim')
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    gz_sim_share, 'launch', 'gz_sim.launch.py')]),
                    launch_arguments={'gz_args': ['-r ', world], 'on_exit_shutdown': 'true'}.items()
             )

    # MoveIt Configuration
    moveit_config = (
        MoveItConfigsBuilder("so101_arm", package_name="so_arm_moveit_config")
        .robot_description(
            file_path=os.path.join(
                get_package_share_directory("so_arm_description"),
                "urdf",
                "robots",
                "so101.urdf.xacro"
            ),
        )
        .robot_description_semantic(file_path="config/so101_arm.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    # Include Gazebo

    # Get ros_gz_bridge configuration file path
    ros_gz_bridge_config = os.path.join(
        get_package_share_directory("so_arm_gazebo"),
        "config",
        "ros_gz_bridge.yaml",
    )

    # ROS-Gazebo Bridge using config file
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        parameters=[{
            'use_sim_time': use_sim_time,
            'config_file': ros_gz_bridge_config,
        }],
        output='screen'
    )

    ros_gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=[
            '/camera_head/depth_image',
            '/camera_head/image',
        ],
        remappings=[
            ('/camera_head/depth_image', '/camera_head/depth/image_rect_raw'),
            ('/camera_head/image', '/camera_head/color/image_raw'),
        ],
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time}
        ],
    )

    # Spawn the robot in Gazebo
    # When spawned, Gazebo will automatically start the gz_ros2_control plugin
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name', robot_name,
            '-allow_renaming', 'true',
            '-z', '0.0',
            '-Y', '0.0',
        ],
        output='screen'
    )

    # Controller Spawners
    # These connect to the controller_manager that Gazebo creates
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

    # Delay controller spawners to wait for Gazebo's controller_manager
    delayed_joint_state_broadcaster_spawner = TimerAction(
        period=5.0,
        actions=[joint_state_broadcaster_spawner],
    )

    delayed_arm_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=joint_state_broadcaster_spawner,
            on_start=[
                TimerAction(
                    period=1.0,
                    actions=[arm_controller_spawner],
                )
            ],
        )
    )

    delayed_gripper_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=arm_controller_spawner,
            on_start=[
                TimerAction(
                    period=1.0,
                    actions=[gripper_controller_spawner],
                )
            ],
        )
    )

    # MoveIt Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": use_sim_time},
            {"publish_robot_description_semantic": True}
        ],
        arguments=["--ros-args", "--log-level", "info"],
    )

    # Start MoveIt after controllers
    delayed_move_group_node = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=gripper_controller_spawner,
            on_start=[
                TimerAction(
                    period=2.0,
                    actions=[move_group_node],
                )
            ],
        )
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
            {"use_sim_time": use_sim_time}
        ],
    )

    delayed_rviz_node = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=move_group_node,
            on_start=[
                TimerAction(
                    period=1.0,
                    actions=[rviz_node],
                )
            ],
        )
    )

    return LaunchDescription(
        declared_arguments
        + [
            # Start Gazebo first
            world_arg,
            use_camera_arg,
            gazebo,
            ros_gz_bridge,
            ros_gz_image_bridge,
            
            # Robot state publisher
            robot_state_publisher_node,
            
            # Spawn robot in Gazebo (this will start gz_ros2_control automatically)
            spawn_entity,
            
            # Wait for Gazebo's controller_manager, then spawn controllers
            delayed_joint_state_broadcaster_spawner,
            delayed_arm_controller_spawner,
            delayed_gripper_controller_spawner,
            
            # MoveIt and RViz
            delayed_move_group_node,
            delayed_rviz_node,
        ]
    )