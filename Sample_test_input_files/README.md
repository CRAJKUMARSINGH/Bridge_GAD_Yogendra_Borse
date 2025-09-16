# Sample Test Input Files for All BridgeGAD Applications

This folder contains standardized test input files and expected outputs for all BridgeGAD applications.

## Test Data Structure

### 1. Basic Bridge Test Data
- `basic_bridge_test.xlsx` - Simple 2-span bridge
- `complex_bridge_test.xlsx` - Multi-span bridge with complex geometry
- `skew_bridge_test.xlsx` - Bridge with skew angle

### 2. LISP Parameter Test Data
- `lisp_test_parameters.xlsx` - LISP-style parameter input
- `minimal_bridge.xlsx` - Minimal parameter set
- `maximum_bridge.xlsx` - Full parameter set

### 3. Expected Outputs
- DXF files for CAD verification
- PDF files for visual verification
- PNG images for quick preview
- Test result reports

## Testing Methodology

1. **Functional Testing** - Each app must generate valid output
2. **Performance Testing** - Response time and resource usage
3. **Compatibility Testing** - Output format validation
4. **User Experience Testing** - BAT file functionality

## Test Results Format

Each test generates:
- Success/Failure status
- Performance metrics
- Output file quality assessment
- Error logs (if any)