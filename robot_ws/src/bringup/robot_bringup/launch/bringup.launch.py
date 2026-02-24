from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_rviz = LaunchConfiguration("use_rviz")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="false",
        description="Use simulation clock"
    )
    declare_use_rviz = DeclareLaunchArgument(
        "use_rviz", default_value="true",
        description="Start RViz2"
    )

    # Process xacro -> robot_description
    xacro_file = PathJoinSubstitution([
        FindPackageShare("robot_description"),
        "urdf",
        "robot.urdf.xacro"
    ])

    robot_description = Command(["xacro ", xacro_file])

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
    # Add Later when the camera has dynamic tf
    # tf_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         PathJoinSubstitution([FindPackageShare("robot_tf"), "launch", "static_tfs.launch.py"])
    #     )
    # )

    use_camera = LaunchConfiguration("use_camera")
    use_perception = LaunchConfiguration("use_perception")

    declare_use_camera = DeclareLaunchArgument(
        "use_camera", default_value="false",
        description="Start camera driver"
    )
    declare_use_perception = DeclareLaunchArgument(
        "use_perception", default_value="false",
        description="Start perception pipeline"
    )

    camera_node = Node(
        condition=IfCondition(use_camera),
        package="robot_astra_driver",   # replace when you know exact driver package
        executable="camera_node",       # replace with your actual executable
        name="camera",
        output="screen",
    )

    perception_node = Node(
        condition=IfCondition(use_perception),
        package="robot_color_detector", # replace later
        executable="detector_node",     # replace later
        name="perception",
        output="screen",
    )

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

    return LaunchDescription([
        declare_use_sim_time,
        declare_use_rviz,
        declare_use_camera,
        declare_use_perception,
        robot_state_publisher,
        camera_node,
        perception_node,
        rviz_node,
    ])