#!/usr/bin/env python3
"""
MANUAL APP DEBUGGING SOLUTION
Author: Rajkumar Singh Chauhan
Email: crajkumarsingh@hotmail.com
Purpose: Debug why Bridge apps are producing empty outputs
"""

import os
import sys
import pandas as pd
import traceback
from pathlib import Path
import json
from datetime import datetime

def debug_bridge_app(app_path, app_name, input_file=None):
    """Debug a specific Bridge application to identify output issues"""
    
    print(f"\n🔍 DEBUGGING: {app_name}")
    print("=" * 50)
    
    if not os.path.exists(app_path):
        print(f"❌ Directory not found: {app_path}")
        return {"app": app_name, "status": "DIR_NOT_FOUND", "issue": "Directory missing"}
    
    os.chdir(app_path)
    debug_info = {
        "app": app_name,
        "path": app_path,
        "timestamp": datetime.now().isoformat(),
        "files_found": [],
        "python_files": [],
        "input_files": [],
        "issues": [],
        "solutions": []
    }
    
    # Check what files exist
    all_files = os.listdir(".")
    python_files = [f for f in all_files if f.endswith('.py')]
    excel_files = [f for f in all_files if f.endswith('.xlsx')]
    
    debug_info["files_found"] = all_files
    debug_info["python_files"] = python_files
    debug_info["input_files"] = excel_files
    
    print(f"📁 Found {len(python_files)} Python files: {python_files}")
    print(f"📄 Found {len(excel_files)} Excel files: {excel_files}")
    
    # Test each Python file
    for py_file in python_files:
        if py_file in ['app.py', 'main.py', 'enhanced_bridge_app.py', 'bridge_design_app.py']:
            print(f"\n🔧 Testing: {py_file}")
            
            try:
                # Read and analyze the Python file
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for common issues
                issues = []
                solutions = []
                
                # Check 1: Import issues
                if 'import' in content:
                    print("   ✅ Has import statements")
                else:
                    issues.append("No import statements found")
                    solutions.append("Add necessary import statements")
                
                # Check 2: Command line arguments
                if 'sys.argv' in content or 'argparse' in content or 'click' in content:
                    print("   ✅ Has command line argument handling")
                    
                    # Test with input file if available
                    if input_file and os.path.exists(input_file):
                        print(f"   🔬 Testing with input: {input_file}")
                        
                        # Try to run the application
                        output_file = f"debug_output_{app_name}.dxf"
                        cmd = f'python {py_file} "{input_file}" "{output_file}"'
                        print(f"   🚀 Command: {cmd}")
                        
                        try:
                            import subprocess
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                            
                            if result.returncode == 0:
                                if os.path.exists(output_file):
                                    file_size = os.path.getsize(output_file)
                                    if file_size > 0:
                                        print(f"   ✅ SUCCESS: Output created ({file_size} bytes)")
                                        solutions.append(f"Working: Use {py_file} with {input_file}")
                                    else:
                                        print("   ⚠️  Output file is empty")
                                        issues.append("Generated file is empty")
                                        solutions.append("Check input data format and processing logic")
                                else:
                                    print("   ⚠️  No output file created")
                                    issues.append("No output file generated")
                                    solutions.append("Check output file path and permissions")
                            else:
                                print(f"   ❌ Error: {result.stderr}")
                                issues.append(f"Runtime error: {result.stderr}")
                                solutions.append("Fix runtime errors in application")
                                
                        except subprocess.TimeoutExpired:
                            print("   ⏰ Timeout: Application took too long")
                            issues.append("Application timeout")
                            solutions.append("Optimize application performance")
                        except Exception as e:
                            print(f"   ❌ Exception: {e}")
                            issues.append(f"Exception: {e}")
                            solutions.append("Debug and fix application exceptions")
                    
                else:
                    print("   ⚠️  No command line argument handling")
                    
                    # Try to run without arguments
                    try:
                        import subprocess
                        result = subprocess.run(f'python {py_file}', shell=True, capture_output=True, text=True, timeout=15)
                        
                        if result.returncode == 0:
                            print("   ✅ Runs without arguments")
                            if result.stdout:
                                print(f"   📤 Output: {result.stdout[:200]}...")
                                solutions.append(f"Working: Run {py_file} directly")
                        else:
                            print(f"   ❌ Error without args: {result.stderr}")
                            issues.append("Requires specific arguments or input")
                            solutions.append("Provide required arguments or modify to use defaults")
                            
                    except Exception as e:
                        print(f"   ❌ Exception running without args: {e}")
                        issues.append(f"Exception without args: {e}")
                
                # Check 3: Excel/data handling
                if 'pandas' in content or 'openpyxl' in content or 'xlrd' in content:
                    print("   ✅ Has Excel/data handling")
                    
                    if excel_files:
                        print(f"   📊 Available Excel files: {excel_files}")
                        
                        # Check Excel file structure
                        for excel_file in excel_files:
                            try:
                                df = pd.read_excel(excel_file)
                                print(f"      📋 {excel_file}: {df.shape[0]} rows, {df.shape[1]} columns")
                                print(f"      📋 Columns: {list(df.columns)[:5]}...")
                                
                                if df.empty:
                                    issues.append(f"Excel file {excel_file} is empty")
                                    solutions.append(f"Add data to {excel_file}")
                                else:
                                    solutions.append(f"Excel file {excel_file} has data - check column mapping")
                                    
                            except Exception as e:
                                print(f"      ❌ Error reading {excel_file}: {e}")
                                issues.append(f"Cannot read {excel_file}: {e}")
                                solutions.append(f"Fix Excel file format for {excel_file}")
                    else:
                        issues.append("No Excel files found but application expects them")
                        solutions.append("Create required Excel input files")
                else:
                    print("   ⚠️  No Excel/data handling detected")
                
                # Check 4: Output generation
                if 'ezdxf' in content or '.dxf' in content:
                    print("   ✅ Has DXF output capability")
                    solutions.append("Application can generate DXF files")
                elif 'matplotlib' in content or 'plt.' in content:
                    print("   ✅ Has plotting capability")
                    solutions.append("Application can generate plots")
                elif '.json' in content or 'json.' in content:
                    print("   ✅ Has JSON output capability")
                    solutions.append("Application can generate JSON files")
                else:
                    issues.append("No clear output format detected")
                    solutions.append("Add output file generation code")
                
                debug_info["issues"].extend(issues)
                debug_info["solutions"].extend(solutions)
                
            except Exception as e:
                print(f"   ❌ Error analyzing {py_file}: {e}")
                debug_info["issues"].append(f"Analysis error for {py_file}: {e}")
    
    return debug_info

def main():
    """Main debugging function"""
    
    print("🎯 BRILLIANT BRIDGE APP DEBUGGING SOLUTION")
    print("==========================================")
    
    # Define applications to debug
    apps_to_debug = [
        {"name": "BridgeGAD-00", "path": "C:/Users/Rajkumar/BridgeGAD-00", "input": "sample_input.xlsx"},
        {"name": "BridgeGAD-03", "path": "C:/Users/Rajkumar/BridgeGAD-03", "input": "input.xlsx"},
        {"name": "BridgeGAD-04", "path": "C:/Users/Rajkumar/BridgeGAD-04", "input": "bridge_parameters_template.xlsx"},
        {"name": "BridgeGAD-06", "path": "C:/Users/Rajkumar/BridgeGAD-06", "input": "input.xlsx"},
        {"name": "Bridge_Slab_Design", "path": "C:/Users/Rajkumar/Bridge_Slab_Design", "input": "variable_mapping.xlsx"},
    ]
    
    debug_results = []
    
    for app in apps_to_debug:
        result = debug_bridge_app(app["path"], app["name"], app.get("input"))
        debug_results.append(result)
    
    # Save debug results
    output_dir = "C:/Users/Rajkumar/BridgeGAD-00"
    timestamp = datetime.now().strftime("%d_%m_%Y_%H%M")
    results_file = f"{output_dir}/DEBUG_RESULTS_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(debug_results, f, indent=2, default=str)
    
    print(f"\n📊 DEBUG RESULTS SUMMARY:")
    print("=" * 40)
    
    for result in debug_results:
        print(f"\n🔧 {result['app']}:")
        if result.get('issues'):
            print(f"   ❌ Issues: {len(result['issues'])}")
            for issue in result['issues'][:3]:  # Show first 3 issues
                print(f"      - {issue}")
        
        if result.get('solutions'):
            print(f"   ✅ Solutions: {len(result['solutions'])}")
            for solution in result['solutions'][:3]:  # Show first 3 solutions
                print(f"      - {solution}")
    
    print(f"\n📁 Full debug results saved to: {results_file}")
    print("\n🎯 DEBUGGING COMPLETED!")
    
    return debug_results

if __name__ == "__main__":
    main()