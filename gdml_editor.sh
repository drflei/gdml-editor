#!/bin/bash
# Launch GDML Editor GUI application
# Stays in current working directory and starts the GUI

# Optionally activate virtual environment if it exists
if [ -f ~/.venv/bin/activate ]; then
    source ~/.venv/bin/activate
fi

# Run gdml_editor from current directory
python -m gdml_editor "$@"

