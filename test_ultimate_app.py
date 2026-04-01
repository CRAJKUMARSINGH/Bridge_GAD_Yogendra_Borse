#!/usr/bin/env python3
"""
Ultimate Bridge GAD Generator - Comprehensive Test Suite
Tests the app with all available input files and generates date-stamped outputs
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def get_timestamp():
    """Get formatted timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_readable_timestamp():
    """Get readable timestamp for reports"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_outputs_folder():
    """Create outputs folder if it doesn't exist"""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    return outputs_dir

def test_drawing_generation():
    """Test drawing generation with all available input files"""
    print("\n" + "="*70)
    print("🧪 ULTIMATE BRIDGE GAD GENERATOR - COMPREHENSIVE TEST SUITE")
    print("="*70 + "\n")
    
    # Import required modules
    try:
        from bridge_gad.bridge_generator import BridgeGADGenerator
        # FIX REPLIT-005: generate_bridge_gad does not exist; use generate_complete_drawing
        from bridge_gad.enhanced_io_utils import SmartInputProcessor
        print("✅ Modules imported successfully\n")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False, []
    
    # Ensure outputs folder exists
    outputs_dir = ensure_outputs_folder()
    print(f"✅ Outputs folder ready: {outputs_dir.absolute()}\n")
    
    # Get timestamp for this test run
    test_timestamp = get_timestamp()
    
    # Find all Excel input files
    inputs_dir = Path("inputs")
    test_files = list(inputs_dir.glob("*.xlsx"))
    
    if not test_files:
        print("❌ No input files found in inputs/ folder")
        return False, []
    
    print(f"📁 Found {len(test_files)} input file(s) to test:\n")
    for i, f in enumerate(test_files, 1):
        size = f.stat().st_size / 1024
        print(f"   {i}. {f.name} ({size:.1f} KB)")
    print()
    
    results = []
    
    # Known span-data format files that can't be processed by BridgeGADGenerator directly
    _SPAN_DATA_FILES = {"spans_only.xlsx"}

    for idx, test_file in enumerate(test_files, 1):
        print(f"{'='*70}")
        print(f"📝 Test {idx}/{len(test_files)}: {test_file.name}")
        print(f"{'='*70}")
        
        try:
            # Start timer
            start_time = time.time()
            
            # Use smart input processor for better format handling
            print(f"  → Reading input with smart processor...")
            processor = SmartInputProcessor()

            # Skip known span-data format files (not compatible with BridgeGADGenerator)
            if test_file.name in _SPAN_DATA_FILES:
                print(f"  ⏭️  SKIPPED: span-data format (not a parameter file)")
                results.append({
                    'test_number': idx,
                    'input_file': str(test_file),
                    'status': 'SKIPPED',
                    'time_seconds': 0,
                    'timestamp': get_readable_timestamp()
                })
                continue
            
            try:
                params = processor.read_input(test_file)
                params = processor.validate_parameters(params)
                print(f"  → Loaded {len(params)} parameters")
            except Exception as e:
                print(f"  ⚠️  Smart processor failed, using direct method: {e}")
                # Fallback to direct generation
                params = None
            
            # Generate date-stamped output filename
            base_name = test_file.stem
            output_file = outputs_dir / f"{base_name}_{test_timestamp}.dxf"
            
            print(f"  → Output: {output_file}")
            print(f"  → Generating DXF drawing...")
            
            # FIX REPLIT-005: use generate_complete_drawing instead of non-existent generate_bridge_gad
            gen = BridgeGADGenerator()
            result = gen.generate_complete_drawing(test_file, output_file)
            
            # End timer
            elapsed = time.time() - start_time
            
            # Check output
            if output_file.exists():
                size = output_file.stat().st_size
                print(f"\n  ✅ SUCCESS!")
                print(f"     • Output: {output_file.name}")
                print(f"     • Size: {size:,} bytes ({size/1024:.1f} KB)")
                print(f"     • Time: {elapsed:.2f} seconds")
                print(f"     • Speed: {size/elapsed/1024:.1f} KB/s")
                
                results.append({
                    'test_number': idx,
                    'input_file': str(test_file),
                    'output_file': str(output_file),
                    'status': 'SUCCESS',
                    'size_bytes': size,
                    'size_kb': round(size/1024, 2),
                    'time_seconds': round(elapsed, 2),
                    'speed_kbps': round(size/elapsed/1024, 2),
                    'timestamp': get_readable_timestamp()
                })
            else:
                print(f"\n  ❌ FAILED: Output file not created")
                results.append({
                    'test_number': idx,
                    'input_file': str(test_file),
                    'output_file': str(output_file),
                    'status': 'FAILED',
                    'error': 'No output file created',
                    'time_seconds': round(elapsed, 2),
                    'timestamp': get_readable_timestamp()
                })
                
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            print(f"\n  ❌ ERROR: {error_msg}")
            results.append({
                'test_number': idx,
                'input_file': str(test_file),
                'status': 'ERROR',
                'error': error_msg,
                'time_seconds': round(elapsed, 2),
                'timestamp': get_readable_timestamp()
            })
        
        print()
    
    # Generate summary report
    generate_summary_report(results, test_timestamp)
    
    # Print summary to console
    print_summary(results)
    
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    skip_count   = sum(1 for r in results if r["status"] == "SKIPPED")
    assert success_count + skip_count == len(results), \
        f"{len(results) - success_count - skip_count} test(s) failed"


def generate_summary_report(results, test_timestamp):
    """Generate detailed JSON and text reports"""
    outputs_dir = Path("outputs")
    
    # JSON report
    json_report = outputs_dir / f"test_report_{test_timestamp}.json"
    with open(json_report, 'w') as f:
        json.dump({
            'test_run_timestamp': test_timestamp,
            'test_run_datetime': get_readable_timestamp(),
            'total_tests': len(results),
            'passed': sum(1 for r in results if r['status'] == 'SUCCESS'),
            'failed': sum(1 for r in results if r['status'] != 'SUCCESS'),
            'results': results
        }, f, indent=2)
    
    print(f"📄 JSON report saved: {json_report.name}")
    
    # Text report
    text_report = outputs_dir / f"test_report_{test_timestamp}.txt"
    with open(text_report, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("🌉 ULTIMATE BRIDGE GAD GENERATOR - TEST REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Test Run: {get_readable_timestamp()}\n")
        f.write(f"Timestamp: {test_timestamp}\n\n")
        
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        f.write(f"Total Tests: {len(results)}\n")
        f.write(f"Passed: {success_count}\n")
        f.write(f"Failed: {len(results) - success_count}\n")
        f.write(f"Success Rate: {success_count/len(results)*100:.1f}%\n\n")
        
        f.write("="*70 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("="*70 + "\n\n")
        
        for r in results:
            f.write(f"Test #{r['test_number']}: {Path(r['input_file']).name}\n")
            f.write(f"  Status: {r['status']}\n")
            if r['status'] == 'SUCCESS':
                f.write(f"  Output: {Path(r['output_file']).name}\n")
                f.write(f"  Size: {r['size_kb']} KB\n")
                f.write(f"  Time: {r['time_seconds']} seconds\n")
                f.write(f"  Speed: {r['speed_kbps']} KB/s\n")
            else:
                f.write(f"  Error: {r.get('error', 'Unknown')}\n")
            f.write(f"  Timestamp: {r['timestamp']}\n")
            f.write("\n")
        
        if success_count > 0:
            f.write("="*70 + "\n")
            f.write("STATISTICS\n")
            f.write("="*70 + "\n\n")
            
            successful = [r for r in results if r['status'] == 'SUCCESS']
            total_size = sum(r['size_kb'] for r in successful)
            total_time = sum(r['time_seconds'] for r in successful)
            avg_size = total_size / len(successful)
            avg_time = total_time / len(successful)
            
            f.write(f"Total Output Size: {total_size:.2f} KB\n")
            f.write(f"Total Processing Time: {total_time:.2f} seconds\n")
            f.write(f"Average File Size: {avg_size:.2f} KB\n")
            f.write(f"Average Processing Time: {avg_time:.2f} seconds\n")
            f.write(f"Overall Speed: {total_size/total_time:.2f} KB/s\n")
    
    print(f"📄 Text report saved: {text_report.name}\n")


def print_summary(results):
    """Print summary to console"""
    print("="*70)
    print("📊 TEST SUMMARY")
    print("="*70 + "\n")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_count = len(results)
    
    print(f"Tests Run: {total_count}")
    print(f"Passed: {success_count} ✅")
    print(f"Failed: {total_count - success_count} ❌")
    print(f"Success Rate: {success_count/total_count*100:.1f}%\n")
    
    if success_count > 0:
        print("✅ Successful Tests:")
        print("-" * 70)
        for r in [x for x in results if x['status'] == 'SUCCESS']:
            print(f"  {r['test_number']}. {Path(r['input_file']).name}")
            print(f"     → {Path(r['output_file']).name}")
            print(f"     → {r['size_kb']} KB in {r['time_seconds']}s ({r['speed_kbps']} KB/s)")
        print()
    
    if success_count < total_count:
        print("❌ Failed Tests:")
        print("-" * 70)
        for r in [x for x in results if x['status'] != 'SUCCESS']:
            print(f"  {r['test_number']}. {Path(r['input_file']).name}")
            print(f"     → Error: {r.get('error', 'Unknown')}")
        print()
    
    if success_count > 0:
        successful = [r for r in results if r['status'] == 'SUCCESS']
        total_size = sum(r['size_kb'] for r in successful)
        total_time = sum(r['time_seconds'] for r in successful)
        
        print("📈 Statistics:")
        print("-" * 70)
        print(f"  Total Output: {total_size:.2f} KB")
        print(f"  Total Time: {total_time:.2f} seconds")
        print(f"  Average Size: {total_size/len(successful):.2f} KB")
        print(f"  Average Time: {total_time/len(successful):.2f} seconds")
        print(f"  Overall Speed: {total_size/total_time:.2f} KB/s")
        print()
    
    print("="*70)
    
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED!")
    elif success_count > 0:
        print("⚠️  SOME TESTS PASSED")
    else:
        print("❌ ALL TESTS FAILED")
    
    print("="*70 + "\n")


def test_app_structure():
    """Test that all required modules exist"""
    print("\n" + "="*70)
    print("🔍 CHECKING APP STRUCTURE")
    print("="*70 + "\n")
    
    required_modules = [
        "src/bridge_gad/__init__.py",
        "src/bridge_gad/bridge_generator.py",
        "src/bridge_gad/io_utils.py",
        "src/bridge_gad/drawing.py",
        "src/bridge_gad/drawing_generator.py",
    ]
    
    all_exist = True
    for module in required_modules:
        if os.path.exists(module):
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module} (MISSING)")
            all_exist = False
    
    print()
    
    if all_exist:
        print("✅ All required modules found!\n")
    else:
        print("❌ Some modules are missing!\n")
    
    assert all_exist, "Required modules are missing"


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌉 ULTIMATE BRIDGE GAD GENERATOR - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Started: {get_readable_timestamp()}")
    print("="*70)
    
    # Test structure
    structure_ok = test_app_structure()
    
    if not structure_ok:
        print("⚠️  Cannot proceed with tests - missing modules")
        sys.exit(1)
    
    # Test drawing generation
    tests_passed, results = test_drawing_generation()
    
    # Final message
    if tests_passed:
        print("✅ All outputs saved with date-stamped filenames in outputs/ folder")
        print(f"✅ Test reports generated: test_report_{get_timestamp()}.json/.txt")
    
    # Exit code
    sys.exit(0 if tests_passed else 1)
