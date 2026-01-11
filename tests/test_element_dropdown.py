"""Tests for element dropdown constants used by the material definition UI."""

from gdml_editor.gui import MaterialDefinitionDialog


def test_element_dropdown_lists_present_and_sized():
    elements_list = MaterialDefinitionDialog.ELEMENTS
    common = MaterialDefinitionDialog.COMMON_ELEMENTS

    assert isinstance(elements_list, list)
    assert isinstance(common, list)

    # Periodic table symbols list should be complete.
    assert len(elements_list) == 118
    # Sanity checks for a few well-known symbols.
    assert "H" in elements_list
    assert "Fe" in elements_list
    assert "U" in elements_list
    assert "Og" in elements_list

    # Common elements should be a subset of the full list.
    assert set(common).issubset(set(elements_list))
