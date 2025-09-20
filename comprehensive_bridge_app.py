#!/usr/bin/env python3
"""
Comprehensive Bridge GAD Generator Application
Incorporates the best features from all BridgeGAD applications
"""

import asyncio
import pygame
import math
import platform
import ezdxf
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from pathlib import Path
import sys
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import our enhanced architecture
try:
    from src.bridge_gad import (
        BridgeParameters, 
        BridgeDrawingGenerator, 
        BridgeType,
        OutputFormat,
        create_slab_bridge,
        create_beam_bridge,
        generate_bridge_drawing
    )
    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False
    logging.warning("Enhanced features not available, using basic functionality")

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Comprehensive Bridge GAD Generator")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)

# Font
font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 20, bold=True)
small_font = pygame.font.SysFont("arial", 14)

# View controls
zoom = 1.0
min_zoom, max_zoom = 0.1, 5.0
pan_x, pan_y = 0, 0

# Input state
input_mode = False
input_text = ""
input_field = 0
current_file_index = 0

# List of SweetWilledDocument files
sweet_willed_files = [
    "SweetWilledDocument-01.xlsx",
    "SweetWilledDocument-02.xlsx", 
    "SweetWilledDocument-03.xlsx",
    "SweetWilledDocument-04.xlsx",
    "SweetWilledDocument-07.xlsx",
    "SweetWilledDocument-08.xlsx",
    "SweetWilledDocument-09.xlsx",
    "SweetWilledDocument-10.xlsx"
]

# Default bridge parameters
bridge_params = {
    'scale1': 100.0, 'scale2': 50.0, 'skew': 0.0, 'datum': 100.0, 'toprl': 110.0,
    'left': 0.0, 'right': 20.0, 'xincr': 5.0, 'yincr': 1.0, 'noch': 4,
    'nspan': 1, 'lbridge': 20.0, 'abtl': 0.0, 'RTL': 105.0, 'Sofl': 103.0,
    'kerbw': 0.3, 'kerbd': 0.2, 'ccbr': 7.5, 'slbthc': 0.2, 'slbthe': 0.15,
    'slbtht': 0.1, 'capt': 104.0, 'capb': 103.5, 'capw': 1.0, 'piertw': 1.0,
    'battr': 10.0, 'pierst': 8.0, 'piern': 1, 'span1': 20.0, 'futrl': 95.0,
    'futd': 1.0, 'futw': 3.0, 'futl': 6.0, 'dwth': 0.3, 'alcw': 1.0,
    'alcd': 1.0, 'alfb': 10.0, 'alfbl': 101.0, 'altb': 10.0, 'altbl': 100.5,
    'alfo': 0.5, 'alfd': 1.0, 'albb': 8.0, 'albbl': 101.5
}

cs_data = [(0.0, 100.5), (5.0, 100.8), (10.0, 101.0), (15.0, 100.7), (20.0, 100.9)]

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

def load_bridge_parameters_from_csv(file_path: str) -> bool:
    """Load bridge parameters from CSV file (misnamed as .xlsx)."""
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check which format we have
        if 'Parameter' in df.columns:
            # Format 1: Parameter,Value,Description
            for _, row in df.iterrows():
                param = row['Parameter']
                value = row['Value']
                if param in bridge_params:
                    bridge_params[param] = float(value)
        elif 'Variable' in df.columns:
            # Format 2: Value,Variable,Description
            for _, row in df.iterrows():
                variable = row['Variable']
                value = row['Value']
                if variable in bridge_params:
                    bridge_params[param] = float(value)
        else:
            print(f"Unknown CSV format in {file_path}")
            return False
            
        init_derived()
        print(f"Successfully loaded parameters from {file_path}")
        return True
        
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return False

def render_parameter_panel():
    """Render parameter input panel."""
    panel_width = 400
    pygame.draw.rect(screen, (240, 240, 240), 
                    (WIDTH - panel_width, 0, panel_width, HEIGHT))
    
    # Panel title
    title = title_font.render("Bridge Parameters", True, BLACK)
    screen.blit(title, (WIDTH - panel_width + 10, 20))
    
    # Current file info
    file_info = small_font.render(f"File: {sweet_willed_files[current_file_index]}", True, BLUE)
    screen.blit(file_info, (WIDTH - panel_width + 10, 50))
    
    y_offset = 80
    count = 0
    for label, value in bridge_params.items():
        if y_offset < HEIGHT - 30 and count < 25:  # Limit display
            text = font.render(f"{label}: {value:.3f}", True, BLACK)
            screen.blit(text, (WIDTH - panel_width + 10, y_offset))
            y_offset += 20
            count += 1

def render_input_screen():
    """Render input screen."""
    screen.fill(WHITE)
    
    # Title
    title = title_font.render("Comprehensive Bridge GAD Generator - Input Mode", True, BLACK)
    screen.blit(title, (50, 50))
    
    # Instructions
    instructions = [
        "Bridge Parameter Files:",
        "Press LEFT/RIGHT arrows to navigate between files",
        "Press ENTER to load current file",
        "Press 'd' to save as DXF",
        "Press 'p' to save as PDF",
        "Press 'g' for enhanced generation"
    ]
    
    y_offset = 100
    for instruction in instructions:
        text = font.render(instruction, True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 25
    
    # Current file
    if 0 <= current_file_index < len(sweet_willed_files):
        current_file = sweet_willed_files[current_file_index]
        text = font.render(f"Current File: {current_file}", True, BLUE)
        screen.blit(text, (50, y_offset + 20))
    
    # File list
    y_offset += 60
    for i, file in enumerate(sweet_willed_files):
        color = BLUE if i == current_file_index else GRAY
        text = font.render(f"{i+1}. {file}", True, color)
        screen.blit(text, (50, y_offset))
        y_offset += 20
        if y_offset > HEIGHT - 50:
            break

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
        "P: Save PDF",
        "G: Enhanced Generation"
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
    if ENHANCED_FEATURES:
        try:
            # Use new enhanced architecture
            params = create_slab_bridge(
                span_length=bridge_params['lbridge'],
                deck_width=bridge_params['ccbr'],
                project_name="BridgeGAD Comprehensive",
                drawing_title="Slab Bridge - General Arrangement"
            )
            
            generator = BridgeDrawingGenerator(params)
            result = generator.generate_drawing([OutputFormat.DXF])
            
            if OutputFormat.DXF in result:
                print(f"Enhanced DXF saved as {result[OutputFormat.DXF]}")
            return
        except Exception as e:
            print(f"Enhanced save failed: {e}")
    
    # Fallback to original functionality
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    
    # Create layers
    layers = [
        ("STRUCTURE", 1, "Main structural elements"),
        ("DIMENSIONS", 6, "Dimension lines and text"),
        ("ANNOTATIONS", 3, "Text and labels"),
        ("GRID", 8, "Grid lines and axes"),
        ("FOUNDATION", 5, "Foundation elements")
    ]
    
    for name, color, description in layers:
        try:
            layer = doc.layers.new(name=name)
            layer.dxf.color = color
            layer.description = description
        except:
            pass  # Layer might already exist
    
    # Draw components
    draw_layout_grid_dxf(msp, doc)
    draw_cross_section_dxf(msp, doc)
    draw_pier_dxf(msp, doc)
    draw_abutment_dxf(msp, doc)
    
    # Add title block
    add_title_block_dxf(msp, doc)
    
    filename = f"comprehensive_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf"
    doc.saveas(filename)
    print(f"DXF saved as {filename}")

def save_enhanced_pdf():
    """Save enhanced PDF."""
    if ENHANCED_FEATURES:
        try:
            # Use new enhanced architecture
            params = create_slab_bridge(
                span_length=bridge_params['lbridge'],
                deck_width=bridge_params['ccbr'],
                project_name="BridgeGAD Comprehensive",
                drawing_title="Slab Bridge - General Arrangement"
            )
            
            generator = BridgeDrawingGenerator(params)
            result = generator.generate_drawing([OutputFormat.PDF])
            
            if OutputFormat.PDF in result:
                print(f"Enhanced PDF saved as {result[OutputFormat.PDF]}")
            return
        except Exception as e:
            print(f"Enhanced PDF save failed: {e}")
    
    # Fallback to original functionality
    filename = f"comprehensive_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf = canvas.Canvas(filename, pagesize=landscape(A4))
    
    # Draw components
    draw_layout_grid_pdf(pdf)
    draw_cross_section_pdf(pdf)
    draw_pier_pdf(pdf)
    draw_abutment_pdf(pdf)
    
    # Add title block
    add_title_block_pdf(pdf)
    
    pdf.showPage()
    pdf.save()
    print(f"PDF saved as {filename}")

def draw_layout_grid_dxf(msp, doc):
    """Draw layout grid in DXF."""
    d1 = 20
    pta1 = (bridge_params['left'], bridge_params['datum'])
    ptb1 = (bridge_params['left'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    pta2 = (bridge_params['right'], bridge_params['datum'])
    ptb2 = (bridge_params['right'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    ptc1 = (bridge_params['left'], bridge_params['datum'] - 2 * d1 * bridge_params['scale1'])
    ptc2 = (bridge_params['right'], bridge_params['datum'] - 2 * d1 * bridge_params['scale1'])
    ptd1 = (bridge_params['left'], bridge_params['toprl'])
    
    # Main grid lines
    msp.add_line(pta1, pta2, dxfattribs={"layer": "GRID"})
    msp.add_line(ptb1, ptb2, dxfattribs={"layer": "GRID"})
    msp.add_line(ptc1, ptc2, dxfattribs={"layer": "GRID"})
    msp.add_line(ptc1, ptd1, dxfattribs={"layer": "GRID"})
    
    # Labels
    ptb3 = (bridge_params['left'] - 25 * bridge_params['scale1'], 
            bridge_params['datum'] - 0.5 * d1 * bridge_params['scale1'])
    msp.add_text("BED LEVEL", dxfattribs={
        "height": 2.5 * bridge_params['scale1'],
        "layer": "ANNOTATIONS"
    }).set_placement(ptb3)
    
    ptb3 = (bridge_params['left'] - 25 * bridge_params['scale1'], 
            bridge_params['datum'] - 1.5 * d1 * bridge_params['scale1'])
    msp.add_text("CHAINAGE", dxfattribs={
        "height": 2.5 * bridge_params['scale1'],
        "layer": "ANNOTATIONS"
    }).set_placement(ptb3)

def draw_cross_section_dxf(msp, doc):
    """Draw cross-section in DXF."""
    ptb3 = None
    for a, (x, y) in enumerate(cs_data, 1):
        xx = x
        
        # Vertical line to datum
        pta5 = (xx, bridge_params['datum'] - 2 * bridge_params['scale1'])
        pta6 = (xx, bridge_params['datum'])
        msp.add_line(pta5, pta6, dxfattribs={"layer": "STRUCTURE"})
        
        # Cross-section line
        ptb4 = (x, y)
        if a > 1 and ptb3 is not None:
            msp.add_line(ptb3, ptb4, dxfattribs={"layer": "STRUCTURE", "lineweight": 2})
        ptb3 = ptb4

def draw_pier_dxf(msp, doc):
    """Draw pier in DXF."""
    # Elevation: Superstructure
    x1 = spane
    y1 = bridge_params['RTL']
    x2 = spane
    y2 = bridge_params['Sofl']
    pta1 = (x1 + 25.0, y1)
    pta2 = (x2 - 25.0, y2)
    
    # Draw superstructure rectangle
    points = [pta1, (pta2[0], pta1[1]), pta2, (pta1[0], pta2[1]), pta1]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "STRUCTURE"})

def draw_abutment_dxf(msp, doc):
    """Draw abutment in DXF."""
    # Basic abutment outline
    x1 = bridge_params['abtl']
    y1 = bridge_params['RTL']
    x2 = x1 + bridge_params['alcw']
    y2 = bridge_params['capt']
    
    pta1 = (x1, y1)
    pta2 = (x2, y2)
    
    points = [pta1, (pta2[0], pta1[1]), pta2, (pta1[0], pta2[1]), pta1]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "STRUCTURE"})

def add_title_block_dxf(msp, doc):
    """Add title block to DXF."""
    # Title block dimensions
    title_height = 40
    title_width = bridge_params['right'] - bridge_params['left']
    
    # Draw title block border
    title_points = [
        (0, 0), (title_width, 0), (title_width, title_height), (0, title_height), (0, 0)
    ]
    msp.add_lwpolyline(title_points, close=True, dxfattribs={
        "layer": "STRUCTURE",
        "lineweight": 3
    })
    
    # Add title
    msp.add_text("Comprehensive Bridge GAD Drawing", dxfattribs={
        "height": 8,
        "layer": "ANNOTATIONS"
    }).set_placement((title_width/2, title_height - 10), align="MIDDLE_CENTER")
    
    # Add date
    date_str = datetime.now().strftime("%Y-%m-%d")
    msp.add_text(f"Date: {date_str}", dxfattribs={
        "height": 4,
        "layer": "ANNOTATIONS"
    }).set_placement((20, title_height - 30), align="TOP_LEFT")

def draw_layout_grid_pdf(pdf):
    """Draw layout grid in PDF."""
    d1 = 20
    pta1 = pt(bridge_params['left'], bridge_params['datum'])
    ptb1 = pt(bridge_params['left'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    pta2 = pt(bridge_params['right'], bridge_params['datum'])
    ptb2 = pt(bridge_params['right'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    
    # Main grid lines
    pdf.setLineWidth(2)
    pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)
    pdf.setLineWidth(1)
    pdf.line(ptb1[0]/mm, ptb1[1]/mm, ptb2[0]/mm, ptb2[1]/mm)

def draw_cross_section_pdf(pdf):
    """Draw cross-section in PDF."""
    ptb3 = None
    for a, (x, y) in enumerate(cs_data, 1):
        xx = hpos(x)
        
        # Vertical line to datum
        pta5 = (xx, vpos(bridge_params['datum'] - 2 * bridge_params['scale1']))
        pta6 = (xx, vpos(bridge_params['datum']))
        pdf.setLineWidth(1)
        pdf.line(pta5[0]/mm, pta5[1]/mm, pta6[0]/mm, pta6[1]/mm)
        
        # Cross-section line
        ptb4 = pt(x, y)
        if a > 1 and ptb3 is not None:
            pdf.setLineWidth(2)
            pdf.line(ptb3[0]/mm, ptb3[1]/mm, ptb4[0]/mm, ptb4[1]/mm)
        ptb3 = ptb4

def draw_pier_pdf(pdf):
    """Draw pier in PDF."""
    # Elevation: Superstructure
    x1 = hpos(spane)
    y1 = vpos(bridge_params['RTL'])
    x2 = hpos(spane)
    y2 = vpos(bridge_params['Sofl'])
    pta1 = (x1 + 25, y1)
    pta2 = (x2 - 25, y2)
    
    pdf.setLineWidth(1)
    pdf.rect(pta1[0]/mm, min(pta1[1], pta2[1])/mm, 
             (pta2[0] - pta1[0])/mm, abs(pta2[1] - pta1[1])/mm, stroke=1, fill=0)

def draw_abutment_pdf(pdf):
    """Draw abutment in PDF."""
    # Basic abutment outline
    x1 = hpos(bridge_params['abtl'])
    y1 = vpos(bridge_params['RTL'])
    x2 = hpos(bridge_params['abtl'] + bridge_params['alcw'])
    y2 = vpos(bridge_params['capt'])
    
    pdf.setLineWidth(1)
    pdf.rect(x1/mm, min(y1, y2)/mm, 
             (x2 - x1)/mm, abs(y2 - y1)/mm, stroke=1, fill=0)

def add_title_block_pdf(pdf):
    """Add title block to PDF."""
    # Add title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50*mm, 250*mm, "Comprehensive Bridge GAD Drawing")
    
    # Add date
    date_str = datetime.now().strftime("%Y-%m-%d")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50*mm, 240*mm, f"Date: {date_str}")

def handle_input(event):
    """Handle input events."""
    global input_mode, input_text, input_field, current_file_index
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            if 0 <= current_file_index < len(sweet_willed_files):
                file_path = sweet_willed_files[current_file_index]
                if load_bridge_parameters_from_csv(file_path):
                    input_mode = False
                    init_derived()
        elif event.key == pygame.K_LEFT:
            current_file_index = max(0, current_file_index - 1)
        elif event.key == pygame.K_RIGHT:
            current_file_index = min(len(sweet_willed_files) - 1, current_file_index + 1)

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
                elif event.key == pygame.K_d:
                    save_enhanced_dxf()
                elif event.key == pygame.K_p:
                    save_enhanced_pdf()
                elif event.key == pygame.K_g and ENHANCED_FEATURES:
                    print("Generating enhanced bridge drawing...")
                    try:
                        params = create_slab_bridge(
                            span_length=bridge_params['lbridge'],
                            deck_width=bridge_params['ccbr'],
                            project_name="BridgeGAD Comprehensive",
                            drawing_title="Slab Bridge - General Arrangement"
                        )
                        
                        results = generate_bridge_drawing(params, [OutputFormat.DXF, OutputFormat.PDF])
                        print("Enhanced drawing generated:")
                        for fmt, path in results.items():
                            print(f"  {fmt.value}: {path}")
                    except Exception as e:
                        print(f"Error in enhanced generation: {e}")
                        
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