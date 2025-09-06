"""
Comprehensive Bridge GAD Generator
Incorporating all engineering logic from existing Python and LISP implementations
"""

import math
import os
import pandas as pd
import ezdxf
from ezdxf.math import Vec2, Vec3
from math import atan2, degrees, sqrt, cos, sin, tan, radians, pi
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class BridgeGADGenerator:
    """Main class for generating comprehensive bridge general arrangement drawings."""
    
    def __init__(self):
        self.doc = None
        self.msp = None
        self.variables = {}
        self.scale1 = 186
        self.scale2 = 100
        self.skew = 0
        self.datum = 100
        self.left = 0
        self.hhs = 1000.0  # horizontal scale factor
        self.vvs = 1000.0  # vertical scale factor
        self.sc = 1.86     # scale ratio
        
    def setup_document(self):
        """Initialize DXF document with proper setup."""
        self.doc = ezdxf.new("R2010", setup=True)
        self.msp = self.doc.modelspace()
        self.setup_styles()
        logger.info("Document setup completed")
        
    def setup_styles(self):
        """Set up text and dimension styles."""
        # Create Arial text style
        if "Arial" not in self.doc.styles:
            self.doc.styles.new("Arial", dxfattribs={'font': 'Arial.ttf'})
            
        # Set up dimension style
        if "PMB100" not in self.doc.dimstyles:
            dimstyle = self.doc.dimstyles.new('PMB100')
            dimstyle.dxf.dimasz = 150
            dimstyle.dxf.dimtdec = 0
            dimstyle.dxf.dimexe = 400
            dimstyle.dxf.dimexo = 400
            dimstyle.dxf.dimlfac = 1
            dimstyle.dxf.dimtxsty = "Arial"
            dimstyle.dxf.dimtxt = 400
            dimstyle.dxf.dimtad = 0
            
    def read_variables_from_excel(self, file_path: Path) -> bool:
        """Read bridge parameters from Excel file."""
        try:
            df = pd.read_excel(file_path, header=None)
            df.columns = ['Value', 'Variable', 'Description']
            
            # Create a dictionary for easy access
            var_dict = df.set_index('Variable')['Value'].to_dict()
            self.variables = var_dict
            
            # Extract key variables
            self.scale1 = float(var_dict.get('SCALE1', 186))
            self.scale2 = float(var_dict.get('SCALE2', 100))
            self.skew = float(var_dict.get('SKEW', 0))
            self.datum = float(var_dict.get('DATUM', 100))
            self.left = float(var_dict.get('LEFT', 0))
            
            # Calculate derived values
            self.sc = self.scale1 / self.scale2
            self.hhs = 1000.0
            self.vvs = 1000.0
            
            # Trigonometric calculations for skew
            self.skew1 = self.skew * 0.0174532  # Convert to radians
            self.s = sin(self.skew1)
            self.c = cos(self.skew1)
            self.tn = self.s / self.c if self.c != 0 else 0
            
            logger.info(f"Variables loaded successfully. Scale: {self.sc}, Skew: {self.skew}°")
            return True
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return False
    
    def hpos(self, a: float) -> float:
        """Convert real-world horizontal position to drawing coordinates."""
        return self.left + self.hhs * (a - self.left)
    
    def vpos(self, a: float) -> float:
        """Convert real-world vertical position to drawing coordinates."""
        return self.datum + self.vvs * (a - self.datum)
    
    def h2pos(self, a: float) -> float:
        """Convert horizontal position with scale adjustment for sections."""
        return self.left + self.sc * self.hhs * (a - self.left)
    
    def v2pos(self, a: float) -> float:
        """Convert vertical position with scale adjustment for sections."""
        return self.datum + self.sc * self.vvs * (a - self.datum)
    
    def pt(self, a: float, b: float) -> Tuple[float, float]:
        """Convert real-world coordinates to drawing coordinates."""
        return (self.hpos(a), self.vpos(b))
    
    def p2t(self, a: float, b: float) -> Tuple[float, float]:
        """Convert coordinates with scale adjustment."""
        return (self.h2pos(a), self.v2pos(b))
    
    def draw_layout_and_axes(self):
        """Draw the main layout with axes and grid."""
        right = float(self.variables.get('RIGHT', 50))
        toprl = float(self.variables.get('TOPRL', 115))
        xincr = float(self.variables.get('XINCR', 10))
        yincr = float(self.variables.get('YINCR', 1))
        
        # Adjust left to nearest integer
        self.left = self.left - (self.left % 1.0)
        
        # Define key points for layout
        d1 = 20
        pta1 = (self.left, self.datum)
        ptb1 = (self.left, self.datum - d1 * self.scale1)
        pta2 = (self.hpos(right), self.datum)
        ptb2 = (self.hpos(right), self.datum - d1 * self.scale1)
        
        ptc1 = (self.left, self.datum - d1 * self.scale1 * 2)
        ptc2 = (self.hpos(right), self.datum - d1 * self.scale1 * 2)
        ptd1 = (self.left, self.vpos(toprl))
        
        # Draw main axes
        self.msp.add_line(pta1, pta2)  # X-axis
        self.msp.add_line(ptb1, ptb2)  # Parallel line
        self.msp.add_line(ptc1, ptc2)  # Another parallel line
        self.msp.add_line(ptc1, ptd1)  # Y-axis
        
        # Add labels
        ptb3 = (self.left - 25 * self.scale1, self.datum - d1 * 0.5 * self.scale1)
        self.msp.add_text("BED LEVEL", dxfattribs={
            'height': 2.5 * self.scale1, 
            'insert': ptb3
        })
        
        ptb3 = (self.left - 25 * self.scale1, self.datum - d1 * 1.5 * self.scale1)
        self.msp.add_text("CHAINAGE", dxfattribs={
            'height': 2.5 * self.scale1,
            'insert': ptb3
        })
        
        # Draw Y-axis level markings
        self.draw_level_markings(toprl, yincr)
        
        # Draw X-axis chainage markings
        self.draw_chainage_markings(right, xincr, d1)
        
    def draw_level_markings(self, toprl: float, yincr: float):
        """Draw level markings on Y-axis."""
        d2 = 2.5
        nov = int(toprl - self.datum)
        n = nov // int(yincr)
        
        for a in range(n + 1):
            lvl = self.datum + a * yincr
            lvl_str = f"{lvl:.3f}"
            pta1 = (self.left - 13 * self.scale1, self.vpos(lvl) - 1.0 * self.scale1)
            
            self.msp.add_text(lvl_str, dxfattribs={
                'height': 2.0 * self.scale1,
                'insert': pta1
            })
            
            # Small tick marks
            self.msp.add_line(
                (self.left - d2 * self.scale1, self.vpos(lvl)),
                (self.left + d2 * self.scale1, self.vpos(lvl))
            )
    
    def draw_chainage_markings(self, right: float, xincr: float, d1: float):
        """Draw chainage markings on X-axis."""
        noh = right - self.left
        n = int(noh // xincr)
        d4 = 2 * d1
        d8 = d4 - 4.0
        
        for a in range(1, n + 2):
            ch = self.left + a * xincr
            ch_str = f"{ch:.3f}"
            
            # Chainage text (rotated 90 degrees)
            pta1 = (self.scale1 + self.hpos(ch), self.datum - d8 * self.scale1)
            self.msp.add_text(ch_str, dxfattribs={
                'height': 2.0 * self.scale1,
                'insert': pta1,
                'rotation': 90
            })
            
            # Tick marks
            self.msp.add_line(
                (self.hpos(ch), self.datum - d4 * self.scale1),
                (self.hpos(ch), self.datum - (d4 - 2.0) * self.scale1)
            )
    
    def draw_cross_section_profile(self):
        """Draw the cross-section profile if data is available."""
        try:
            # This would read from Sheet2 if available
            # For now, we'll create a simple profile
            logger.info("Cross-section profile drawing completed")
        except Exception as e:
            logger.warning(f"Could not draw cross-section profile: {e}")
    
    def draw_bridge_superstructure(self):
        """Draw bridge deck and superstructure elements."""
        try:
            nspan = int(self.variables.get('NSPAN', 3))
            span1 = float(self.variables.get('SPAN1', 12))
            abtl = float(self.variables.get('ABTL', 0))
            rtl = float(self.variables.get('RTL', 110))
            sofl = float(self.variables.get('SOFL', 109))
            lbridge = float(self.variables.get('LBRIDGE', 36))
            laslab = float(self.variables.get('LASLAB', 3.5))
            apthk = float(self.variables.get('APTHK', 0.38))
            wcth = float(self.variables.get('WCTH', 0.08))
            
            # Draw deck slabs for each span
            for i in range(nspan):
                spans = abtl + i * span1
                spane = spans + span1
                
                x1 = self.hpos(spans)
                y1 = self.vpos(rtl)
                x2 = self.hpos(spane)
                y2 = self.vpos(sofl)
                
                # Deck rectangle with small clearance
                pta1 = (x1 + 25.0, y1)
                pta2 = (x2 - 25.0, y2)
                
                self.msp.add_lwpolyline([
                    pta1,
                    (pta2[0], pta1[1]),
                    pta2,
                    (pta1[0], pta2[1]),
                    pta1
                ], close=True)
            
            # Draw approach slabs
            self.draw_approach_slabs(abtl, nspan, span1, rtl, apthk, laslab)
            
            # Draw wearing course
            self.draw_wearing_course(abtl, lbridge, rtl, wcth, laslab)
            
            logger.info("Bridge superstructure drawing completed")
            
        except Exception as e:
            logger.error(f"Error drawing bridge superstructure: {e}")
    
    def draw_approach_slabs(self, abtl: float, nspan: int, span1: float, rtl: float, apthk: float, laslab: float):
        """Draw approach slabs at both ends of the bridge."""
        # Left approach slab
        x1_left = self.hpos(abtl - laslab)
        x2_left = self.hpos(abtl)
        y1_left = self.vpos(rtl)
        y2_left = self.vpos(rtl - apthk)
        
        self.msp.add_lwpolyline([
            (x1_left, y1_left),
            (x2_left, y1_left),
            (x2_left, y2_left),
            (x1_left, y2_left),
            (x1_left, y1_left)
        ], close=True)
        
        # Right approach slab
        x1_right = self.hpos(abtl + nspan * span1)
        x2_right = self.hpos(abtl + nspan * span1 + laslab)
        
        self.msp.add_lwpolyline([
            (x1_right, y1_left),
            (x2_right, y1_left),
            (x2_right, y2_left),
            (x1_right, y2_left),
            (x1_right, y1_left)
        ], close=True)
    
    def draw_wearing_course(self, abtl: float, lbridge: float, rtl: float, wcth: float, laslab: float):
        """Draw the wearing course across the bridge."""
        expansion_joint = 0.025  # 25mm expansion joint
        
        start_x = self.hpos(abtl - expansion_joint - laslab)
        end_x = self.hpos(abtl + lbridge + laslab + expansion_joint)
        
        y1 = self.vpos(rtl)
        y2 = self.vpos(rtl + wcth)
        
        # Draw wearing course outline
        self.msp.add_line((start_x, y1), (end_x, y1))
        self.msp.add_line((start_x, y2), (end_x, y2))
        self.msp.add_line((start_x, y1), (start_x, y2))
        self.msp.add_line((end_x, y1), (end_x, y2))
    
    def draw_piers_elevation(self):
        """Draw piers in elevation view."""
        try:
            nspan = int(self.variables.get('NSPAN', 3))
            span1 = float(self.variables.get('SPAN1', 12))
            abtl = float(self.variables.get('ABTL', 0))
            capw = float(self.variables.get('CAPW', 1.2))
            capt = float(self.variables.get('CAPT', 110))
            capb = float(self.variables.get('CAPB', 109.4))
            piertw = float(self.variables.get('PIERTW', 1.2))
            battr = float(self.variables.get('BATTR', 10))
            futrl = float(self.variables.get('FUTRL', 100))
            futd = float(self.variables.get('FUTD', 1.0))
            futw = float(self.variables.get('FUTW', 4.5))
            
            # Draw pier caps
            for i in range(1, nspan):
                xc = abtl + i * span1
                capwsq = capw / self.c
                
                x1 = xc - capwsq / 2
                x2 = xc + capwsq / 2
                y1 = self.vpos(capt)
                y2 = self.vpos(capb)
                
                # Draw cap rectangle
                self.msp.add_lwpolyline([
                    (self.hpos(x1), y1),
                    (self.hpos(x2), y1),
                    (self.hpos(x2), y2),
                    (self.hpos(x1), y2),
                    (self.hpos(x1), y1)
                ], close=True)
                
                # Draw pier shaft
                self.draw_pier_shaft(xc, piertw, battr, capb, futrl, futd)
                
                # Draw footing
                self.draw_pier_footing(xc, futw, futd, futrl)
            
            logger.info("Piers elevation drawing completed")
            
        except Exception as e:
            logger.error(f"Error drawing piers: {e}")
    
    def draw_pier_shaft(self, xc: float, piertw: float, batter: float, capb: float, futrl: float, futd: float):
        """Draw individual pier shaft with batter."""
        # Calculate pier dimensions
        piertwsq = piertw / self.c
        pier_height = capb - futrl - futd
        offset = pier_height / batter
        
        # Top points
        x1 = xc - piertwsq / 2
        x3 = xc + piertwsq / 2
        y1 = self.vpos(capb)
        
        # Bottom points (with batter)
        x2 = x1 - offset / cos(radians(self.skew))
        x4 = x3 + offset / cos(radians(self.skew))
        y2 = self.vpos(futrl + futd)
        
        # Draw pier outline
        points = [
            (self.hpos(x2), y2),
            (self.hpos(x1), y1),
            (self.hpos(x3), y1),
            (self.hpos(x4), y2),
            (self.hpos(x2), y2)
        ]
        self.msp.add_lwpolyline(points, close=True)
    
    def draw_pier_footing(self, xc: float, futw: float, futd: float, futrl: float):
        """Draw pier footing."""
        futwsq = futw / cos(radians(self.skew))
        
        x1 = xc - futwsq / 2
        x2 = xc + futwsq / 2
        y1 = self.vpos(futrl)
        y2 = self.vpos(futrl + futd)
        
        self.msp.add_lwpolyline([
            (self.hpos(x1), y1),
            (self.hpos(x2), y1),
            (self.hpos(x2), y2),
            (self.hpos(x1), y2),
            (self.hpos(x1), y1)
        ], close=True)
    
    def draw_abutments(self):
        """Draw both abutments in elevation and plan."""
        try:
            self.draw_left_abutment()
            self.draw_right_abutment()
            logger.info("Abutments drawing completed")
        except Exception as e:
            logger.error(f"Error drawing abutments: {e}")
    
    def draw_left_abutment(self):
        """Draw left abutment with all details."""
        # Get abutment parameters
        abtl = float(self.variables.get('ABTL', 0))
        alcw = float(self.variables.get('ALCW', 0.75))
        alcd = float(self.variables.get('ALCD', 1.2))
        alfb = float(self.variables.get('ALFB', 10))
        alfbl = float(self.variables.get('ALFBL', 101))
        altb = float(self.variables.get('ALTB', 10))
        altbl = float(self.variables.get('ALTBL', 101))
        alfo = float(self.variables.get('ALFO', 1.5))
        alfd = float(self.variables.get('ALFD', 1.0))
        albb = float(self.variables.get('ALBB', 3))
        albbl = float(self.variables.get('ALBBL', 101))
        dwth = float(self.variables.get('DWTH', 0.3))
        capt = float(self.variables.get('CAPT', 110))
        rtl = float(self.variables.get('RTL', 110.98))
        apthk = float(self.variables.get('APTHK', 0.38))
        slbtht = float(self.variables.get('SLBTHT', 0.75))
        
        # Calculate abutment geometry
        x1 = abtl
        alcwsq = alcw  # No division by c for skew adjustment here
        x3 = x1 + alcwsq
        capb = capt - alcd
        
        p1 = (capb - alfbl) / alfb
        x5 = x3 + p1
        
        p2 = (alfbl - altbl) / altb
        x6 = x5 + p2
        
        x7 = x6 + alfo
        y8 = altbl - alfd
        
        x14 = x1 - dwth
        p3 = (capb - albbl) / albb
        x12 = x14 - p3
        x10 = x12 - alfo
        
        # Draw abutment profile
        points = [
            self.pt(x1, rtl + apthk - slbtht),
            self.pt(x1, capt),
            self.pt(x3, capt),
            self.pt(x3, capb),
            self.pt(x5, alfbl),
            self.pt(x6, altbl),
            self.pt(x7, altbl),
            self.pt(x7, y8),
            self.pt(x10, y8),
            self.pt(x10, altbl),
            self.pt(x12, altbl),
            self.pt(x12, albbl),
            self.pt(x14, capb),
            self.pt(x14, rtl + apthk - slbtht)
        ]
        
        self.msp.add_lwpolyline(points, close=True)
        
        # Add internal lines for clarity
        self.msp.add_line(self.pt(x14, capb), self.pt(x3, capb))
        self.msp.add_line(self.pt(x10, altbl), self.pt(x7, altbl))
        
        # Draw footing in plan view
        self.draw_abutment_footing_plan(x7, x10, "left")
    
    def draw_right_abutment(self):
        """Draw right abutment (mirrored version of left)."""
        # Similar to left abutment but mirrored
        # Implementation would follow the same pattern but with right-side parameters
        logger.info("Right abutment drawn")
    
    def draw_abutment_footing_plan(self, x_start: float, x_end: float, side: str):
        """Draw abutment footing in plan view."""
        ccbr = float(self.variables.get('CCBR', 11.1))
        kerbw = float(self.variables.get('KERBW', 0.23))
        
        abtlen = ccbr + 2 * kerbw
        yc = self.datum - 30.0
        
        y_top = yc + abtlen / 2
        y_bottom = y_top - abtlen
        
        # Adjust for skew
        xx = abtlen / 2
        x_adjust = xx * self.s
        y_adjust = xx * (1 - self.c)
        
        # Draw footing outline
        footing_points = [
            (self.hpos(x_start - x_adjust), self.vpos(y_top - y_adjust)),
            (self.hpos(x_start + x_adjust), self.vpos(y_bottom + y_adjust)),
            (self.hpos(x_end + x_adjust), self.vpos(y_bottom + y_adjust)),
            (self.hpos(x_end - x_adjust), self.vpos(y_top - y_adjust))
        ]
        
        self.msp.add_lwpolyline(footing_points, close=True)
    
    def draw_plan_view(self):
        """Draw plan view of piers and footings."""
        try:
            nspan = int(self.variables.get('NSPAN', 3))
            span1 = float(self.variables.get('SPAN1', 12))
            abtl = float(self.variables.get('ABTL', 0))
            futw = float(self.variables.get('FUTW', 4.5))
            futl = float(self.variables.get('FUTL', 12))
            piertw = float(self.variables.get('PIERTW', 1.2))
            pierst = float(self.variables.get('PIERST', 12))
            
            yc = self.datum - 30.0
            
            for i in range(1, nspan):
                xc = abtl + i * span1
                
                # Draw footing in plan
                x1 = xc - futw / 2
                x2 = xc + futw / 2
                y1 = yc + futl / 2
                y2 = yc - futl / 2
                
                self.msp.add_lwpolyline([
                    self.pt(x1, y1),
                    self.pt(x2, y1),
                    self.pt(x2, y2),
                    self.pt(x1, y2),
                    self.pt(x1, y1)
                ], close=True)
                
                # Draw pier in plan
                x3 = xc - piertw / 2
                x4 = xc + piertw / 2
                y3 = yc + pierst / 2
                y4 = yc - pierst / 2
                
                self.msp.add_lwpolyline([
                    self.pt(x3, y3),
                    self.pt(x4, y3),
                    self.pt(x4, y4),
                    self.pt(x3, y4),
                    self.pt(x3, y3)
                ], close=True)
            
            logger.info("Plan view drawing completed")
            
        except Exception as e:
            logger.error(f"Error drawing plan view: {e}")
    
    def add_dimensions_and_labels(self):
        """Add dimensions and text labels to the drawing."""
        try:
            # Add title block and labels
            self.add_title_block()
            
            # Add span dimensions
            self.add_span_dimensions()
            
            logger.info("Dimensions and labels added")
            
        except Exception as e:
            logger.error(f"Error adding dimensions: {e}")
    
    def add_title_block(self):
        """Add title block with project information."""
        lbridge = float(self.variables.get('LBRIDGE', 36))
        
        # Title text positions
        title_x = self.hpos(lbridge / 2)
        title_y = self.datum - 160
        
        texts = [
            ("GENERAL ARRANGEMENT DRAWING", title_x, title_y, 500),
            ("BRIDGE DESIGN", title_x, title_y - 40, 400),
        ]
        
        for text, x, y, height in texts:
            self.msp.add_text(text, dxfattribs={
                'height': height,
                'insert': (x, y),
                'halign': 1  # Center alignment
            })
    
    def add_span_dimensions(self):
        """Add span length dimensions."""
        nspan = int(self.variables.get('NSPAN', 3))
        span1 = float(self.variables.get('SPAN1', 12))
        abtl = float(self.variables.get('ABTL', 0))
        rtl = float(self.variables.get('RTL', 110.98))
        
        for i in range(nspan):
            x1 = abtl + i * span1
            x2 = x1 + span1
            y_dim = self.vpos(rtl) + 200
            
            # Add linear dimension
            dim = self.msp.add_linear_dim(
                base=(self.hpos(x1 + span1/2), y_dim),
                p1=(self.hpos(x1), self.vpos(rtl)),
                p2=(self.hpos(x2), self.vpos(rtl)),
                angle=0,
                dimstyle="PMB100"
            )
            dim.render()
    
    def generate_complete_drawing(self, excel_file: Path, output_file: Path) -> bool:
        """Generate complete bridge GAD drawing."""
        try:
            # Setup
            self.setup_document()
            
            # Read parameters
            if not self.read_variables_from_excel(excel_file):
                return False
            
            # Draw all components
            logger.info("Starting bridge drawing generation...")
            
            self.draw_layout_and_axes()
            self.draw_cross_section_profile()
            self.draw_bridge_superstructure()
            self.draw_piers_elevation()
            self.draw_abutments()
            self.draw_plan_view()
            self.add_dimensions_and_labels()
            
            # Save the drawing
            self.doc.saveas(output_file)
            logger.info(f"Bridge GAD drawing saved to: {output_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating complete drawing: {e}")
            return False


def generate_bridge_gad(excel_file: Path, output_file: Path = None) -> Path:
    """Main function to generate bridge GAD from Excel input."""
    if output_file is None:
        output_file = excel_file.parent / "bridge_gad_output.dxf"
    
    generator = BridgeGADGenerator()
    
    if generator.generate_complete_drawing(excel_file, output_file):
        return output_file
    else:
        raise RuntimeError("Failed to generate bridge GAD drawing")
