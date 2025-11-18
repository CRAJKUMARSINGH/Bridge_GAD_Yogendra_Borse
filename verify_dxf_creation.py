#!/usr/bin/env python3
"""
Verification script for DXF creation functionality
"""

def test_dxf_creation():
    """Test DXF creation with enhanced features."""
    print("Testing DXF creation functionality...")
    
    # Test basic DXF creation
    try:
        import ezdxf
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
        layer = doc.layers.add("TEST_LAYER")
        layer.dxf.color = 1
        print("✓ Layer creation successful")
    except Exception as e:
        print(f"✗ Layer creation failed: {e}")
        return False
    
    # Test entity creation
    try:
        # Add a line
        line = msp.add_line((0, 0), (100, 100))
        
        # Add text
        text = msp.add_text("Test Text", dxfattribs={"height": 10})
        text.set_placement((50, 50))
        
        # Add polyline
        points = [(0, 0), (100, 0), (100, 100), (0, 100)]
        polyline = msp.add_lwpolyline(points, close=True)
        
        print("✓ Entity creation successful")
    except Exception as e:
        print(f"✗ Entity creation failed: {e}")
        return False
    
    # Test dimension style creation
    try:
        if "TEST_DIM" not in doc.dimstyles:
            dimstyle = doc.dimstyles.add("TEST_DIM")
            dimstyle.dxf.dimtxt = 2.5
            dimstyle.dxf.dimasz = 1.0
        print("✓ Dimension style creation successful")
    except Exception as e:
        print(f"✗ Dimension style creation failed: {e}")
        return False
    
    # Test saving
    try:
        doc.saveas("test_output.dxf")
        print("✓ DXF saving successful")
        
        # Clean up
        import os
        if os.path.exists("test_output.dxf"):
            os.remove("test_output.dxf")
    except Exception as e:
        print(f"✗ DXF saving failed: {e}")
        return False
    
    print("All DXF creation tests passed!")
    return True

if __name__ == "__main__":
    success = test_dxf_creation()
    if success:
        print("\n✓ DXF creation verification completed successfully!")
    else:
        print("\n✗ DXF creation verification failed!")
        exit(1)