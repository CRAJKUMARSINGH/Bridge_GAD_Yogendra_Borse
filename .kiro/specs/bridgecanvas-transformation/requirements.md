# Requirements Document: BridgeCanvas Transformation

## Introduction

This document specifies the requirements for transforming the bloated Bridge_GAD_Yogendra_Borse application (200+ files, 30+ dependencies, 10 tabs) into a lean, focused BridgeCanvas application (<20 files, 7 dependencies, 1 tab). The transformation follows the principle of "do one thing perfectly" by eliminating feature creep, removing unnecessary abstractions, and focusing exclusively on the core functionality: uploading Excel bridge parameters and generating professional AutoCAD DXF drawings.

The transformation addresses critical issues in the current system: excessive complexity (200+ files), poor performance (25-48 seconds), and unreliable test results (71.4% success rate). The target system will achieve <20 files, <8 seconds total processing time, and 100% test success rate (7/7 inputs).

## Glossary

- **BridgeCanvas**: The target lean application resulting from this transformation
- **Bridge_GAD**: The current bloated application being transformed
- **DXF**: Drawing Exchange Format - AutoCAD's file format for CAD drawings
- **Streamlit**: Python web framework for building data applications
- **Excel_Parameters**: Bridge design parameters stored in Excel format (3-column: Value, Variable, Description)
- **Drawing_Generator**: Core engine that converts Excel parameters to DXF drawings
- **Transformation**: The process of converting Bridge_GAD to BridgeCanvas
- **Feature_Bloat**: Unnecessary features that add complexity without value (9 tabs to be removed)
- **Abstraction_Layer**: Intermediate code layers that add overhead without benefit
- **Test_Success_Rate**: Percentage of test inputs that generate valid drawings successfully

## Requirements

### Requirement 1: Application Simplification

**User Story:** As a developer, I want to reduce the application from 200+ files to <20 files, so that the codebase is maintainable and understandable.

#### Acceptance Criteria

1. THE System SHALL contain fewer than 20 total files after transformation
2. THE System SHALL remove all 9 unnecessary tab features (Bill Generation, Templates, Quality Check, 3D Visualization, Design Comparison, AI Optimizer, Export Manager, History, Help)
3. THE System SHALL delete all redundant modules (living_gad.py, telemetry.py, updater.py, plugin_*.py, mesh_builder.py, lisp_mirror.py)
4. THE System SHALL maintain only core files (streamlit_app.py, bridge_generator.py, io_utils.py, parameters.py)
5. THE System SHALL reduce documentation from 20+ markdown files to 2 files (README.md, START_HERE.md)

### Requirement 2: Dependency Reduction

**User Story:** As a system administrator, I want to reduce dependencies from 30+ to 7, so that the application has a smaller footprint and fewer security vulnerabilities.

#### Acceptance Criteria

1. THE System SHALL use exactly 7 dependencies (streamlit, ezdxf, pandas, openpyxl, matplotlib, python-dateutil, pyyaml)
2. THE System SHALL remove all AI/ML dependencies (numpy, scipy, tensorflow, torch)
3. THE System SHALL remove all 3D visualization dependencies (plotly, vtk)
4. THE System SHALL remove all multi-format export dependencies (reportlab, cairosvg, pillow)
5. THE System SHALL remove all backend dependencies (fastapi, uvicorn, pydantic)

### Requirement 3: Single-Tab User Interface

**User Story:** As a user, I want a simple single-tab interface, so that I can quickly upload Excel files and generate drawings without navigation complexity.

#### Acceptance Criteria

1. THE Streamlit_App SHALL contain exactly 1 tab (Drawing Generation)
2. THE Streamlit_App SHALL provide file upload functionality for Excel files (.xlsx, .xls)
3. WHEN a user uploads an Excel file, THE Streamlit_App SHALL display a preview of the parameters
4. THE Streamlit_App SHALL provide a "Generate Drawing" button
5. WHEN drawing generation completes, THE Streamlit_App SHALL provide a download button for the DXF file
6. THE Streamlit_App SHALL contain approximately 100 lines of code (vs 1000+ currently)

### Requirement 4: Excel Parameter Reading

**User Story:** As a user, I want to upload Excel files with bridge parameters, so that the system can generate drawings from my design data.

#### Acceptance Criteria

1. WHEN a valid Excel file is uploaded, THE IO_Utils SHALL read parameters from the 3-column format (Value, Variable, Description)
2. THE IO_Utils SHALL return a dictionary mapping variable names to float values
3. WHEN an invalid Excel file is uploaded, THE IO_Utils SHALL return a descriptive error message
4. THE IO_Utils SHALL skip empty or invalid rows without failing
5. THE IO_Utils SHALL convert all numeric values to float type

### Requirement 5: Parameter Validation

**User Story:** As a user, I want my bridge parameters validated, so that I receive clear error messages for invalid inputs before drawing generation.

#### Acceptance Criteria

1. THE Validator SHALL check that all required parameters are present (NSPAN, SPAN1, ABTL, RTL, DATUM, LEFT, RIGHT, SCALE1, SCALE2)
2. WHEN a required parameter is missing, THE Validator SHALL return an error message identifying the missing parameter
3. THE Validator SHALL verify that NSPAN is a positive integer
4. THE Validator SHALL verify that span lengths (SPAN1) are positive values
5. THE Validator SHALL verify that skew angle (SKEW) is between -45 and +45 degrees
6. THE Validator SHALL verify that scale values (SCALE1, SCALE2) are positive

### Requirement 6: DXF Drawing Generation

**User Story:** As a user, I want to generate AutoCAD DXF drawings from Excel parameters, so that I can use the drawings in AutoCAD for bridge design.

#### Acceptance Criteria

1. WHEN valid parameters are provided, THE Drawing_Generator SHALL create a complete DXF file
2. THE Drawing_Generator SHALL generate drawings in AutoCAD R2010 format
3. THE Drawing_Generator SHALL draw all bridge components (superstructure, piers, abutments, plan view)
4. THE Drawing_Generator SHALL apply coordinate transformations using specified scales (SCALE1/SCALE2)
5. THE Drawing_Generator SHALL apply skew angles to all components correctly
6. THE Drawing_Generator SHALL save the output as a valid DXF file

### Requirement 7: Bridge Component Drawing

**User Story:** As a civil engineer, I want complete bridge drawings with all components, so that I have comprehensive design documentation.

#### Acceptance Criteria

1. THE Drawing_Generator SHALL draw the bridge superstructure (deck and approach slabs)
2. THE Drawing_Generator SHALL draw piers in elevation view with correct count (NSPAN - 1)
3. THE Drawing_Generator SHALL draw pier components (cap, shaft with batter, footing)
4. THE Drawing_Generator SHALL draw left and right abutments with correct geometry
5. THE Drawing_Generator SHALL draw plan view showing all footings
6. THE Drawing_Generator SHALL draw layout axes and grid lines

### Requirement 8: Coordinate Transformation

**User Story:** As a developer, I want accurate coordinate transformations, so that real-world bridge dimensions are correctly scaled in the drawing.

#### Acceptance Criteria

1. THE Drawing_Generator SHALL transform horizontal coordinates using formula: drawingX = left + hScale * (realX - left)
2. THE Drawing_Generator SHALL transform vertical coordinates using formula: drawingY = datum + vScale * (realY - datum)
3. THE Drawing_Generator SHALL calculate horizontal scale as SCALE1 / SCALE2
4. THE Drawing_Generator SHALL maintain linear transformation properties
5. WHEN skew angle is applied, THE Drawing_Generator SHALL adjust component widths by dividing by cos(skew_angle)

### Requirement 9: Performance Optimization

**User Story:** As a user, I want fast drawing generation, so that I don't waste time waiting for results.

#### Acceptance Criteria

1. THE System SHALL complete the entire workflow (upload to download) in less than 8 seconds
2. THE Drawing_Generator SHALL generate drawings in less than 5 seconds
3. THE IO_Utils SHALL read and validate parameters in less than 1 second
4. THE Streamlit_App SHALL update the UI in less than 2 seconds
5. THE System SHALL achieve 5-6x performance improvement over the current system (25-48 seconds)

### Requirement 10: Test Success Rate

**User Story:** As a quality assurance engineer, I want 100% test success rate, so that all valid inputs produce correct drawings.

#### Acceptance Criteria

1. THE System SHALL successfully generate drawings for all 7 test input files
2. THE System SHALL achieve 100% test success rate (7/7 inputs pass)
3. WHEN any test input is provided, THE System SHALL generate a valid DXF file
4. THE System SHALL improve from current 71.4% success rate (5/7) to 100%
5. THE System SHALL validate all generated DXF files can be opened in AutoCAD

### Requirement 11: Error Handling

**User Story:** As a user, I want clear error messages, so that I can quickly fix problems with my input files.

#### Acceptance Criteria

1. WHEN an invalid Excel file is uploaded, THE System SHALL display error message "Invalid Excel file. Please upload a valid .xlsx file."
2. WHEN required parameters are missing, THE System SHALL list all missing parameters
3. WHEN parameter values are invalid, THE System SHALL specify which parameter and why it's invalid
4. WHEN file write fails, THE System SHALL display error message "Cannot save file. Check write permissions."
5. IF drawing generation fails, THEN THE System SHALL not create partial output files

### Requirement 12: File Type Restrictions

**User Story:** As a security-conscious user, I want the system to accept only valid Excel files, so that malicious files cannot be uploaded.

#### Acceptance Criteria

1. THE System SHALL accept only .xlsx and .xls file extensions
2. THE System SHALL verify file magic numbers (not just extensions)
3. THE System SHALL reject executable files
4. THE System SHALL limit file size to maximum 10 MB
5. THE System SHALL prevent path traversal attacks in file paths

### Requirement 13: DXF-Only Output

**User Story:** As a user, I want DXF output only, so that the system is fast and focused on AutoCAD compatibility.

#### Acceptance Criteria

1. THE System SHALL generate only DXF format output
2. THE System SHALL not generate PDF output
3. THE System SHALL not generate PNG output
4. THE System SHALL not generate SVG output
5. THE System SHALL remove all multi-format export functionality

### Requirement 14: Stateless Operation

**User Story:** As a user, I want a stateless application, so that my data is not stored and privacy is maintained.

#### Acceptance Criteria

1. THE System SHALL not store user data between sessions
2. THE System SHALL not maintain drawing history
3. THE System SHALL not track user analytics or telemetry
4. THE System SHALL delete temporary files immediately after download
5. THE System SHALL not use session state management

### Requirement 15: Memory Efficiency

**User Story:** As a system administrator, I want low memory usage, so that the application can run on modest hardware.

#### Acceptance Criteria

1. THE System SHALL use less than 100 MB base memory (vs 300+ MB currently)
2. THE System SHALL use less than 50 MB per drawing generation (vs 150+ MB currently)
3. THE System SHALL clean up temporary resources immediately after use
4. THE System SHALL not accumulate memory leaks during operation
5. THE System SHALL stream file output without buffering entire files in memory

### Requirement 16: Code Simplification

**User Story:** As a developer, I want simplified code without unnecessary abstractions, so that I can understand and maintain the system easily.

#### Acceptance Criteria

1. THE System SHALL use direct ezdxf library calls (no wrapper classes)
2. THE System SHALL remove Pydantic validation models (use basic type checking)
3. THE System SHALL remove multiple abstraction layers between UI and DXF generation
4. THE System SHALL reduce bridge_generator.py from 1200+ lines to approximately 800 lines
5. THE System SHALL use functional approach in Streamlit app (no complex class hierarchies)

### Requirement 17: AutoCAD Version Compatibility

**User Story:** As a CAD user, I want drawings compatible with AutoCAD, so that I can open and edit them in standard CAD software.

#### Acceptance Criteria

1. THE System SHALL generate DXF files in AutoCAD R2010 format by default
2. THE System SHALL support AutoCAD R2006 format as an option
3. WHEN a DXF file is generated, THE System SHALL ensure it can be opened in AutoCAD without errors
4. THE System SHALL use ezdxf library version 1.4.0 or higher for format support
5. THE System SHALL generate valid DXF structure according to AutoCAD specifications

### Requirement 18: Deployment to Streamlit Cloud

**User Story:** As a user, I want the application deployed to Streamlit Cloud, so that I can access it from any device without installation.

#### Acceptance Criteria

1. THE System SHALL be deployable to Streamlit Cloud
2. THE System SHALL work with Streamlit Cloud's Python 3.8+ environment
3. THE System SHALL use only dependencies available on Streamlit Cloud
4. THE System SHALL handle file uploads through Streamlit Cloud's infrastructure
5. THE System SHALL provide HTTPS access through Streamlit Cloud

### Requirement 19: Documentation Quality

**User Story:** As a new user, I want clear documentation, so that I can start using the system within 5 minutes.

#### Acceptance Criteria

1. THE System SHALL provide a README.md with comprehensive installation and usage instructions
2. THE System SHALL provide a START_HERE.md with 5-minute quick start guide
3. THE Documentation SHALL include parameter reference explaining all required Excel columns
4. THE Documentation SHALL include troubleshooting section for common issues
5. THE Documentation SHALL include example workflow with screenshots

### Requirement 20: Test Coverage

**User Story:** As a developer, I want comprehensive test coverage, so that I can confidently make changes without breaking functionality.

#### Acceptance Criteria

1. THE System SHALL achieve at least 80% code coverage
2. THE System SHALL include unit tests for parameter reading and validation
3. THE System SHALL include unit tests for coordinate transformation
4. THE System SHALL include integration tests for end-to-end workflow
5. THE System SHALL include tests for all 7 provided test input files

### Requirement 21: Pier Drawing Accuracy

**User Story:** As a civil engineer, I want accurate pier drawings, so that the design reflects correct structural geometry.

#### Acceptance Criteria

1. WHEN drawing piers, THE Drawing_Generator SHALL draw pier cap as a rectangle with correct width (CAPW) and height (CAPT - CAPB)
2. THE Drawing_Generator SHALL draw pier shaft with batter angle (BATTR) applied correctly
3. THE Drawing_Generator SHALL draw pier footing with correct width (FUTW) and depth (FUTD)
4. THE Drawing_Generator SHALL connect pier cap, shaft, and footing as continuous geometry
5. THE Drawing_Generator SHALL adjust pier widths for skew angle by dividing by cos(skew_angle)

### Requirement 22: Abutment Drawing Accuracy

**User Story:** As a civil engineer, I want accurate abutment drawings, so that the design reflects correct foundation geometry.

#### Acceptance Criteria

1. WHEN drawing abutments, THE Drawing_Generator SHALL draw left and right abutments with correct positioning
2. THE Drawing_Generator SHALL apply front batter (ALFB/ARFB) to abutment faces
3. THE Drawing_Generator SHALL apply toe batter (ALTB/ARTB) to abutment toes
4. THE Drawing_Generator SHALL draw abutment footings with correct offset (ALFO/ARFO) and depth (ALFD/ARFD)
5. THE Drawing_Generator SHALL mirror geometry correctly for right-side abutment

### Requirement 23: Plan View Accuracy

**User Story:** As a civil engineer, I want accurate plan view drawings, so that I can see the bridge layout from above.

#### Acceptance Criteria

1. THE Drawing_Generator SHALL draw plan view below the elevation view
2. THE Drawing_Generator SHALL draw all pier footings in plan view with correct dimensions
3. THE Drawing_Generator SHALL draw abutment footings in plan view at correct positions
4. THE Drawing_Generator SHALL apply skew angle to all plan view components
5. THE Drawing_Generator SHALL add labels to all piers (P1, P2, ...) and abutments (A1, A2)

### Requirement 24: Default Parameter Values

**User Story:** As a user, I want sensible default values for optional parameters, so that I don't have to specify every parameter.

#### Acceptance Criteria

1. THE System SHALL provide default value of 0.0 for SKEW (no skew)
2. THE System SHALL provide default value of 186.0 for SCALE1
3. THE System SHALL provide default value of 100.0 for SCALE2
4. WHEN an optional parameter is missing, THE System SHALL use the default value
5. THE System SHALL document all default values in the parameter reference

### Requirement 25: Transformation Phases

**User Story:** As a project manager, I want the transformation completed in phases, so that progress can be tracked and risks managed.

#### Acceptance Criteria

1. THE Transformation SHALL complete Phase 1 (Core Extraction) on Day 1
2. THE Transformation SHALL complete Phase 2 (Cleanup and Optimization) on Day 1-2
3. THE Transformation SHALL complete Phase 3 (Testing and Validation) on Day 2
4. THE Transformation SHALL complete Phase 4 (Documentation and Deployment) on Day 2-3
5. THE Transformation SHALL achieve all success metrics by end of Day 3

### Requirement 26: Geometric Consistency

**User Story:** As a quality assurance engineer, I want geometric consistency checks, so that generated drawings are structurally valid.

#### Acceptance Criteria

1. THE System SHALL verify that pier count equals NSPAN - 1
2. THE System SHALL verify that abutment count equals 2
3. THE System SHALL verify that total bridge length equals NSPAN * SPAN1
4. THE System SHALL verify that all components are within drawing bounds
5. THE System SHALL verify that all polylines are properly closed

### Requirement 27: Resource Limits

**User Story:** As a system administrator, I want resource limits, so that the system cannot be abused or crash from excessive inputs.

#### Acceptance Criteria

1. THE System SHALL limit maximum file upload size to 10 MB
2. THE System SHALL timeout operations that exceed 30 seconds
3. THE System SHALL limit maximum number of spans (NSPAN) to prevent excessive complexity
4. THE System SHALL limit drawing complexity to prevent memory exhaustion
5. THE System SHALL handle resource exhaustion gracefully with error messages

### Requirement 28: Python Version Compatibility

**User Story:** As a developer, I want Python 3.8+ compatibility, so that the system works on modern Python installations.

#### Acceptance Criteria

1. THE System SHALL run on Python 3.8 or higher
2. THE System SHALL be tested on Python versions 3.8, 3.9, 3.10, and 3.11
3. THE System SHALL use only Python standard library features available in 3.8+
4. THE System SHALL specify Python version requirement in documentation
5. THE System SHALL use type hints compatible with Python 3.8+

### Requirement 29: Logging and Debugging

**User Story:** As a developer, I want minimal logging, so that the system is fast but still debuggable when issues occur.

#### Acceptance Criteria

1. THE System SHALL log only errors (not info or debug messages)
2. THE System SHALL include error details in log messages (file path, parameter name, error type)
3. THE System SHALL not log user data or sensitive information
4. THE System SHALL not log every operation (remove verbose logging)
5. THE System SHALL provide stack traces for unexpected errors

### Requirement 30: Code Quality Standards

**User Story:** As a developer, I want high code quality, so that the system is maintainable and professional.

#### Acceptance Criteria

1. THE System SHALL follow PEP 8 Python style guidelines
2. THE System SHALL include docstrings for all public functions and classes
3. THE System SHALL use type hints for function parameters and return values
4. THE System SHALL have no unused imports or variables
5. THE System SHALL pass linting checks (flake8, pylint)
