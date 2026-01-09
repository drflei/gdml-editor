"""
GDML Editor - A GUI application for editing GDML geometry files.

This package provides tools for:
- Editing GDML geometry files with a graphical interface
- Defining custom materials (compounds and mixtures)
- Managing user-defined material databases
- Visualizing geometries with VTK
- Changing materials on logical volumes
"""

__version__ = "1.0.0"
__author__ = "GDML Editor Contributors"

from gdml_editor.gui import GDMLEditorApp, UserMaterialDatabase

__all__ = ['GDMLEditorApp', 'UserMaterialDatabase']
