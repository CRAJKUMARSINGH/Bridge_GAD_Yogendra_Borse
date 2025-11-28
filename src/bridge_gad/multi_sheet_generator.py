"""
Multi-Sheet Detailed Drawing Generator
Generates 4 separate A4 landscape sheets with detailed views:
1. Pier Elevation (enlarged)
2. Abutment Elevation (enlarged)
3. Plan View (top)
4. Section View (profile)
All with borders, labels, dimensions, and RKS LEGAL title block
"""

import ezdxf
from ezdxf.math import Vec2, Vec3
from pathlib import Path
from typing import Dict, Tuple
import math


class DetailedSheetGenerator:
    """Generates detailed A4 landscape sheets with professional formatting"""
    
    # A4 Landscape dimensions (mm to DXF units)
    A4_WIDTH = 297
    A4_HEIGHT = 210
    MARGIN = 10
    TITLE_HEIGHT = 30
    
    def __init__(self, acad_version: str = "R2010"):
        """Initialize for multi-sheet generation"""
        self.acad_version = acad_version
        self.sheets = []
    
    def _create_sheet(self, sheet_title: str):
        """Create new sheet document"""
        doc = ezdxf.new(self.acad_version)
        msp = doc.modelspace()
        return doc, msp
    
    def _draw_border(self, msp, sheet_num: int):
        """Draw A4 landscape border with professional frame"""
        # Outer border
        points_outer = [
            (self.MARGIN, self.MARGIN),
            (self.A4_WIDTH - self.MARGIN, self.MARGIN),
            (self.A4_WIDTH - self.MARGIN, self.A4_HEIGHT - self.MARGIN),
            (self.MARGIN, self.A4_HEIGHT - self.MARGIN),
            (self.MARGIN, self.MARGIN)
        ]
        msp.add_lwpolyline(points_outer, dxfattribs={'lineweight': 50})
        
        # Inner border
        inner_margin = self.MARGIN + 2
        points_inner = [
            (inner_margin, inner_margin),
            (self.A4_WIDTH - inner_margin, inner_margin),
            (self.A4_WIDTH - inner_margin, self.A4_HEIGHT - inner_margin),
            (inner_margin, self.A4_HEIGHT - inner_margin),
            (inner_margin, inner_margin)
        ]
        msp.add_lwpolyline(points_inner, dxfattribs={'lineweight': 25})
    
    def _draw_title_block(self, msp, sheet_title: str, sheet_num: int, total_sheets: int, variables: Dict):
        """Draw professional RKS LEGAL title block"""
        y_pos = self.MARGIN + 2
        
        # Title block background rectangle
        title_y_start = self.A4_HEIGHT - self.MARGIN - 25
        title_y_end = self.A4_HEIGHT - self.MARGIN - 5
        
        rect_points = [
            (self.MARGIN + 3, title_y_start),
            (self.A4_WIDTH - self.MARGIN - 3, title_y_start),
            (self.A4_WIDTH - self.MARGIN - 3, title_y_end),
            (self.MARGIN + 3, title_y_end),
            (self.MARGIN + 3, title_y_start)
        ]
        msp.add_lwpolyline(rect_points, dxfattribs={'lineweight': 35})
        
        # Title text
        title_text = sheet_title
        msp.add_text(title_text, dxfattribs={
            'height': 3.5,
            'style': 'STANDARD'
        }).set_placement((self.MARGIN + 5, title_y_end - 5))
        
        # Company info
        company = str(variables.get('COMPANY_NAME', 'RKS LEGAL'))
        msp.add_text(f"By: {company}", dxfattribs={
            'height': 2,
            'style': 'STANDARD'
        }).set_placement((self.MARGIN + 5, title_y_end - 10))
        
        # Project info
        project = str(variables.get('PROJECT_NAME', 'Bridge Project'))
        msp.add_text(f"Project: {project}", dxfattribs={
            'height': 2,
            'style': 'STANDARD'
        }).set_placement((self.A4_WIDTH - 80, title_y_end - 5))
        
        # Sheet number
        sheet_text = f"Sheet {sheet_num} of {total_sheets}"
        msp.add_text(sheet_text, dxfattribs={
            'height': 2,
            'style': 'STANDARD'
        }).set_placement((self.A4_WIDTH - 80, title_y_end - 10))
        
        # Contact info footer
        address = str(variables.get('ADDRESS', '303 Vallabh Apartment, Udaipur'))
        email = str(variables.get('EMAIL', 'crajkumarsingh@hotmail.com'))
        phone = str(variables.get('MOBILE', '+919414163019'))
        
        footer_y = self.MARGIN + 3
        msp.add_text(f"📍 {address[:40]}", dxfattribs={'height': 1.5}).set_placement((self.MARGIN + 5, footer_y))
        msp.add_text(f"📧 {email}", dxfattribs={'height': 1.5}).set_placement((self.MARGIN + 5, footer_y - 3))
        msp.add_text(f"📱 {phone}", dxfattribs={'height': 1.5}).set_placement((self.MARGIN + 5, footer_y - 6))
    
    def _draw_dimensions(self, msp, positions: list, labels: list):
        """Add dimension lines and labels"""
        for pos, label in zip(positions, labels):
            x, y = pos
            # Dimension line
            msp.add_line((x - 5, y), (x + 5, y), dxfattribs={'lineweight': 15})
            # Label text
            msp.add_text(label, dxfattribs={'height': 2}).set_placement((x - 3, y + 2))
    
    def generate_pier_elevation(self, variables: Dict) -> ezdxf.Drawing:
        """Generate detailed pier elevation sheet"""
        doc, msp = self._create_sheet("PIER ELEVATION")
        self._draw_border(msp, 1)
        self._draw_title_block(msp, "PIER ELEVATION - ENLARGED", 1, 4, variables)
        
        # Get dimensions
        piertw = float(variables.get('PIERTW', 1.2))
        span1 = float(variables.get('SPAN1', 12))
        rtl = float(variables.get('RTL', 110.98))
        datum = float(variables.get('DATUM', 100))
        futd = float(variables.get('FUTD', 1.0))
        futw = float(variables.get('FUTW', 4.5))
        
        # Draw pier (scaled for A4)
        scale = 3  # Scale factor for detail sheet
        pier_base_x = 100
        pier_base_y = 80
        
        # Pier shaft
        pier_top_y = pier_base_y + (rtl - datum) * scale
        pier_points = [
            (pier_base_x, pier_base_y),
            (pier_base_x + piertw * scale, pier_base_y),
            (pier_base_x + piertw * scale, pier_top_y),
            (pier_base_x, pier_top_y),
            (pier_base_x, pier_base_y)
        ]
        msp.add_lwpolyline(pier_points, dxfattribs={'lineweight': 50, 'color': 2})
        
        # Footing
        foot_y = pier_base_y - futd * scale
        foot_points = [
            (pier_base_x - (futw - piertw) / 2 * scale, pier_base_y),
            (pier_base_x + piertw * scale + (futw - piertw) / 2 * scale, pier_base_y),
            (pier_base_x + piertw * scale + (futw - piertw) / 2 * scale, foot_y),
            (pier_base_x - (futw - piertw) / 2 * scale, foot_y),
            (pier_base_x - (futw - piertw) / 2 * scale, pier_base_y)
        ]
        msp.add_lwpolyline(foot_points, dxfattribs={'lineweight': 35, 'color': 3})
        
        # Dimensions - Pier width
        dim_y = pier_base_y - 10
        msp.add_line((pier_base_x, dim_y), (pier_base_x + piertw * scale, dim_y), 
                    dxfattribs={'lineweight': 15})
        msp.add_text(f"Pier Width: {piertw}m", dxfattribs={'height': 2.5}).set_placement(
            (pier_base_x + piertw * scale / 2 - 8, dim_y - 3))
        
        # Dimensions - Pier height
        dim_x = pier_base_x - 15
        msp.add_line((dim_x, pier_base_y), (dim_x, pier_top_y), 
                    dxfattribs={'lineweight': 15})
        height_label = f"Height: {rtl - datum:.2f}m"
        msp.add_text(height_label, dxfattribs={'height': 2.5}).set_placement(
            (dim_x - 12, pier_base_y + (pier_top_y - pier_base_y) / 2))
        
        # Dimensions - Footing width
        foot_dim_y = foot_y - 8
        msp.add_line((pier_base_x - (futw - piertw) / 2 * scale, foot_dim_y), 
                    (pier_base_x + piertw * scale + (futw - piertw) / 2 * scale, foot_dim_y), 
                    dxfattribs={'lineweight': 15})
        msp.add_text(f"Footing Width: {futw}m", dxfattribs={'height': 2.5}).set_placement(
            (pier_base_x + piertw * scale / 2 - 10, foot_dim_y - 3))
        
        # Ground line
        msp.add_line((pier_base_x - 15, pier_base_y), (pier_base_x + piertw * scale + 15, pier_base_y),
                    dxfattribs={'lineweight': 25, 'linetype': 'DASHED'})
        msp.add_text("GROUND LEVEL", dxfattribs={'height': 2}).set_placement(
            (pier_base_x - 10, pier_base_y + 2))
        
        return doc
    
    def generate_abutment_elevation(self, variables: Dict) -> ezdxf.Drawing:
        """Generate detailed abutment elevation sheet"""
        doc, msp = self._create_sheet("ABUTMENT ELEVATION")
        self._draw_border(msp, 2)
        self._draw_title_block(msp, "ABUTMENT ELEVATION - ENLARGED", 2, 4, variables)
        
        # Get dimensions
        abtl = float(variables.get('ABTL', 13))
        rtl = float(variables.get('RTL', 110.98))
        datum = float(variables.get('DATUM', 100))
        ccbr = float(variables.get('CCBR', 11.1))
        futw = float(variables.get('FUTW', 4.5))
        futd = float(variables.get('FUTD', 1.0))
        
        scale = 2.5
        abt_base_x = 100
        abt_base_y = 80
        
        # Abutment wall
        abt_top_y = abt_base_y + (rtl - datum) * scale
        abt_points = [
            (abt_base_x, abt_base_y),
            (abt_base_x + abtl * scale, abt_base_y),
            (abt_base_x + abtl * scale, abt_top_y),
            (abt_base_x, abt_top_y),
            (abt_base_x, abt_base_y)
        ]
        msp.add_lwpolyline(abt_points, dxfattribs={'lineweight': 50, 'color': 4})
        
        # Footing
        foot_y = abt_base_y - futd * scale
        foot_points = [
            (abt_base_x - 5, abt_base_y),
            (abt_base_x + abtl * scale + 5, abt_base_y),
            (abt_base_x + abtl * scale + 5, foot_y),
            (abt_base_x - 5, foot_y),
            (abt_base_x - 5, abt_base_y)
        ]
        msp.add_lwpolyline(foot_points, dxfattribs={'lineweight': 35, 'color': 5})
        
        # Dimensions
        dim_y = abt_base_y - 10
        msp.add_line((abt_base_x, dim_y), (abt_base_x + abtl * scale, dim_y), 
                    dxfattribs={'lineweight': 15})
        msp.add_text(f"Length: {abtl}m", dxfattribs={'height': 2.5}).set_placement(
            (abt_base_x + abtl * scale / 2 - 8, dim_y - 3))
        
        dim_x = abt_base_x - 15
        msp.add_line((dim_x, abt_base_y), (dim_x, abt_top_y), 
                    dxfattribs={'lineweight': 15})
        height_label = f"Height: {rtl - datum:.2f}m"
        msp.add_text(height_label, dxfattribs={'height': 2.5}).set_placement(
            (dim_x - 12, abt_base_y + (abt_top_y - abt_base_y) / 2))
        
        # Ground line
        msp.add_line((abt_base_x - 10, abt_base_y), (abt_base_x + abtl * scale + 10, abt_base_y),
                    dxfattribs={'lineweight': 25, 'linetype': 'DASHED'})
        msp.add_text("GROUND LEVEL", dxfattribs={'height': 2}).set_placement(
            (abt_base_x, abt_base_y + 2))
        
        return doc
    
    def generate_plan_view(self, variables: Dict) -> ezdxf.Drawing:
        """Generate plan view (top view) sheet"""
        doc, msp = self._create_sheet("PLAN VIEW")
        self._draw_border(msp, 3)
        self._draw_title_block(msp, "PLAN VIEW - TOP", 3, 4, variables)
        
        nspan = int(variables.get('NSPAN', 3))
        span1 = float(variables.get('SPAN1', 12))
        ccbr = float(variables.get('CCBR', 11.1))
        piertw = float(variables.get('PIERTW', 1.2))
        
        scale = 2.0
        start_x = 80
        start_y = 100
        
        # Draw spans (rectangles)
        for i in range(nspan):
            x_pos = start_x + i * span1 * scale
            rect_points = [
                (x_pos, start_y),
                (x_pos + span1 * scale, start_y),
                (x_pos + span1 * scale, start_y + ccbr * scale),
                (x_pos, start_y + ccbr * scale),
                (x_pos, start_y)
            ]
            msp.add_lwpolyline(rect_points, dxfattribs={'lineweight': 40, 'color': 1})
            
            # Span label
            span_label = f"Span {i+1}: {span1}m"
            msp.add_text(span_label, dxfattribs={'height': 2}).set_placement(
                (x_pos + span1 * scale / 2 - 5, start_y + ccbr * scale + 3))
        
        # Draw piers (between spans)
        for i in range(nspan - 1):
            pier_x = start_x + (i + 1) * span1 * scale
            pier_points = [
                (pier_x - piertw * scale / 2, start_y - 5),
                (pier_x + piertw * scale / 2, start_y - 5),
                (pier_x + piertw * scale / 2, start_y + ccbr * scale + 5),
                (pier_x - piertw * scale / 2, start_y + ccbr * scale + 5),
                (pier_x - piertw * scale / 2, start_y - 5)
            ]
            msp.add_lwpolyline(pier_points, dxfattribs={'lineweight': 50, 'color': 2})
        
        # Dimensions - Span lengths
        dim_y = start_y - 15
        for i in range(nspan):
            x_pos = start_x + i * span1 * scale
            msp.add_line((x_pos, dim_y), (x_pos + span1 * scale, dim_y), 
                        dxfattribs={'lineweight': 15})
        
        # Dimension - Width
        dim_x = start_x - 15
        msp.add_line((dim_x, start_y), (dim_x, start_y + ccbr * scale), 
                    dxfattribs={'lineweight': 15})
        msp.add_text(f"Width: {ccbr}m", dxfattribs={'height': 2.5}).set_placement(
            (dim_x - 8, start_y + ccbr * scale / 2))
        
        # Total length dimension
        total_length = nspan * span1
        total_dim_y = start_y + ccbr * scale + 15
        msp.add_line((start_x, total_dim_y), (start_x + total_length * scale, total_dim_y), 
                    dxfattribs={'lineweight': 20})
        msp.add_text(f"Total Length: {total_length}m", dxfattribs={'height': 2.5}).set_placement(
            (start_x + total_length * scale / 2 - 12, total_dim_y + 3))
        
        return doc
    
    def generate_section_view(self, variables: Dict) -> ezdxf.Drawing:
        """Generate section/profile view sheet"""
        doc, msp = self._create_sheet("SECTION VIEW")
        self._draw_border(msp, 4)
        self._draw_title_block(msp, "SECTION VIEW - PROFILE", 4, 4, variables)
        
        # Get dimensions
        span1 = float(variables.get('SPAN1', 12))
        ccbr = float(variables.get('CCBR', 11.1))
        slbthe = float(variables.get('SLBTHE', 0.75))
        rtl = float(variables.get('RTL', 110.98))
        datum = float(variables.get('DATUM', 100))
        futd = float(variables.get('FUTD', 1.0))
        piertw = float(variables.get('PIERTW', 1.2))
        
        scale_h = 3.0  # Horizontal scale
        scale_v = 4.0  # Vertical scale (exaggerated for clarity)
        
        start_x = 60
        start_y = 80
        
        # Draw ground/datum line
        ground_y = start_y
        msp.add_line((start_x, ground_y), (start_x + span1 * scale_h + piertw * scale_h * 2, ground_y),
                    dxfattribs={'lineweight': 25, 'linetype': 'DASHED'})
        msp.add_text("DATUM", dxfattribs={'height': 2}).set_placement((start_x, ground_y - 3))
        
        # Draw deck slab
        deck_y_top = ground_y + (rtl - datum) * scale_v
        slab_points = [
            (start_x + piertw * scale_h, deck_y_top - slbthe * scale_v),
            (start_x + span1 * scale_h + piertw * scale_h, deck_y_top - slbthe * scale_v),
            (start_x + span1 * scale_h + piertw * scale_h, deck_y_top),
            (start_x + piertw * scale_h, deck_y_top),
            (start_x + piertw * scale_h, deck_y_top - slbthe * scale_v)
        ]
        msp.add_lwpolyline(slab_points, dxfattribs={'lineweight': 50, 'color': 6})
        
        # Draw pier
        pier_top_y = deck_y_top - slbthe * scale_v
        pier_points = [
            (start_x + span1 * scale_h, ground_y - futd * scale_v),
            (start_x + span1 * scale_h + piertw * scale_h, ground_y - futd * scale_v),
            (start_x + span1 * scale_h + piertw * scale_h, pier_top_y),
            (start_x + span1 * scale_h, pier_top_y),
            (start_x + span1 * scale_h, ground_y - futd * scale_v)
        ]
        msp.add_lwpolyline(pier_points, dxfattribs={'lineweight': 45, 'color': 2})
        
        # Dimensions - Slab thickness
        slab_dim_x = start_x + piertw * scale_h - 8
        msp.add_line((slab_dim_x, deck_y_top - slbthe * scale_v), 
                    (slab_dim_x, deck_y_top), 
                    dxfattribs={'lineweight': 15})
        msp.add_text(f"{slbthe}m", dxfattribs={'height': 2}).set_placement(
            (slab_dim_x - 5, deck_y_top - slbthe * scale_v / 2))
        
        # Dimensions - Span
        span_dim_y = deck_y_top + 8
        msp.add_line((start_x + piertw * scale_h, span_dim_y), 
                    (start_x + span1 * scale_h + piertw * scale_h, span_dim_y), 
                    dxfattribs={'lineweight': 15})
        msp.add_text(f"Span: {span1}m", dxfattribs={'height': 2.5}).set_placement(
            (start_x + span1 * scale_h / 2 - 4, span_dim_y + 2))
        
        # Dimensions - Height
        height_dim_x = start_x + span1 * scale_h + piertw * scale_h + 8
        msp.add_line((height_dim_x, ground_y - futd * scale_v), 
                    (height_dim_x, deck_y_top), 
                    dxfattribs={'lineweight': 15})
        height_val = (rtl - datum) + futd
        msp.add_text(f"Height: {height_val:.2f}m", dxfattribs={'height': 2.5}).set_placement(
            (height_dim_x + 2, ground_y - futd * scale_v + height_val * scale_v / 2))
        
        return doc
    
    def generate_all_sheets(self, variables: Dict, output_path: Path) -> bool:
        """Generate all 4 sheets and combine into single PDF/DXF"""
        try:
            # Generate all sheets
            sheets = [
                self.generate_pier_elevation(variables),
                self.generate_abutment_elevation(variables),
                self.generate_plan_view(variables),
                self.generate_section_view(variables)
            ]
            
            # Save as individual files
            output_dir = output_path.parent
            output_stem = output_path.stem
            
            filenames = []
            for i, sheet in enumerate(sheets, 1):
                filename = output_dir / f"{output_stem}_Sheet{i}.dxf"
                sheet.saveas(filename)
                filenames.append(filename)
            
            return True
        except Exception as e:
            print(f"Error generating sheets: {e}")
            return False
