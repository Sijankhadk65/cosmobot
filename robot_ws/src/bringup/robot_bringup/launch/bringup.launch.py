from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Common
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_rviz = LaunchConfiguration("use_rviz")

    # URDF/Xacro toggles (affect robot_description)
    use_gazebo = LaunchConfiguration("use_gazebo")
    add_world = LaunchConfiguration("add_world")
    use_camera_urdf = LaunchConfiguration("use_camera_urdf")

    # Runtime nodes toggles
    use_camera_driver = LaunchConfiguration("use_camera_driver")
    use_perception = LaunchConfiguration("use_perception")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="false",
        description="Use simulation clock"
    )
    declare_use_rviz = DeclareLaunchArgument(
        "use_rviz", default_value="true",
        description="Start RViz2"
    )

    # Joint State Pulisher
    use_jsp_gui = LaunchConfiguration("use_jsp_gui")

    declare_use_jsp_gui = DeclareLaunchArgument(
        "use_jsp_gui", default_value="true",
        description="Start joint_state_publisher_gui for visualization (dev only)"
    )

    # Xacro args
    declare_use_gazebo = DeclareLaunchArgument(
        "use_gazebo", default_value="false",
        description="Enable Gazebo ros2_control plugin (xacro arg)"
    )
    declare_add_world = DeclareLaunchArgument(
        "add_world", default_value="true",
        description="Add world link/frame in the model (xacro arg)"
    )
    declare_use_camera_urdf = DeclareLaunchArgument(
        "use_camera_urdf", default_value="true",
        description="Include camera link/frame in robot_description (xacro arg)"
    )

    # Runtime nodes
    declare_use_camera_driver = DeclareLaunchArgument(
        "use_camera_driver", default_value="false",
        description="Start camera driver node"
    )
    declare_use_perception = DeclareLaunchArgument(
        "use_perception", default_value="false",
        description="Start perception pipeline"
    )

    # ---- robot_description from SO-101 xacro ----
    # IMPORTANT: Your provided xacros reference $(find so_arm_description),
    # so your package should be named "so_arm_description".
    xacro_file = PathJoinSubstitution([
        FindPackageShare("so_arm_description"),
        "urdf",
        "so101.urdf.xacro"
    ])

    robot_description = Command([
        TextSubstitution(text="xacro "),
        xacro_file,
        TextSubstitution(text=" use_gazebo:="), use_gazebo,
        TextSubstitution(text=" add_world:="), add_world,
        TextSubstitution(text=" use_camera:="), use_camera_urdf,
    ])

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "robot_description": robot_description
        }],
    )

    # ---- Optional runtime nodes (placeholders for now) ----
    camera_node = Node(
        condition=IfCondition(use_camera_driver),
        package="openni2_camera",
        executable="openni2_camera_driver",
        name="astra",
        output="screen",
        parameters=[
            {"camera": "camera"},  # publishes under /camera/...
            {"depth_registration": True},
            {"color_depth_synchronization": True},
        ],
    )

    perception_node = Node(
        condition=IfCondition(use_perception),
        package="robot_color_detector", # replace later
        executable="detector_node",     # replace later
        name="perception",
        output="screen",
    )

    # ---- RViz ----
    rviz_config = PathJoinSubstitution([
        FindPackageShare("robot_bringup"),
        "rviz",
        "robot.rviz"
    ])

    rviz_node = Node(
        condition=IfCondition(use_rviz),
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # Joint State Publisher Node
    joint_state_publisher_gui_node = Node(
        condition=IfCondition(use_jsp_gui),
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_use_rviz,

        declare_use_gazebo,
        declare_add_world,
        declare_use_camera_urdf,

        declare_use_camera_driver,
        declare_use_perception,

        declare_use_jsp_gui,

        robot_state_publisher,
        joint_state_publisher_gui_node,
        camera_node,
        perception_node,
        rviz_node,
    ])