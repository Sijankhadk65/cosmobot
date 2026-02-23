#!/usr/bin/env bash
set -e

# Source ROS
if [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
fi

# Source overlay if present
if [ -f "/workspace/robot_ws/install/setup.bash" ]; then
  source "/workspace/robot_ws/install/setup.bash"
fi

exec "$@"