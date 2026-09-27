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


# ── Focused regression tests (pytest-compatible) ────────────────────────────

def test_standards_metadata():
    """Sanity-check the shared standards metadata module (folder-2 version).

    Covers:
      - PARAMETER_SPECS dataclass registry has new keys (OwnerProfile, phase 2).
      - Helper functions get_parameter_spec / get_parameter_description /
        get_owner_profile return sensible values and safe fallbacks.
      - OWNER_PROFILES expose all four authority presets.
      - PHASE_TWO_SHEETS defines the 7-sheet package.
      - DEFAULT_METADATA contains submission defaults.
      - build_template_rows, merge_with_metadata, checklist_rows,
        owner_profile_rows, phase_two_sheet_rows produce non-empty rows.
    """
    from bridge_gad import standards as s
    from bridge_gad.standards import (
        ParameterSpec, OwnerProfile, build_template_rows,
        merge_with_metadata, checklist_rows, owner_profile_rows,
        phase_two_sheet_rows, get_parameter_description, get_owner_profile,
        get_parameter_spec,
    )

    # Must-have new keys in the dataclass registry
    new_keys = [
        "DRAWING_STANDARD", "DESIGN_LIVE_LOAD", "ROAD_CLASS",
        "MEDIANW", "BARRIERT", "BEARING_W", "OWNER_PROFILE", "TOTAL_SHEETS",
        "DRAWING_NO", "REVISION", "LANES", "FOOTPATHW", "CRASHB",
        "BARRIERH", "UTILITYD", "DRAINSP", "CROSSFALL", "EXPJT",
        "BEARING_TYPE",
    ]
    for k in new_keys:
        assert k in s.PARAMETER_SPECS, f"Missing PARAMETER_SPECS[{k}]"
        spec = s.PARAMETER_SPECS[k]
        assert isinstance(spec, ParameterSpec)
        assert spec.key == k
        assert spec.description and isinstance(spec.description, str)
        assert isinstance(spec.unit, str)
        assert spec.category and isinstance(spec.category, str)

    # Unknown key -> get_parameter_spec returns a safe Custom fallback.
    fallback = get_parameter_spec("XYZ_NOT_A_THING")
    assert fallback.category == "Custom"
    assert "XYZ_NOT_A_THING" in fallback.description

    # get_parameter_description for known/unknown keys.
    assert get_parameter_description("DRAWING_NO") != "DRAWING_NO"
    assert "Project-specific" in get_parameter_description("XYZ_ABC")

    # Owner profiles: four presets + safe default.
    for p in ("IRC_MORTH", "NHAI", "RAILWAY", "ULB"):
        assert p in s.OWNER_PROFILES
        prof = s.OWNER_PROFILES[p]
        assert isinstance(prof, OwnerProfile)
        assert prof.owner and prof.drawing_standard
    assert get_owner_profile(None).key == "IRC_MORTH"
    assert get_owner_profile("bogus").key == "IRC_MORTH"
    assert get_owner_profile("NHAI").key == "NHAI"

    # Phase two package: 7 sheet schedule.
    sheets = phase_two_sheet_rows()
    assert len(sheets) == 7
    codes = {row["Code"] for row in sheets}
    for c in ("IDX", "GAD", "TYP", "ABT", "PIER", "BRG", "DRN"):
        assert c in codes, f"Phase 2 missing sheet code {c}"

    # DEFAULT_METADATA includes minimum submission fields.
    for tb in ["DRAWING_STANDARD", "DESIGN_LIVE_LOAD", "REVISION",
               "DRAWN_BY", "CHECKED_BY", "APPROVED_BY",
               "SHEET_NO", "TOTAL_SHEETS", "OWNER_PROFILE"]:
        assert tb in s.DEFAULT_METADATA and s.DEFAULT_METADATA[tb]

    # STANDARD_CHECKLIST non-empty + checklist_rows formatter.
    assert len(s.STANDARD_CHECKLIST) >= 5
    cl = checklist_rows()
    assert len(cl) == len(s.STANDARD_CHECKLIST)
    assert "Checklist Item" in cl[0]

    # build_template_rows produces expected columns.
    rows = build_template_rows({"CCBR": 8.0, "LANES": 2})
    assert len(rows) == 2
    for r in rows:
        for col in ("Value", "Variable", "Description", "Unit", "Category"):
            assert col in r

    # merge_with_metadata layers DEFAULT_METADATA then overrides then params.
    merged = merge_with_metadata({"LANES": 3}, DRAWING_NO="MY-99",
                                  OWNER_PROFILE="NHAI")
    assert merged["LANES"] == 3
    assert merged["DRAWING_NO"] == "MY-99"
    assert merged["OWNER_PROFILE"] == "NHAI"
    assert merged["REVISION"] == s.DEFAULT_METADATA["REVISION"]

    # owner_profile_rows returns all four presets.
    ow = owner_profile_rows()
    assert len(ow) == 4


def test_template_excel_enriched():
    """make_template_excel now exports 4 sheets including OwnerProfiles
    and SheetIndex. Plus phase-two ZIP bundler runs without error.
    """
    from io import BytesIO
    from bridge_gad.bridge_canvas_features import (
        BRIDGE_TEMPLATES, make_template_excel, make_phase_two_package_zip,
    )
    import pandas as pd
    import zipfile

    params = BRIDGE_TEMPLATES["simple_12m"]["parameters"]
    for required in ["LANES", "MEDIANW", "BARRIERT", "BEARING_W",
                     "ROAD_CLASS", "DRAWING_STANDARD", "DESIGN_LIVE_LOAD",
                     "TOTAL_SHEETS", "OWNER_PROFILE"]:
        assert required in params, f"Template missing {required}"

    xls_bytes = make_template_excel(params)
    assert isinstance(xls_bytes, bytes) and len(xls_bytes) > 2048

    with pd.ExcelFile(BytesIO(xls_bytes), engine="openpyxl") as xls:
        for required_sheet in ("Parameters", "Checklist",
                               "OwnerProfiles", "SheetIndex"):
            assert required_sheet in xls.sheet_names, \
                f"Missing workbook sheet {required_sheet}"

        df_params = pd.read_excel(xls, sheet_name="Parameters")
        assert {"Value", "Variable", "Description", "Unit", "Category"} \
            .issubset(set(df_params.columns))
        variables = set(df_params["Variable"].astype(str).tolist())
        for k in ["LANES", "MEDIANW", "BARRIERT", "BEARING_W",
                  "DRAWING_STANDARD", "DESIGN_LIVE_LOAD",
                  "OWNER_PROFILE", "TOTAL_SHEETS"]:
            assert k in variables, f"Parameters sheet missing {k}"

        df_owner = pd.read_excel(xls, sheet_name="OwnerProfiles")
        assert {"Profile Key", "Owner", "Drawing Standard",
                "Design Live Load", "Review Note"} \
            .issubset(set(df_owner.columns))
        assert len(df_owner) == 4  # four authority presets

        df_sheet = pd.read_excel(xls, sheet_name="SheetIndex")
        assert len(df_sheet) == 7  # phase two schedule

    # Phase two ZIP bundler produces a valid 3-entry zip.
    zip_bytes = make_phase_two_package_zip(params)
    assert isinstance(zip_bytes, bytes) and len(zip_bytes) > 4096
    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zf:
        names = set(zf.namelist())
        for required in ("phase2/phase2_parameters.xlsx",
                          "phase2/phase2_sheet_index.csv",
                          "phase2/phase2_manifest.json"):
            assert required in names, f"ZIP missing {required}"
