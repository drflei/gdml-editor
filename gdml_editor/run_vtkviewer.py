#!/usr/bin/env python3
"""Wrapper to run pyg4ometry VtkViewer without sys.modules conflicts.

ISSUE:
Running `python -m pyg4ometry.visualisation.VtkViewer` causes a RuntimeWarning:
  "RuntimeWarning: 'pyg4ometry.visualisation.VtkViewer' found in sys.modules 
   after import of package 'pyg4ometry.visualisation', but prior to execution 
   of 'pyg4ometry.visualisation.VtkViewer'; this may result in unpredictable 
   behaviour"

ROOT CAUSE:
The VtkViewer module gets cached in sys.modules during the package import,
creating a "frozen" module reference. When runpy tries to execute it as a
script, it finds the cached module already in sys.modules, triggering the warning.

FIX:
Clear the cached VtkViewer modules from sys.modules BEFORE importing, ensuring
a fresh import without the frozen module conflict.

INTERACTIVE EDITING:
Supports changing materials and properties before visualization.

USAGE:
  python run_vtkviewer.py <gdml_file> [options]
  
OPTIONS:
  --list-volumes          List all logical volumes and their materials
  --list-materials        List all materials in the registry
  --change-material VOLUME MATERIAL   Change material of a logical volume
  
EXAMPLES:
  # View GDML file
  python run_vtkviewer.py HEPI-PbF2.gdml
  
  # List all volumes and materials
  python run_vtkviewer.py HEPI-PbF2.gdml --list-volumes
  python run_vtkviewer.py HEPI-PbF2.gdml --list-materials
  
  # Change material and view
  python run_vtkviewer.py HEPI-PbF2.gdml --change-material lv_radiator G4_WATER
"""

import sys
import os
import argparse

# FIX: Clear any cached VtkViewer modules that cause the frozen runpy warning
# This must happen before any pyg4ometry imports
modules_to_clear = [k for k in sys.modules.keys() if 'VtkViewer' in k]
for mod in modules_to_clear:
    del sys.modules[mod]

# Ensure DISPLAY is set for X11 (hardware acceleration)
os.environ["DISPLAY"] = ":0"


def list_volumes(reg):
    """List all logical volumes and their materials."""
    print("\nLogical Volumes:")
    print("-" * 80)
    print(f"{'Volume Name':<40} {'Material':<30}")
    print("-" * 80)
    for name, lv in reg.logicalVolumeDict.items():
        if hasattr(lv, 'material'):
            mat_name = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
        else:
            mat_name = "(Assembly - no material)"
        print(f"{name:<40} {mat_name:<30}")
    print("-" * 80)


def list_materials(reg):
    """List all materials in the registry."""
    print("\nMaterials:")
    print("-" * 80)
    for name, mat in reg.materialDict.items():
        print(f"  {name}")
    print("-" * 80)


def change_material(reg, volume_name, material_name):
    """Change the material of a logical volume."""
    # Find the logical volume
    if volume_name not in reg.logicalVolumeDict:
        print(f"Error: Volume '{volume_name}' not found")
        print("\nAvailable volumes:")
        for name in reg.logicalVolumeDict.keys():
            print(f"  {name}")
        return False
    
    lv = reg.logicalVolumeDict[volume_name]
    
    # Check if it's an assembly (no material)
    if not hasattr(lv, 'material'):
        print(f"Error: '{volume_name}' is an assembly volume and has no material")
        return False
    
    # Find or create the material
    if material_name not in reg.materialDict:
        # Try to create as a NIST material
        try:
            import pyg4ometry
            # Use pyg4ometry's NIST material database
            new_material = pyg4ometry.geant4.nist_material_2geant4Material(
                material_name, reg
            )
            print(f"Created NIST material: {material_name}")
        except Exception as e:
            print(f"Error: Material '{material_name}' not found and cannot create as NIST material")
            print(f"Error details: {e}")
            print("\nAvailable materials:")
            for name in reg.materialDict.keys():
                print(f"  {name}")
            return False
    
    # Change the material
    old_material = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
    lv.material = reg.materialDict[material_name]
    print(f"✓ Changed material of '{volume_name}' from '{old_material}' to '{material_name}'")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="View and edit GDML geometry with pyg4ometry VtkViewer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("gdml_file", help="GDML file to visualize")
    parser.add_argument("--list-volumes", action="store_true", 
                        help="List all logical volumes and their materials")
    parser.add_argument("--list-materials", action="store_true",
                        help="List all available materials")
    parser.add_argument("--change-material", nargs=2, metavar=("VOLUME", "MATERIAL"),
                        action="append", help="Change material of a volume (can be used multiple times)")
    parser.add_argument("--save", metavar="FILE", help="Save modified geometry to new GDML file")
    
    args = parser.parse_args()
    gdml_file = args.gdml_file
    args = parser.parse_args()
    gdml_file = args.gdml_file
    
    # Import VTK and pyg4ometry AFTER clearing sys.modules
    import vtk
    import pyg4ometry
    
    print(f"Loading GDML: {gdml_file}")
    
    # Read GDML file
    reader = pyg4ometry.gdml.Reader(gdml_file)
    reg = reader.getRegistry()
    world_lv = reg.getWorldVolume()
    
    # Handle listing operations
    if args.list_volumes:
        list_volumes(reg)
        if not args.change_material and not args.list_materials:
            sys.exit(0)
    
    if args.list_materials:
        list_materials(reg)
        if not args.change_material:
            sys.exit(0)
    
    # Handle material changes
    if args.change_material:
        print("\nApplying material changes:")
        for volume_name, material_name in args.change_material:
            change_material(reg, volume_name, material_name)
    
    # Save modified geometry if requested
    if args.save:
        print(f"\nSaving modified geometry to: {args.save}")
        writer = pyg4ometry.gdml.Writer()
        writer.addDetector(reg)
        writer.write(args.save)
        print(f"✓ Saved to {args.save}")
    
    # Create VtkViewer and add geometry
    viewer = pyg4ometry.visualisation.VtkViewer()
    viewer.addLogicalVolume(world_lv)
    
    print("\nStarting interactive viewer...")
    print("Rotate: Left mouse | Zoom: Right mouse | Pan: Middle mouse")
    print("Press 'q' in window to quit")
    
    # Configure render window
    viewer.renWin.SetSize(1024, 768)
    viewer.renWin.SetWindowName(f"pyg4ometry Viewer - {gdml_file}")
    viewer.ren.ResetCamera()
    
    # Force initial render before starting interactor
    viewer.renWin.Render()
    
    print(f"Window created. If you don't see it, check your X server on Windows.")
    print("Window should be titled: pyg4ometry Viewer")
    
    # Start interactive event loop (blocks until window is closed)
    # This allows full 3D interaction with the geometry
    viewer.iren.Initialize()
    viewer.iren.Start()
    
    print("Viewer closed.")
