# Enhanced Bridge GAD Generator

## Overview

The Enhanced Bridge General Arrangement Drawing (GAD) Generator is a Python application that creates professional engineering drawings for bridge structures. This enhanced version incorporates all the missing functionality from the original LISP implementation while maintaining a user-friendly interface.

## Features

### Drawing Capabilities

1. **Layout Grid System**
   - Professional axis labeling
   - Elevation and chainage markers
   - Grid line organization

2. **Pier Drawing**
   - Complete elevation view
   - Pier cap with proper scaling
   - Pier with batter (slope)
   - Foundation footing details
   - Plan view with skew rotation

3. **Abutment Drawing**
   - Detailed elevation representation
   - Plan view with skew compensation
   - Internal structural elements
   - Proper engineering proportions

4. **Cross-Section Plotting**
   - River level annotations
   - Chainage markers
   - Grid integration

5. **Professional Output**
   - DXF file generation with layer organization
   - PDF file generation
   - Professional title blocks
   - Dimension standards compliance

## Installation

### Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - pygame
  - ezdxf
  - reportlab

### Installation Steps

1. Clone or download the repository
2. Install required packages:
   ```bash
   pip install pygame ezdxf reportlab
   ```

## Usage

### Running the Application

1. Navigate to the application directory:
   ```bash
   cd BridgeGAD-00
   ```

2. Run the main application:
   ```bash
   python simple_bridge_app.py
   ```

### Controls

#### Main Drawing View
- **Mouse Wheel**: Zoom in/out
- **Mouse Drag**: Pan the drawing
- **R**: Reset view
- **I**: Enter input mode
- **D**: Save as DXF
- **P**: Save as PDF

#### Input Mode
- **Left/Right Arrow Keys**: Navigate between parameter files
- **Enter**: Load selected parameter file
- **R**: Return to drawing view

### Parameter Files

The application supports loading bridge parameters from CSV files. The expected format includes:

1. **Header Row**: Value, Variable, Description
2. **Data Rows**: Numeric values for each bridge parameter
3. **Supported Parameters**:
   - Scale factors (SCALE1, SCALE2)
   - Skew angle (SKEW)
   - Datum and elevation levels
   - Bridge dimensions
   - Structural element sizes
   - Material properties

## Output Files

### DXF Files

Professional CAD files with:
- 9 organized layers for different drawing elements
- Proper dimension styles
- Text styling and positioning
- Engineering standards compliance

### PDF Files

Print-ready documents with:
- Complete bridge drawings
- Professional title blocks
- Proper scaling and layout

## Code Structure

### Main Components

1. **simple_bridge_app.py**: Main application file
   - UI rendering and interaction
   - Drawing functions for all elements
   - File I/O operations
   - Parameter management

2. **Drawing Functions**:
   - `draw_layout_grid()`: Grid system rendering
   - `draw_pier()`: Pier geometry drawing
   - `draw_abutment()`: Abutment geometry drawing
   - `draw_cross_section()`: Cross-section plotting

3. **Export Functions**:
   - `save_dxf()`: DXF file generation
   - `save_pdf()`: PDF file generation

### Coordinate System

The application uses a comprehensive coordinate transformation system:
- `hpos()`: Horizontal position calculation
- `vpos()`: Vertical position calculation
- `pt()`: Point creation with transformation

### Skew Handling

Complete skew angle management:
- Degree to radian conversion
- Trigonometric calculations
- Skew compensation for all elements
- Plan view rotation

## Testing

### Verification Scripts

1. **test_enhanced_bridge.py**: Comprehensive functionality tests
2. **verify_dxf_creation.py**: DXF generation verification

### Running Tests

```bash
python test_enhanced_bridge.py
python verify_dxf_creation.py
```

## Development

### Extending Functionality

The modular design allows for easy extensions:
1. Add new drawing functions
2. Extend parameter system
3. Add new export formats
4. Enhance UI elements

### Code Organization

- Separate functions for each drawing element
- Consistent function signatures
- Proper error handling
- Comprehensive documentation

## Troubleshooting

### Common Issues

1. **Missing Python Packages**:
   ```bash
   pip install pygame ezdxf reportlab
   ```

2. **Parameter Loading Errors**:
   - Verify CSV file format
   - Check parameter names match expected values
   - Ensure numeric values are properly formatted

3. **Drawing Display Issues**:
   - Use zoom controls (mouse wheel)
   - Reset view with 'R' key
   - Check window size and resolution

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on original LISP implementation for AutoCAD
- Enhanced with modern Python libraries
- Designed for professional engineering use