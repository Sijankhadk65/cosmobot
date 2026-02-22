#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# shellcheck disable=SC1091
source "$ROOT_DIR/ci/env.sh"

echo "==> Build + Test (inside Docker)"
"$ROOT_DIR/ci/run_in_docker.sh" "
  set -euo pipefail
  cd $ROS_WS
  colcon build $COLCON_BUILD_ARGS
  colcon test
  colcon test-result --verbose
"