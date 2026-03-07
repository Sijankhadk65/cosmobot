import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Launch configuration variables
    is_sim = LaunchConfiguration("is_sim")
    robot_name = LaunchConfiguration("robot_name")
    use_camera = LaunchConfiguration("use_camera")

    # Declare launch arguments
    is_sim_arg = DeclareLaunchArgument(
        "is_sim",
        default_value="True"
    )
    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="so101_arm"
    )

    use_camera_arg = DeclareLaunchArgument(
        name='use_camera',
        default_value='true',
        description='Flag to enable the RGBD camera for Gazebo point cloud simulation'
    )

    robot_description = ParameterValue(
        Command(
            [
                "xacro ",
                os.path.join(
                    get_package_share_directory("so_arm_description"),
                    "urdf",
                    "so101.urdf.xacro",
                ),
                " robot_name:=",
                robot_name,
                " use_camera:=",
                use_camera,
                " use_gazebo:=true"
            ]
        ),
        value_type=str,
    )

    # Declare argument for world file
    default_world = os.path.join(
        get_package_share_directory('gazebo_world'),
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


    # Bridge parameters file
    bridge_params = os.path.join(get_package_share_directory('gazebo_world'), 'config', 'ros_gz_bridge.yml')

    # ROS-Gazebo bridge
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '--log-level', 'parameter_bridge:=debug',
            '-p',
            f'config_file:={bridge_params}',
        ],
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


    # Nodes
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
        }],
        output='screen'
    )

    # Spawn the robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', robot_name,
            '-allow_renaming', 'true',
            '-z', '0.0'  # Lift the robot slightly above ground
        ],
        output='screen'
    )
    # Set use_sim_time flag
    set_use_sim_time = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="set_use_sim_time",
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription([
        # Launch arguments
        is_sim_arg,
        robot_name_arg,
        world_arg,
        use_camera_arg,
        
        # Launch Gazebo and bridges
        gazebo,
        ros_gz_bridge,
        ros_gz_image_bridge,
        
        # Nodes
        robot_state_publisher_node,
        spawn_entity,
        set_use_sim_time,
    ])