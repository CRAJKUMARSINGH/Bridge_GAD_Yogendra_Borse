# 📋 BridgeGAD Test Input Files Documentation

## 🎯 Overview
This folder contains comprehensive test input files designed to validate all BridgeGAD applications across different scenarios and configurations.

## 📄 Test Files Description

### 1. **test_bridge_small_single_span.xlsx**
- **Purpose**: Basic functionality test
- **Configuration**: Single span, no skew, minimal parameters
- **Expected Output**: Simple bridge drawing with basic elements
- **Use Case**: Initial validation, quick testing

### 2. **test_bridge_medium_multi_span.xlsx**
- **Purpose**: Multi-span bridge with moderate complexity
- **Configuration**: 3 spans, 15° skew, moderate parameters
- **Expected Output**: Complex bridge with multiple piers and spans
- **Use Case**: Standard bridge design validation

### 3. **test_bridge_large_complex_skew.xlsx**
- **Purpose**: Large-scale bridge with significant skew
- **Configuration**: 4 spans, 30° skew, complex geometry
- **Expected Output**: Professional-grade bridge drawing
- **Use Case**: Advanced functionality and performance testing

### 4. **test_lisp_style_input.xlsx**
- **Purpose**: LISP parameter compatibility test
- **Configuration**: Traditional LISP parameter naming and structure
- **Expected Output**: Bridge drawing using LISP-style processing
- **Use Case**: Legacy compatibility validation

### 5. **test_minimal_config.xlsx**
- **Purpose**: Minimal parameter test
- **Configuration**: Only essential parameters provided
- **Expected Output**: Basic bridge with default values
- **Use Case**: Error handling and default value testing

### 6. **test_stress_max_parameters.xlsx**
- **Purpose**: Maximum parameter stress test
- **Configuration**: All possible parameters, complex abutments
- **Expected Output**: Comprehensive bridge with all features
- **Use Case**: Performance testing and feature completeness

### 7. **Configuration Files (*.yaml)**
- **config_small.yaml**: Basic configuration for small bridges
- **config_medium.yaml**: Standard configuration with PDF output
- **config_large.yaml**: Advanced configuration with all features

## 🧪 Testing Instructions

### Quick Test Command:
```bash
# Test with different files
bridge-gad generate test_bridge_small_single_span.xlsx --output small_test.dxf
bridge-gad generate test_bridge_medium_multi_span.xlsx --config config_medium.yaml --output medium_test.pdf
bridge-gad lisp test_lisp_style_input.xlsx --output lisp_test.dxf
```

### Comprehensive Test Suite:
```bash
# Run all tests
for file in test_*.xlsx; do
    echo "Testing: $file"
    bridge-gad generate "$file" --output "results_${file%.xlsx}.dxf"
done
```

## ✅ Expected Results

Each test should produce:
1. **Valid output file** (DXF/PDF) without errors
2. **Proper scaling** according to configuration
3. **Correct geometry** for bridges, piers, abutments
4. **Professional appearance** with dimensions and labels
5. **Error-free execution** with informative messages

## 🐛 Common Issues to Test

1. **File Format Validation**: Ensure Excel files are properly formatted
2. **Parameter Range Validation**: Test boundary conditions
3. **Skew Angle Handling**: Verify trigonometric calculations
4. **Multi-span Coordination**: Check pier placement and span continuity
5. **Output Quality**: Validate DXF/PDF generation integrity

## 📊 Performance Benchmarks

- **Small Bridge**: < 5 seconds generation time
- **Medium Bridge**: < 15 seconds generation time  
- **Large Complex Bridge**: < 30 seconds generation time
- **Memory Usage**: < 500MB for largest configurations

Created by: Rajkumar Singh Chauhan
Email: crajkumarsingh@hotmail.com
