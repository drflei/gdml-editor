"""Tests for removal of local element dropdown helpers."""

import pytest

pytest.importorskip("tkinter")

import gdml_editor.gui as gui


def test_element_dropdown_helpers_exposed():
    """The material editor exposes the complete element list."""
    assert len(gui.MaterialDefinitionDialog.ELEMENTS) == 118
    assert "Fe" in gui.MaterialDefinitionDialog.ELEMENTS
