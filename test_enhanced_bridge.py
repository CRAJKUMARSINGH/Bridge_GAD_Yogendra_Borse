#!/usr/bin/env python3
"""
Test script for the enhanced bridge GAD generator
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_dxf_creation():
    """Test that DXF creation works without errors."""
    try:
        import ezdxf
        # Test basic DXF creation
        doc = ezdxf.new("R2010", setup=True)  # type: ignore
        msp = doc.modelspace()
        
        # Test adding a simple line
        msp.add_line((0, 0), (100, 100))
        
        # Test adding text
        msp.add_text("Test", dxfattribs={"height": 10}).set_placement((50, 50))
        
        # Test creating layers
        if "TEST_LAYER" not in doc.layers:
            layer = doc.layers.add("TEST_LAYER")
            layer.dxf.color = 2
            
        print("✓ DXF creation test passed")
        return True
    except Exception as e:
        print(f"✗ DXF creation test failed: {e}")
        return False

def test_bridge_functions():
    """Test that bridge drawing functions work."""
    try:
        # Import the main module
        import simple_bridge_app
        
        # Test initialization
        simple_bridge_app.init_derived()
        
        # Test coordinate functions
        x_pos = simple_bridge_app.hpos(10.0)
        y_pos = simple_bridge_app.vpos(105.0)
        
        # Test point creation
        point = simple_bridge_app.pt(10.0, 105.0)
        
        print("✓ Bridge functions test passed")
        return True
    except Exception as e:
        print(f"✗ Bridge functions test failed: {e}")
        return False

def test_parameter_loading():
    """Test parameter loading functionality."""
    try:
        # Create a sample CSV file for testing
        sample_csv = """Value,Variable,Description
100.0,SCALE1,Scale factor for plan and elevation
50.0,SCALE2,Scale factor for sections
0.0,SKEW,Skew angle in degrees
100.0,DATUM,Datum level
110.0,TOPRL,Top level on Y axis
0.0,LEFT,Starting chainage of X axis
20.0,RIGHT,End chainage of X axis
5.0,XINCR,Interval of distances on X axis
1.0,YINCR,Interval of levels on Y axis
4,NOCH,Total number of chainages
1,NSPAN,Number of spans
20.0,LBRIDGE,Length of bridge
0.0,ABTL,Chainage of left abutment
105.0,RTL,Road top level
103.0,Sofl,Soffit level
0.3,KERBW,Width of kerb
0.2,KERBD,Depth of kerb
7.5,CCBR,Clear carriageway width
0.2,SLBTHC,Thickness of slab at center
0.15,SLBTHE,Thickness of slab at edge
0.1,SLBTHT,Thickness of slab at tip
104.0,CAPT,Pier cap top RL
103.5,CAPB,Pier cap bottom RL
1.0,CAPW,Cap width
1.0,PIERTW,Pier top width
10.0,BATTR,Pier batter
8.0,PIERST,Straight length of pier
1,PIERN,Pier serial number
20.0,SPAN1,Span individual length
95.0,FUTRL,Founding RL
1.0,FUTD,Depth of footing
3.0,FUTW,Width of footing
6.0,FUTL,Length of footing
0.3,DWTH,Dirtwall thickness
1.0,ALCW,Abutment left cap width
1.0,ALCD,Abutment left cap depth
10.0,ALFB,Abutment left front batter
101.0,ALFBL,Abutment left front batter RL
10.0,ALTB,Abutment left toe batter
100.5,ALTBL,Abutment left toe batter level
0.5,ALFO,Abutment left front offset
1.0,ALFD,Abutment left footing depth
8.0,ALBB,Abutment left back batter
101.5,ALBBL,Abutment left back batter RL
101.0,ALFBR,Abutment right front batter RL
100.5,ALTBR,Abutment right toe batter level
101.5,ALBBR,Abutment right back batter RL
95.0,ARFL,Abutment right footing level"""
        
        # Write sample CSV file
        with open("test_params.csv", "w") as f:
            f.write(sample_csv)
        
        # Import and test parameter loading
        import simple_bridge_app
        result = simple_bridge_app.load_bridge_parameters_from_csv("test_params.csv")
        
        # Clean up
        if os.path.exists("test_params.csv"):
            os.remove("test_params.csv")
        
        if result:
            print("✓ Parameter loading test passed")
            return True
        else:
            print("✗ Parameter loading test failed")
            return False
            
    except Exception as e:
        # Clean up
        if os.path.exists("test_params.csv"):
            os.remove("test_params.csv")
        print(f"✗ Parameter loading test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running enhanced bridge GAD tests...")
    print("=" * 50)
    
    tests = [
        test_dxf_creation,
        test_bridge_functions,
        test_parameter_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())