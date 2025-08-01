"""Script to generate test data files for the Bridge GAD Generator."""

import pandas as pd
from pathlib import Path

# Create test data directory if it doesn't exist
test_data_dir = Path(__file__).parent / "test_data"
test_data_dir.mkdir(exist_ok=True)

def generate_test_excel():
    """Generate a test Excel file with bridge parameters."""
    # Test data for the Excel file
    test_data = {
        'Parameter': [
            'SCALE1', 'SCALE2', 'SKEW', 'DATUM', 'TOPRL', 'LEFT', 'RIGHT', 
            'XINCR', 'YINCR', 'NOCH', 'NSPAN', 'LBRIDGE', 'ABTL', 'RTL', 
            'SOFL', 'KERBW', 'KERBD', 'CCBR', 'SLBTHC', 'SLBTHE', 'SLBTHT',
            'CAPT', 'CAPB', 'CAPW', 'PIERTW', 'BATTR', 'PIERST', 'PIERN',
            'SPAN1', 'FUTRL', 'FUTD', 'FUTW', 'FUTL', 'LASLAB', 'APWTH',
            'APTHK', 'WCTH'
        ],
        'Value': [
            100.0, 100.0, 0.0, 100.0, 105.0, 0.0, 100.0, 10.0, 1.0, 10, 3, 95.0,
            2.5, 104.0, 103.5, 0.3, 0.3, 7.0, 0.2, 0.25, 0.15, 103.0, 102.0, 1.5,
            1.2, 1.5, 1.0, 1, 30.0, 95.0, 0.5, 2.0, 1.5, 5.0, 8.0, 0.2, 0.075
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Save to Excel
    output_file = test_data_dir / "test_bridge_data.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bridge Parameters')
    
    print(f"Generated test Excel file: {output_file}")

def generate_test_config():
    """Generate a test configuration YAML file."""
    config_content = """# Test configuration for Bridge GAD Generator

drawing:
  paper_size: A3
  orientation: landscape
  scale: 100

bridge:
  spans: 3
  span_lengths: [30.0, 35.0, 30.0]
  deck_width: 10.5
  num_girders: 5
  girder_spacing: 2.5
  girder_depth: 1.5
  abutment_width: 1.2
  pier_width: 1.0
  pier_height: 5.0

output:
  format: dxf
  directory: output
  layers:
    outline: "BRIDGE_OUTLINE"
    dimensions: "DIMENSIONS"
    text: "TEXT"
    centerline: "CENTERLINE"
"""
    output_file = test_data_dir / "test_config.yaml"
    output_file.write_text(config_content)
    print(f"Generated test config file: {output_file}")

if __name__ == "__main__":
    generate_test_excel()
    generate_test_config()
    print("Test data generation complete.")
