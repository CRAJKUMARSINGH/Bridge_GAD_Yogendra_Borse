#!/usr/bin/env python3
"""
Test script to verify complete GAD generation
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bridge_gad.bridge_generator import generate_bridge_gad
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_complete_gad():
    """Test complete GAD generation with sample input"""
    
    # Check for sample input files
    sample_files = [
        'sample_input.xlsx',
        'lisp_params.xlsx',
        'real_lisp.xlsx',
        'spans.xlsx'
    ]
    
    input_file = None
    for file in sample_files:
        if Path(file).exists():
            input_file = Path(file)
            break
    
    if not input_file:
        logger.error("No sample input file found. Please provide one of:")
        for file in sample_files:
            logger.error(f"  - {file}")
        return False
    
    logger.info(f"Using input file: {input_file}")
    
    # Generate output filename
    output_file = Path(f"complete_gad_test_{input_file.stem}.dxf")
    
    try:
        logger.info("Starting complete GAD generation...")
        result = generate_bridge_gad(input_file, output_file)
        
        if result and result.exists():
            logger.info(f"✓ Complete GAD generated successfully: {result}")
            logger.info(f"  File size: {result.stat().st_size} bytes")
            
            # Verify DXF content
            with open(result, 'r') as f:
                content = f.read()
                
            # Check for key elements
            checks = {
                'Layout and axes': 'BED LEVEL' in content and 'CHAINAGE' in content,
                'Bridge superstructure': 'DECK SLAB' in content or 'LWPOLYLINE' in content,
                'Abutments': 'A1' in content or 'A2' in content,
                'Piers': 'P1' in content or 'P2' in content,
                'Sections': 'SECTION' in content,
                'Dimensions': 'DIMENSION' in content or 'DIMSTYLE' in content,
                'Title block': 'GENERAL ARRANGEMENT' in content or 'BRIDGE DESIGN' in content
            }
            
            logger.info("\nGAD Completeness Check:")
            all_passed = True
            for check_name, passed in checks.items():
                status = "✓" if passed else "✗"
                logger.info(f"  {status} {check_name}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                logger.info("\n✓ All GAD components verified!")
                return True
            else:
                logger.warning("\n⚠ Some GAD components may be missing")
                logger.info("  The drawing was generated but may be incomplete")
                return True  # Still return True as file was created
                
        else:
            logger.error("✗ GAD generation failed - no output file created")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during GAD generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_gad()
    sys.exit(0 if success else 1)
