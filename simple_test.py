import math
import os
import pandas as pd
import ezdxf

# Read the Excel file with proper error handling
def read_excel_safely():
    try:
        file_path = r'c:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES\input.xlsx'
        df = pd.read_excel(file_path)
        print("Excel file read successfully!")
        print("Columns:", df.columns.tolist())
        print("Number of rows:", len(df))
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

# Test the enhanced bridge app
def test_enhanced_app():
    print("Testing Enhanced Bridge GAD Generator...")
    try:
        # Try to import and run the enhanced app
        import enhanced_bridge_app
        print("Enhanced bridge app imported successfully!")
        return True
    except Exception as e:
        print(f"Error importing enhanced bridge app: {e}")
        return False

# Test the main app
def test_main_app():
    print("Testing main bridge app...")
    try:
        # Try to import and run the main app
        import app
        print("Main bridge app imported successfully!")
        return True
    except Exception as e:
        print(f"Error importing main bridge app: {e}")
        return False

if __name__ == "__main__":
    print("=== Bridge GAD Generator Test ===")
    
    # Test Excel reading
    print("\n1. Testing Excel file reading:")
    df = read_excel_safely()
    
    # Test enhanced app
    print("\n2. Testing enhanced app:")
    test_enhanced_app()
    
    # Test main app
    print("\n3. Testing main app:")
    test_main_app()
    
    print("\n=== Test Complete ===")