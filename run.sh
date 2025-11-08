#!/bin/bash

# Ensure the virtual environment is activated if exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Move to the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add src/ to PYTHONPATH only if not already present
case ":$PYTHONPATH:" in
  *":$SCRIPT_DIR/src:"*) ;;
  *) export PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" ;;
esac

# Run the package as a module so relative imports work
exec python3 -m pypixelcolor "$@"
