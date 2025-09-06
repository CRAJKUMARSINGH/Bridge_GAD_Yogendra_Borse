# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The Bridge GAD Generator is a comprehensive Python application that generates Bridge General Arrangement Drawings (GAD) from Excel input parameters. It incorporates decades of engineering expertise previously implemented in LISP and Python, now unified into a modern, fully-functional system.

## Development Commands

### Setup and Installation

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install in development mode
pip install -e ".[dev]"

# Or install dependencies directly
pip install -r requirements.txt
```

### Core Development Commands

```bash
# Generate bridge GAD from Excel input
bridge-gad generate input.xlsx --output bridge_design.dxf

# Start web API server
bridge-gad serve --host 127.0.0.1 --port 8000

# Start with auto-reload for development
bridge-gad serve --reload

# Show version
bridge-gad version

# Generate using legacy slab bridge method
bridge-gad gad spans.xlsx --out slab_bridge.dxf

# Generate using LISP-style parameters
bridge-gad lisp lisp_params.xlsx --out lisp_bridge.dxf
```

### Testing and Quality

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=bridge_gad --cov-report=term-missing

# Code formatting
black .
isort .

# Type checking (if mypy is installed)
mypy src/bridge_gad
```

### Quick Development Setup

```bash
# Create sample input file
python create_sample_input.py

# Generate test drawing
bridge-gad generate sample_input.xlsx

# Start development server
bridge-gad serve --reload
```

## Architecture Overview

### Core Components

1. **Bridge Generator (`bridge_generator.py`)**: Main engineering logic
   - Comprehensive bridge drawing generation incorporating LISP algorithms
   - Coordinate transformation functions (`hpos`, `vpos`, `h2pos`, `v2pos`)
   - Bridge component drawing (abutments, piers, caps, footings, deck)
   - Skew angle calculations and geometric transformations

2. **CLI Interface (`__main__.py`)**: Command-line interface
   - Multiple commands for different use cases
   - Excel file input handling
   - Configuration management

3. **Web API (`api.py`)**: FastAPI-based REST API
   - File upload endpoints
   - Drawing generation API
   - CORS enabled for web integration

4. **Configuration (`config.py`)**: Settings management
   - Bridge parameters configuration
   - Drawing and output settings
   - YAML-based configuration loading

### Key Engineering Features

- **Coordinate Systems**: Dual coordinate transformation supporting both plan/elevation and section scales
- **Skew Bridge Support**: Full trigonometric calculations for skewed bridges
- **Multiple Views**: Elevation, plan, and cross-sectional views
- **Comprehensive Components**: 
  - Abutments with detailed geometry (batters, footings, return walls)
  - Piers with caps, shafts, and footings
  - Deck slabs with approach slabs and wearing course
  - Proper dimensioning and labeling

### Data Flow

1. **Input**: Excel files with bridge parameters (over 50 engineering parameters)
2. **Processing**: 
   - Parameter validation and extraction
   - Coordinate transformations
   - Engineering calculations (batters, skew adjustments, scaling)
3. **Drawing Generation**: 
   - DXF document creation with proper layers and styles
   - Sequential drawing of all bridge components
   - Dimensioning and annotation
4. **Output**: Professional DXF drawings ready for CAD software

### Integration Points

- **Excel Integration**: Reads structured parameter sheets
- **CAD Integration**: Outputs industry-standard DXF format
- **Web Integration**: REST API for web applications
- **LISP Legacy**: Incorporates proven algorithms from AutoCAD LISP

### Important Engineering Constants

- Scale factors: Typically 1:100 for sections, 1:200 for plans
- Drawing units: Millimeters (1 unit = 1mm)
- Coordinate reference: Left-most chainage and datum level
- Skew calculations: Full trigonometric support for any skew angle

### File Structure

```
src/bridge_gad/
├── __init__.py           # Package initialization
├── __main__.py           # CLI interface
├── api.py               # FastAPI web interface
├── config.py            # Configuration management
├── bridge_generator.py  # Main engineering logic
├── core.py             # Core utilities
├── drawing.py          # Legacy drawing functions
└── [other modules]     # Additional functionality

attached_assets/         # Reference implementations
├── bridge_gad_app.py   # Comprehensive Python implementation
├── both abuts ok.py    # Abutment-specific logic
├── bridge_code.lsp     # Original LISP algorithms
└── input.xlsx         # Sample parameter file
```

### Development Tips

1. **Parameter Files**: Use `create_sample_input.py` to generate test Excel files
2. **Drawing Verification**: Generated DXF files can be opened in any CAD software
3. **API Testing**: Use the `/health` endpoint to verify API status
4. **Debugging**: Enable logging with `--log-level DEBUG` for detailed output
5. **Coordinate System**: Remember the dual scaling system for different views

### Legacy Integration

This application preserves and enhances decades of bridge engineering expertise:
- Original LISP algorithms for coordinate transformation
- Proven geometric calculations for bridge components
- Industry-standard drawing conventions and dimensioning
- Comprehensive parameter set covering all bridge aspects

The codebase successfully migrates complex AutoCAD LISP routines to modern Python while maintaining full engineering accuracy and adding web API capabilities for modern integration scenarios.
