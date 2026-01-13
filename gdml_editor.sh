#!/bin/bash
# Launch GDML Editor GUI application
# Stays in current working directory and starts the GUI

# Optionally activate virtual environment if it exists
if [ -f ~/.venv/bin/activate ]; then
    source ~/.venv/bin/activate
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run gdml_editor by adding its parent directory to PYTHONPATH
PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH" python -m gdml_editor "$@"

