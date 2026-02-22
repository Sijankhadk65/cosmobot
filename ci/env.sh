#!/usr/bin/env bash
set -euo pipefail

# Workspace inside repo
export ROS_WS="robot_ws"

# docker-compose file path
export COMPOSE_FILE="docker/docker-compose.yml"

# docker-compose service that contains ROS2 + build tools
# (adjust if your service is named differently)
export ROS_SERVICE="ros"

# Default colcon args
export COLCON_BUILD_ARGS="--cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"