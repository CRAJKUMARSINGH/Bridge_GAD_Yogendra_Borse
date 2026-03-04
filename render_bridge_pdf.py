"""
Render actual bridge drawing to PDF with proper visualization
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

def render_dxf_to_pdf(dxf_file):
    """Render DXF drawing to PDF with actual visualization"""
    print(f"🎨 Rendering bridge drawing to PDF...")
    print(f"📁 Input: {dxf_file}")
    
    try:
        # Load DXF
        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()
        
        # Create PDF
        pdf_file = dxf_file.with_suffix('.pdf')
        
        # Create figure with large size for detail
        fig = plt.figure(figsize=(20, 14), dpi=150)
        ax = fig.add_subplot(111)
        
        # Setup rendering context
        ctx = RenderContext(doc)
        
        # Create matplotlib backend
        out = MatplotlibBackend(ax)
        
        # Render the drawing - skip problematic text entities
        print("🔨 Rendering entities...")
        
        # Draw lines and polylines first
        for entity in msp:
            entity_type = entity.dxftype()
            if entity_type in ['LINE', 'LWPOLYLINE', 'POLYLINE', 'CIRCLE', 'ARC']:
                try:
                    Frontend(ctx, out).draw_entity(entity)
                except Exception as e:
                    print(f"⚠️  Skipped {entity_type}: {e}")
        
        # Finalize the drawing
        out.finalize()
        
        # Set title and labels
        ax.set_title('Bridge General Arrangement Drawing', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Chainage (m)', fontsize=12)
        ax.set_ylabel('Level (m)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # Add info text
        info_text = f"Generated from: {dxf_file.name}\nBridge GAD Generator | RKS LEGAL"
        fig.text(0.5, 0.02, info_text, ha='center', fontsize=10, style='italic')
        
        # Save to PDF
        print("💾 Saving PDF...")
        plt.tight_layout()
        fig.savefig(pdf_file, format='pdf', bbox_inches='tight', dpi=150)
        plt.close(fig)
        
        print(f"✅ PDF created: {pdf_file}")
        return pdf_file
        
    except Exception as e:
        print(f"❌ Error rendering PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    dxf_file = Path("outputs/best_bridge.dxf")
    
    if not dxf_file.exists():
        print(f"❌ DXF file not found: {dxf_file}")
        return False
    
    pdf_file = render_dxf_to_pdf(dxf_file)
    
    if pdf_file:
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\n📄 PDF with actual drawing: {pdf_file.absolute()}")
        print("\nOpening PDF...")
        
        # Open the PDF
        import subprocess
        subprocess.run(['start', str(pdf_file)], shell=True)
        
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
