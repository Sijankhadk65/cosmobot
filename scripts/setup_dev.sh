#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Checking Docker..."
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker not found. Install Docker first."
  exit 1
fi

echo "==> Checking Conda..."
if ! command -v conda >/dev/null 2>&1; then
  echo "WARNING: Conda not found."
  echo "Install Miniconda/Anaconda if you want local Python tooling."
else
  echo "==> Creating/updating Conda environment..."
  conda env update -f env/conda/environment.yml --prune || true
fi

echo "==> Installing Python dev tools (ruff, black, mypy)..."
if command -v pip >/dev/null 2>&1; then
  pip install -r env/requirements/dev.txt || true
fi

echo "==> Setup complete."
echo ""
echo "Next steps:"
echo "1. Build Docker image:"
echo "   docker compose build"
echo ""
echo "2. Build ROS workspace inside container:"
echo "   docker compose run ros bash"
echo "   colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
echo ""
echo "3. Run format:"
echo "   ./scripts/format.sh"