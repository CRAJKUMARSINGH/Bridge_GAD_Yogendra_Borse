#!/usr/bin/env python3
"""
Verify GAD completeness by analyzing the DXF file
"""

import ezdxf
from pathlib import Path
import sys

def analyze_gad_file(dxf_file):
    """Analyze DXF file to verify all GAD components"""
    
    print(f"\n{'='*60}")
    print(f"GAD Completeness Analysis: {dxf_file}")
    print(f"{'='*60}\n")
    
    try:
        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()
        
        # Count entities by type
        entity_counts = {}
        for entity in msp:
            entity_type = entity.dxftype()
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        print("Entity Summary:")
        print("-" * 40)
        for entity_type, count in sorted(entity_counts.items()):
            print(f"  {entity_type:20s}: {count:4d}")
        
        total_entities = sum(entity_counts.values())
        print(f"  {'TOTAL':20s}: {total_entities:4d}")
        print()
        
        # Check for specific components
        print("Component Verification:")
        print("-" * 40)
        
        # Check for text elements
        texts = [e for e in msp if e.dxftype() == 'TEXT']
        text_content = [t.dxf.text for t in texts]
        
        components = {
            'Layout Grid': any('BED LEVEL' in t or 'CHAINAGE' in t for t in text_content),
            'Deck Slab': any('DECK SLAB' in t for t in text_content),
            'Abutments': any('A1' in t or 'A2' in t for t in text_content),
            'Piers': any(f'P{i}' in t for t in text_content for i in range(1, 10)),
            'Cross Sections': any('SECTION' in t for t in text_content),
            'Title Block': any('GENERAL ARRANGEMENT' in t or 'BRIDGE DESIGN' in t for t in text_content),
            'Polylines (structures)': entity_counts.get('LWPOLYLINE', 0) > 0,
            'Lines (details)': entity_counts.get('LINE', 0) > 0,
            'Dimensions': entity_counts.get('DIMENSION', 0) > 0,
        }
        
        all_present = True
        for component, present in components.items():
            status = "✓" if present else "✗ MISSING"
            print(f"  {status} {component}")
            if not present:
                all_present = False
        
        print()
        
        # Detailed text analysis
        print("Text Elements Found:")
        print("-" * 40)
        for i, text in enumerate(text_content[:20], 1):  # Show first 20
            print(f"  {i:2d}. {text}")
        if len(text_content) > 20:
            print(f"  ... and {len(text_content) - 20} more")
        print()
        
        # Drawing extents
        print("Drawing Extents:")
        print("-" * 40)
        try:
            extents = msp.extents()
            if extents:
                print(f"  Min: ({extents[0].x:.2f}, {extents[0].y:.2f})")
                print(f"  Max: ({extents[1].x:.2f}, {extents[1].y:.2f})")
                width = extents[1].x - extents[0].x
                height = extents[1].y - extents[0].y
                print(f"  Size: {width:.2f} x {height:.2f}")
        except:
            print("  Could not determine extents")
        print()
        
        # Final verdict
        print("="*60)
        if all_present and total_entities > 50:
            print("✓ GAD IS COMPLETE - All components present!")
            print(f"  Total entities: {total_entities}")
            print(f"  Text labels: {len(texts)}")
            print(f"  Structural elements: {entity_counts.get('LWPOLYLINE', 0)}")
            return True
        elif total_entities > 20:
            print("⚠ GAD IS PARTIAL - Some components may be missing")
            print(f"  Total entities: {total_entities}")
            return False
        else:
            print("✗ GAD IS INCOMPLETE - Very few entities found")
            print(f"  Total entities: {total_entities}")
            return False
        
    except Exception as e:
        print(f"✗ Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Find the most recent GAD test file
    test_files = list(Path('.').glob('complete_gad_test_*.dxf'))
    
    if not test_files:
        print("No GAD test files found. Run test_complete_gad.py first.")
        sys.exit(1)
    
    # Use the most recent file
    latest_file = max(test_files, key=lambda p: p.stat().st_mtime)
    
    success = analyze_gad_file(latest_file)
    sys.exit(0 if success else 1)
