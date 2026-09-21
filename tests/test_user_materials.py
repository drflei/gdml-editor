"""Tests for persistent user-defined material handling."""

import pytest

pytest.importorskip("tkinter")
try:
    from pyg4ometry import geant4 as g4
except (ImportError, OSError) as exc:
    pytest.skip(f"pyg4ometry.geant4 is unavailable: {exc}", allow_module_level=True)

import gdml_editor.gui as gui


def test_user_material_database_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(gui.Path, "home", lambda: tmp_path)
    database = gui.UserMaterialDatabase()
    database.add_material("Water", {
        "type": "compound",
        "density": 1.0,
        "density_unit": "g/cm3",
        "composition": "H2O",
    })

    reloaded = gui.UserMaterialDatabase()
    assert reloaded.get_material("Water")["composition"] == "H2O"
    assert reloaded.list_materials() == ["Water"]


def test_user_material_ui_is_exposed():
    assert hasattr(gui, "UserMaterialDatabase")
    assert hasattr(gui, "MaterialDefinitionDialog")
    assert hasattr(gui, "MaterialManagementDialog")


def test_nist_material_list_available():
    """pyg4ometry NIST material list should be available and contain common entries."""
    mats = list(g4.getNistMaterialList())
    assert "G4_AIR" in mats
