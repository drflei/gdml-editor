"""Tests for material handling (pyg4ometry-only)."""

import pytest

pytest.importorskip("tkinter")
g4 = pytest.importorskip("pyg4ometry.geant4")

import gdml_editor.gui as gui


def test_user_material_helpers_removed():
    """Local user-material helpers should be removed in favor of pyg4ometry."""
    assert not hasattr(gui, "UserMaterialDatabase")
    assert not hasattr(gui, "MaterialDefinitionDialog")
    assert not hasattr(gui, "MaterialManagementDialog")


def test_nist_material_list_available():
    """pyg4ometry NIST material list should be available and contain common entries."""
    mats = list(g4.getNistMaterialList())
    assert "G4_AIR" in mats
