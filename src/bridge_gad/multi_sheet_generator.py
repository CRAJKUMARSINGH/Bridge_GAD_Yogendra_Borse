"""
Multi-sheet detailed drawing generator.

Generates detailed A4 landscape sheets and a phase two package that is closer to
an actual submission bundle.
"""

import ezdxf
from ezdxf.math import Vec2, Vec3
from pathlib import Path
from typing import Dict, Tuple
import math

from .standards import get_owner_profile, phase_two_sheet_rows


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
        """Draw standards-aware title block."""
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
        company = str(variables.get('COMPANY_NAME', 'Bridge GAD Generator'))
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
        
        drawing_no = str(variables.get("DRAWING_NO", "GAD-001"))
        revision = str(variables.get("REVISION", "R0"))
        owner_profile = get_owner_profile(variables.get("OWNER_PROFILE"))
        msp.add_text(f"Drg: {drawing_no}  Rev: {revision}", dxfattribs={'height': 1.8}).set_placement(
            (self.A4_WIDTH - 80, title_y_end - 15)
        )
        msp.add_text(f"Basis: {owner_profile.owner}", dxfattribs={'height': 1.8}).set_placement(
            (self.MARGIN + 70, title_y_end - 10)
        )

        # Contact info footer. PII defaults come from env vars.
        import os as _os
        address = str(variables.get('ADDRESS', '303 Vallabh Apartment, Udaipur'))
        email = str(variables.get('EMAIL', _os.environ.get('CONTACT_EMAIL', 'contact@example.com')))
        phone = str(variables.get('MOBILE', _os.environ.get('CONTACT_PHONE', '+91XXXXXXXXXX')))
        
        footer_y = self.MARGIN + 3
        msp.add_text(f"Addr: {address[:40]}", dxfattribs={'height': 1.5}).set_placement((self.MARGIN + 5, footer_y))
        msp.add_text(f"Email: {email}", dxfattribs={'height': 1.5}).set_placement((self.MARGIN + 5, footer_y - 3))
        msp.add_text(f"Phone: {phone}", dxfattribs={'height': 1.5}).set_placement((self.MARGIN + 5, footer_y - 6))

    def _save_sheet_set(self, sheets, output_path: Path):
        """Save a sheet list to numbered DXF files."""

        output_dir = output_path.parent
        output_stem = output_path.stem
        filenames = []
        for i, sheet in enumerate(sheets, 1):
            filename = output_dir / f"{output_stem}_Sheet{i}.dxf"
            sheet.saveas(filename)
            filenames.append(filename)
        return filenames

    def generate_index_sheet(self, variables: Dict) -> ezdxf.Drawing:
        """Generate the phase two drawing index sheet."""

        doc, msp = self._create_sheet("DRAWING INDEX")
        schedule = phase_two_sheet_rows()
        self._draw_border(msp, 1)
        self._draw_title_block(msp, "DRAWING INDEX AND BASIS", 1, len(schedule), variables)

        start_x = 25
        start_y = 150
        row_h = 12
        col_x = [start_x, start_x + 22, start_x + 52, start_x + 150]

        msp.add_text("Sheet", dxfattribs={'height': 2.5}).set_placement((col_x[0], start_y))
        msp.add_text("Code", dxfattribs={'height': 2.5}).set_placement((col_x[1], start_y))
        msp.add_text("Title", dxfattribs={'height': 2.5}).set_placement((col_x[2], start_y))
        msp.add_text("Purpose", dxfattribs={'height': 2.5}).set_placement((col_x[3], start_y))

        y = start_y - 8
        for row in schedule:
            msp.add_line((start_x, y + 3), (self.A4_WIDTH - 25, y + 3))
            msp.add_text(row["Sheet No"], dxfattribs={'height': 2.0}).set_placement((col_x[0], y))
            msp.add_text(row["Code"], dxfattribs={'height': 2.0}).set_placement((col_x[1], y))
            msp.add_text(row["Title"], dxfattribs={'height': 2.0}).set_placement((col_x[2], y))
            msp.add_text(row["Purpose"], dxfattribs={'height': 1.8}).set_placement((col_x[3], y))
            y -= row_h

        profile = get_owner_profile(variables.get("OWNER_PROFILE"))
        msp.add_text(f"Owner Profile: {profile.owner}", dxfattribs={'height': 2.2}).set_placement((25, 55))
        msp.add_text(f"Drawing Standard: {profile.drawing_standard[:70]}", dxfattribs={'height': 2.0}).set_placement((25, 47))
        msp.add_text(f"Live Load Basis: {profile.design_live_load[:72]}", dxfattribs={'height': 2.0}).set_placement((25, 39))
        msp.add_text(profile.review_note[:90], dxfattribs={'height': 1.8}).set_placement((25, 31))
        return doc

    def generate_bearing_joint_sheet(self, variables: Dict) -> ezdxf.Drawing:
        """Generate a notes-driven bearing and expansion joint sheet."""

        doc, msp = self._create_sheet("BEARING AND JOINT NOTES")
        total = len(phase_two_sheet_rows())
        self._draw_border(msp, 6)
        self._draw_title_block(msp, "BEARING AND EXPANSION JOINT NOTES", 6, total, variables)

        bearing_type = str(variables.get("BEARING_TYPE", "As per design"))
        bearing_w = float(variables.get("BEARING_W", 0.0))
        expjt = float(variables.get("EXPJT", 0.025))
        span1 = float(variables.get("SPAN1", 12))

        box = [(30, 60), (267, 60), (267, 145), (30, 145), (30, 60)]
        msp.add_lwpolyline(box, dxfattribs={'lineweight': 35})
        msp.add_text("Typical note set", dxfattribs={'height': 3.0}).set_placement((35, 138))
        notes = [
            f"1. Bearing system: {bearing_type}",
            f"2. Indicative bearing seat width: {bearing_w:.2f} m",
            f"3. Expansion joint movement gap shown in GAD: {expjt:.3f} m",
            f"4. Review expansion provisions against final span arrangement of {span1:.2f} m typical span.",
            "5. Final bearing schedule, load table, and manufacturer data to be issued in detail drawings.",
        ]
        y = 126
        for note in notes:
            msp.add_text(note, dxfattribs={'height': 2.2}).set_placement((38, y))
            y -= 14
        return doc

    def generate_drainage_utility_sheet(self, variables: Dict) -> ezdxf.Drawing:
        """Generate a drainage, safety, and utility notes sheet."""

        doc, msp = self._create_sheet("DRAINAGE SAFETY UTILITY")
        total = len(phase_two_sheet_rows())
        self._draw_border(msp, 7)
        self._draw_title_block(msp, "DRAINAGE, SAFETY AND UTILITY NOTES", 7, total, variables)

        drainsp = float(variables.get("DRAINSP", 0.0))
        barrierh = float(variables.get("BARRIERH", 0.0))
        barrier_type = str(variables.get("BARRIERT", "Barrier / parapet"))
        utilityd = float(variables.get("UTILITYD", 0.0))

        box = [(30, 60), (267, 60), (267, 145), (30, 145), (30, 60)]
        msp.add_lwpolyline(box, dxfattribs={'lineweight': 35})
        notes = [
            f"1. Drainage spout spacing shown/assumed: {drainsp:.2f} m",
            f"2. Safety edge treatment: {barrier_type}, height {barrierh:.2f} m",
            f"3. Utility duct width reserved in typical section: {utilityd:.2f} m",
            "4. Confirm outlet locations, down-take routing, and maintenance access in detail design.",
            "5. Barrier, kerb, and utility details to be coordinated with owner-specific standard drawings.",
        ]
        y = 132
        for note in notes:
            msp.add_text(note, dxfattribs={'height': 2.2}).set_placement((38, y))
            y -= 14
        return doc
    
    def _draw_dimensions(self, msp, positions: list, labels: list):
        """Add dimension lines and labels"""
        for pos, label in zip(positions, labels):
            x, y = pos
            # Dimension line
            msp.add_line((x - 5, y), (x + 5, y), dxfattribs={'lineweight': 15})
            # Label text
            msp.add_text(label, dxfattribs={'height': 2}).set_placement((x - 3, y + 2))
    
    def generate_pier_elevation(self, variables: Dict, sheet_num: int = 1, total_sheets: int = 4) -> ezdxf.Drawing:
        """Generate detailed pier elevation sheet"""
        doc, msp = self._create_sheet("PIER ELEVATION")
        self._draw_border(msp, sheet_num)
        self._draw_title_block(msp, "PIER ELEVATION - ENLARGED", sheet_num, total_sheets, variables)
        
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
    
    def generate_abutment_elevation(self, variables: Dict, sheet_num: int = 2, total_sheets: int = 4) -> ezdxf.Drawing:
        """Generate detailed abutment elevation sheet"""
        doc, msp = self._create_sheet("ABUTMENT ELEVATION")
        self._draw_border(msp, sheet_num)
        self._draw_title_block(msp, "ABUTMENT ELEVATION - ENLARGED", sheet_num, total_sheets, variables)
        
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
    
    def generate_plan_view(self, variables: Dict, sheet_num: int = 3, total_sheets: int = 4) -> ezdxf.Drawing:
        """Generate plan view (top view) sheet"""
        doc, msp = self._create_sheet("PLAN VIEW")
        self._draw_border(msp, sheet_num)
        self._draw_title_block(msp, "PLAN VIEW - TOP", sheet_num, total_sheets, variables)
        
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
    
    def generate_section_view(self, variables: Dict, sheet_num: int = 4, total_sheets: int = 4) -> ezdxf.Drawing:
        """Generate section/profile view sheet"""
        doc, msp = self._create_sheet("SECTION VIEW")
        self._draw_border(msp, sheet_num)
        self._draw_title_block(msp, "SECTION VIEW - PROFILE", sheet_num, total_sheets, variables)
        
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
                self.generate_pier_elevation(variables, 1, 4),
                self.generate_abutment_elevation(variables, 2, 4),
                self.generate_plan_view(variables, 3, 4),
                self.generate_section_view(variables, 4, 4),
            ]
            
            self._save_sheet_set(sheets, output_path)
            return True
        except Exception as e:
            print(f"Error generating sheets: {e}")
            return False

    def generate_phase_two_package(self, variables: Dict, output_path: Path) -> bool:
        """Generate the seven-sheet phase two package."""

        try:
            total = len(phase_two_sheet_rows())
            variables = dict(variables)
            variables.setdefault("TOTAL_SHEETS", str(total))
            sheets = [
                self.generate_index_sheet(variables),
                self.generate_plan_view(variables, 2, total),
                self.generate_section_view(variables, 3, total),
                self.generate_abutment_elevation(variables, 4, total),
                self.generate_pier_elevation(variables, 5, total),
                self.generate_bearing_joint_sheet(variables),
                self.generate_drainage_utility_sheet(variables),
            ]
            self._save_sheet_set(sheets, output_path)
            return True
        except Exception as e:
            print(f"Error generating phase two package: {e}")
            return False
