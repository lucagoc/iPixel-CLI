#!/usr/bin/env bash
set -euo pipefail

# Change to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

if [ -d ".venv" ]; then
    ./scripts/setup_venv.sh
    echo "Virtual environment activated."
else
    echo "No virtual environment found. Proceeding with the system Python environment."
fi

echo "==> Installing package in editable mode"
python -m pip install -e .

echo "==> Installation complete."
