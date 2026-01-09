#!/usr/bin/env python3
"""Setup script for gdml-editor package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="gdml-editor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A GUI application for editing GDML geometry files with user-defined materials support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gdml-editor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyg4ometry>=1.0.0",
        "vtk>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gdml-editor=gdml_editor.gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
