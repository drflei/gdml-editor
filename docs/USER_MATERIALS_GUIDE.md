# User-Defined Materials Feature Guide

## Overview

The GDML Editor now includes a comprehensive user-defined materials system that allows you to create, manage, and use custom materials in your geometry files. Materials are stored in a persistent database and can be used across multiple GDML files.

## Features

### 1. Material Database
- Materials are stored in `~/.gdml_editor/user_materials.json`
- Persistent storage across sessions
- Easy backup and sharing (just copy the JSON file)

### 2. Material Types

#### Compound Materials
Define materials using molecular formulas:
- **Example formulas**: H2O, SiO2, CaCO3, PbF2, Al2O3
- Automatically calculates element ratios from formula
- Ideal for pure chemical compounds

#### Mixture Materials
Define materials by mass fraction of elements:
- Specify each element and its mass fraction
- Fractions must sum to 1.0
- Ideal for alloys, composites, and complex mixtures

### 3. Material Properties

#### Required Properties:
- **Name**: Unique identifier for the material
- **Density**: Material density with units (g/cm³, mg/cm³, or kg/m³)
- **Composition**: Either molecular formula (compound) or element fractions (mixture)

#### Optional Properties (Hidden by Default):
- **State**: solid, liquid, or gas (default: solid)
- **Temperature**: With units (K or °C)
- **Pressure**: With units (pascal, bar, or atm)

## Usage Guide

### Creating a New Material

1. **From Menu Bar**: 
   - Go to `Materials → Define New Material...`

2. **Fill in Material Details**:
   - Enter a unique material name
   - Select material type (Compound or Mixture)
   - Enter density and select units

3. **Define Composition**:
   
   **For Compound Materials**:
   - Enter molecular formula (e.g., `H2O`, `SiO2`, `CaCO3`)
   - Formula parser automatically determines element ratios
   
   **For Mixture Materials**:
   - Add elements using "Add Element" button
   - Enter element symbol and mass fraction for each
   - Mass fractions must sum to 1.0
   - Use "Remove" button to delete element rows

4. **Optional Advanced Properties** (click checkbox to show):
   - Set state (solid/liquid/gas)
   - Specify temperature
   - Specify pressure

5. **Save**: Click "Save Material" button

### Using User Materials

1. **Open a GDML file**
2. **Select a volume** from the tree
3. **In "Change Material" section**:
   - Select "User Defined" radio button
   - Choose your material from dropdown
   - Click "Info" button to view material details
   - Click "Apply Material Change"

### Managing Materials

Access material management via `Materials → Manage User Materials...`:

- **View**: Click on any material to see its details
- **Edit**: Select a material and click "Edit Selected"
- **Delete**: Select a material and click "Delete Selected"
- **Create**: Click "New Material" to add another

## Examples

### Example 1: Water (Compound)
```
Name: Water
Type: Compound
Density: 1.0 g/cm³
Formula: H2O
State: liquid
```

### Example 2: Borosilicate Glass (Compound)
```
Name: BorosilicateGlass
Type: Compound
Density: 2.23 g/cm³
Formula: B2O3SiO2
State: solid
```

### Example 3: Stainless Steel 316 (Mixture)
```
Name: StainlessSteel316
Type: Mixture
Density: 8.0 g/cm³
Composition:
  Fe: 0.68
  Cr: 0.17
  Ni: 0.12
  Mo: 0.03
State: solid
```

### Example 4: Custom Scintillator (Mixture)
```
Name: CustomScintillator
Type: Mixture
Density: 1.032 g/cm³
Composition:
  H: 0.0854
  C: 0.9146
State: solid
Temperature: 293.15 K
Pressure: 101325 pascal
```

### Example 5: Lead Fluoride Crystal (Compound)
```
Name: LeadFluoride
Type: Compound
Density: 7.77 g/cm³
Formula: PbF2
State: solid
```

## Technical Details

### Formula Parsing
Compound formulas are parsed to extract elements and their stoichiometric ratios:
- Element symbols are case-sensitive (H, He, Li, etc.)
- Numbers follow element symbols (H2O → 2 hydrogen, 1 oxygen)
- Parentheses are supported for complex formulas

### Unit Conversions
The system automatically converts units to Geant4/GDML standards:
- **Density**: All units converted to g/cm³
- **Temperature**: Celsius converted to Kelvin
- **Pressure**: bar and atm converted to pascal

### Material Creation
When applying a user material to a volume:
1. System checks if material exists in registry
2. If not, creates material using pyg4ometry
3. For compounds: Uses `MaterialCompound` class
4. For mixtures: Uses `Material` class with element mass fractions
5. Material is added to registry and becomes available

### Database Format
Materials are stored in JSON format at `~/.gdml_editor/user_materials.json`:
```json
{
  "MaterialName": {
    "type": "compound",
    "density": 2.5,
    "density_unit": "g/cm3",
    "composition": "SiO2",
    "state": "solid"
  }
}
```

## Tips and Best Practices

1. **Naming Convention**: Use descriptive names without spaces
2. **Backup Database**: Regularly backup `~/.gdml_editor/user_materials.json`
3. **Share Materials**: Copy the JSON file to share materials with colleagues
4. **Verify Formulas**: Double-check molecular formulas for accuracy
5. **Mass Fractions**: Ensure mixture fractions sum to exactly 1.0
6. **Element Symbols**: Use correct element symbols (case-sensitive)
7. **Density Units**: Match units to your source data for accuracy

## Troubleshooting

### Material Not Created
- Check formula syntax for compounds
- Verify element symbols are correct
- Ensure mass fractions sum to 1.0 for mixtures

### Element Not Found
- Use standard element symbols (H, He, Li, C, N, O, etc.)
- Check for typos in element names
- Ensure elements exist in NIST database

### Density Issues
- Verify density value is positive
- Check unit selection matches your data
- Consider material state when specifying density

## Integration with GDML

User materials are fully integrated with the GDML workflow:
1. Materials are created in the pyg4ometry registry
2. Can be assigned to any logical volume
3. Saved with geometry when exporting GDML
4. Materials persist in the GDML file for later use

## Future Enhancements

Potential future additions:
- Import materials from external databases
- Export material definitions
- Optical properties support
- Material templates library
- Batch material creation
