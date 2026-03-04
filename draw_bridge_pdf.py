"""
Draw bridge directly to PDF using matplotlib - simple and effective
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ezdxf

def draw_bridge_to_pdf(dxf_file):
    """Draw bridge entities directly to PDF"""
    print(f"🎨 Drawing bridge to PDF...")
    
    # Load DXF
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(20, 14), dpi=150)
    
    # Draw lines
    print("📐 Drawing lines...")
    for line in msp.query('LINE'):
        start = line.dxf.start
        end = line.dxf.end
        ax.plot([start.x, end.x], [start.y, end.y], 'k-', linewidth=0.5)
    
    # Draw polylines
    print("📐 Drawing polylines...")
    for pline in msp.query('LWPOLYLINE'):
        points = list(pline.get_points('xy'))
        if points:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            if pline.closed:
                xs.append(xs[0])
                ys.append(ys[0])
            ax.plot(xs, ys, 'k-', linewidth=0.8)
    
    # Draw text (simplified)
    print("📝 Adding text labels...")
    for text in msp.query('TEXT'):
        try:
            insert = text.dxf.insert
            content = text.dxf.text
            height = text.dxf.height if hasattr(text.dxf, 'height') else 2.0
            rotation = text.dxf.rotation if hasattr(text.dxf, 'rotation') else 0
            
            if insert and content:
                ax.text(insert.x, insert.y, content, 
                       fontsize=max(4, height/50), 
                       rotation=rotation,
                       ha='left', va='bottom')
        except:
            pass
    
    # Set up axes
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.set_xlabel('Chainage (m)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Level (m)', fontsize=14, fontweight='bold')
    ax.set_title('Bridge General Arrangement Drawing', fontsize=18, fontweight='bold', pad=20)
    
    # Add footer
    fig.text(0.5, 0.02, 'Bridge GAD Generator | RKS LEGAL', 
             ha='center', fontsize=10, style='italic')
    
    # Save
    pdf_file = Path("outputs/bridge_drawing.pdf")
    print(f"💾 Saving to {pdf_file}...")
    plt.tight_layout()
    fig.savefig(pdf_file, format='pdf', bbox_inches='tight', dpi=150)
    plt.close(fig)
    
    print(f"✅ PDF created: {pdf_file}")
    return pdf_file

def main():
    dxf_file = Path("outputs/best_bridge.dxf")
    
    if not dxf_file.exists():
        print(f"❌ DXF file not found")
        return False
    
    try:
        pdf_file = draw_bridge_to_pdf(dxf_file)
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS - Bridge Drawing PDF Created!")
        print("=" * 60)
        print(f"\n📄 PDF: {pdf_file.absolute()}")
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
    success = main()
    sys.exit(0 if success else 1)
