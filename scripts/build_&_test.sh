#!/bin/bash

# Move to the tools directory, no matter where it is launched from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Build the project (example command, modify as needed)
echo "🔧 Building..."
./build.sh

# Deploy the project (example command, modify as needed)
echo "🎢 Deploying locally..."
pip install ../dist/pypixelcolor-1.0.0-py3-none-any.whl --force-reinstall
