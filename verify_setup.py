#!/usr/bin/env python
"""
Verification script for GDML Editor package setup.
Checks that all required files are in place and properly configured.
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def check_file(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"{GREEN}✓{NC} {description}: {path}")
        return True
    else:
        print(f"{RED}✗{NC} {description}: {path} NOT FOUND")
        return False

def check_dir(path, description):
    """Check if a directory exists."""
    if os.path.isdir(path):
        print(f"{GREEN}✓{NC} {description}: {path}/")
        return True
    else:
        print(f"{RED}✗{NC} {description}: {path}/ NOT FOUND")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("GDML Editor - Package Setup Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Core package structure
    print(f"\n{YELLOW}Core Package Structure:{NC}")
    all_passed &= check_dir("gdml_editor", "Package directory")
    all_passed &= check_file("gdml_editor/__init__.py", "Package init")
    all_passed &= check_file("gdml_editor/gui.py", "Main GUI module")
    all_passed &= check_file("gdml_editor/view_gdml.py", "GDML viewer")
    all_passed &= check_file("gdml_editor/run_vtkviewer.py", "VTK viewer")
    
    # Setup files
    print(f"\n{YELLOW}Setup Files:{NC}")
    all_passed &= check_file("setup.py", "Setup script")
    all_passed &= check_file("pyproject.toml", "Project config")
    all_passed &= check_file("requirements.txt", "Requirements")
    all_passed &= check_file("MANIFEST.in", "Manifest")
    
    # Documentation
    print(f"\n{YELLOW}Documentation:{NC}")
    all_passed &= check_file("README.md", "README")
    all_passed &= check_file("LICENSE", "License")
    all_passed &= check_file("CHANGELOG.md", "Changelog")
    all_passed &= check_file("CONTRIBUTING.md", "Contributing guide")
    all_passed &= check_dir("docs", "Documentation directory")
    
    # CI/CD
    print(f"\n{YELLOW}CI/CD:{NC}")
    all_passed &= check_dir(".github/workflows", "GitHub Actions")
    all_passed &= check_file(".github/workflows/python-package.yml", "CI workflow")
    
    # Development files
    print(f"\n{YELLOW}Development:{NC}")
    all_passed &= check_file(".gitignore", "Git ignore")
    all_passed &= check_file("launch_gui.sh", "Launch script")
    all_passed &= check_dir("tests", "Tests directory")
    
    # Publication scripts
    print(f"\n{YELLOW}Publication:{NC}")
    all_passed &= check_file("publish.sh", "Publication script")
    
    # Check Python imports
    print(f"\n{YELLOW}Import Checks:{NC}")
    try:
        import gdml_editor
        print(f"{GREEN}✓{NC} gdml_editor package can be imported")
        print(f"  Version: {gdml_editor.__version__}")
    except ImportError as e:
        print(f"{RED}✗{NC} Cannot import gdml_editor: {e}")
        all_passed = False
    
    # Check dependencies
    print(f"\n{YELLOW}Dependency Checks:{NC}")
    dependencies = {
        'pyg4ometry': 'pyg4ometry',
        'vtk': 'vtk',
        'numpy': 'numpy'
    }
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"{GREEN}✓{NC} {name} is installed")
        except ImportError:
            print(f"{YELLOW}⚠{NC} {name} not installed (will be installed with package)")
    
    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print(f"{GREEN}✓ All checks passed! Package is ready for publication.{NC}")
        print("\nRun ./publish.sh to build and get publication instructions.")
        return 0
    else:
        print(f"{RED}✗ Some checks failed. Please fix the issues above.{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
