#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# shellcheck disable=SC1091
source "$ROOT_DIR/ci/env.sh"

if [ $# -lt 1 ]; then
  echo "Usage: ci/run_in_docker.sh <command...>"
  exit 1
fi

docker compose -f "$COMPOSE_FILE" run --rm "$ROS_SERVICE" bash -lc "$*"