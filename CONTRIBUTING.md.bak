# Contributing to GDML Editor

Thank you for your interest in contributing to GDML Editor! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/gdml-editor/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - pyg4ometry and VTK versions

### Suggesting Features

1. Check [Issues](https://github.com/yourusername/gdml-editor/issues) for existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Proposed implementation (if applicable)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/gdml-editor.git
cd gdml-editor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=gdml_editor --cov-report=html

# Run specific test
pytest tests/test_materials.py
```

### Code Style

We follow PEP 8 with some modifications:

```bash
# Format code
black gdml_editor/

# Check style
flake8 gdml_editor/

# Type checking
mypy gdml_editor/
```

### Code Standards

- **Line Length**: 100 characters max
- **Imports**: Organized (standard, third-party, local)
- **Docstrings**: Google style for all public functions/classes
- **Type Hints**: Use where appropriate
- **Comments**: Explain why, not what

### Commit Messages

Follow conventional commits:

```
feat: add material export feature
fix: resolve element dropdown filtering bug
docs: update installation instructions
test: add tests for material validation
refactor: simplify unit conversion logic
style: format code with black
chore: update dependencies
```

## Project Structure

```
gdml-editor/
├── gdml_editor/           # Main package
│   ├── __init__.py
│   ├── gui.py             # Main application
│   ├── view_gdml.py       # GDML viewer utilities
│   └── run_vtkviewer.py   # VTK viewer
├── tests/                 # Test files
├── docs/                  # Documentation
├── .github/               # GitHub workflows
├── setup.py               # Package setup
├── pyproject.toml         # Build configuration
└── README.md              # Main documentation
```

## Adding Features

### New Material Property

1. Update `UserMaterialDatabase` class
2. Modify `MaterialDefinitionDialog` UI
3. Update `create_user_material_in_registry()` method
4. Add validation in `save_material()`
5. Update documentation
6. Add tests

### New Element Feature

1. Modify `MaterialDefinitionDialog.ELEMENTS`
2. Update dropdown logic in `add_element_row()`
3. Test with pyg4ometry NIST database
4. Update documentation

## Testing Guidelines

### Unit Tests

- Test individual functions/methods
- Mock external dependencies
- Cover edge cases
- Use pytest fixtures

### Integration Tests

- Test component interactions
- Use real pyg4ometry objects
- Test file I/O
- Test GUI interactions (where possible)

### Test Example

```python
def test_material_creation():
    db = UserMaterialDatabase("test.json")
    
    material_data = {
        'type': 'compound',
        'density': 1.0,
        'density_unit': 'g/cm3',
        'composition': 'H2O',
        'state': 'liquid'
    }
    
    db.add_material('Water', material_data)
    
    result = db.get_material('Water')
    assert result['type'] == 'compound'
    assert result['composition'] == 'H2O'
```

## Documentation

### Docstrings

Use Google style:

```python
def create_material(name, density, composition):
    """Create a new material in the database.
    
    Args:
        name: Material name (unique identifier)
        density: Material density in g/cm³
        composition: Molecular formula or element list
        
    Returns:
        Material object from pyg4ometry registry
        
    Raises:
        ValueError: If material already exists
        KeyError: If element not found in NIST database
    """
```

### README Updates

- Keep installation instructions current
- Add new features to feature list
- Update examples for new functionality
- Include screenshots when appropriate

## Release Process

1. Update version in `__init__.py` and `setup.py`
2. Update `CHANGELOG.md`
3. Create git tag (`git tag -a v1.0.0 -m "Release v1.0.0"`)
4. Push tag (`git push origin v1.0.0`)
5. GitHub Actions will build and publish to PyPI

## Questions?

- Open a [Discussion](https://github.com/yourusername/gdml-editor/discussions)
- Join our community chat
- Email maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
