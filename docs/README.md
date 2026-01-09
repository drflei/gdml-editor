# GDML Editor Application

A GUI application for editing GDML geometry files with Geant4 materials.

## Installation

The application is located in `~/gdml_editor/` and uses the Python virtual environment at `~/.venv/`.

## Files

- `gdml_editor_gui.py` - Main GUI application
- `run_vtkviewer.py` - Command-line VTK viewer with material editing
- `view_gdml.py` - GDML file viewer and converter
- `launch_gui.sh` - Launcher script for the GUI

## Usage

### GUI Application

```bash
cd ~/gdml_editor
source ~/.venv/bin/activate
python gdml_editor_gui.py
```

Or use the launcher:
```bash
~/gdml_editor/launch_gui.sh
```

### Command-Line Tools

**VTK Viewer with Material Editing:**
```bash
cd ~/gdml_editor
source ~/.venv/bin/activate

# View GDML file
python run_vtkviewer.py file.gdml

# List volumes and materials
python run_vtkviewer.py file.gdml --list-volumes
python run_vtkviewer.py file.gdml --list-materials

# Change materials
python run_vtkviewer.py file.gdml --change-material PbF2_Radiator G4_WATER

# Multiple changes and save
python run_vtkviewer.py file.gdml \
  --change-material Volume1 G4_WATER \
  --change-material Volume2 G4_Al \
  --save modified.gdml
```

**GDML Viewer/Converter:**
```bash
# Export to VRML
python view_gdml.py file.gdml --format wrl

# Export to other formats
python view_gdml.py file.gdml --format obj
python view_gdml.py file.gdml --format stl

# Try interactive viewer (may not work in WSL)
python view_gdml.py file.gdml --interactive
```

## Features

### GUI Application

- **Open and save GDML files**
- **Browse logical volumes** with search/filter
- **View volume properties** (type, material, solid info)
- **Change materials** using:
  - Existing materials in the GDML
  - 250+ Geant4 built-in materials (searchable dropdown)
- **Interactive VTK viewer** integration
- **Real-time updates** of volume tree display

### Supported Materials

The application includes 250+ Geant4 materials:
- All NIST elements (H to Cf)
- Plastics, polymers, rubbers
- Scintillators and crystals
- Biological tissues and organs
- Gases (compressed and liquid)
- Metals, oxides, compounds
- And many more...

## Requirements

- Python 3.12+
- pyg4ometry
- vtk
- tkinter (system package)

The virtual environment at `~/.venv/` should already have these installed.

## Known Issues

### sys.modules RuntimeWarning

Fixed: The application clears cached VtkViewer modules from sys.modules before importing to avoid the frozen runpy RuntimeWarning.

### Interactive VTK Viewing in WSL

The interactive VTK viewer requires an X server on Windows (VcXsrv, X410, etc.). If the interactive viewer doesn't work:
- Use the export formats (VRML, OBJ, STL) instead
- Or view files using external tools

## Developer Notes

The application fixes the `python -m pyg4ometry.visualisation.VtkViewer` RuntimeWarning by clearing sys.modules before import. See the code comments in each file for details.
