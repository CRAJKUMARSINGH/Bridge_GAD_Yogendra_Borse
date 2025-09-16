#!/usr/bin/env python3
"""
Comprehensive Test Input File Generator for All BridgeGAD Applications
Creates various test scenarios with different bridge configurations
Author: Rajkumar Singh Chauhan
Email: crajkumarsingh@hotmail.com
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def create_comprehensive_test_inputs():
    """Create comprehensive test input files for all BridgeGAD applications"""
    
    # Create output directory
    output_dir = Path("Sample_test_input_files")
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 Creating Comprehensive Test Input Files for All BridgeGAD Applications")
    print("=" * 80)
    
    # Test Case 1: Small Single Span Bridge
    print("📄 Creating Test Case 1: Small Single Span Bridge")
    small_bridge_data = {
        'Parameter': [
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT',
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL',
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN',
            'SPAN1', 'FUTRL', 'FUTD', 'FUTW', 'FUTL'
        ],
        'Value': [
            100, 50, 0, 100, 110, 0, 30, 5, 1, 7,  # Basic layout
            1, 20, 0, 108, 106.5, 0.5, 0.15, 7.5, 0.25, 0.20, 0.15,  # Bridge geometry
            107.5, 106.5, 2.0, 1.0, 4, 2.0, 1,  # Pier/abutment
            20, 104, 2.0, 3.0, 4.0  # Span and foundation
        ]
    }
    small_bridge_df = pd.DataFrame(small_bridge_data)
    small_bridge_df.to_excel(output_dir / "test_bridge_small_single_span.xlsx", index=False)
    
    # Test Case 2: Medium Multi-Span Bridge
    print("📄 Creating Test Case 2: Medium Multi-Span Bridge")
    medium_bridge_data = {
        'Parameter': [
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT',
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL',
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN',
            'SPAN1', 'FUTRL1', 'FUTD1', 'FUTW1', 'FUTL1',
            'SPAN2', 'FUTRL2', 'FUTD2', 'FUTW2', 'FUTL2',
            'SPAN3', 'FUTRL3', 'FUTD3', 'FUTW3', 'FUTL3'
        ],
        'Value': [
            100, 50, 15, 100, 115, 0, 80, 10, 2, 9,  # Basic layout with skew
            3, 75, 0, 113, 111.5, 0.5, 0.15, 8.5, 0.30, 0.25, 0.15,  # Bridge geometry
            112.5, 111.5, 2.5, 1.2, 4, 3.0, 2,  # Pier/abutment
            25, 102, 2.5, 3.5, 5.0,  # Span 1
            25, 101, 3.0, 4.0, 5.5,  # Span 2
            25, 100, 3.5, 4.5, 6.0   # Span 3
        ]
    }
    medium_bridge_df = pd.DataFrame(medium_bridge_data)
    medium_bridge_df.to_excel(output_dir / "test_bridge_medium_multi_span.xlsx", index=False)
    
    # Test Case 3: Large Complex Bridge with Skew
    print("📄 Creating Test Case 3: Large Complex Bridge with Skew")
    large_bridge_data = {
        'Parameter': [
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT',
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL',
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN'
        ],
        'Value': [
            200, 100, 30, 100, 120, 0, 150, 15, 2, 11,  # Large scale with significant skew
            4, 140, 0, 118, 116.5, 0.6, 0.20, 12.0, 0.40, 0.35, 0.20,  # Large bridge geometry
            117.5, 116.5, 3.0, 1.5, 3, 4.0, 3  # Heavy pier/abutment
        ]
    }
    large_bridge_df = pd.DataFrame(large_bridge_data)
    large_bridge_df.to_excel(output_dir / "test_bridge_large_complex_skew.xlsx", index=False)
    
    # Test Case 4: LISP-style Input with Cross-section Data
    print("📄 Creating Test Case 4: LISP-style Input with Cross-section Data")
    lisp_data = {
        'Parameter': ['scale1', 'scale2', 'skew', 'datum', 'toprl', 'left', 'right', 'xincr', 'yincr', 'noch'],
        'Value': [100, 100, 0, 100, 110, 0, 50, 10, 1, 6]
    }
    
    # Add cross-section data
    cross_section_data = []
    chainages = [0, 10, 20, 30, 40, 50]
    base_level = 98.5
    for i, ch in enumerate(chainages):
        cross_section_data.extend([
            {'Parameter': f'chainage_{i+1}', 'Value': ch},
            {'Parameter': f'level_{i+1}', 'Value': base_level + np.random.uniform(-1, 2)}
        ])
    
    # Convert lisp_data to list format to match cross_section_data
    lisp_data_list = [{'Parameter': k, 'Value': v} for k, v in zip(lisp_data['Parameter'], lisp_data['Value'])]
    lisp_df = pd.DataFrame(lisp_data_list + cross_section_data)
    lisp_df.to_excel(output_dir / "test_lisp_style_input.xlsx", index=False)
    
    # Test Case 5: Minimal Configuration Test
    print("📄 Creating Test Case 5: Minimal Configuration Test")
    minimal_data = {
        'Parameter': ['NSPAN', 'SPAN1', 'CCBR', 'DATUM', 'TOPRL'],
        'Value': [1, 15, 7.5, 100, 105]
    }
    minimal_df = pd.DataFrame(minimal_data)
    minimal_df.to_excel(output_dir / "test_minimal_config.xlsx", index=False)
    
    # Test Case 6: Stress Test with Maximum Parameters
    print("📄 Creating Test Case 6: Stress Test with Maximum Parameters")
    max_params = {
        'Parameter': [
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT',
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL',
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN',
            'DWTH', 'ALCW', 'ALCD', 'ALFB', 'ALFBL', 'ALTB', 'ALTBL',
            'ALFO', 'ALFD', 'ALBB', 'ALBBL', 'ARCW', 'ARCD', 'ARFB',
            'ARFBL', 'ARTB', 'ARTBL', 'ARFO', 'ARFD', 'ARBB', 'ARBBL'
        ],
        'Value': [
            # Scale and layout
            500, 250, 45, 100, 125, 0, 200, 20, 5, 15,
            # Bridge configuration
            5, 180, 10, 123, 121.5, 0.75, 0.25, 14.0, 0.50, 0.40, 0.25,
            # Pier configuration
            122.5, 121.5, 4.0, 2.0, 2.5, 5.0, 4,
            # Left abutment details
            1.5, 3.0, 1.0, 3, 115, 4, 110, 2.0, 3.0, 2, 118,
            # Right abutment details
            3.0, 1.0, 3, 115, 4, 110, 2.0, 3.0, 2, 118
        ]
    }
    max_params_df = pd.DataFrame(max_params)
    max_params_df.to_excel(output_dir / "test_stress_max_parameters.xlsx", index=False)
    
    # Create YAML configuration files
    print("📄 Creating YAML Configuration Files")
    yaml_configs = {
        'config_small.yaml': {
            'bridge': {'scale': 100, 'output_format': 'dxf'},
            'drawing': {'title': 'Small Bridge Test', 'units': 'mm'}
        },
        'config_medium.yaml': {
            'bridge': {'scale': 100, 'output_format': 'pdf'},
            'drawing': {'title': 'Medium Bridge Test', 'units': 'mm', 'layers': True}
        },
        'config_large.yaml': {
            'bridge': {'scale': 200, 'output_format': 'both'},
            'drawing': {'title': 'Large Bridge Test', 'units': 'mm', 'detailed': True}
        }
    }
    
    import yaml
    for filename, config in yaml_configs.items():
        with open(output_dir / filename, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    print("\n✅ Comprehensive Test Input Files Created Successfully!")
    print(f"📁 Location: {output_dir.absolute()}")
    print("\n📋 Generated Files:")
    for file in output_dir.glob("*"):
        print(f"   📄 {file.name}")
    
    return output_dir

def create_test_documentation():
    """Create comprehensive test documentation"""
    
    doc_content = """# 📋 BridgeGAD Test Input Files Documentation

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
"""
    
    with open("Sample_test_input_files/README_TEST_FILES.md", "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    print("📚 Test documentation created: README_TEST_FILES.md")

if __name__ == "__main__":
    create_comprehensive_test_inputs()
    create_test_documentation()
    print("\n🎉 All test files and documentation created successfully!")