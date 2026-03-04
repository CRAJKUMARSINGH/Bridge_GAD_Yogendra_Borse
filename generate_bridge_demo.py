"""
Bridge Element Generator - Demo
Generates professional bridge drawings with various elements
Output: Timestamped DXF, PNG, and PDF files in outputs/ folder
"""
import ezdxf
from datetime import datetime
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm

def create_timestamped_filename(prefix="bridge", extension="dxf"):
    """Create timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def dxf_to_image(doc, width=3000, height=2000):
    """Convert DXF entities to PIL Image - IMPROVED: Higher resolution for professional quality"""
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')  # Enable anti-aliasing
    
    msp = doc.modelspace()
    
    # Calculate bounds
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    
    for entity in msp:
        if entity.dxftype() == 'LWPOLYLINE':
            points = list(entity.get_points('xy'))
            for x, y in points:
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
        elif entity.dxftype() == 'LINE':
            start, end = entity.dxf.start, entity.dxf.end
            min_x, max_x = min(min_x, start.x, end.x), max(max_x, start.x, end.x)
            min_y, max_y = min(min_y, start.y, end.y), max(max_y, start.y, end.y)
    
    # Add margins
    margin = 50
    scale_x = (width - 2 * margin) / (max_x - min_x) if max_x > min_x else 1
    scale_y = (height - 2 * margin) / (max_y - min_y) if max_y > min_y else 1
    scale = min(scale_x, scale_y)
    
    def transform(x, y):
        # Transform coordinates to image space (flip Y axis)
        px = int((x - min_x) * scale + margin)
        py = int(height - ((y - min_y) * scale + margin))
        return px, py
    
    # Draw entities - IMPROVED: Professional engineering colors
    color_map = {
        1: '#2C3E50',  # Dark blue-gray (structure)
        2: '#34495E',  # Medium gray (secondary)
        3: '#7F8C8D',  # Light gray (tertiary)
        4: '#95A5A6',  # Very light gray (background)
        5: '#2C3E50',  # Dark (deck)
        6: '#E74C3C',  # Red (bearings - highlight)
        7: '#000000'   # Black (text/dimensions)
    }
    
    # IMPROVED: Dynamic line width based on resolution
    line_width = max(3, int(width / 500))
    
    for entity in msp:
        if entity.dxftype() == 'LWPOLYLINE':
            points = list(entity.get_points('xy'))
            if points:
                transformed = [transform(x, y) for x, y in points]
                color = color_map.get(entity.dxf.color, 'black')
                draw.line(transformed, fill=color, width=line_width)
        
        elif entity.dxftype() == 'LINE':
            start, end = entity.dxf.start, entity.dxf.end
            p1 = transform(start.x, start.y)
            p2 = transform(end.x, end.y)
            color = color_map.get(entity.dxf.color, 'black')
            draw.line([p1, p2], fill=color, width=line_width)
        
        elif entity.dxftype() == 'TEXT':
            insert = entity.dxf.insert
            text = entity.dxf.text
            pos = transform(insert.x, insert.y)
            try:
                font_size = int(width / 100)  # Scale font with resolution
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            draw.text(pos, text, fill='black', font=font)
    
    return img

def save_as_png(doc, filepath):
    """Save DXF as PNG image - IMPROVED: Higher resolution with proper DPI"""
    img = dxf_to_image(doc, width=3000, height=2000)
    png_path = filepath.with_suffix('.png')
    # Save with proper DPI metadata
    img.save(png_path, 'PNG', dpi=(300, 300), optimize=True)
    return png_path

def save_as_pdf(doc, filepath, title="Bridge Drawing"):
    """Save DXF as PDF - IMPROVED: Higher quality with metadata"""
    # First create high-res PNG
    img = dxf_to_image(doc, width=4000, height=2667)
    
    # Save PNG temporarily
    temp_png = filepath.with_suffix('.temp.png')
    img.save(temp_png, 'PNG')
    
    # Create PDF with metadata
    pdf_path = filepath.with_suffix('.pdf')
    c = pdf_canvas.Canvas(str(pdf_path), pagesize=landscape(A4))
    
    # IMPROVED: Add professional metadata
    c.setTitle(title)
    c.setAuthor("RKS LEGAL - Bridge GAD Generator")
    c.setSubject("Bridge Engineering Drawing")
    c.setKeywords("bridge, CAD, engineering, AutoCAD, DXF, IRC, IS")
    c.setCreator("Bridge GAD Generator v1.0")
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, landscape(A4)[1] - 30, title)
    
    # Add image
    img_width, img_height = img.size
    pdf_width, pdf_height = landscape(A4)
    
    # Scale to fit
    scale = min((pdf_width - 60) / img_width, (pdf_height - 80) / img_height)
    scaled_width = img_width * scale
    scaled_height = img_height * scale
    
    c.drawImage(str(temp_png), 30, 40, width=scaled_width, height=scaled_height)
    
    # Add footer - IMPROVED: Larger, more readable
    c.setFont("Helvetica", 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(30, 20, f"Generated: {timestamp} | Bridge GAD Generator | RKS LEGAL - Techno Legal Consultants")
    
    c.save()
    
    # Clean up temp file
    temp_png.unlink()
    
    return pdf_path

def draw_bridge_pier(msp, x, y, width=1.2, height=8.0, cap_height=1.0):
    """Draw a bridge pier with cap"""
    # Pier shaft
    pier_points = [
        (x - width/2, y),
        (x + width/2, y),
        (x + width/2, y + height),
        (x - width/2, y + height),
        (x - width/2, y)
    ]
    msp.add_lwpolyline(pier_points, dxfattribs={'color': 1})  # Red
    
    # Pier cap (wider)
    cap_width = width * 1.5
    cap_points = [
        (x - cap_width/2, y + height),
        (x + cap_width/2, y + height),
        (x + cap_width/2, y + height + cap_height),
        (x - cap_width/2, y + height + cap_height),
        (x - cap_width/2, y + height)
    ]
    msp.add_lwpolyline(cap_points, dxfattribs={'color': 2})  # Yellow
    
    # Add text label
    msp.add_text(
        f"PIER",
        dxfattribs={
            'height': 0.5,
            'color': 7,
            'insert': (x - 0.3, y + height/2)
        }
    )

def draw_bridge_abutment(msp, x, y, width=2.0, height=6.0):
    """Draw a bridge abutment"""
    # Main abutment wall
    abt_points = [
        (x, y),
        (x + width, y),
        (x + width * 0.8, y + height),
        (x + width * 0.2, y + height),
        (x, y)
    ]
    msp.add_lwpolyline(abt_points, dxfattribs={'color': 3})  # Green
    
    # Footing
    footing_points = [
        (x - 0.5, y),
        (x + width + 0.5, y),
        (x + width + 0.5, y - 1.0),
        (x - 0.5, y - 1.0),
        (x - 0.5, y)
    ]
    msp.add_lwpolyline(footing_points, dxfattribs={'color': 4})  # Cyan
    
    # Add text label
    msp.add_text(
        "ABUTMENT",
        dxfattribs={
            'height': 0.5,
            'color': 7,
            'insert': (x + 0.2, y + height/2)
        }
    )

def draw_bridge_deck(msp, x1, y, x2, thickness=0.6):
    """Draw bridge deck/slab"""
    deck_points = [
        (x1, y),
        (x2, y),
        (x2, y + thickness),
        (x1, y + thickness),
        (x1, y)
    ]
    msp.add_lwpolyline(deck_points, dxfattribs={'color': 5})  # Blue
    
    # Add hatching for concrete
    hatch = msp.add_hatch(color=8)
    hatch.paths.add_polyline_path(deck_points)
    hatch.set_pattern_fill("ANSI31", scale=0.1)
    
    # Add text label
    mid_x = (x1 + x2) / 2
    msp.add_text(
        "BRIDGE DECK",
        dxfattribs={
            'height': 0.4,
            'color': 7,
            'insert': (mid_x - 2, y + thickness/2)
        }
    )

def draw_bearing(msp, x, y, width=0.4, height=0.2):
    """Draw bearing pad"""
    bearing_points = [
        (x - width/2, y),
        (x + width/2, y),
        (x + width/2, y + height),
        (x - width/2, y + height),
        (x - width/2, y)
    ]
    msp.add_lwpolyline(bearing_points, dxfattribs={'color': 6})  # Magenta

def draw_foundation(msp, x, y, width=3.0, depth=2.0):
    """Draw foundation/footing"""
    foundation_points = [
        (x - width/2, y),
        (x + width/2, y),
        (x + width/2, y - depth),
        (x - width/2, y - depth),
        (x - width/2, y)
    ]
    msp.add_lwpolyline(foundation_points, dxfattribs={'color': 4})  # Cyan
    
    # Add hatching
    hatch = msp.add_hatch(color=8)
    hatch.paths.add_polyline_path(foundation_points)
    hatch.set_pattern_fill("ANSI32", scale=0.2)

def draw_dimension_line(msp, x1, y, x2, offset=1.0, text=None):
    """Draw dimension line with arrows"""
    y_dim = y + offset
    
    # Dimension line
    msp.add_line((x1, y_dim), (x2, y_dim), dxfattribs={'color': 7})
    
    # Extension lines
    msp.add_line((x1, y), (x1, y_dim + 0.3), dxfattribs={'color': 7})
    msp.add_line((x2, y), (x2, y_dim + 0.3), dxfattribs={'color': 7})
    
    # Arrows
    arrow_size = 0.3
    # Left arrow
    msp.add_line((x1, y_dim), (x1 + arrow_size, y_dim + arrow_size/2), dxfattribs={'color': 7})
    msp.add_line((x1, y_dim), (x1 + arrow_size, y_dim - arrow_size/2), dxfattribs={'color': 7})
    # Right arrow
    msp.add_line((x2, y_dim), (x2 - arrow_size, y_dim + arrow_size/2), dxfattribs={'color': 7})
    msp.add_line((x2, y_dim), (x2 - arrow_size, y_dim - arrow_size/2), dxfattribs={'color': 7})
    
    # Dimension text
    if text is None:
        text = f"{abs(x2 - x1):.2f}m"
    mid_x = (x1 + x2) / 2
    msp.add_text(
        text,
        dxfattribs={
            'height': 0.3,
            'color': 7,
            'insert': (mid_x - 0.5, y_dim + 0.2)
        }
    )

def draw_title_block(msp, x, y):
    """Draw title block"""
    # Border
    border_points = [
        (x, y),
        (x + 15, y),
        (x + 15, y + 5),
        (x, y + 5),
        (x, y)
    ]
    msp.add_lwpolyline(border_points, dxfattribs={'color': 7})
    
    # Title
    msp.add_text(
        "BRIDGE ELEMENTS DEMONSTRATION",
        dxfattribs={
            'height': 0.6,
            'color': 1,
            'insert': (x + 0.5, y + 4)
        }
    )
    
    # Details
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msp.add_text(f"Date: {timestamp}", dxfattribs={'height': 0.3, 'color': 7, 'insert': (x + 0.5, y + 3)})
    msp.add_text("Generated by: Bridge GAD Generator", dxfattribs={'height': 0.3, 'color': 7, 'insert': (x + 0.5, y + 2.5)})
    msp.add_text("Scale: 1:100", dxfattribs={'height': 0.3, 'color': 7, 'insert': (x + 0.5, y + 2)})
    msp.add_text("Units: Meters", dxfattribs={'height': 0.3, 'color': 7, 'insert': (x + 0.5, y + 1.5)})
    msp.add_text("RKS LEGAL - Techno Legal Consultants", dxfattribs={'height': 0.25, 'color': 7, 'insert': (x + 0.5, y + 0.5)})

def generate_simple_bridge():
    """Generate a simple bridge with all elements"""
    print("🌉 Generating Simple Bridge...")
    
    # Create DXF document
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    
    # Bridge parameters
    span_length = 12.0
    pier_height = 8.0
    deck_thickness = 0.6
    
    # Ground level
    ground_y = 0
    
    # Draw left abutment
    draw_bridge_abutment(msp, 0, ground_y, width=2.0, height=6.0)
    draw_foundation(msp, 1.0, ground_y, width=3.0, depth=2.0)
    
    # Draw right abutment
    draw_bridge_abutment(msp, span_length + 2, ground_y, width=2.0, height=6.0)
    draw_foundation(msp, span_length + 3, ground_y, width=3.0, depth=2.0)
    
    # Draw bridge deck
    deck_y = 6.0
    draw_bearing(msp, 1.6, deck_y, width=0.4, height=0.2)
    draw_bearing(msp, span_length + 2.4, deck_y, width=0.4, height=0.2)
    draw_bridge_deck(msp, 1.6, deck_y + 0.2, span_length + 2.4, thickness=deck_thickness)
    
    # Add dimensions
    draw_dimension_line(msp, 0, ground_y - 3, span_length + 4, offset=-1, text=f"{span_length + 4:.1f}m TOTAL")
    draw_dimension_line(msp, 1.6, deck_y + deck_thickness, span_length + 2.4, offset=1, text=f"{span_length:.1f}m SPAN")
    
    # Add title block
    draw_title_block(msp, -5, -8)
    
    # Save DXF
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    filename = create_timestamped_filename("simple_bridge", "dxf")
    filepath = output_dir / filename
    doc.saveas(filepath)
    print(f"  ✅ DXF: {filepath}")
    
    # Save PNG
    png_path = save_as_png(doc, filepath)
    print(f"  ✅ PNG: {png_path}")
    
    # Save PDF
    pdf_path = save_as_pdf(doc, filepath, "Simple Bridge")
    print(f"  ✅ PDF: {pdf_path}")
    
    return filepath, png_path, pdf_path

def generate_multi_span_bridge():
    """Generate a multi-span bridge"""
    print("🌉 Generating Multi-Span Bridge...")
    
    # Create DXF document
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    
    # Bridge parameters
    num_spans = 3
    span_length = 12.0
    pier_height = 8.0
    deck_thickness = 0.6
    pier_width = 1.2
    
    # Ground level
    ground_y = 0
    deck_y = pier_height
    
    # Draw left abutment
    draw_bridge_abutment(msp, 0, ground_y, width=2.0, height=pier_height - 2)
    draw_foundation(msp, 1.0, ground_y, width=3.0, depth=2.0)
    
    # Draw piers
    for i in range(1, num_spans):
        pier_x = i * span_length + 2
        draw_bridge_pier(msp, pier_x, ground_y, width=pier_width, height=pier_height, cap_height=1.0)
        draw_foundation(msp, pier_x, ground_y, width=2.5, depth=2.0)
        draw_bearing(msp, pier_x, deck_y + 1.0, width=0.4, height=0.2)
    
    # Draw right abutment
    right_x = num_spans * span_length + 2
    draw_bridge_abutment(msp, right_x, ground_y, width=2.0, height=pier_height - 2)
    draw_foundation(msp, right_x + 1, ground_y, width=3.0, depth=2.0)
    
    # Draw continuous bridge deck
    draw_bearing(msp, 1.6, deck_y - 2, width=0.4, height=0.2)
    draw_bearing(msp, right_x + 0.4, deck_y - 2, width=0.4, height=0.2)
    draw_bridge_deck(msp, 1.6, deck_y + 1.2, right_x + 0.4, thickness=deck_thickness)
    
    # Add dimensions for each span
    for i in range(num_spans):
        x1 = i * span_length + 1.6 if i == 0 else i * span_length + 2
        x2 = (i + 1) * span_length + 2
        draw_dimension_line(msp, x1, deck_y + deck_thickness + 1.2, x2, offset=1 + i*0.5, text=f"SPAN {i+1}: {span_length:.1f}m")
    
    # Total length dimension
    draw_dimension_line(msp, 0, ground_y - 3, right_x + 2, offset=-1, text=f"{right_x + 2:.1f}m TOTAL")
    
    # Add title block
    draw_title_block(msp, -5, -8)
    
    # Save DXF
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    filename = create_timestamped_filename("multi_span_bridge", "dxf")
    filepath = output_dir / filename
    doc.saveas(filepath)
    print(f"  ✅ DXF: {filepath}")
    
    # Save PNG
    png_path = save_as_png(doc, filepath)
    print(f"  ✅ PNG: {png_path}")
    
    # Save PDF
    pdf_path = save_as_pdf(doc, filepath, "Multi-Span Bridge")
    print(f"  ✅ PDF: {pdf_path}")
    
    return filepath, png_path, pdf_path

def generate_bridge_cross_section():
    """Generate bridge cross-section view"""
    print("🌉 Generating Bridge Cross-Section...")
    
    # Create DXF document
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    
    # Parameters
    deck_width = 10.0
    deck_thickness = 0.6
    kerb_width = 0.3
    kerb_height = 0.15
    
    # Center line
    center_x = 0
    deck_y = 5.0
    
    # Draw deck slab
    deck_points = [
        (center_x - deck_width/2, deck_y),
        (center_x + deck_width/2, deck_y),
        (center_x + deck_width/2, deck_y + deck_thickness),
        (center_x - deck_width/2, deck_y + deck_thickness),
        (center_x - deck_width/2, deck_y)
    ]
    msp.add_lwpolyline(deck_points, dxfattribs={'color': 5})
    
    # Add hatching
    hatch = msp.add_hatch(color=8)
    hatch.paths.add_polyline_path(deck_points)
    hatch.set_pattern_fill("ANSI31", scale=0.1)
    
    # Draw kerbs
    # Left kerb
    left_kerb = [
        (center_x - deck_width/2, deck_y + deck_thickness),
        (center_x - deck_width/2 + kerb_width, deck_y + deck_thickness),
        (center_x - deck_width/2 + kerb_width, deck_y + deck_thickness + kerb_height),
        (center_x - deck_width/2, deck_y + deck_thickness + kerb_height),
        (center_x - deck_width/2, deck_y + deck_thickness)
    ]
    msp.add_lwpolyline(left_kerb, dxfattribs={'color': 3})
    
    # Right kerb
    right_kerb = [
        (center_x + deck_width/2 - kerb_width, deck_y + deck_thickness),
        (center_x + deck_width/2, deck_y + deck_thickness),
        (center_x + deck_width/2, deck_y + deck_thickness + kerb_height),
        (center_x + deck_width/2 - kerb_width, deck_y + deck_thickness + kerb_height),
        (center_x + deck_width/2 - kerb_width, deck_y + deck_thickness)
    ]
    msp.add_lwpolyline(right_kerb, dxfattribs={'color': 3})
    
    # Draw girders (simplified)
    girder_spacing = 2.5
    num_girders = 4
    girder_width = 0.4
    girder_depth = 1.2
    
    for i in range(num_girders):
        girder_x = center_x - (num_girders - 1) * girder_spacing / 2 + i * girder_spacing
        girder_points = [
            (girder_x - girder_width/2, deck_y - girder_depth),
            (girder_x + girder_width/2, deck_y - girder_depth),
            (girder_x + girder_width/2, deck_y),
            (girder_x - girder_width/2, deck_y),
            (girder_x - girder_width/2, deck_y - girder_depth)
        ]
        msp.add_lwpolyline(girder_points, dxfattribs={'color': 1})
    
    # Add center line
    msp.add_line((center_x, deck_y - 2), (center_x, deck_y + 2), dxfattribs={'color': 7, 'linetype': 'DASHED'})
    msp.add_text("CL", dxfattribs={'height': 0.3, 'color': 7, 'insert': (center_x - 0.3, deck_y + 2.5)})
    
    # Add dimensions
    draw_dimension_line(msp, center_x - deck_width/2, deck_y - 2, center_x + deck_width/2, offset=-1, text=f"{deck_width:.1f}m WIDTH")
    
    # Add labels
    msp.add_text("CROSS-SECTION VIEW", dxfattribs={'height': 0.5, 'color': 1, 'insert': (center_x - 3, deck_y + 3)})
    
    # Add title block
    draw_title_block(msp, -8, deck_y - 6)
    
    # Save DXF
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    filename = create_timestamped_filename("bridge_cross_section", "dxf")
    filepath = output_dir / filename
    doc.saveas(filepath)
    print(f"  ✅ DXF: {filepath}")
    
    # Save PNG
    png_path = save_as_png(doc, filepath)
    print(f"  ✅ PNG: {png_path}")
    
    # Save PDF
    pdf_path = save_as_pdf(doc, filepath, "Bridge Cross-Section")
    print(f"  ✅ PDF: {pdf_path}")
    
    return filepath, png_path, pdf_path

def main():
    """Generate all bridge drawings"""
    print("=" * 70)
    print("🌉 BRIDGE ELEMENT GENERATOR")
    print("=" * 70)
    print()
    
    # Ensure output directory exists
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate drawings
    all_files = []
    
    try:
        # Simple bridge
        dxf1, png1, pdf1 = generate_simple_bridge()
        all_files.extend([dxf1, png1, pdf1])
        
        # Multi-span bridge
        dxf2, png2, pdf2 = generate_multi_span_bridge()
        all_files.extend([dxf2, png2, pdf2])
        
        # Cross-section
        dxf3, png3, pdf3 = generate_bridge_cross_section()
        all_files.extend([dxf3, png3, pdf3])
        
        print()
        print("=" * 70)
        print("✅ ALL DRAWINGS GENERATED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("📁 Generated Files:")
        print()
        print("Simple Bridge:")
        print(f"  📄 DXF: {dxf1.name}")
        print(f"  🖼️  PNG: {png1.name}")
        print(f"  📕 PDF: {pdf1.name}")
        print()
        print("Multi-Span Bridge:")
        print(f"  📄 DXF: {dxf2.name}")
        print(f"  🖼️  PNG: {png2.name}")
        print(f"  📕 PDF: {pdf2.name}")
        print()
        print("Bridge Cross-Section:")
        print(f"  📄 DXF: {dxf3.name}")
        print(f"  🖼️  PNG: {png3.name}")
        print(f"  📕 PDF: {pdf3.name}")
        print()
        print("=" * 70)
        print("📂 Location: outputs/ folder")
        print("🎨 Formats: DXF (AutoCAD R2010), PNG (300 DPI), PDF (Print-ready)")
        print("📏 Units: Meters")
        print()
        print("🚀 Open these files in:")
        print("  • DXF: AutoCAD, LibreCAD, or any DXF viewer")
        print("  • PNG: Any image viewer")
        print("  • PDF: Adobe Reader, browser, or any PDF viewer")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
