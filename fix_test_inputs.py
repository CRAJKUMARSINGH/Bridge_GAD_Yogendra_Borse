#!/usr/bin/env python3
"""
Fix Test Input Files to Match Expected Format
Creates proper 3-column format based on working sample_input.xlsx
"""

import pandas as pd
import shutil
from pathlib import Path

def fix_test_input_format():
    """Fix the test input files to match the expected 3-column format"""
    
    # Read the working sample to understand the format
    sample_df = pd.read_excel('sample_input.xlsx')
    print("Working sample format:")
    print(f"Columns: {sample_df.columns.tolist()}")
    print(f"Shape: {sample_df.shape}")
    
    # Create corrected test files
    output_dir = Path("Sample_test_input_files")
    
    # Test Case 1: Small Single Span Bridge (corrected format)
    small_bridge_data = {
        sample_df.columns[0]: [  # First column (numeric values)
            100, 100, 0, 100, 110, 0, 50, 10, 1, 7,  # Basic parameters
            1, 20, 0, 108, 106.5, 0.5, 0.15, 7.5, 0.25, 0.20, 0.15,  # Bridge
            107.5, 106.5, 2.0, 1.0, 4, 2.0, 1,  # Pier
            20, 104, 2.0, 3.0, 4.0  # Foundation
        ],
        sample_df.columns[1]: [  # Second column (parameter names)
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT',
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL',
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN',
            'SPAN1', 'FUTRL', 'FUTD', 'FUTW', 'FUTL'
        ],
        sample_df.columns[2]: [  # Third column (descriptions)
            'Drawing scale for plans and elevations',
            'Drawing scale for sections',
            'Degree of skew in plan of the bridge',
            'Datum level for the drawing',
            'Top RL of the bridge',
            'Left most chainage of the bridge',
            'Right most chainage of the bridge',
            'Interval of distances on X-axis (m)',
            'Interval of levels on Y-axis (m)',
            'Total number of chainages on cross-section',
            'Number of spans',
            'Length of bridge',
            'Chainage of left abutment',
            'RL of top of right abutment',
            'Soffit level',
            'Width of kerb at deck top',
            'Depth of kerb above deck top',
            'Clear carriageway width of bridge',
            'Thickness of slab at center',
            'Thickness of slab at edge',
            'Thickness of slab at tip',
            'RL of pier cap top',
            'RL of pier cap bottom',
            'Width of pier cap',
            'Width of pier top',
            'Pier batter',
            'Straight length of pier',
            'Serial number of pier for cross-section',
            'Span 1 length',
            'Founding RL of pier foundation',
            'Depth of pier foundation',
            'Width of rectangular pier foundation',
            'Length of pier foundation'
        ]
    }
    
    small_df = pd.DataFrame(small_bridge_data)
    small_df.to_excel(output_dir / "test_small_bridge_CORRECTED.xlsx", index=False)
    
    # Test Case 2: Multi-span bridge
    multi_span_data = {
        sample_df.columns[0]: [
            100, 100, 15, 100, 115, 0, 80, 10, 2, 9,
            3, 75, 0, 113, 111.5, 0.5, 0.15, 8.5, 0.30, 0.25, 0.15,
            112.5, 111.5, 2.5, 1.2, 4, 3.0, 2,
            25, 102, 2.5, 3.5, 5.0,  # Span 1
            25, 101, 3.0, 4.0, 5.5,  # Span 2  
            25, 100, 3.5, 4.5, 6.0   # Span 3
        ],
        sample_df.columns[1]: [
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT',
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL',
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN',
            'SPAN1', 'FUTRL1', 'FUTD1', 'FUTW1', 'FUTL1',
            'SPAN2', 'FUTRL2', 'FUTD2', 'FUTW2', 'FUTL2',
            'SPAN3', 'FUTRL3', 'FUTD3', 'FUTW3', 'FUTL3'
        ],
        sample_df.columns[2]: [
            'Drawing scale for plans and elevations',
            'Drawing scale for sections',
            'Degree of skew in plan (15 degrees)',
            'Datum level for the drawing',
            'Top RL of the bridge',
            'Left most chainage of the bridge',
            'Right most chainage of the bridge',
            'Interval of distances on X-axis (m)',
            'Interval of levels on Y-axis (m)',
            'Total number of chainages on cross-section',
            'Number of spans (3)',
            'Length of bridge',
            'Chainage of left abutment',
            'RL of top of right abutment',
            'Soffit level',
            'Width of kerb at deck top',
            'Depth of kerb above deck top',
            'Clear carriageway width of bridge',
            'Thickness of slab at center',
            'Thickness of slab at edge',
            'Thickness of slab at tip',
            'RL of pier cap top',
            'RL of pier cap bottom',
            'Width of pier cap',
            'Width of pier top',
            'Pier batter',
            'Straight length of pier',
            'Serial number of pier for cross-section',
            'Span 1 length',
            'Founding RL of pier 1 foundation',
            'Depth of pier 1 foundation',
            'Width of pier 1 foundation',
            'Length of pier 1 foundation',
            'Span 2 length',
            'Founding RL of pier 2 foundation',
            'Depth of pier 2 foundation',
            'Width of pier 2 foundation',
            'Length of pier 2 foundation',
            'Span 3 length',
            'Founding RL of pier 3 foundation',
            'Depth of pier 3 foundation',
            'Width of pier 3 foundation',
            'Length of pier 3 foundation'
        ]
    }
    
    multi_df = pd.DataFrame(multi_span_data)
    multi_df.to_excel(output_dir / "test_multi_span_bridge_CORRECTED.xlsx", index=False)
    
    print("✅ Corrected test input files created:")
    print("   📄 test_small_bridge_CORRECTED.xlsx")
    print("   📄 test_multi_span_bridge_CORRECTED.xlsx")

if __name__ == "__main__":
    fix_test_input_format()