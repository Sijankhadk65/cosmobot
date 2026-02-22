#!/usr/bin/env bash
set -euo pipefail

# Repo root (works even if called from another directory)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Formatting Python (ruff format)..."
ruff format .

echo "==> Formatting Python imports / fixing safe issues (ruff check --fix)..."
# --fix only applies safe fixes by default; keep it as a hygiene step
ruff check . --fix

echo "==> Formatting C/C++ (clang-format)..."
if ! command -v clang-format >/dev/null 2>&1; then
  echo "ERROR: clang-format not found in PATH."
  echo "Install it in your Docker image or system, or skip C++ formatting."
  exit 1
fi

# Find C/C++ sources under robot_ws/src only (avoid build/install/log)
# Add more roots if you keep C++ outside robot_ws/src.
mapfile -t CPP_FILES < <(
  find "$ROOT_DIR/robot_ws/src" \
    -type f \( -name "*.c" -o -name "*.cc" -o -name "*.cpp" -o -name "*.cxx" -o -name "*.h" -o -name "*.hpp" \) \
    -not -path "*/build/*" -not -path "*/install/*" -not -path "*/log/*" \
    -print
)

if [ "${#CPP_FILES[@]}" -eq 0 ]; then
  echo "No C/C++ files found under robot_ws/src. Skipping clang-format."
else
  clang-format -i "${CPP_FILES[@]}"
  echo "Formatted ${#CPP_FILES[@]} C/C++ files."
fi

echo "✅ Format complete."