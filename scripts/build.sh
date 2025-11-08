#!/bin/bash

# Move to the tools directory, no matter where it is launched from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# Build the project (example command, modify as needed)
echo "Building the project..."

# Install tools
pip install build

# Run the build command
python3 -m build
