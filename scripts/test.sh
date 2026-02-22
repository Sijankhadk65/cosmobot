#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/robot_ws"

echo "==> Running colcon build..."
colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

echo "==> Running colcon test..."
colcon test

echo "==> Showing test results..."
colcon test-result --verbose

echo "✅ Tests complete."