"""
GDML Editor - A GUI application for editing GDML geometry files.

This package provides tools for:
- Editing GDML geometry files with a graphical interface
- Defining custom materials (compounds and mixtures)
- Managing user-defined material databases
- Visualizing geometries with VTK
- Changing materials on logical volumes
"""

__version__ = "1.0.1"
__author__ = "GDML Editor Contributors"

# Lazy imports to avoid circular import issues when running as module
def __getattr__(name):
    if name == 'GDMLEditorApp':
        from gdml_editor.gui import GDMLEditorApp
        return GDMLEditorApp
    elif name == 'UserMaterialDatabase':
        from gdml_editor.gui import UserMaterialDatabase
        return UserMaterialDatabase
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['GDMLEditorApp', 'UserMaterialDatabase']
