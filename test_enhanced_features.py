#!/usr/bin/env python3
"""
Test Script for Enhanced BridgeGAD Features

This script tests the new object-oriented architecture and enhanced features
to ensure they work correctly and integrate properly with the existing system.
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if enhanced modules can be imported"""
    try:
        from src.bridge_gad import (
            BridgeType,
            OutputFormat, 
            MaterialType,
            BridgeParameters,
            BridgeDrawingGenerator,
            create_slab_bridge
        )
        logger.info("✓ All enhanced modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_parameter_creation():
    """Test parameter creation and validation"""
    try:
        from src.bridge_gad import create_slab_bridge, BridgeType, MaterialType
        
        # Test basic parameter creation
        params = create_slab_bridge(
            span_length=20.0,  # Valid span for slab bridge
            deck_width=8.0,
            project_name="Test Bridge"
        )
        
        assert params.bridge_type == BridgeType.SLAB
        assert params.span_length == 20.0
        assert params.deck_width == 8.0
        assert params.material == MaterialType.CONCRETE
        
        logger.info("✓ Parameter creation and validation works")
        return True
    except Exception as e:
        logger.error(f"✗ Parameter creation failed: {e}")
        return False

def test_drawing_generator():
    """Test drawing generator functionality"""
    try:
        from src.bridge_gad import (
            BridgeDrawingGenerator,
            create_slab_bridge,
            OutputFormat
        )
        
        # Create test parameters
        params = create_slab_bridge(
            span_length=25.0,
            deck_width=7.5,
            project_name="Test Generator",
            drawing_title="Test Drawing"
        )
        
        # Create generator
        generator = BridgeDrawingGenerator(params)
        
        # Test DXF generation
        result = generator.generate_drawing([OutputFormat.DXF])
        
        assert OutputFormat.DXF in result
        assert os.path.exists(result[OutputFormat.DXF])
        
        logger.info(f"✓ Drawing generator created: {result[OutputFormat.DXF]}")
        return True
    except Exception as e:
        logger.error(f"✗ Drawing generator failed: {e}")
        return False

def test_coordinate_transformations():
    """Test coordinate transformation functions"""
    try:
        from src.bridge_gad import create_slab_bridge
        
        params = create_slab_bridge(
            span_length=15.0,  # Valid span for slab bridge
            deck_width=8.0,
            scale1=100.0,
            scale2=50.0,
            datum=100000.0
        )
        
        transforms = params.get_coordinate_transformations()
        
        # Test transformations
        test_val = 105000.0
        vpos_result = transforms['vpos'](test_val)
        hpos_result = transforms['hpos'](test_val)
        
        assert isinstance(vpos_result, float)
        assert isinstance(hpos_result, float)
        
        logger.info("✓ Coordinate transformations work correctly")
        return True
    except Exception as e:
        logger.error(f"✗ Coordinate transformations failed: {e}")
        return False

def test_backward_compatibility():
    """Test that existing app.py functions still work"""
    try:
        # Import existing app functions
        import app
        
        # Test that basic functions exist
        assert hasattr(app, 'save_dxf')
        assert hasattr(app, 'save_pdf')
        assert hasattr(app, 'setup')
        
        logger.info("✓ Backward compatibility maintained")
        return True
    except Exception as e:
        logger.error(f"✗ Backward compatibility test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    tests = [
        ("Import Test", test_imports),
        ("Parameter Creation", test_parameter_creation), 
        ("Drawing Generator", test_drawing_generator),
        ("Coordinate Transformations", test_coordinate_transformations),
        ("Backward Compatibility", test_backward_compatibility)
    ]
    
    results = []
    logger.info("=" * 50)
    logger.info("BridgeGAD Enhanced Features Test Suite")
    logger.info("=" * 50)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name:25s} : {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("-" * 50)
    logger.info(f"Total: {len(results)}, Passed: {passed}, Failed: {failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed! Enhanced features are working correctly.")
        return True
    else:
        logger.warning(f"⚠️  {failed} test(s) failed. Some features may not work correctly.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
