"""
Verify bridge drawing layout - check elevation, plan, and section borders
"""
import ezdxf
from pathlib import Path

def analyze_drawing_layout(dxf_file):
    """Analyze the drawing to check segment borders"""
    print("🔍 Analyzing Bridge Drawing Layout...")
    print("=" * 60)
    
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    
    # Collect all entities by type
    lines = list(msp.query('LINE'))
    polylines = list(msp.query('LWPOLYLINE'))
    texts = list(msp.query('TEXT'))
    
    print(f"\n📊 Entity Count:")
    print(f"  Lines: {len(lines)}")
    print(f"  Polylines: {len(polylines)}")
    print(f"  Text: {len(texts)}")
    
    # Find extents
    all_x = []
    all_y = []
    
    for line in lines:
        all_x.extend([line.dxf.start.x, line.dxf.end.x])
        all_y.extend([line.dxf.start.y, line.dxf.end.y])
    
    for pline in polylines:
        points = list(pline.get_points('xy'))
        all_x.extend([p[0] for p in points])
        all_y.extend([p[1] for p in points])
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    print(f"\n📐 Drawing Extents:")
    print(f"  X range: {min_x:.2f} to {max_x:.2f} (width: {max_x-min_x:.2f})")
    print(f"  Y range: {min_y:.2f} to {max_y:.2f} (height: {max_y-min_y:.2f})")
    
    # Analyze text labels to identify sections
    print(f"\n📝 Text Labels Found:")
    section_labels = {}
    
    for text in texts:
        try:
            content = text.dxf.text
            insert = text.dxf.insert
            
            if content and insert:
                # Look for section identifiers
                content_upper = content.upper()
                if any(keyword in content_upper for keyword in ['ELEVATION', 'PLAN', 'SECTION', 'PIER', 'ABUTMENT']):
                    section_labels[content] = (insert.x, insert.y)
                    print(f"  '{content}' at ({insert.x:.1f}, {insert.y:.1f})")
        except:
            pass
    
    # Identify Y-coordinate ranges for different views
    print(f"\n🎯 Analyzing View Segments:")
    
    # Group entities by Y-coordinate ranges
    y_groups = {
        'upper': [],  # Elevation view (typically higher Y)
        'middle': [],  # Could be section
        'lower': []   # Plan view (typically lower Y)
    }
    
    y_threshold_1 = min_y + (max_y - min_y) * 0.66  # Upper third boundary
    y_threshold_2 = min_y + (max_y - min_y) * 0.33  # Lower third boundary
    
    for pline in polylines:
        points = list(pline.get_points('xy'))
        if points:
            avg_y = sum(p[1] for p in points) / len(points)
            if avg_y > y_threshold_1:
                y_groups['upper'].append(pline)
            elif avg_y > y_threshold_2:
                y_groups['middle'].append(pline)
            else:
                y_groups['lower'].append(pline)
    
    print(f"\n  Upper region (Y > {y_threshold_1:.1f}): {len(y_groups['upper'])} polylines")
    print(f"  Middle region ({y_threshold_2:.1f} < Y < {y_threshold_1:.1f}): {len(y_groups['middle'])} polylines")
    print(f"  Lower region (Y < {y_threshold_2:.1f}): {len(y_groups['lower'])} polylines")
    
    # Check for proper separation
    print(f"\n✅ Layout Assessment:")
    
    if len(y_groups['upper']) > 0 and len(y_groups['lower']) > 0:
        print(f"  ✓ Multiple view segments detected")
        print(f"  ✓ Elevation view (upper): ~{len(y_groups['upper'])} elements")
        print(f"  ✓ Plan view (lower): ~{len(y_groups['lower'])} elements")
        
        # Calculate spacing between views
        upper_min_y = min(p[1] for pline in y_groups['upper'] for p in pline.get_points('xy'))
        lower_max_y = max(p[1] for pline in y_groups['lower'] for p in pline.get_points('xy'))
        spacing = upper_min_y - lower_max_y
        
        print(f"  ✓ Vertical spacing between views: {spacing:.2f} units")
        
        if spacing > 1000:
            print(f"  ✓ Good separation between elevation and plan views")
        else:
            print(f"  ⚠️  Views might be too close together")
    else:
        print(f"  ⚠️  Could not clearly identify separate view segments")
    
    # Check for pier and abutment elements
    print(f"\n🏗️  Bridge Components:")
    
    pier_count = sum(1 for text in texts if 'P' in text.dxf.text and len(text.dxf.text) <= 3)
    abutment_count = sum(1 for text in texts if 'A' in text.dxf.text and len(text.dxf.text) <= 3)
    
    print(f"  Pier labels: {pier_count}")
    print(f"  Abutment labels: {abutment_count}")
    
    # Estimate view types based on polyline distribution
    print(f"\n📋 Estimated View Layout:")
    print(f"  • ELEVATION VIEW: Upper portion (bridge side view)")
    print(f"  • PLAN VIEW: Lower portion (bridge top view)")
    
    if len(y_groups['middle']) > 5:
        print(f"  • SECTION VIEW: Middle portion detected")
    
    print("\n" + "=" * 60)
    print("✅ Layout verification complete!")
    
    return True

def main():
    dxf_file = Path("outputs/best_bridge.dxf")
    
    if not dxf_file.exists():
        print(f"❌ DXF file not found")
        return False
    
    try:
        analyze_drawing_layout(dxf_file)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
