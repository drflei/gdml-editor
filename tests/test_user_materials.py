#!/usr/bin/env python3
"""Test script for user-defined materials feature."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gdml_editor_gui import UserMaterialDatabase

def test_material_database():
    """Test the material database functionality."""
    
    print("=" * 60)
    print("Testing User Material Database")
    print("=" * 60)
    
    # Create a test database in current directory
    db = UserMaterialDatabase("test_materials.json")
    
    # Test 1: Add a compound material (Water)
    print("\n1. Adding compound material: Water")
    water_data = {
        'type': 'compound',
        'density': 1.0,
        'density_unit': 'g/cm3',
        'composition': 'H2O',
        'state': 'liquid',
        'temperature': 293.15,
        'temp_unit': 'K'
    }
    db.add_material('Water', water_data)
    print("   ✓ Water added successfully")
    
    # Test 2: Add a mixture material (Stainless Steel)
    print("\n2. Adding mixture material: Stainless Steel 316")
    steel_data = {
        'type': 'mixture',
        'density': 8.0,
        'density_unit': 'g/cm3',
        'composition': [
            {'element': 'Fe', 'fraction': 0.68},
            {'element': 'Cr', 'fraction': 0.17},
            {'element': 'Ni', 'fraction': 0.12},
            {'element': 'Mo', 'fraction': 0.03}
        ],
        'state': 'solid'
    }
    db.add_material('StainlessSteel316', steel_data)
    print("   ✓ Stainless Steel 316 added successfully")
    
    # Test 3: Add compound material (Lead Fluoride)
    print("\n3. Adding compound material: Lead Fluoride")
    pbf2_data = {
        'type': 'compound',
        'density': 7.77,
        'density_unit': 'g/cm3',
        'composition': 'PbF2',
        'state': 'solid'
    }
    db.add_material('LeadFluoride', pbf2_data)
    print("   ✓ Lead Fluoride added successfully")
    
    # Test 4: Add compound material (Silicon Dioxide)
    print("\n4. Adding compound material: Silicon Dioxide")
    sio2_data = {
        'type': 'compound',
        'density': 2.65,
        'density_unit': 'g/cm3',
        'composition': 'SiO2',
        'state': 'solid'
    }
    db.add_material('SiliconDioxide', sio2_data)
    print("   ✓ Silicon Dioxide added successfully")
    
    # Test 5: List all materials
    print("\n5. Listing all materials:")
    materials = db.list_materials()
    for mat in materials:
        print(f"   - {mat}")
    
    # Test 6: Retrieve and display material details
    print("\n6. Material details:")
    for mat_name in materials:
        mat_data = db.get_material(mat_name)
        print(f"\n   {mat_name}:")
        print(f"      Type: {mat_data['type']}")
        print(f"      Density: {mat_data['density']} {mat_data['density_unit']}")
        if mat_data['type'] == 'compound':
            print(f"      Formula: {mat_data['composition']}")
        else:
            print(f"      Composition:")
            for comp in mat_data['composition']:
                print(f"         {comp['element']}: {comp['fraction']}")
    
    # Test 7: Update a material
    print("\n7. Updating Water temperature to 300K")
    water_data['temperature'] = 300.0
    db.add_material('Water', water_data)
    updated = db.get_material('Water')
    print(f"   ✓ Updated temperature: {updated['temperature']} K")
    
    # Test 8: Remove a material
    print("\n8. Removing SiliconDioxide")
    db.remove_material('SiliconDioxide')
    print(f"   ✓ Removed. Remaining materials: {db.list_materials()}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print(f"Database saved to: {db.db_file}")
    print("=" * 60)

if __name__ == "__main__":
    test_material_database()
