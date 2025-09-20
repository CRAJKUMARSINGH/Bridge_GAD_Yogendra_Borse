# Enhanced Bridge GAD Generator

This is an enhanced version of the Bridge General Arrangement Drawing (GAD) generator that incorporates professional engineering drawing capabilities from the original LISP code.

## Features

### Enhanced Drawing Capabilities
- **Professional Layout Grid**: Enhanced grid system with proper annotations and dimensioning
- **Detailed Pier Drawing**: Complete pier geometry with cap, batter, and foundation footing
- **Advanced Abutment Drawing**: Full abutment geometry with plan and elevation views
- **Cross-Section Plotting**: River cross-section with proper chainage and level annotations
- **Skew Angle Support**: Proper handling of bridge skew angles in all components

### DXF Export Features
- **Layered Drawing**: Organized layers for different drawing elements (GRID, STRUCTURE, DIMENSIONS, etc.)
- **Professional Dimensioning**: Proper dimension styles with arrows and text
- **Title Block**: Professional title block with drawing information
- **Engineering Standards**: Compliance with standard bridge drawing practices

### User Interface
- **Interactive Controls**: Zoom, pan, and navigation controls
- **Parameter Display**: Real-time display of bridge parameters
- **Multiple Export Formats**: DXF and PDF export capabilities

## Usage

1. Run the application using the batch file:
   ```
   RUN_ENHANCED_BRIDGE_APP.bat
   ```

2. Navigate between parameter files using LEFT/RIGHT arrow keys
3. Load parameters with ENTER
4. Use mouse wheel to zoom in/out
5. Click and drag to pan the view
6. Press 'D' to export as DXF
7. Press 'P' to export as PDF

## Key Enhancements

### Pier Drawing
- Enhanced elevation view with proper pier cap dimensions
- Accurate batter calculations for pier sides
- Foundation footing with correct dimensions
- Plan view representation with skew rotation

### Abutment Drawing
- Complete abutment geometry with all structural elements
- Proper plan view with skew adjustments
- Detailed elevation view with face, toe, and back elements
- Accurate dimensioning and annotations

### Layout Grid
- Professional grid system with bed level and chainage markers
- Proper scaling for plan and elevation views
- Level and chainage annotations
- Dimension lines and extension lines

### Cross-Section
- River cross-section plotting with chainage markers
- Level annotations at each point
- Grid line markers for reference

## Technical Implementation

The application incorporates functionality from the original LISP code including:
- `layout()` function for grid system generation
- `cs()` function for cross-section plotting
- `pier()` function for pier geometry
- `abt1()` function for abutment geometry
- `st()` function for dimension styling

## File Structure

- `simple_bridge_app.py` - Main application with enhanced features
- `RUN_ENHANCED_BRIDGE_APP.bat` - Batch file to run the application
- `test_enhanced_bridge.py` - Test script for verification
- `ENHANCED_BRIDGE_APP_README.md` - This documentation

## Requirements

- Python 3.7+
- pygame
- ezdxf
- reportlab

## Export Capabilities

### DXF Export
The DXF export creates a professional drawing with:
- Multiple layers for organization
- Proper dimension styles
- Title block with drawing information
- Engineering standard line weights and colors

### PDF Export
The PDF export provides:
- Vector-based drawing output
- Professional layout and formatting
- Standard paper sizes

## Controls

- **Mouse Wheel**: Zoom in/out
- **Mouse Drag**: Pan the view
- **R**: Reset view
- **I**: Input mode
- **D**: Save as DXF
- **P**: Save as PDF
- **Arrow Keys**: Navigate parameter files (in input mode)
- **ENTER**: Load selected parameter file (in input mode)

## Parameter Files

The application can load bridge parameters from CSV files (misnamed as .xlsx). The parameters include:
- Scale factors for plan/elevation and sections
- Bridge geometry (span length, width, etc.)
- Pier dimensions (cap width, batter, etc.)
- Abutment dimensions (cap width, face batter, etc.)
- Foundation details
- Skew angle