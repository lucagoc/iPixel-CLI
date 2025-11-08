#!/bin/bash

# Move to the tools directory, no matter where it is launched from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# Create a virtual environment in the project folder
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Display a confirmation message
echo "Virtual environment set up and activated."
