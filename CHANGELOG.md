# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-09

### Added
- Initial release of GDML Editor
- GUI application for editing GDML geometry files
- User-defined materials feature
  - Compound materials using molecular formulas
  - Mixture materials by element mass fractions
  - Persistent JSON database for materials
  - Material management dialog (view, edit, delete)
- Element dropdown selector with 118 periodic table elements
- Type-ahead filtering for element selection
- Common elements quick reference
- NIST material database integration (400+ materials)
- VTK visualization integration
- Material search and filtering
- pyg4ometry-first architecture
- Comprehensive documentation
  - User Materials Guide
  - Element Dropdown Guide
  - Implementation Summary
  - Refactoring Summary
  - Code Comparison

### Features
- Browse logical volumes in tree view
- View volume properties
- Change materials on volumes
- Save/load GDML files
- Unit conversions (density, temperature, pressure)
- Advanced material properties (state, temperature, pressure)
- Error validation and helpful messages

### Technical
- Clean, modular code architecture
- Helper methods for unit conversions
- Single responsibility principle
- 40% code reduction through refactoring
- Dictionary-based conversions (O(1) lookup)
- Element caching in registry
- Type-ahead autocomplete
- Comprehensive test suite

## [Unreleased]

### Planned
- Material import/export (CSV, XML)
- Material templates library
- Optical properties support
- Batch material operations
- Element tooltips with properties
- Recently used materials
- Material comparison tools
