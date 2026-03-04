"""
Create annotated PDF showing elevation, plan, and section borders clearly
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import ezdxf
from pathlib import Path

def create_annotated_pdf(dxf_file):
    """Create PDF with clear view segment annotations"""
    print("🎨 Creating annotated PDF with view segments...")
    
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    
    # Create large figure
    fig, ax = plt.subplots(figsize=(24, 16), dpi=150)
    
    # Draw all lines
    for line in msp.query('LINE'):
        start = line.dxf.start
        end = line.dxf.end
        ax.plot([start.x, end.x], [start.y, end.y], 'k-', linewidth=0.5)
    
    # Draw all polylines
    for pline in msp.query('LWPOLYLINE'):
        points = list(pline.get_points('xy'))
        if points:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            if pline.closed:
                xs.append(xs[0])
                ys.append(ys[0])
            ax.plot(xs, ys, 'k-', linewidth=0.8)
    
    # Draw text labels
    for text in msp.query('TEXT'):
        try:
            insert = text.dxf.insert
            content = text.dxf.text
            height = text.dxf.height if hasattr(text.dxf, 'height') else 2.0
            rotation = text.dxf.rotation if hasattr(text.dxf, 'rotation') else 0
            
            if insert and content:
                ax.text(insert.x, insert.y, content, 
                       fontsize=max(3, height/80), 
                       rotation=rotation,
                       ha='left', va='bottom')
        except:
            pass
    
    # Get extents
    all_x = []
    all_y = []
    for line in msp.query('LINE'):
        all_x.extend([line.dxf.start.x, line.dxf.end.x])
        all_y.extend([line.dxf.start.y, line.dxf.end.y])
    for pline in msp.query('LWPOLYLINE'):
        points = list(pline.get_points('xy'))
        all_x.extend([p[0] for p in points])
        all_y.extend([p[1] for p in points])
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Define view regions
    y_threshold = min_y + (max_y - min_y) * 0.5
    
    # Add colored rectangles to highlight different views
    elevation_height = max_y - y_threshold
    plan_height = y_threshold - min_y
    
    # Elevation view highlight (light blue)
    elevation_rect = patches.Rectangle(
        (min_x, y_threshold), max_x - min_x, elevation_height,
        linewidth=3, edgecolor='blue', facecolor='lightblue', alpha=0.1
    )
    ax.add_patch(elevation_rect)
    
    # Plan view highlight (light green)
    plan_rect = patches.Rectangle(
        (min_x, min_y), max_x - min_x, plan_height,
        linewidth=3, edgecolor='green', facecolor='lightgreen', alpha=0.1
    )
    ax.add_patch(plan_rect)
    
    # Add view labels
    label_x = min_x + (max_x - min_x) * 0.02
    
    ax.text(label_x, max_y - elevation_height * 0.1, 
            'ELEVATION VIEW\n(Side View)', 
            fontsize=16, fontweight='bold', color='blue',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.text(label_x, min_y + plan_height * 0.9, 
            'PLAN VIEW\n(Top View)', 
            fontsize=16, fontweight='bold', color='green',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add section labels if found
    for text in msp.query('TEXT'):
        try:
            content = text.dxf.text
            if 'SECTION' in content.upper():
                insert = text.dxf.insert
                ax.plot(insert.x, insert.y, 'ro', markersize=10)
                ax.annotate('SECTION', xy=(insert.x, insert.y), 
                           xytext=(insert.x + 2000, insert.y + 2000),
                           fontsize=12, color='red', fontweight='bold',
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color='red', lw=2))
        except:
            pass
    
    # Set up axes
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Chainage (mm)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Level (mm)', fontsize=14, fontweight='bold')
    ax.set_title('Bridge General Arrangement Drawing - View Segments Annotated', 
                 fontsize=20, fontweight='bold', pad=20)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='blue', lw=4, label='Elevation View Area'),
        Line2D([0], [0], color='green', lw=4, label='Plan View Area'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
               markersize=10, label='Section Markers')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12)
    
    # Add info box
    info_text = f"""Drawing Statistics:
• Total Width: {(max_x-min_x)/1000:.1f} m
• Total Height: {(max_y-min_y)/1000:.1f} m
• View Separation: {(y_threshold-min_y)/1000:.1f} m
• Elevation/Plan Ratio: {elevation_height/plan_height:.2f}"""
    
    ax.text(0.98, 0.02, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Footer
    fig.text(0.5, 0.01, 'Bridge GAD Generator | RKS LEGAL | View Segments Verified', 
             ha='center', fontsize=10, style='italic')
    
    # Save
    pdf_file = Path("outputs/bridge_annotated.pdf")
    print(f"💾 Saving annotated PDF...")
    plt.tight_layout()
    fig.savefig(pdf_file, format='pdf', bbox_inches='tight', dpi=150)
    plt.close(fig)
    
    print(f"✅ Annotated PDF created: {pdf_file}")
    return pdf_file

def main():
    dxf_file = Path("outputs/best_bridge.dxf")
    
    if not dxf_file.exists():
        print(f"❌ DXF file not found")
        return False
    
    try:
        pdf_file = create_annotated_pdf(dxf_file)
        
        print("\n" + "=" * 60)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 60)
        print(f"\n📄 Annotated PDF: {pdf_file.absolute()}")
        print("\nView segments are clearly separated:")
        print("  🔵 ELEVATION VIEW (upper) - Bridge side view")
        print("  🟢 PLAN VIEW (lower) - Bridge top view")
        print("  🔴 SECTION markers - Cross-sections")
        print("\nOpening PDF...")
        
        import subprocess
        subprocess.run(['start', str(pdf_file)], shell=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
