#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

CONTAINER_NAME="my_robot_ros"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "ERROR: Container '${CONTAINER_NAME}' is not running."
  echo "Start it with: docker compose -f docker/docker-compose.yml up -d"
  exit 1
fi

# Default to bash if no args given
if [ $# -eq 0 ]; then
  docker exec -it "$CONTAINER_NAME" bash
else
  docker exec -it "$CONTAINER_NAME" bash -lc "$*"
fi