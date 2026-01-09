# GDML Editor - Quick Start Guide

## Installation

### From PyPI (once published)
```bash
pip install gdml-editor
```

### From Source
```bash
git clone https://github.com/drflei/gdml-editor.git
cd gdml-editor
pip install -e .
```

## Running the Editor

After installation, you can launch the editor in three ways:

### Method 1: Command Line (Recommended after pip install)
```bash
gdml-editor
```

### Method 2: Python Module
```bash
python -m gdml_editor.gui
```

### Method 3: Launch Script (Development)
```bash
./launch_gui.sh
```

## Quick Tutorial

### 1. Opening a GDML File
- Click **File → Open** or press `Ctrl+O`
- Navigate to your GDML file and select it
- The geometry tree will populate on the left

### 2. Viewing 3D Geometry
- Click **View → Show 3D View** or press `Ctrl+D`
- Use mouse to rotate, zoom, and pan
- Right-click for view options

### 3. Editing Materials

#### Using Built-in NIST Materials
1. Select a volume in the tree
2. Right-click → **Change Material**
3. Browse NIST materials (e.g., G4_WATER, G4_Al)
4. Click **Apply**

#### Creating Custom Materials
1. Click **Materials → User Materials** or press `Ctrl+M`
2. Click **Add New Material**
3. Fill in the material properties:
   - **Name**: e.g., "MyCustomAlloy"
   - **Density**: e.g., "2.7" (g/cm³)
   - **Type**: Choose "Compound" or "Mixture"
   - **State**: Solid, Liquid, or Gas
   - **Elements**: Click "Add Element"
     - Select from dropdown (118 elements available)
     - Use type-ahead: type "Al" to filter to Aluminum
     - Enter composition (atoms for compound, fraction for mixture)
4. Click **OK** to save

### 4. Managing User Materials
- **View All**: Click "View Details" in the material list
- **Edit**: Select material → click "Edit"
- **Delete**: Select material → click "Delete"
- **Apply to Volume**: Select volume, right-click → change to user material

### 5. Editing Geometry

#### Moving Volumes
1. Select a volume in the tree
2. Right-click → **Edit Position**
3. Modify X, Y, Z coordinates
4. Click **Apply**

#### Changing Dimensions
1. Select a volume
2. Right-click → **Edit Dimensions**
3. Modify size parameters
4. Click **Apply**

### 6. Saving Changes
- Click **File → Save** or press `Ctrl+S`
- Overwrites the original file
- Or **File → Save As** to save to a new location

## Common Element Symbols Quick Reference

| Element | Symbol | Z | Common Use |
|---------|--------|---|------------|
| Hydrogen | H | 1 | Water, organic materials |
| Carbon | C | 6 | Organic materials, plastics |
| Nitrogen | N | 7 | Air, organic materials |
| Oxygen | O | 8 | Water, air, oxides |
| Aluminum | Al | 13 | Metal structures |
| Silicon | Si | 14 | Electronics, glass |
| Iron | Fe | 26 | Steel, structures |
| Copper | Cu | 29 | Electronics, alloys |
| Lead | Pb | 82 | Shielding |

## Material Definition Examples

### Example 1: Water (Compound)
- **Name**: Water
- **Density**: 1.0 g/cm³
- **Type**: Compound
- **Elements**:
  - H (Hydrogen): 2 atoms
  - O (Oxygen): 1 atom

### Example 2: Air (Mixture by mass fraction)
- **Name**: Air
- **Density**: 0.001205 g/cm³
- **Type**: Mixture
- **Elements**:
  - N (Nitrogen): 0.7494 (74.94%)
  - O (Oxygen): 0.2369 (23.69%)
  - Ar (Argon): 0.0128 (1.28%)
  - C (Carbon): 0.0006 (0.06%)

### Example 3: Brass (Mixture by mass fraction)
- **Name**: Brass
- **Density**: 8.5 g/cm³
- **Type**: Mixture
- **State**: Solid
- **Elements**:
  - Cu (Copper): 0.70 (70%)
  - Zn (Zinc): 0.30 (30%)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open GDML file |
| Ctrl+S | Save GDML file |
| Ctrl+D | Show 3D view |
| Ctrl+M | User materials dialog |
| Ctrl+F | Find in tree |
| Ctrl+Q | Quit |

## Troubleshooting

### Issue: "Cannot import pyg4ometry"
**Solution**: Install dependencies
```bash
pip install pyg4ometry vtk
```

### Issue: "X11 connection error" (Linux)
**Solution**: Ensure X server is running or use headless mode

### Issue: "Material not found in registry"
**Solution**: 
1. Check material name spelling
2. For user materials, ensure they're defined before use
3. Try using NIST material names (prefix with G4_)

### Issue: "Invalid GDML file"
**Solution**: Validate your GDML file format:
```python
import pyg4ometry
reg = pyg4ometry.geant4.Registry()
reader = pyg4ometry.gdml.Reader(reg)
reader.read("yourfile.gdml")
```

## Advanced Usage

### Scripting with Python API
```python
from gdml_editor import GDMLEditorApp, UserMaterialDatabase

# Load user materials
db = UserMaterialDatabase()
materials = db.load_materials()

# Create custom material programmatically
material = {
    "name": "ScriptedMaterial",
    "density": 2.5,
    "density_unit": "g/cm3",
    "type": "compound",
    "elements": [
        {"symbol": "Si", "composition": 1},
        {"symbol": "O", "composition": 2}
    ],
    "state": "solid"
}
db.save_material("ScriptedMaterial", material)
```

## Getting Help

- **Documentation**: See `docs/` folder for detailed guides
- **Issues**: Report bugs on GitHub Issues
- **Contributing**: See CONTRIBUTING.md

## Links

- **GitHub**: https://github.com/drflei/gdml-editor
- **PyPI**: https://pypi.org/project/gdml-editor/
- **pyg4ometry**: https://github.com/stewartboogert/pyg4ometry
- **Geant4**: https://geant4.web.cern.ch/

---

**Happy Geometry Editing! 🎯**
