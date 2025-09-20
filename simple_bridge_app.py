#!/usr/bin/env python3
"""
Simple Bridge GAD Generator Application
Simplified version that works with current environment
"""

import asyncio
import pygame
import math
import platform
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
# noinspection PyUnresolvedReferences
from pathlib import Path
import sys
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Bridge GAD Generator")
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
    'alfo': 0.5, 'alfd': 1.0, 'albb': 8.0, 'albbl': 101.5,
    # Additional parameters for right abutment
    'alfbr': 101.0, 'altbr': 100.5, 'albbr': 101.5, 'arfl': 95.0
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
        # Simple CSV parsing without pandas
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return False
            
        # Parse header
        header = lines[0].strip().split(',')
        
        # Check which format we have
        if 'Parameter' in header:
            # Format 1: Parameter,Value,Description
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    param = parts[0]
                    value = parts[1]
                    if param in bridge_params:
                        bridge_params[param] = float(value)
        elif 'Variable' in header:
            # Format 2: Value,Variable,Description
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    value = parts[0]
                    variable = parts[1]
                    if variable in bridge_params:
                        bridge_params[variable] = float(value)
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
    title = title_font.render("Simple Bridge GAD Generator - Input Mode", True, BLACK)
    screen.blit(title, (50, 50))
    
    # Instructions
    instructions = [
        "Bridge Parameter Files:",
        "Press LEFT/RIGHT arrows to navigate between files",
        "Press ENTER to load current file",
        "Press 'd' to save as DXF",
        "Press 'p' to save as PDF"
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
        "P: Save PDF"
    ]
    
    y_offset = 20
    for control in controls:
        text = font.render(control, True, BLACK)
        screen.blit(text, (10, y_offset))
        y_offset += 20

def draw_layout_grid():
    """Draw the layout grid system with enhanced details."""
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
    
    # Vertical grid lines with level annotations
    nov = int(bridge_params['toprl'] - bridge_params['datum'])
    for i in range(nov + 1):
        lvl = bridge_params['datum'] + i * bridge_params['yincr']
        pta1 = pt(bridge_params['left'] - 13 * bridge_params['scale1'], lvl)
        text = font.render(f"{lvl:.3f}", True, BLACK)
        screen.blit(text, (pta1[0] - 40, pta1[1] - 10))
        
        # Grid line
        if i > 0:
            pta1 = pt(bridge_params['left'] - 2.5 * bridge_params['scale1'], lvl)
            pta2 = pt(bridge_params['left'] + 2.5 * bridge_params['scale1'], lvl)
            pygame.draw.line(screen, GRAY, pta1, pta2, 1)
    
    # Horizontal grid lines with chainage annotations
    noh = bridge_params['right'] - bridge_params['left']
    n = int(noh / bridge_params['xincr'])
    d4 = 2 * d1
    d5 = d4 - 2.0
    d8 = d4 - 4.0
    
    for a in range(1, n + 1):
        ch = bridge_params['left'] + a * bridge_params['xincr']
        b1 = f"{ch:.3f}"
        pta1 = pt(ch, bridge_params['datum'] - d8 * bridge_params['scale1'])
        
        # Chainage text
        text = font.render(b1, True, BLACK)
        text = pygame.transform.rotate(text, 90)
        screen.blit(text, (pta1[0] - 10, pta1[1] - 20))
        
        # Grid line
        pta1 = pt(ch, bridge_params['datum'] - d4 * bridge_params['scale1'])
        pta2 = pt(ch, bridge_params['datum'] - d5 * bridge_params['scale1'])
        pygame.draw.line(screen, GRAY, pta1, pta2, 1)

def draw_cross_section():
    """Draw the cross-section with enhanced annotations."""
    ptb3 = None
    d1 = 20
    d4 = 2 * d1
    d5 = d4 - 2.0
    d8 = d4 - 4.0
    d9 = d1 - 4.0
    
    for a, (x, y) in enumerate(cs_data, 1):
        b1 = f"{x:.3f}"
        b2 = f"{y:.3f}"
        xx = hpos(x)
        
        # River level annotation
        pta2 = (xx + 0.9 * bridge_params['scale1'], 
                vpos(bridge_params['datum'] - d9 * bridge_params['scale1']))
        text = font.render(b2, True, BLACK)
        text = pygame.transform.rotate(text, 90)
        screen.blit(text, (pta2[0], pta2[1] - 20))
        
        # Chainage annotation (if not on grid)
        b = (x - bridge_params['left']) % bridge_params['xincr']
        if b != 0.0:
            pta1 = (xx + 0.9 * bridge_params['scale1'], 
                    vpos(bridge_params['datum'] - d8 * bridge_params['scale1']))
            text = font.render(b1, True, BLACK)
            text = pygame.transform.rotate(text, 90)
            screen.blit(text, (pta1[0], pta1[1] - 20))
            
            # Grid line markers
            pta1 = (xx, vpos(bridge_params['datum'] - d4 * bridge_params['scale1']))
            pta2 = (xx, vpos(bridge_params['datum'] - d5 * bridge_params['scale1']))
            pygame.draw.line(screen, BLACK, pta1, pta2, 1)
        
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
    """Draw the pier geometry with enhanced details."""
    # Initialize derived variables
    skew1 = bridge_params['skew'] * 0.0174532
    s = math.sin(skew1)
    c = math.cos(skew1)
    tn = s / c if c != 0 else 0
    spane = bridge_params['abtl'] + bridge_params['span1']
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
    
    # Elevation: Pier cap
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
    
    # Elevation: Pier with batter
    piertwsq = bridge_params['piertw'] / c if c != 0 else bridge_params['piertw']
    x1 = spane - piertwsq / 2
    x3 = x1 + piertwsq
    y2 = bridge_params['futrl'] + bridge_params['futd']
    ofset = (bridge_params['capb'] - y2) / bridge_params['battr']
    ofsetsq = ofset / c if c != 0 else ofset
    x2 = x1 - ofsetsq
    x4 = x3 + ofsetsq
    y4 = y2
    
    pta1 = pt(x1, bridge_params['capb'])
    pta2 = pt(x2, y2)
    pta3 = pt(x3, bridge_params['capb'])
    pta4 = pt(x4, y4)
    
    # Draw pier sides with batter
    pygame.draw.line(screen, BLACK, pta1, pta2, 2)
    pygame.draw.line(screen, BLACK, pta3, pta4, 2)
    
    # Elevation: Foundation footing
    futwsq = bridge_params['futw'] / c if c != 0 else bridge_params['futw']
    x5 = spane - futwsq / 2
    x6 = x5 + futwsq
    y6 = bridge_params['futrl']
    y5 = y4
    
    pta5 = pt(x5, y5)
    pta6 = pt(x6, y6)
    
    # Draw foundation footing
    pygame.draw.rect(screen, BLACK, 
                    (pta5[0], min(pta5[1], pta6[1]), 
                     pta6[0] - pta5[0], abs(pta6[1] - pta5[1])), 1)
    
    # Plan view: Foundation footing (simplified representation)
    x7 = spane - bridge_params['futw'] / 2
    x8 = x7 + bridge_params['futw']
    y7 = yc + bridge_params['futl'] / 2
    y8 = y7 - bridge_params['futl']
    
    # Offset for plan view visibility
    plan_offset_y = 100
    pta7 = pt(x7, y7 - plan_offset_y)
    pta8 = pt(x8, y8 - plan_offset_y)
    
    # Draw plan view rectangle
    pygame.draw.rect(screen, BLACK, 
                    (pta7[0], min(pta7[1], pta8[1]), 
                     pta8[0] - pta7[0], abs(pta8[1] - pta7[1])), 1)
    
    # Plan view: Pier with batter (simplified representation)
    pierstsq = (bridge_params['pierst'] / c) + abs(bridge_params['piertw'] * tn) if c != 0 else bridge_params['pierst']
    x1_pier = spane - bridge_params['piertw'] / 2
    x3_pier = x1_pier + bridge_params['piertw']
    x2_pier = x1_pier - ofset
    x4_pier = x3_pier + ofset
    y9 = yc + pierstsq / 2
    y10 = y9 - pierstsq
    
    # Draw pier plan lines
    lines = [
        ((x2_pier, y9), (x2_pier, y10)),
        ((x1_pier, y9), (x1_pier, y10)),
        ((x3_pier, y9), (x3_pier, y10)),
        ((x4_pier, y9), (x4_pier, y10))
    ]
    
    for start, end in lines:
        start_pt = pt(start[0], start[1] - plan_offset_y)
        end_pt = pt(end[0], end[1] - plan_offset_y)
        pygame.draw.line(screen, BLACK, start_pt, end_pt, 2)

def draw_abutment():
    """Draw the abutment geometry with enhanced details."""
    # Initialize derived variables
    skew1 = bridge_params['skew'] * 0.0174532
    s = math.sin(skew1)
    c = math.cos(skew1)
    
    # Calculate abutment dimensions
    ccbrsq = bridge_params['ccbr'] / c if c != 0 else bridge_params['ccbr']
    kerbwsq = bridge_params['kerbw'] / c if c != 0 else bridge_params['kerbw']
    abtlen = ccbrsq + 2 * kerbwsq
    
    # Elevation calculations (enhanced)
    x1 = bridge_params['abtl']
    alcwsq = bridge_params['alcw']
    x3 = x1 + alcwsq
    capb = bridge_params['capt'] - bridge_params['alcd']
    p1 = (capb - bridge_params['alfbl']) / bridge_params['alfb']
    x5 = x3 + p1
    p2 = (bridge_params['alfbl'] - bridge_params['altbl']) / bridge_params['altb']
    x6 = x5 + p2
    alfosq = bridge_params['alfo']
    x7 = x6 + alfosq
    y8 = bridge_params['altbl'] - bridge_params['alfd']
    dwthsq = bridge_params['dwth']
    x14 = x1 - dwthsq
    p3 = (capb - bridge_params['albbl']) / bridge_params['albb']
    x12 = x14 - p3
    x10 = x12 - alfosq
    
    # Create elevation points
    points = [
        pt(x1, bridge_params['RTL']), pt(x1, bridge_params['capt']), pt(x3, bridge_params['capt']), pt(x3, capb),
        pt(x5, bridge_params['alfbl']), pt(x6, bridge_params['altbl']), pt(x7, bridge_params['altbl']), pt(x7, y8),
        pt(x10, y8), pt(x10, bridge_params['altbl']), pt(x12, bridge_params['altbl']), pt(x12, bridge_params['albbl']),
        pt(x14, capb), pt(x14, bridge_params['RTL']), pt(x1, bridge_params['RTL'])
    ]
    
    # Draw elevation outline
    for i in range(len(points) - 1):
        pygame.draw.line(screen, BLACK, points[i], points[i+1], 1)
    
    # Draw internal lines
    pygame.draw.line(screen, BLACK, pt(x14, capb), pt(x3, capb), 1)
    pygame.draw.line(screen, BLACK, pt(x10, bridge_params['altbl']), pt(x7, bridge_params['altbl']), 1)
    pygame.draw.line(screen, BLACK, pt(x12, bridge_params['albbl']), pt(x12, bridge_params['RTL']), 1)
    pygame.draw.line(screen, BLACK, pt(x12, bridge_params['RTL']), pt(x14, bridge_params['RTL']), 1)
    
    # Plan view calculations
    yc = bridge_params['datum'] - 30.0
    y20 = yc + abtlen / 2
    y21 = y20 - abtlen
    y16 = y20 + 0.15
    y17 = y21 - 0.15
    footl = (y16 - y17) / 2
    x_skew = footl * s
    y_skew = footl * (1 - c)
    
    # Create plan view points with offset for visibility
    plan_offset_y = 100
    pt16 = pt(x10 - x_skew, y16 - y_skew - plan_offset_y)
    pt17 = pt(x10 + x_skew, y17 + y_skew - plan_offset_y)
    pt18 = pt(x7 - x_skew, y16 - y_skew - plan_offset_y)
    pt19 = pt(x7 + x_skew, y17 + y_skew - plan_offset_y)
    
    # Draw plan view outline
    plan_points = [pt16, pt17, pt19, pt18, pt16]
    for i in range(len(plan_points) - 1):
        pygame.draw.line(screen, BLACK, plan_points[i], plan_points[i+1], 1)
    
    # Additional plan view lines with skew adjustment
    xx = abtlen / 2
    x = xx * s
    y = xx * (1 - c)
    y20_adj = y20 - y
    y21_adj = y21 + y
    
    # Create additional plan view points
    plan_lines = [
        (pt(x12 - x, y20_adj - plan_offset_y), pt(x12 + x, y21_adj - plan_offset_y)),
        (pt(x14 - x, y20_adj - plan_offset_y), pt(x14 + x, y21_adj - plan_offset_y)),
        (pt(x1 - x, y20_adj - plan_offset_y), pt(x1 + x, y21_adj - plan_offset_y)),
        (pt(x3 - x, y20_adj - plan_offset_y), pt(x3 + x, y21_adj - plan_offset_y)),
        (pt(x5 - x, y20_adj - plan_offset_y), pt(x5 + x, y21_adj - plan_offset_y)),
        (pt(x6 - x, y20_adj - plan_offset_y), pt(x6 + x, y21_adj - plan_offset_y)),
        (pt(x12 + x, y21_adj - plan_offset_y), pt(x6 + x, y21_adj - plan_offset_y)),
        (pt(x12 - x, y20_adj - plan_offset_y), pt(x6 - x, y20_adj - plan_offset_y))
    ]
    
    # Draw additional plan view lines
    for start, end in plan_lines:
        pygame.draw.line(screen, BLACK, start, end, 1)

def save_dxf():
    """Save DXF with enhanced bridge drawing capabilities."""
    # noinspection PyUnresolvedReferences
    doc = ezdxf.new("R2010", setup=True)  # type: ignore
    msp = doc.modelspace()
    
    # Create layers for different elements
    layers = [
        ("GRID", 1, "Grid lines and axes"),
        ("STRUCTURE", 2, "Main structural elements"),
        ("DIMENSIONS", 3, "Dimension lines and text"),
        ("ANNOTATIONS", 4, "Text and labels"),
        ("ABUTMENT", 5, "Abutment elements"),
        ("PIER", 6, "Pier elements"),
        ("FOUNDATION", 7, "Foundation elements"),
        ("CROSS_SECTION", 8, "Cross-section data"),
        ("TITLE_BLOCK", 9, "Title block elements")
    ]
    
    for name, color, description in layers:
        try:
            layer = doc.layers.add(name=name)
            layer.dxf.color = color
            layer.description = description
        except:
            pass  # Layer might already exist
    
    # Set up dimension style
    if "PMB100" not in doc.dimstyles:
        dimstyle = doc.dimstyles.add("PMB100")
        dimstyle.dxf.dimtxt = 400    # Text height
        dimstyle.dxf.dimasz = 150    # Arrow size
        dimstyle.dxf.dimexe = 400    # Extension line extension
        dimstyle.dxf.dimexo = 400    # Extension line offset
        dimstyle.dxf.dimlfac = 1.0   # Linear factor
        dimstyle.dxf.dimdec = 0      # Decimal places
    
    # Draw enhanced components using the improved functions
    draw_layout_grid_dxf(msp, doc)
    draw_cross_section_dxf(msp, doc)
    draw_pier_dxf(msp, doc)
    draw_abutment_dxf(msp, doc)
    add_enhanced_title_block_dxf(msp, doc)
    
    filename = f"enhanced_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf"
    doc.saveas(filename)
    print(f"Enhanced DXF saved as {filename}")

def save_pdf():
    """Save PDF."""
    filename = f"simple_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
    """Draw enhanced layout grid in DXF with proper dimensioning."""
    d1 = 20
    pta1 = (bridge_params['left'], bridge_params['datum'])
    ptb1 = (bridge_params['left'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    pta2 = (bridge_params['right'], bridge_params['datum'])
    ptb2 = (bridge_params['right'], bridge_params['datum'] - d1 * bridge_params['scale1'])
    ptc1 = (bridge_params['left'], bridge_params['datum'] - 2 * d1 * bridge_params['scale1'])
    ptc2 = (bridge_params['right'], bridge_params['datum'] - 2 * d1 * bridge_params['scale1'])
    ptd1 = (bridge_params['left'], bridge_params['toprl'])
    
    # Main grid lines
    msp.add_line(pta1, pta2, dxfattribs={"layer": "GRID", "lineweight": 2})
    msp.add_line(ptb1, ptb2, dxfattribs={"layer": "GRID", "lineweight": 1})
    msp.add_line(ptc1, ptc2, dxfattribs={"layer": "GRID", "lineweight": 1})
    msp.add_line(ptc1, ptd1, dxfattribs={"layer": "GRID", "lineweight": 2})
    
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
    
    # Vertical grid lines with level annotations
    nov = int(bridge_params['toprl'] - bridge_params['datum'])
    for i in range(nov + 1):
        lvl = bridge_params['datum'] + i * bridge_params['yincr']
        pta1 = (bridge_params['left'] - 13 * bridge_params['scale1'], lvl)
        msp.add_text(f"{lvl:.3f}", dxfattribs={
            "height": 2.0 * bridge_params['scale1'],
            "layer": "ANNOTATIONS"
        }).set_placement((pta1[0] - 40, pta1[1] - 2.5))
        
        # Grid line
        if i > 0:
            pta1 = (bridge_params['left'] - 2.5 * bridge_params['scale1'], lvl)
            pta2 = (bridge_params['left'] + 2.5 * bridge_params['scale1'], lvl)
            msp.add_line(pta1, pta2, dxfattribs={
                "layer": "GRID",
                "color": 7  # Gray
            })
    
    # Horizontal grid lines with chainage annotations
    noh = bridge_params['right'] - bridge_params['left']
    n = int(noh / bridge_params['xincr'])
    d4 = 2 * d1
    d5 = d4 - 2.0
    d8 = d4 - 4.0
    
    for a in range(1, n + 1):
        ch = bridge_params['left'] + a * bridge_params['xincr']
        b1 = f"{ch:.3f}"
        pta1 = (ch, bridge_params['datum'] - d8 * bridge_params['scale1'])
        
        # Chainage text
        msp.add_text(b1, dxfattribs={
            "height": 2.0 * bridge_params['scale1'],
            "rotation": 90,
            "layer": "ANNOTATIONS"
        }).set_placement((pta1[0], pta1[1] - 5))
        
        # Grid line
        pta1 = (ch, bridge_params['datum'] - d4 * bridge_params['scale1'])
        pta2 = (ch, bridge_params['datum'] - d5 * bridge_params['scale1'])
        msp.add_line(pta1, pta2, dxfattribs={
            "layer": "GRID",
            "color": 7  # Gray
        })

def draw_cross_section_dxf(msp, doc):
    """Draw enhanced cross-section in DXF."""
    ptb3 = None
    d1 = 20
    d4 = 2 * d1
    d5 = d4 - 2.0
    d8 = d4 - 4.0
    d9 = d1 - 4.0
    
    for a, (x, y) in enumerate(cs_data, 1):
        b1 = f"{x:.3f}"
        b2 = f"{y:.3f}"
        xx = x
        
        # River level annotation
        pta2 = (xx + 0.9 * bridge_params['scale1'], 
                bridge_params['datum'] - d9 * bridge_params['scale1'])
        msp.add_text(b2, dxfattribs={
            "height": 2.0 * bridge_params['scale1'],
            "rotation": 90,
            "layer": "CROSS_SECTION"
        }).set_placement((pta2[0], pta2[1] - 5))
        
        # Chainage annotation (if not on grid)
        b = (x - bridge_params['left']) % bridge_params['xincr']
        if b != 0.0:
            pta1 = (xx + 0.9 * bridge_params['scale1'], 
                    bridge_params['datum'] - d8 * bridge_params['scale1'])
            msp.add_text(b1, dxfattribs={
                "height": 1.8 * bridge_params['scale1'],
                "rotation": 90,
                "layer": "CROSS_SECTION"
            }).set_placement((pta1[0], pta1[1] - 5))
            
            # Grid line markers
            pta1 = (xx, bridge_params['datum'] - d4 * bridge_params['scale1'])
            pta2 = (xx, bridge_params['datum'] - d5 * bridge_params['scale1'])
            msp.add_line(pta1, pta2, dxfattribs={
                "layer": "CROSS_SECTION"
            })
        
        # Vertical line to datum
        pta5 = (xx, bridge_params['datum'] - 2 * bridge_params['scale1'])
        pta6 = (xx, bridge_params['datum'])
        msp.add_line(pta5, pta6, dxfattribs={
            "layer": "CROSS_SECTION"
        })
        
        # Cross-section line
        ptb4 = (x, y)
        if a > 1 and ptb3 is not None:
            msp.add_line(ptb3, ptb4, dxfattribs={
                "layer": "CROSS_SECTION",
                "lineweight": 2
            })
        ptb3 = ptb4

def draw_pier_dxf(msp, doc):
    """Draw enhanced pier in DXF with proper engineering details."""
    # Initialize derived variables
    skew1 = bridge_params['skew'] * 0.0174532
    s = math.sin(skew1)
    c = math.cos(skew1)
    tn = s / c if c != 0 else 0
    spane = bridge_params['abtl'] + bridge_params['span1']
    yc = bridge_params['datum'] - 30.0
    
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
    
    # Elevation: Pier cap
    capwsq = bridge_params['capw'] / c if c != 0 else bridge_params['capw']
    x1 = spane - capwsq / 2
    x2 = x1 + capwsq
    y1 = bridge_params['capt']
    y2 = bridge_params['capb']
    pta1 = (x1, y1)
    pta2 = (x2, y2)
    
    # Draw pier cap
    points = [pta1, (pta2[0], pta1[1]), pta2, (pta1[0], pta2[1]), pta1]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "PIER"})
    
    # Elevation: Pier with batter
    piertwsq = bridge_params['piertw'] / c if c != 0 else bridge_params['piertw']
    x1 = spane - piertwsq / 2
    x3 = x1 + piertwsq
    y2 = bridge_params['futrl'] + bridge_params['futd']
    ofset = (bridge_params['capb'] - y2) / bridge_params['battr']
    ofsetsq = ofset / c if c != 0 else ofset
    x2 = x1 - ofsetsq
    x4 = x3 + ofsetsq
    y4 = y2
    
    pta1 = (x1, bridge_params['capb'])
    pta2 = (x2, y2)
    pta3 = (x3, bridge_params['capb'])
    pta4 = (x4, y4)
    
    # Draw pier sides with batter
    msp.add_line(pta1, pta2, dxfattribs={
        "layer": "PIER",
        "lineweight": 2
    })
    msp.add_line(pta3, pta4, dxfattribs={
        "layer": "PIER",
        "lineweight": 2
    })
    
    # Elevation: Foundation footing
    futwsq = bridge_params['futw'] / c if c != 0 else bridge_params['futw']
    x5 = spane - futwsq / 2
    x6 = x5 + futwsq
    y6 = bridge_params['futrl']
    y5 = y4
    
    pta5 = (x5, y5)
    pta6 = (x6, y6)
    
    # Draw foundation footing
    points = [pta5, (pta6[0], pta5[1]), pta6, (pta5[0], pta6[1]), pta5]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "FOUNDATION"})
    
    # Plan view: Foundation footing (rotated for skew)
    x7 = spane - bridge_params['futw'] / 2
    x8 = x7 + bridge_params['futw']
    y7 = yc + bridge_params['futl'] / 2
    y8 = y7 - bridge_params['futl']
    
    pta7 = (x7, y7)
    pta8 = (x8, y8)
    
    # Rotate for skew
    center = (spane, yc)
    rect_points = [pta7, (pta7[0], pta8[1]), pta8, (pta8[0], pta7[1])]
    
    def rotate_point(point, center, angle_deg):
        angle_rad = math.radians(angle_deg)
        x, y = point[0] - center[0], point[1] - center[1]
        new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        return (new_x + center[0], new_y + center[1])
    
    rotated_points = [rotate_point(p, center, bridge_params['skew']) for p in rect_points]
    
    # Offset for plan view (move down for visibility)
    plan_offset = -50
    plan_points = [(p[0], p[1] + plan_offset) for p in rotated_points]
    msp.add_lwpolyline(plan_points, close=True, dxfattribs={"layer": "FOUNDATION"})
    
    # Plan view: Pier with batter (rotated for skew)
    pierstsq = (bridge_params['pierst'] / c) + abs(bridge_params['piertw'] * tn) if c != 0 else bridge_params['pierst']
    x1 = spane - bridge_params['piertw'] / 2
    x3 = x1 + bridge_params['piertw']
    x2 = x1 - ofset
    x4 = x3 + ofset
    y9 = yc + pierstsq / 2
    y10 = y9 - pierstsq
    
    # Draw pier plan lines
    lines = [
        ((x2, y9), (x2, y10)),
        ((x1, y9), (x1, y10)),
        ((x3, y9), (x3, y10)),
        ((x4, y9), (x4, y10))
    ]
    
    for start, end in lines:
        start_rot = rotate_point(start, center, bridge_params['skew'])
        end_rot = rotate_point(end, center, bridge_params['skew'])
        plan_start = (start_rot[0], start_rot[1] + plan_offset)
        plan_end = (end_rot[0], end_rot[1] + plan_offset)
        msp.add_line(plan_start, plan_end, dxfattribs={
            "layer": "PIER"
        })

def draw_abutment_dxf(msp, doc):
    """Draw enhanced abutment in DXF with proper engineering details."""
    # Initialize derived variables
    skew1 = bridge_params['skew'] * 0.0174532
    s = math.sin(skew1)
    c = math.cos(skew1)
    
    # Calculate abutment dimensions
    ccbrsq = bridge_params['ccbr'] / c if c != 0 else bridge_params['ccbr']
    kerbwsq = bridge_params['kerbw'] / c if c != 0 else bridge_params['kerbw']
    abtlen = ccbrsq + 2 * kerbwsq
    
    # Elevation calculations
    x1 = bridge_params['abtl']
    alcwsq = bridge_params['alcw']
    x3 = x1 + alcwsq
    capb = bridge_params['capt'] - bridge_params['alcd']
    p1 = (capb - bridge_params['alfbl']) / bridge_params['alfb']
    p1sq = p1
    x5 = x3 + p1sq
    p2 = (bridge_params['alfbl'] - bridge_params['altbl']) / bridge_params['altb']
    p2sq = p2
    x6 = x5 + p2sq
    alfosq = bridge_params['alfo']
    x7 = x6 + alfosq
    y8 = bridge_params['altbl'] - bridge_params['alfd']
    dwthsq = bridge_params['dwth']
    x14 = x1 - dwthsq
    p3 = (capb - bridge_params['albbl']) / bridge_params['albb']
    p3sq = p3
    x12 = x14 - p3sq
    x10 = x12 - alfosq
    
    # Create elevation points
    points = [
        (x1, bridge_params['RTL']), (x1, bridge_params['capt']), (x3, bridge_params['capt']), (x3, capb),
        (x5, bridge_params['alfbl']), (x6, bridge_params['altbl']), (x7, bridge_params['altbl']), (x7, y8),
        (x10, y8), (x10, bridge_params['altbl']), (x12, bridge_params['altbl']), (x12, bridge_params['albbl']),
        (x14, capb), (x14, bridge_params['RTL']), (x1, bridge_params['RTL'])
    ]
    
    # Draw elevation outline
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "ABUTMENT"})
    
    # Draw internal lines
    msp.add_line((x14, capb), (x3, capb), dxfattribs={"layer": "ABUTMENT"})
    msp.add_line((x10, bridge_params['altbl']), (x7, bridge_params['altbl']), dxfattribs={"layer": "ABUTMENT"})
    msp.add_line((x12, bridge_params['albbl']), (x12, bridge_params['RTL']), dxfattribs={"layer": "ABUTMENT"})
    msp.add_line((x12, bridge_params['RTL']), (x14, bridge_params['RTL']), dxfattribs={"layer": "ABUTMENT"})
    
    # Plan view calculations
    yc = bridge_params['datum'] - 30.0
    y20 = yc + abtlen / 2
    y21 = y20 - abtlen
    y16 = y20 + 0.15
    y17 = y21 - 0.15
    footl = (y16 - y17) / 2
    x_skew = footl * s
    y_skew = footl * (1 - c)
    
    # Create plan view points
    pt16 = (x10 - x_skew, y16 - y_skew)
    pt17 = (x10 + x_skew, y17 + y_skew)
    pt18 = (x7 - x_skew, y16 - y_skew)
    pt19 = (x7 + x_skew, y17 + y_skew)
    
    # Draw plan view outline
    plan_points = [pt16, pt17, pt19, pt18, pt16]
    msp.add_lwpolyline(plan_points, close=True, dxfattribs={"layer": "ABUTMENT"})
    
    # Additional plan view lines with skew adjustment
    xx = abtlen / 2
    x = xx * s
    y = xx * (1 - c)
    y20 -= y
    y21 += y
    
    # Create additional plan view points
    plan_lines = [
        ((x12 - x, y20), (x12 + x, y21)),
        ((x14 - x, y20), (x14 + x, y21)),
        ((x1 - x, y20), (x1 + x, y21)),
        ((x3 - x, y20), (x3 + x, y21)),
        ((x5 - x, y20), (x5 + x, y21)),
        ((x6 - x, y20), (x6 + x, y21)),
        ((x12 + x, y21), (x6 + x, y21)),
        ((x12 - x, y20), (x6 - x, y20))
    ]
    
    # Draw additional plan view lines
    for start, end in plan_lines:
        msp.add_line(start, end, dxfattribs={"layer": "ABUTMENT"})

def add_enhanced_title_block_dxf(msp, doc):
    """Add enhanced title block to DXF with professional details."""
    # Title block dimensions
    title_height = 40
    title_width = bridge_params['right'] - bridge_params['left']
    
    # Draw title block border
    title_points = [
        (0, 0), (title_width, 0), (title_width, title_height), (0, title_height), (0, 0)
    ]
    msp.add_lwpolyline(title_points, close=True, dxfattribs={
        "layer": "TITLE_BLOCK",
        "lineweight": 3
    })
    
    # Add title
    msp.add_text("Bridge General Arrangement Drawing", dxfattribs={
        "height": 8,
        "layer": "TITLE_BLOCK"
    }).set_placement((title_width/2, title_height - 10), align="MIDDLE_CENTER")
    
    # Add scale
    scale_ratio = int(1000/bridge_params['scale1'])
    msp.add_text(f"Scale: 1:{scale_ratio}", dxfattribs={
        "height": 4,
        "layer": "TITLE_BLOCK"
    }).set_placement((title_width - 20, title_height - 20), align="TOP_RIGHT")
    
    # Add drawing number
    msp.add_text("Drawing No: BGD-001", dxfattribs={
        "height": 4,
        "layer": "TITLE_BLOCK"
    }).set_placement((20, title_height - 20), align="TOP_LEFT")
    
    # Add date
    date_str = datetime.now().strftime("%Y-%m-%d")
    msp.add_text(f"Date: {date_str}", dxfattribs={
        "height": 4,
        "layer": "TITLE_BLOCK"
    }).set_placement((20, title_height - 30), align="TOP_LEFT")
    
    # Add designed by
    msp.add_text("Designed by: BridgeGAD-00", dxfattribs={
        "height": 4,
        "layer": "TITLE_BLOCK"
    }).set_placement((title_width - 20, title_height - 30), align="TOP_RIGHT")

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
    pdf.drawString(50*mm, 250*mm, "Simple Bridge GAD Drawing")
    
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
    start_pos = (0, 0)
    
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
                    save_dxf()
                elif event.key == pygame.K_p:
                    save_pdf()
                        
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
