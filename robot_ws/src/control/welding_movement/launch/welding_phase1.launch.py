from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory("welding_movement")
    params_file = os.path.join(pkg_share, "config", "welding_params.yaml")

    return LaunchDescription([
        Node(
            package="welding_movement",
            executable="weld_controller",
            name="weld_controller_node",
            output="screen",
            parameters=[params_file],
        )
    ])