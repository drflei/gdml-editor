"""Tests for removal of local element dropdown helpers."""

import pytest

pytest.importorskip("tkinter")

import gdml_editor.gui as gui


def test_element_dropdown_helpers_removed():
    """Local MaterialDefinitionDialog should no longer exist."""
    assert not hasattr(gui, "MaterialDefinitionDialog")
