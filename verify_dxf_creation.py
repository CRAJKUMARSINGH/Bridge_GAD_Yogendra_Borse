#!/usr/bin/env python3
"""
Verification script for DXF creation functionality
"""

import ezdxf
from datetime import datetime

def test_dxf_creation():
    """Test DXF creation with enhanced features."""
    print("Testing DXF creation functionality...")
    
    # Test basic DXF creation
    try:
        doc = ezdxf.new("R2010", setup=True)  # type: ignore
        print("✓ Basic DXF creation successful")
    except Exception as e:
        print(f"✗ Basic DXF creation failed: {e}")
        return False
    
    # Test modelspace access
    try:
        msp = doc.modelspace()
        print("✓ Modelspace access successful")
    except Exception as e:
        print(f"✗ Modelspace access failed: {e}")
        return False
    
    # Test layer creation
    try:
        layer = doc.layers.add(name="TEST_LAYER")
        layer.dxf.color = 1
        print("✓ Layer creation successful")
    except Exception as e:
        print(f"✗ Layer creation failed: {e}")
        return False
    
    # Test entity creation
    try:
        msp.add_line((0, 0), (100, 100))
        print("✓ Entity creation successful")
    except Exception as e:
        print(f"✗ Entity creation failed: {e}")
        return False
    
    # Test dimension style creation
    try:
        if "TEST_STYLE" not in doc.dimstyles:
            dimstyle = doc.dimstyles.add("TEST_STYLE")
            dimstyle.dxf.dimtxt = 200
            dimstyle.dxf.dimasz = 100
        print("✓ Dimension style creation successful")
    except Exception as e:
        print(f"✗ Dimension style creation failed: {e}")
        return False
    
    # Test saving
    try:
        filename = f"test_dxf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf"
        doc.saveas(filename)
        print(f"✓ DXF saving successful: {filename}")
    except Exception as e:
        print(f"✗ DXF saving failed: {e}")
        return False
    
    print("All DXF creation tests passed!")
    return True

if __name__ == "__main__":
    test_dxf_creation()