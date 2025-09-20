#!/usr/bin/env python3
"""
Test script for parameter loading from SweetWilledDocument files
"""

import os

def load_bridge_parameters_from_csv(file_path: str) -> dict:
    """Load bridge parameters from CSV file (misnamed as .xlsx)."""
    bridge_params = {}
    
    try:
        # Simple CSV parsing without pandas
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return bridge_params
            
        # Parse header
        header = lines[0].strip().split(',')
        
        # Check which format we have
        if 'Parameter' in header:
            # Format 1: Parameter,Value,Description
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    param = parts[0]
                    value = parts[1]
                    try:
                        bridge_params[param] = float(value)
                    except ValueError:
                        bridge_params[param] = value
        elif 'Variable' in header:
            # Format 2: Value,Variable,Description
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    value = parts[0]
                    variable = parts[1]
                    try:
                        bridge_params[variable] = float(value)
                    except ValueError:
                        bridge_params[variable] = value
        else:
            print(f"Unknown CSV format in {file_path}")
            return bridge_params
            
        print(f"Successfully loaded parameters from {file_path}")
        return bridge_params
        
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return bridge_params

def main():
    """Test parameter loading for all SweetWilledDocument files."""
    sweet_willed_files = [
        "SweetWilledDocument-01.xlsx",
        "SweetWilledDocument-02.xlsx", 
        "SweetWilledDocument-03.xlsx",
        "SweetWilledDocument-04.xlsx",
        "SweetWilledDocument-07.xlsx",
        "SweetWilledDocument-08.xlsx",
        "SweetWilledDocument-09.xlsx",
        "SweetWilledDocument-10.xlsx"
    ]
    
    print("Testing parameter loading from SweetWilledDocument files...")
    print("=" * 60)
    
    for file_name in sweet_willed_files:
        if os.path.exists(file_name):
            print(f"\nFile: {file_name}")
            params = load_bridge_parameters_from_csv(file_name)
            print(f"  Loaded {len(params)} parameters")
            if params:
                # Show first 5 parameters
                count = 0
                for key, value in params.items():
                    print(f"    {key}: {value}")
                    count += 1
                    if count >= 5:
                        print(f"    ... and {len(params) - 5} more")
                        break
        else:
            print(f"\nFile not found: {file_name}")

if __name__ == "__main__":
    main()