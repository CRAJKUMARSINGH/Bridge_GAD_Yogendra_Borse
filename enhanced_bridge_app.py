"""
Enhanced Bridge GAD Generator Application
Integrates all missing LISP functions from bridge_code.lsp
"""

import asyncio
import pygame
import math
import platform
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))
from bridge_gad.enhanced_lisp_functions import EnhancedLispFunctions

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Bridge GAD Generator")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)

# Font
font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 20, bold=True)

# View controls
zoom = 1.0
min_zoom, max_zoom = 0.1, 5.0
pan_x, pan_y = 0, 0

# Input state
input_mode = False
input_text = ""
input_field = 0
input_labels = [
    "Scale1 (plan/elevation): ",
    "Scale2 (sections): ",
    "Skew angle (degrees): ",
    "Datum level: ",
    "Top RL: ",
    "Left chainage: ",
    "Right chainage: ",
    "X increment (m): ",
    "Y increment (m): ",
    "Number of chainages: ",
    "Number of spans: ",
    "Bridge length (m): ",
    "Left abutment chainage: ",
    "Right abutment top level: ",
    "Soffit level: ",
    "Kerb width (m): ",
    "Kerb depth (m): ",
    "Clear carriageway width (m): ",
    "Slab thickness center (m): ",
    "Slab thickness edge (m): ",
    "Slab thickness tip (m): ",
    "Pier cap top level: ",
    "Pier cap bottom level: ",
    "Pier cap width (m): ",
    "Pier top width (m): ",
    "Pier batter ratio: ",
    "Pier straight length (m): ",
    "Pier number for section: ",
    "Span length (m): ",
    "Foundation level (m): ",
    "Foundation depth (m): ",
    "Foundation width (m): ",
    "Foundation length (m): ",
    "Dirt wall thickness (m): ",
    "Abutment left cap width (m): ",
    "Abutment left cap depth (m): ",
    "Abutment left face batter: ",
    "Abutment left face bottom level: ",
    "Abutment left toe batter: ",
    "Abutment left toe bottom level: ",
    "Abutment left face offset (m): ",
    "Abutment left face depth (m): ",
    "Abutment left back batter: ",
    "Abutment left back bottom level: ",
    "Enter cross-section points (x,y) or 'done': "
]

input_data = []

# Default bridge parameters
bridge_params = {
    'scale1': 1.0, 'scale2': 1.0, 'skew': 15.0, 'datum': 100.0, 'toprl': 110.0,
    'left': 0.0, 'right': 100.0, 'xincr': 10.0, 'yincr': 1.0, 'noch': 5,
    'nspan': 1, 'lbridge': 100.0, 'abtl': 0.0, 'RTL': 105.0, 'Sofl': 104.0,
    'kerbw': 1.0, 'kerbd': 0.5, 'ccbr': 8.0, 'slbthc': 0.3, 'slbthe': 0.25,
    'slbtht': 0.15, 'capt': 103.0, 'capb': 102.5, 'capw': 2.0, 'piertw': 1.5,
    'battr': 12.0, 'pierst': 10.0, 'piern': 1, 'span1': 50.0, 'futrl': 99.0,
    'futd': 1.0, 'futw': 3.0, 'futl': 5.0, 'dwth': 0.5, 'alcw': 2.0,
    'alcd': 0.5, 'alfb': 6.0, 'alfbl': 101.5, 'altb': 12.0, 'altbl': 100.5,
    'alfo': 1.0, 'alfd': 1.0, 'albb': 6.0, 'albbl': 101.5
}

cs_data = [(0.0, 100.5), (20.0, 101.0), (40.0, 100.8), (60.0, 101.2), (80.0, 100.7)]

def init_derived():
    """Initialize derived variables."""
    global hs, vs, vvs, hhs, skew1, s, c, tn, sc, spane, RTL2, ccbrsq, kerbwsq, abtlen
    hs = 1.0
    vs = 1.0
    vvs = 50.0 * zoom
    hhs = 50.0 * zoom
    skew1 = bridge_params['skew'] * 0.0174532
    s = math.sin(skew1)
    c = math.cos(skew1)
    tn = s / c if c != 0 else 0
    sc = bridge_params['scale1'] / bridge_params['scale2']
    spane = bridge_params['abtl'] + bridge_params['span1']
    RTL2 = bridge_params['RTL'] - 30 * sc
    ccbrsq = bridge_params['ccbr'] / c if c != 0 else bridge_params['ccbr']
    kerbwsq = bridge_params['kerbw'] / c if c != 0 else bridge_params['kerbw']
    abtlen = ccbrsq + 2 * kerbwsq

def vpos(a, for_dxf=False):
    """Vertical position calculation."""
    a = (1000 if for_dxf else vvs) * (a - bridge_params['datum'])
    return (0 if for_dxf else HEIGHT) - a + (0 if for_dxf else pan_y)

def hpos(a, for_dxf=False):
    """Horizontal position calculation."""
    a = (1000 if for_dxf else hhs) * (a - bridge_params['left'])
    return a + (0 if for_dxf else 50 + pan_x)

def pt(a, b, for_dxf=False):
    """Point creation."""
    return (hpos(a, for_dxf), vpos(b, for_dxf))

def render_parameter_panel():
    """Render parameter input panel."""
    panel_width = 400
    pygame.draw.rect(screen, (240, 240, 240), 
                    (WIDTH - panel_width, 0, panel_width, HEIGHT))
    
    # Panel title
    title = title_font.render("Bridge Parameters", True, BLACK)
    screen.blit(title, (WIDTH - panel_width + 10, 20))
    
    y_offset = 60
    for i, (label, value) in enumerate(bridge_params.items()):
        if y_offset < HEIGHT - 30:
            text = font.render(f"{label}: {value:.3f}", True, BLACK)
            screen.blit(text, (WIDTH - panel_width + 10, y_offset))
            y_offset += 25

def render_input_screen():
    """Render input screen."""
    screen.fill(WHITE)
    
    # Title
    title = title_font.render("Enhanced Bridge GAD Generator - Input Mode", True, BLACK)
    screen.blit(title, (50, 50))
    
    # Instructions
    instructions = [
        "Enter bridge parameters:",
        "Press ENTER to confirm each value",
        "Press 'i' to return to drawing mode",
        "Press 'd' to save as DXF",
        "Press 'p' to save as PDF"
    ]
    
    y_offset = 100
    for instruction in instructions:
        text = font.render(instruction, True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 25
    
    # Current input field
    if input_field < len(input_labels):
        label = input_labels[input_field]
        text = font.render(f"{label}{input_text}", True, BLUE)
        screen.blit(text, (50, y_offset + 20))
    
    # Input data display
    y_offset += 60
    for i, data in enumerate(input_data):
        if i < 20:  # Limit display
            text = font.render(f"{i+1}: {data}", True, GREEN)
            screen.blit(text, (50, y_offset))
            y_offset += 20

def render_drawing():
    """Render the bridge drawing."""
    screen.fill(WHITE)
    
    # Draw bridge components
    init_derived()
    
    # Draw layout grid
    draw_layout_grid()
    
    # Draw cross-section
    draw_cross_section()
    
    # Draw pier
    draw_pier()
    
    # Draw abutment
    draw_abutment()
    
    # Draw parameter panel
    render_parameter_panel()
    
    # Draw controls info
    controls = [
        "Controls:",
        "Mouse wheel: Zoom",
        "Mouse drag: Pan",
        "R: Reset view",
        "I: Input mode",
        "D: Save DXF",
        "P: Save PDF"
    ]
    
    y_offset = 20
    for control in controls:
        text = font.render(control, True, BLACK)
        screen.blit(text, (10, y_offset))
        y_offset += 20

def draw_layout_grid():
    """Draw the layout grid system."""
    d1 = 20
    pta1 = pt(bridge_params['left'], bridge_params['datum'])
    ptb1 = pt(bridge_params['left'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    pta2 = pt(bridge_params['right'], bridge_params['datum'])
    ptb2 = pt(bridge_params['right'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    ptc1 = pt(bridge_params['left'], bridge_params['datum'] - 2 * d1 * bridge_params['scale1'])
    ptc2 = pt(bridge_params['right'], bridge_params['datum'] - 2 * d1 * bridge_params['scale1'])
    ptd1 = pt(bridge_params['left'], bridge_params['toprl'])
    
    # Main grid lines
    pygame.draw.line(screen, BLACK, pta1, pta2, 2)
    pygame.draw.line(screen, BLACK, ptb1, ptb2, 1)
    pygame.draw.line(screen, BLACK, ptc1, ptc2, 1)
    pygame.draw.line(screen, BLACK, ptc1, ptd1, 2)
    
    # Labels
    ptb3 = pt(bridge_params['left'] - 25 * bridge_params['scale1'], 
               bridge_params['datum'] - 0.5 * d1 * bridge_params['scale1'])
    text = font.render("BED LEVEL", True, BLACK)
    screen.blit(text, ptb3)
    
    ptb3 = pt(bridge_params['left'] - 25 * bridge_params['scale1'], 
               bridge_params['datum'] - 1.5 * d1 * bridge_params['scale1'])
    text = font.render("CHAINAGE", True, BLACK)
    screen.blit(text, ptb3)

def draw_cross_section():
    """Draw the cross-section."""
    ptb3 = None
    for a, (x, y) in enumerate(cs_data, 1):
        b2 = f"{y:.3f}"
        xx = hpos(x)
        
        # River level annotation
        pta2 = (xx + 0.9 * bridge_params['scale1'], 
                vpos(bridge_params['datum'] - 16 * bridge_params['scale1']))
        text = font.render(b2, True, BLACK)
        text = pygame.transform.rotate(text, 90)
        screen.blit(text, (pta2[0], pta2[1] - 20))
        
        # Vertical line to datum
        pta5 = (xx, vpos(bridge_params['datum'] - 2 * bridge_params['scale1']))
        pta6 = (xx, vpos(bridge_params['datum']))
        pygame.draw.line(screen, BLACK, pta5, pta6, 1)
        
        # Cross-section line
        ptb4 = pt(x, y)
        if a > 1 and ptb3 is not None:
            pygame.draw.line(screen, BLACK, ptb3, ptb4, 2)
        ptb3 = ptb4

def draw_pier():
    """Draw the pier geometry."""
    yc = bridge_params['datum'] - 30.0
    
    # Elevation: Superstructure
    x1 = hpos(spane)
    y1 = vpos(bridge_params['RTL'])
    x2 = hpos(spane)
    y2 = vpos(bridge_params['Sofl'])
    pta1 = (x1 + 25, y1)
    pta2 = (x2 - 25, y2)
    
    pygame.draw.rect(screen, BLACK, 
                    (pta1[0], min(pta1[1], pta2[1]), 
                     pta2[0] - pta1[0], abs(pta2[1] - pta1[1])), 1)
    
    # Pier cap
    capwsq = bridge_params['capw'] / c if c != 0 else bridge_params['capw']
    x1 = spane - capwsq / 2
    x2 = x1 + capwsq
    y1 = bridge_params['capt']
    y2 = bridge_params['capb']
    pta1 = pt(x1, y1)
    pta2 = pt(x2, y2)
    
    pygame.draw.rect(screen, BLACK, 
                    (pta1[0], min(pta1[1], pta2[1]), 
                     pta2[0] - pta1[0], abs(pta2[1] - pta1[1])), 1)

def draw_abutment():
    """Draw the abutment geometry."""
    # Basic abutment outline
    x1 = bridge_params['abtl']
    y1 = bridge_params['RTL']
    x2 = x1 + bridge_params['alcw']
    y2 = bridge_params['capt']
    
    pta1 = pt(x1, y1)
    pta2 = pt(x2, y2)
    
    pygame.draw.rect(screen, BLACK, 
                    (pta1[0], min(pta1[1], pta2[1]), 
                     pta2[0] - pta1[0], abs(pta2[1] - pta1[1])), 1)

def save_enhanced_dxf():
    """Save enhanced DXF with all LISP functions."""
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    
    # Create enhanced LISP functions instance
    enhanced = EnhancedLispFunctions(doc, msp)
    
    # Set up text styles
    enhanced.st()
    
    # Create professional layout
    enhanced.create_professional_layout(
        width=bridge_params['right'] - bridge_params['left'],
        height=bridge_params['toprl'] - bridge_params['datum'],
        title="Enhanced Bridge GAD Drawing",
        scale=f"1:{int(1000/bridge_params['scale1'])}",
        drawing_number="BGD-ENHANCED-001"
    )
    
    # Draw enhanced components
    enhanced.enhanced_layout(
        bridge_params['left'], bridge_params['right'], 
        bridge_params['datum'], bridge_params['toprl'],
        bridge_params['scale1'], bridge_params['xincr'], bridge_params['yincr']
    )
    
    enhanced.enhanced_cs(
        cs_data, bridge_params['left'], bridge_params['datum'],
        bridge_params['scale1'], bridge_params['xincr']
    )
    
    enhanced.enhanced_pier(
        spane, bridge_params['RTL'], bridge_params['Sofl'],
        bridge_params['capt'], bridge_params['capb'], bridge_params['capw'],
        bridge_params['piertw'], bridge_params['battr'], bridge_params['pierst'],
        bridge_params['futrl'], bridge_params['futd'], bridge_params['futw'],
        bridge_params['futl'], bridge_params['skew'], c, s, tn
    )
    
    enhanced.enhanced_abt1(
        bridge_params['abtl'], bridge_params['RTL'], bridge_params['capt'],
        bridge_params['ccbr'], bridge_params['kerbw'], bridge_params['dwth'],
        bridge_params['alcw'], bridge_params['alcd'], bridge_params['alfb'],
        bridge_params['alfbl'], bridge_params['altb'], bridge_params['altbl'],
        bridge_params['alfo'], bridge_params['alfd'], bridge_params['albb'],
        bridge_params['albbl'], bridge_params['skew'], c, s
    )
    
    doc.saveas("enhanced_bridge_gad.dxf")
    print("Enhanced DXF saved as 'enhanced_bridge_gad.dxf'")

def handle_input(event):
    """Handle input events."""
    global input_mode, input_text, input_field, input_data, bridge_params
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            if input_text:
                input_data.append(input_text)
                
                # Update bridge parameters
                if input_field < len(input_labels) - 1:  # Not cross-section data
                    try:
                        value = float(input_text)
                        param_name = list(bridge_params.keys())[input_field]
                        bridge_params[param_name] = value
                    except (ValueError, IndexError):
                        pass
                
                input_text = ""
                input_field += 1
                
                if input_field >= len(input_labels):
                    input_mode = False
                    init_derived()
                    
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
        elif event.unicode.isprintable():
            input_text += event.unicode

def update_loop():
    """Main update loop."""
    global zoom, pan_x, pan_y, input_mode
    
    mouse_dragging = False
    start_pan_x, start_pan_y = pan_x, pan_y
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
            
        if input_mode:
            handle_input(event)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom = min(max_zoom, zoom * 1.1)
                    init_derived()
                elif event.key == pygame.K_MINUS:
                    zoom = max(min_zoom, zoom / 1.1)
                    init_derived()
                elif event.key == pygame.K_r:
                    zoom, pan_x, pan_y = 1.0, 0, 0
                    init_derived()
                elif event.key == pygame.K_i:
                    input_mode = True
                    input_text = ""
                    input_field = 0
                    input_data = []
                elif event.key == pygame.K_d:
                    save_enhanced_dxf()
                elif event.key == pygame.K_p:
                    print("PDF export not implemented yet")
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    zoom = min(max_zoom, zoom * 1.1)
                    init_derived()
                elif event.button == 5:  # Mouse wheel down
                    zoom = max(min_zoom, zoom / 1.1)
                    init_derived()
                elif event.button == 1:  # Left mouse button
                    mouse_dragging = True
                    start_pos = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_dragging = False
                    
            elif event.type == pygame.MOUSEMOTION and mouse_dragging:
                pan_x = start_pan_x + (event.pos[0] - start_pos[0])
                pan_y = start_pan_y + (event.pos[1] - start_pos[1])
    
    # Render
    if input_mode:
        render_input_screen()
    else:
        render_drawing()
    
    pygame.display.flip()
    clock.tick(FPS)
    return True

async def main():
    """Main function."""
    init_derived()
    running = True
    
    while running:
        running = update_loop()
        await asyncio.sleep(1.0 / FPS)

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())
