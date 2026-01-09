#!/bin/bash
# Launch GDML Editor GUI application
# Activates the Python virtual environment and starts the GUI

source ~/.venv/bin/activate
cd ~/gdml_editor
python -m gdml_editor.gui "$@"

