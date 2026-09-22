"""Tests for VTK viewer display preflight behavior."""

from pathlib import Path


def test_viewer_does_not_override_display_setting():
    source = (Path(__file__).parents[1] / "gdml_editor" / "run_vtkviewer.py").read_text(
        encoding="utf-8"
    )

    assert 'os.environ["DISPLAY"] = ":0"' not in source


def test_gui_does_not_override_display_setting():
    source = (Path(__file__).parents[1] / "gdml_editor" / "gui.py").read_text(
        encoding="utf-8"
    )

    assert 'os.environ["DISPLAY"] = ":0"' not in source


def test_project_excludes_incompatible_vtk_release():
    project_root = Path(__file__).parents[1]
    pyproject = (project_root / "pyproject.toml").read_text(encoding="utf-8")
    requirements = (project_root / "requirements.txt").read_text(encoding="utf-8")

    assert '"vtk>=9.0.0,<9.6"' in pyproject
    assert "vtk>=9.0.0,<9.6" in requirements