#!/bin/bash

# Ensure the virtual environment is activated if exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Move to the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the CLI with all passed arguments
python3 "$SCRIPT_DIR/src/pypixel_color_lucagoc/pypixel-cli.py" "$@"
