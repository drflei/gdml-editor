# GDML Editor

A professional GUI application for editing GDML (Geometry Description Markup Language) files with advanced user-defined materials support.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pyg4ometry](https://img.shields.io/badge/pyg4ometry-1.0+-green.svg)](https://github.com/g4edge/pyg4ometry)

## Features

### 🎯 Core Functionality
- **Visual GDML Editing**: Browse and modify GDML geometry files with an intuitive GUI
- **Material Management**: Change materials on logical volumes with ease
- **VTK Visualization**: Integrated 3D geometry viewer
- **NIST Database**: Access to 400+ Geant4/NIST materials
- **Save/Load**: Read and write GDML files seamlessly

### 🔬 User-Defined Materials
- **Compound Materials**: Define materials using molecular formulas (H2O, SiO2, PbF2, etc.)
- **Mixture Materials**: Create materials by element mass fractions
- **Persistent Database**: Materials saved in JSON database for reuse
- **Element Dropdown**: Select from all 118 periodic table elements
- **Type-Ahead Filtering**: Quick element search with autocomplete
- **Advanced Properties**: Optional state, temperature, and pressure settings
- **Material Manager**: Edit, delete, and organize custom materials

### 🚀 Professional Features
- **pyg4ometry Integration**: Leverages native pyg4ometry features
- **Unit Conversions**: Automatic handling of density, temperature, pressure units
- **Error Prevention**: Validation and helpful error messages
- **Material Search**: Filter volumes and materials quickly
- **Batch Operations**: Efficient multi-material workflows

## Installation

### From PyPI (Recommended)

```bash
pip install gdml-editor
```

### From Source

```bash
git clone https://github.com/yourusername/gdml-editor.git
cd gdml-editor
pip install -e .
```

### Requirements

- Python 3.8+
- pyg4ometry >= 1.0.0
- VTK >= 9.0.0

## Quick Start

### Launch the GUI

```bash
gdml-editor
```

Or from Python:

```python
from gdml_editor.gui import main
main()
```

### Basic Workflow

1. **Open GDML File**: File → Open GDML...
2. **Select Volume**: Click on volume in the tree
3. **Change Material**: 
   - Choose source (Existing/NIST/User-defined)
   - Select material
   - Click "Apply Material Change"
4. **Save**: File → Save or Save As...

## User-Defined Materials

### Creating a Compound Material

**Example: Lead Fluoride Crystal**

```
1. Materials → Define New Material
2. Name: LeadFluoride
3. Type: Compound (Formula)
4. Density: 7.77 g/cm³
5. Formula: PbF2
6. Click "Save Material"
```

### Creating a Mixture Material

**Example: Stainless Steel 316**

```
1. Materials → Define New Material
2. Name: StainlessSteel316
3. Type: Mixture (Elements)
4. Density: 8.0 g/cm³
5. Add elements:
   - Fe: 0.68
   - Cr: 0.17
   - Ni: 0.12
   - Mo: 0.03
6. Click "Save Material"
```

### Element Selection

The element dropdown provides:
- All 118 periodic table elements
- Type-ahead filtering (type "Fe" to find Iron)
- Common elements quick reference
- Error prevention (no typos)

## Material Database

Materials are stored in `~/.gdml_editor/user_materials.json` and persist across sessions.

**Manage Materials:**
- Materials → Manage User Materials
- View, edit, or delete existing materials
- Export/import by copying JSON file

## Documentation

- [User Materials Guide](docs/USER_MATERIALS_GUIDE.md)
- [Element Dropdown Guide](docs/ELEMENT_DROPDOWN_GUIDE.md)
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)
- [Refactoring Summary](docs/REFACTORING_SUMMARY.md)
- [Code Comparison](docs/CODE_COMPARISON.md)

## Examples

### Compound Materials

```python
from gdml_editor import UserMaterialDatabase

db = UserMaterialDatabase()

# Water
db.add_material('Water', {
    'type': 'compound',
    'density': 1.0,
    'density_unit': 'g/cm3',
    'composition': 'H2O',
    'state': 'liquid',
    'temperature': 293.15,
    'temp_unit': 'K'
})

# Silicon Dioxide
db.add_material('SiliconDioxide', {
    'type': 'compound',
    'density': 2.65,
    'density_unit': 'g/cm3',
    'composition': 'SiO2',
    'state': 'solid'
})
```

### Mixture Materials

```python
# Brass
db.add_material('Brass', {
    'type': 'mixture',
    'density': 8.4,
    'density_unit': 'g/cm3',
    'composition': [
        {'element': 'Cu', 'fraction': 0.65},
        {'element': 'Zn', 'fraction': 0.35}
    ],
    'state': 'solid'
})
```

## Architecture

### pyg4ometry-First Design

The application is built on pyg4ometry's native features:
- Uses `MaterialCompound` for chemical formulas
- Uses `Material.add_element_massfraction()` for mixtures
- Leverages NIST element database
- Follows Geant4 unit conventions

### Modular Code Structure

- **Helper Methods**: Unit conversions, element management
- **Single Responsibility**: Each method has one clear purpose
- **Clean Code**: 40% reduction in code complexity
- **Testable**: Isolated functions for easy testing

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/gdml-editor.git
cd gdml-editor
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black gdml_editor/

# Lint
flake8 gdml_editor/

# Type check
mypy gdml_editor/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Material import/export (CSV, XML)
- [ ] Material templates library
- [ ] Optical properties support
- [ ] Batch material operations
- [ ] Element tooltips with properties
- [ ] Recently used materials
- [ ] Material comparison tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use GDML Editor in your research, please cite:

```bibtex
@software{gdml_editor,
  title = {GDML Editor: GUI for GDML Geometry Files},
  author = {GDML Editor Contributors},
  year = {2026},
  url = {https://github.com/yourusername/gdml-editor}
}
```

## Acknowledgments

- Built on [pyg4ometry](https://github.com/g4edge/pyg4ometry) by the Geant4 community
- Uses [VTK](https://vtk.org/) for 3D visualization
- Inspired by the needs of particle physics detector design

## Support

- 📫 Issues: [GitHub Issues](https://github.com/yourusername/gdml-editor/issues)
- 📖 Documentation: [Wiki](https://github.com/yourusername/gdml-editor/wiki)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/gdml-editor/discussions)

## Screenshots

### Main Interface
![Main Interface](docs/screenshots/main_interface.png)

### Material Definition
![Material Definition](docs/screenshots/material_definition.png)

### Element Dropdown
![Element Dropdown](docs/screenshots/element_dropdown.png)

---

**Made with ❤️ for the particle physics community**
