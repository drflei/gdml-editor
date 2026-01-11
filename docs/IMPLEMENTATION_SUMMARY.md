# User-Defined Materials Feature - Implementation Summary

## Feature Overview

A comprehensive user-defined materials system has been added to the GDML Editor GUI, enabling users to create, manage, and apply custom materials to geometry volumes.

## Implementation Components

### 1. UserMaterialDatabase Class
**Location**: In gdml_editor/gui.py

**Features**:
- JSON-based persistent storage at `~/.gdml_editor/user_materials.json`
- CRUD operations: add, remove, get, list materials
- Automatic file management with directory creation
- Thread-safe save/load operations

**Methods**:
- `load()`: Load materials from JSON file
- `save()`: Save materials to JSON file
- `add_material(name, material_data)`: Add or update material
- `remove_material(name)`: Delete material
- `get_material(name)`: Retrieve material data
- `list_materials()`: Get sorted list of material names
- `get_all_materials()`: Get complete materials dictionary

### 2. MaterialDefinitionDialog Class
**Location**: In gdml_editor/gui.py

**Features**:
- Modal dialog for creating/editing materials
- Support for both compound and mixture types
- Dynamic UI that adapts to material type
- Form validation with helpful error messages
- Optional advanced properties (collapsible section)

**Material Types**:

**A. Compound Materials**:
- Define using molecular formula (e.g., H2O, SiO2, PbF2)
- Single text entry for formula
- Examples provided in UI
- Automatically parsed by pyg4ometry

**B. Mixture Materials**:
- Define by mass fraction of elements
- Dynamic element rows (add/remove)
- Validation: fractions must sum to 1.0
- Scrollable list for many elements

**Properties**:
- **Required**: Name, Density (with units), Composition
- **Optional**: State, Temperature, Pressure (hidden by default)
- **Units Supported**:
  - Density: g/cm³, mg/cm³, kg/m³
  - Temperature: K, °C
  - Pressure: pascal, bar, atm

### 3. MaterialManagementDialog Class
**Location**: In gdml_editor/gui.py

**Features**:
- View all user-defined materials in a list
- Display detailed material information
- Edit existing materials (opens MaterialDefinitionDialog)
- Delete materials with confirmation
- Create new materials
- Real-time list updates

### 4. Main Application Integration

**Menu Integration**:
- New "Materials" menu added to menu bar
- "Define New Material..." command
- "Manage User Materials..." command

**Material Selection UI**:
- Volume Properties panel contains a single **Material** dropdown
- Dropdown values are a combined list of:
  - materials already present in the loaded registry
  - all Geant4/NIST `G4_...` material names (created on demand)
  - user materials from `~/.gdml_editor/user_materials.json`

**Material Application**:
- Uses `apply_selected_material()` in the main app
- Material creation/lookup is centralized in `_ensure_material_in_registry()`
- Supports user-defined + existing + Geant4/NIST materials
- Performs unit conversions for Geant4 compatibility when creating user materials

### 5. Material Creation in Registry
**Method**: `create_user_material_in_registry(mat_name, mat_data)`

**Features**:
- Converts user-defined materials to pyg4ometry objects
- Handles unit conversions:
  - Density → g/cm³
  - Temperature → Kelvin
  - Pressure → pascal
- Creates appropriate material type:
  - `MaterialCompound` for compounds
  - `Material` with element fractions for mixtures
- Integrates with NIST element database
- Sets optional properties (temperature, pressure, state)

## Key Technical Details

### Database Format
```json
{
  "MaterialName": {
    "type": "compound" | "mixture",
    "density": float,
    "density_unit": "g/cm3" | "mg/cm3" | "kg/m3",
    "composition": string (compound) | array (mixture),
    "state": "solid" | "liquid" | "gas",
    "temperature": float (optional),
    "temp_unit": "K" | "C" (optional),
    "pressure": float (optional),
    "pressure_unit": "pascal" | "bar" | "atm" (optional)
  }
}
```

### Mixture Composition Format
```json
"composition": [
  {"element": "Fe", "fraction": 0.68},
  {"element": "Cr", "fraction": 0.17},
  {"element": "Ni", "fraction": 0.12},
  {"element": "Mo", "fraction": 0.03}
]
```

### Validation Rules
1. **Name**: Must be non-empty, unique
2. **Density**: Must be positive number
3. **Compound Formula**: Must be non-empty string
4. **Mixture Elements**: 
   - At least one element required
   - Each element must have name and fraction
   - Fractions must be between 0 and 1
   - Total fractions must sum to 1.0 (±0.001 tolerance)
5. **Temperature/Pressure**: If provided, must be valid numbers

## User Workflow

### Creating a Material
1. Materials → Define New Material...
2. Enter name and select type (Compound/Mixture)
3. Enter density with units
4. Define composition:
   - Compound: Enter formula (e.g., H2O)
   - Mixture: Add elements with fractions
5. Optionally set advanced properties
6. Click "Save Material"

### Using a Material
1. Open GDML file
2. Select volume from tree
3. In the Volume Properties panel, select a material from the dropdown
4. Click Apply
5. If the material does not exist in the registry yet (e.g. a `G4_...` NIST material), it is created on demand and then applied

### Managing Materials
1. Materials → Manage User Materials...
2. Select material from list to view details
3. Edit, delete, or create new materials
4. Changes persist in database

## Integration with pyg4ometry

Materials are seamlessly integrated with pyg4ometry:
- Created as proper `Material` or `MaterialCompound` objects
- Added to registry's `materialDict`
- Available for assignment to logical volumes
- Saved in GDML file when exported
- Compatible with Geant4 simulation

## Benefits

1. **Persistence**: Materials stored in database, reusable across projects
2. **Flexibility**: Support for both compounds and mixtures
3. **User-Friendly**: Intuitive GUI with validation and error checking
4. **Standards Compliant**: Proper Geant4/GDML format and units
5. **Extensible**: Easy to add more properties or material types
6. **Portable**: Database is simple JSON file, easy to backup/share

## Files Modified

- **gdml_editor/gui.py**: Main application module with all GUI classes and methods
- **USER_MATERIALS_GUIDE.md**: Comprehensive user documentation
- **test_user_materials.py**: Test script demonstrating database functionality

## Testing

Run `test_user_materials.py` to verify database operations:
- Create compound and mixture materials
- List and retrieve materials
- Update existing materials
- Delete materials
- Verify persistence

## Future Enhancements

Potential additions:
- Material import/export (CSV, XML)
- Material library templates
- Optical properties support
- Isotope-specific compositions
- Material validation against NIST database
- Material comparison tools
- Batch material operations
