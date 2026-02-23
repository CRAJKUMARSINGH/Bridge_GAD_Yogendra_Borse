#!/usr/bin/env python3
"""
Fix Excel format for failed test files
Converts key-value format to the expected 3-column format
"""

import pandas as pd
from pathlib import Path

def convert_key_value_to_standard(input_file, output_file=None):
    """Convert key-value Excel format to standard 3-column format"""
    
    if output_file is None:
        output_file = input_file
    
    print(f"📝 Converting: {input_file}")
    
    # Read the key-value format
    df = pd.read_excel(input_file)
    
    # Check if it's key-value format
    if 'key' in df.columns and 'value' in df.columns:
        print("  → Detected key-value format")
        
        # Create standard 3-column format
        standard_df = pd.DataFrame({
            'Value': df['value'],
            'Variable': df['key'].str.upper(),
            'Description': df['key'].str.replace('_', ' ').str.title()
        })
        
        # Save without header (as expected by bridge_generator)
        standard_df.to_excel(output_file, index=False, header=False)
        print(f"  ✅ Converted to standard format: {output_file}")
        return True
        
    else:
        print("  ⚠️  Not a key-value format, checking other formats...")
        
        # Check if it's a simple data table (like spans.xlsx)
        if len(df.columns) >= 3:
            print("  → Detected multi-column data format")
            
            # Try to extract span information
            if 'Length (m)' in df.columns or 'Length' in str(df.columns[0]):
                print("  → Converting span data to standard format")
                
                # Create variables from the data
                variables = []
                
                # Add basic bridge parameters
                if 'Length (m)' in df.columns:
                    lengths = df['Length (m)'].dropna().tolist()
                    variables.append([sum(lengths), 'LBRIDGE', 'Total bridge length'])
                    variables.append([len(lengths), 'NSPAN', 'Number of spans'])
                    
                    for i, length in enumerate(lengths, 1):
                        variables.append([length, f'SPAN{i}', f'Span {i} length'])
                
                if 'Width (m)' in df.columns:
                    width = df['Width (m)'].iloc[0]
                    variables.append([width, 'CCBR', 'Carriageway width'])
                
                if 'Thickness (m)' in df.columns:
                    thickness = df['Thickness (m)'].iloc[0]
                    variables.append([thickness * 1000, 'SLABTH', 'Slab thickness (mm)'])
                
                if 'Pier_Width (m)' in df.columns or 'Pier Width (m)' in df.columns:
                    col = 'Pier_Width (m)' if 'Pier_Width (m)' in df.columns else 'Pier Width (m)'
                    pier_width = df[col].iloc[0]
                    variables.append([pier_width * 1000, 'PIERTW', 'Pier top width (mm)'])
                
                # Add default values for required parameters
                defaults = [
                    [186, 'SCALE1', 'Drawing scale for plans'],
                    [100, 'SCALE2', 'Drawing scale denominator'],
                    [0, 'SKEW', 'Degree of skew'],
                    [100, 'DATUM', 'Datum level'],
                    [110, 'TOPRL', 'Top RL of bridge'],
                    [7500, 'CCBR', 'Carriageway width (mm)'],
                    [250, 'SLABTH', 'Slab thickness (mm)'],
                    [1000, 'PIERTW', 'Pier top width (mm)'],
                ]
                
                # Add defaults that aren't already in variables
                existing_vars = [v[1] for v in variables]
                for default in defaults:
                    if default[1] not in existing_vars:
                        variables.append(default)
                
                # Create DataFrame
                standard_df = pd.DataFrame(variables, columns=['Value', 'Variable', 'Description'])
                
                # Save without header
                standard_df.to_excel(output_file, index=False, header=False)
                print(f"  ✅ Converted span data to standard format: {output_file}")
                return True
        
        print("  ❌ Unknown format, cannot convert")
        return False

def main():
    """Fix all failed Excel files"""
    print("\n" + "="*60)
    print("🔧 FIXING EXCEL FORMATS")
    print("="*60 + "\n")
    
    failed_files = [
        'inputs/real_lisp.xlsx',
        'inputs/spans.xlsx'
    ]
    
    success_count = 0
    
    for file in failed_files:
        if Path(file).exists():
            if convert_key_value_to_standard(file):
                success_count += 1
            print()
        else:
            print(f"⚠️  File not found: {file}\n")
    
    print("="*60)
    print(f"✅ Fixed {success_count}/{len(failed_files)} files")
    print("="*60 + "\n")
    
    return success_count == len(failed_files)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
