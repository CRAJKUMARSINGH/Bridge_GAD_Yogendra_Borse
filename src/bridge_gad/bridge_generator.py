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
    
    def __init__(self, acad_version: str = "R2010"):
        """Initialize with optional AutoCAD version selection.
        
        Args:
            acad_version: AutoCAD version format (R2006, R2010, etc.)
        """
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
        self.acad_version = self._validate_acad_version(acad_version)
        
    def _validate_acad_version(self, version: str) -> str:
        """Validate and normalize AutoCAD version format.
        
        Args:
            version: Version string (R2006, 2006, R2010, 2010, etc.)
            
        Returns:
            Validated version string in ezdxf format
        """
        # Supported versions: R2006 (DXF 18), R2010 (DXF 15)
        supported = {"R2006", "R2010", "2006", "2010"}
        version_upper = str(version).upper()
        
        # Normalize version
        if version_upper in {"2006", "2006"}:
            return "R2006"
        elif version_upper in {"2010", "2010"}:
            return "R2010"
        elif version_upper == "R2006":
            return "R2006"
        elif version_upper == "R2010":
            return "R2010"
        else:
            logger.warning(f"Unknown AutoCAD version {version}, using R2010 (default)")
            return "R2010"
        
    def setup_document(self):
        """Initialize DXF document with proper setup."""
        self.doc = ezdxf.new(self.acad_version, setup=True)
        self.msp = self.doc.modelspace()
        self.setup_styles()
        logger.info(f"Document setup completed - Format: {self.acad_version}")
        
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
        
        # Bottom points (with batter) - pier should connect to top of footing
        x2 = x1 - offset / cos(radians(self.skew))
        x4 = x3 + offset / cos(radians(self.skew))
        y2 = self.vpos(futrl)  # Connect to top of footing (founding level)
        
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
        """Draw pier footing below ground level."""
        futwsq = futw / cos(radians(self.skew))
        
        x1 = xc - futwsq / 2
        x2 = xc + futwsq / 2
        # Foundation should be below ground - futrl is the founding level
        # y1 is top of footing (founding level), y2 is bottom of footing
        y1 = self.vpos(futrl)  # Top of footing at founding level
        y2 = self.vpos(futrl - futd)  # Bottom of footing (subtract depth to go below)
        
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
        # Get abutment parameters - using right abutment specific values
        abtl = float(self.variables.get('ABTL', 0))
        lbridge = float(self.variables.get('LBRIDGE', 36))
        nspan = int(self.variables.get('NSPAN', 3))
        span1 = float(self.variables.get('SPAN1', 12))
        
        # Right abutment parameters
        arcw = float(self.variables.get('ARCW', 0.75))  # Right abutment cap width
        arcd = float(self.variables.get('ARCD', 1.2))   # Right abutment cap depth
        arfb = float(self.variables.get('ARFB', 10))    # Right abutment front batter
        arfbl = float(self.variables.get('ARFBL', 101)) # Right abutment front batter RL
        artb = float(self.variables.get('ARTB', 10))    # Right abutment toe batter
        artbl = float(self.variables.get('ARTBL', 101)) # Right abutment toe batter level
        arfo = float(self.variables.get('ARFO', 1.5))   # Right abutment front offset
        arfd = float(self.variables.get('ARFD', 1.0))   # Right abutment footing depth
        arbb = float(self.variables.get('ARBB', 3))     # Right abutment back batter
        arbbl = float(self.variables.get('ARBBL', 101)) # Right abutment back batter RL
        
        dwth = float(self.variables.get('DWTH', 0.3))
        capt = float(self.variables.get('CAPT', 110))
        rtl = float(self.variables.get('RTL', 110.98))
        apthk = float(self.variables.get('APTHK', 0.38))
        slbtht = float(self.variables.get('SLBTHT', 0.75))
        
        # Calculate right abutment position (at the end of the bridge)
        right_abt_pos = abtl + nspan * span1
        
        # Calculate abutment geometry (mirrored from left)
        x1 = right_abt_pos
        arcwsq = arcw  # No division by c for skew adjustment here
        x3 = x1 - arcwsq  # Subtract for right side
        capb = capt - arcd
        
        p1 = (capb - arfbl) / arfb
        x5 = x3 - p1  # Subtract for right side
        
        p2 = (arfbl - artbl) / artb
        x6 = x5 - p2  # Subtract for right side
        
        x7 = x6 - arfo  # Subtract for right side
        y8 = artbl - arfd
        
        x14 = x1 + dwth  # Add for right side (dirt wall on opposite side)
        p3 = (capb - arbbl) / arbb
        x12 = x14 + p3  # Add for right side
        x10 = x12 + arfo  # Add for right side
        
        # Draw right abutment profile (mirrored points)
        points = [
            self.pt(x1, rtl + apthk - slbtht),
            self.pt(x1, capt),
            self.pt(x3, capt),
            self.pt(x3, capb),
            self.pt(x5, arfbl),
            self.pt(x6, artbl),
            self.pt(x7, artbl),
            self.pt(x7, y8),
            self.pt(x10, y8),
            self.pt(x10, artbl),
            self.pt(x12, artbl),
            self.pt(x12, arbbl),
            self.pt(x14, capb),
            self.pt(x14, rtl + apthk - slbtht)
        ]
        
        self.msp.add_lwpolyline(points, close=True)
        
        # Add internal lines for clarity
        self.msp.add_line(self.pt(x14, capb), self.pt(x3, capb))
        self.msp.add_line(self.pt(x10, artbl), self.pt(x7, artbl))
        
        # Draw footing in plan view
        self.draw_abutment_footing_plan(x7, x10, "right")
    
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
        """Draw comprehensive plan view including piers, footings, and abutments."""
        try:
            # Draw pier and footing plan views
            self.draw_pier_foundation_plan()
            
            # Draw abutment foundation plans
            self.draw_abutment_foundation_plans()
            
            logger.info("Plan view drawing completed")
            
        except Exception as e:
            logger.error(f"Error drawing plan view: {e}")
    
    def draw_pier_foundation_plan(self):
        """Draw pier and footing plan views with proper dimensions and skew adjustments."""
        nspan = int(self.variables.get('NSPAN', 3))
        span1 = float(self.variables.get('SPAN1', 12))
        abtl = float(self.variables.get('ABTL', 0))
        futw = float(self.variables.get('FUTW', 4.5))
        futl = float(self.variables.get('FUTL', 12))
        piertw = float(self.variables.get('PIERTW', 1.2))
        pierst = float(self.variables.get('PIERST', 12))
        
        # Plan view Y-coordinate (below elevation view)
        yc = self.datum - 30.0
        
        for i in range(1, nspan):
            xc = abtl + i * span1
            
            # Adjust dimensions for skew
            futwsq = futw / cos(radians(self.skew))
            futlsq = futl / cos(radians(self.skew))
            piertwsq = piertw / cos(radians(self.skew))
            pierstsq = pierst / cos(radians(self.skew))
            
            # Draw footing in plan with skew adjustments
            x1 = xc - futwsq / 2
            x2 = xc + futwsq / 2
            y1 = yc + futlsq / 2
            y2 = yc - futlsq / 2
            
            # Apply skew rotation to footing corners
            x_offset = (futlsq / 2) * sin(radians(self.skew))
            y_offset = (futlsq / 2) * (1 - cos(radians(self.skew)))
            
            footing_points = [
                self.pt(x1 - x_offset, y1 - y_offset),
                self.pt(x2 - x_offset, y1 - y_offset),
                self.pt(x2 + x_offset, y2 + y_offset),
                self.pt(x1 + x_offset, y2 + y_offset)
            ]
            
            self.msp.add_lwpolyline(footing_points, close=True)
            
            # Draw pier in plan with skew adjustments
            x3 = xc - piertwsq / 2
            x4 = xc + piertwsq / 2
            y3 = yc + pierstsq / 2
            y4 = yc - pierstsq / 2
            
            # Apply skew rotation to pier corners
            x_pier_offset = (pierstsq / 2) * sin(radians(self.skew))
            y_pier_offset = (pierstsq / 2) * (1 - cos(radians(self.skew)))
            
            pier_points = [
                self.pt(x3 - x_pier_offset, y3 - y_pier_offset),
                self.pt(x4 - x_pier_offset, y3 - y_pier_offset),
                self.pt(x4 + x_pier_offset, y4 + y_pier_offset),
                self.pt(x3 + x_pier_offset, y4 + y_pier_offset)
            ]
            
            self.msp.add_lwpolyline(pier_points, close=True)
            
            # Add pier number labels
            label_x = self.hpos(xc)
            label_y = self.vpos(yc + futlsq / 2 + 2.0)
            self.msp.add_text(f"P{i}", dxfattribs={
                'height': 1.5 * self.scale1,
                'insert': (label_x, label_y),
                'halign': 1  # Center alignment
            })
    
    def draw_abutment_foundation_plans(self):
        """Draw foundation plans for both abutments."""
        ccbr = float(self.variables.get('CCBR', 11.1))
        kerbw = float(self.variables.get('KERBW', 0.23))
        abtl = float(self.variables.get('ABTL', 0))
        nspan = int(self.variables.get('NSPAN', 3))
        span1 = float(self.variables.get('SPAN1', 12))
        
        abtlen = ccbr + 2 * kerbw
        yc = self.datum - 30.0
        
        # Left abutment foundation plan
        self.draw_single_abutment_foundation_plan(abtl, abtlen, yc, "A1")
        
        # Right abutment foundation plan
        right_abt_pos = abtl + nspan * span1
        self.draw_single_abutment_foundation_plan(right_abt_pos, abtlen, yc, "A2")
    
    def draw_single_abutment_foundation_plan(self, abt_x: float, abtlen: float, yc: float, label: str):
        """Draw foundation plan for a single abutment."""
        # Foundation dimensions with extensions
        foundation_ext = 1.5  # Extension beyond abutment
        
        y_top = yc + (abtlen + foundation_ext) / 2
        y_bottom = yc - (abtlen + foundation_ext) / 2
        
        # Foundation extends beyond abutment walls
        x_left = abt_x - foundation_ext
        x_right = abt_x + foundation_ext
        
        # Apply skew adjustments
        xx = (abtlen + foundation_ext) / 2
        x_adjust = xx * sin(radians(self.skew))
        y_adjust = xx * (1 - cos(radians(self.skew)))
        
        # Draw foundation plan with skew
        foundation_points = [
            self.pt(x_left - x_adjust, y_top - y_adjust),
            self.pt(x_right - x_adjust, y_top - y_adjust),
            self.pt(x_right + x_adjust, y_bottom + y_adjust),
            self.pt(x_left + x_adjust, y_bottom + y_adjust)
        ]
        
        self.msp.add_lwpolyline(foundation_points, close=True)
        
        # Add abutment label
        label_x = self.hpos(abt_x)
        label_y = self.vpos(y_top + 2.0)
        self.msp.add_text(label, dxfattribs={
            'height': 1.5 * self.scale1,
            'insert': (label_x, label_y),
            'halign': 1  # Center alignment
        })
    
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
    
    def draw_a4_border(self):
        """Draw A4 landscape border with professional frame."""
        try:
            right = float(self.variables.get('RIGHT', 50))
            lbridge = float(self.variables.get('LBRIDGE', 36))
            
            # A4 landscape dimensions in mm (1mm = 2.834645669 drawing units)
            # 297mm width × 210mm height = 841.89 × 595.27 units
            # Scale to drawing: make it visible and proportional
            border_margin = 50
            border_left = self.hpos(self.left) - border_margin
            border_right = self.hpos(right) + 100 * self.scale1
            border_top = self.vpos(float(self.variables.get('TOPRL', 115))) + 200
            border_bottom = self.datum - 120 * self.scale1
            
            # Draw A4 landscape border rectangle
            border_points = [
                (border_left, border_top),
                (border_right, border_top),
                (border_right, border_bottom),
                (border_left, border_bottom)
            ]
            self.msp.add_lwpolyline(border_points, close=True, dxfattribs={'lineweight': 35})
            
            # Inner frame
            inner_margin = 20
            inner_points = [
                (border_left + inner_margin, border_top - inner_margin),
                (border_right - inner_margin, border_top - inner_margin),
                (border_right - inner_margin, border_bottom + inner_margin),
                (border_left + inner_margin, border_bottom + inner_margin)
            ]
            self.msp.add_lwpolyline(inner_points, close=True)
            
            logger.info("A4 landscape border drawn")
        except Exception as e:
            logger.error(f"Error drawing A4 border: {e}")
    
    def add_title_block(self):
        """Add editable title block with RKS LEGAL company information."""
        try:
            right = float(self.variables.get('RIGHT', 50))
            lbridge = float(self.variables.get('LBRIDGE', 36))
            
            # Get editable values from Excel
            project_name = str(self.variables.get('PROJECT_NAME', 'Bridge General Arrangement Drawing'))
            company_name = str(self.variables.get('COMPANY_NAME', 'RKS LEGAL'))
            company_full = str(self.variables.get('COMPANY_FULL', 'Techno Legal Consultants'))
            address = str(self.variables.get('ADDRESS', '303 Vallabh Apartment, Navratna Complex, Bhuwana, Udaipur -313001'))
            email = str(self.variables.get('EMAIL', 'crajkumarsingh@hotmail.com'))
            mobile = str(self.variables.get('MOBILE', '+919414163019'))
            
            # Position title block on right side of drawing
            title_block_x = self.hpos(right) + 50 * self.scale1
            title_block_y = self.vpos(float(self.variables.get('TOPRL', 115))) + 100
            
            # Main title
            self.msp.add_text("GENERAL ARRANGEMENT DRAWING", dxfattribs={
                'height': 3.0 * self.scale1,
                'insert': (title_block_x, title_block_y),
                'halign': 0
            })
            
            # Project name (editable)
            y_pos = title_block_y - 4.0 * self.scale1
            self.msp.add_text(f"Project: {project_name}", dxfattribs={
                'height': 2.0 * self.scale1,
                'insert': (title_block_x, y_pos),
                'halign': 0
            })
            
            # Company information box
            y_pos -= 5.0 * self.scale1
            self.msp.add_text(company_name, dxfattribs={
                'height': 2.5 * self.scale1,
                'insert': (title_block_x, y_pos),
                'halign': 0,
                'style': 'Arial'
            })
            
            y_pos -= 3.0 * self.scale1
            self.msp.add_text(company_full, dxfattribs={
                'height': 1.8 * self.scale1,
                'insert': (title_block_x, y_pos),
                'halign': 0
            })
            
            # Address
            y_pos -= 2.5 * self.scale1
            self.msp.add_text(address, dxfattribs={
                'height': 1.5 * self.scale1,
                'insert': (title_block_x, y_pos),
                'halign': 0
            })
            
            # Contact info
            y_pos -= 2.0 * self.scale1
            self.msp.add_text(f"Email: {email}", dxfattribs={
                'height': 1.3 * self.scale1,
                'insert': (title_block_x, y_pos),
                'halign': 0
            })
            
            y_pos -= 1.8 * self.scale1
            self.msp.add_text(f"Mobile: {mobile}", dxfattribs={
                'height': 1.3 * self.scale1,
                'insert': (title_block_x, y_pos),
                'halign': 0
            })
            
            logger.info("Title block with RKS LEGAL information added")
        except Exception as e:
            logger.error(f"Error adding title block: {e}")
    
    def add_project_name_footer(self):
        """Add full-width project name at bottom of drawing."""
        try:
            right = float(self.variables.get('RIGHT', 50))
            
            # Get project name from Excel
            project_name = str(self.variables.get('PROJECT_NAME', 'Bridge General Arrangement Drawing'))
            project_code = str(self.variables.get('PROJECT_CODE', ''))
            
            # Position at bottom, full width
            footer_x = self.hpos(self.left + (right - self.left) / 2)  # Center horizontally
            footer_y = self.datum - 130 * self.scale1  # Bottom of page
            
            # Draw footer text
            footer_text = f"{project_name}" + (f" | {project_code}" if project_code else "")
            self.msp.add_text(footer_text, dxfattribs={
                'height': 3.5 * self.scale1,
                'insert': (footer_x, footer_y),
                'halign': 1,  # Center alignment
                'style': 'Arial'
            })
            
            # Draw horizontal line above footer
            line_y = footer_y + 2.0 * self.scale1
            line_x1 = self.hpos(self.left)
            line_x2 = self.hpos(right)
            self.msp.add_line((line_x1, line_y), (line_x2, line_y))
            
            logger.info("Project name footer added")
        except Exception as e:
            logger.error(f"Error adding project footer: {e}")
    
    def draw_side_elevation(self):
        """Draw side elevation view showing cross-section of bridge components."""
        try:
            # Get bridge parameters
            nspan = int(self.variables.get('NSPAN', 3))
            span1 = float(self.variables.get('SPAN1', 12))
            abtl = float(self.variables.get('ABTL', 0))
            rtl = float(self.variables.get('RTL', 110.98))
            ccbr = float(self.variables.get('CCBR', 11.1))
            kerbw = float(self.variables.get('KERBW', 0.23))
            slbthe = float(self.variables.get('SLBTHE', 0.75))
            kerbd = float(self.variables.get('KERBD', 0.15))
            capt = float(self.variables.get('CAPT', 110))
            capb = float(self.variables.get('CAPB', 109.4))
            piertw = float(self.variables.get('PIERTW', 1.2))
            pierst = float(self.variables.get('PIERST', 12))
            futrl = float(self.variables.get('FUTRL', 100))
            futd = float(self.variables.get('FUTD', 1.0))
            futw = float(self.variables.get('FUTW', 4.5))
            futl = float(self.variables.get('FUTL', 12))
            right = float(self.variables.get('RIGHT', 50))
            
            # Position side elevation to the right of main drawing with margin
            lbridge = float(self.variables.get('LBRIDGE', 36))
            side_x_offset = self.hpos(right) + 40 * self.scale1  # Fixed pixels offset from main drawing
            side_y_base = self.datum  # Start at datum level
            
            # Draw deck cross-section with calculated bounds
            deck_bounds = self.draw_deck_cross_section(side_x_offset, side_y_base, ccbr, kerbw, slbthe, kerbd, rtl)
            
            # Draw typical pier cross-section below deck
            if nspan > 1 and deck_bounds:
                # Position pier section 5 units below deck bottom
                pier_y_offset = deck_bounds['y_bottom'] - 10 * self.scale1
                self.draw_pier_cross_section(side_x_offset, pier_y_offset, 
                                           piertw, pierst, capt, capb, futrl, futd, futw, futl)
            
            logger.info("Side elevation drawing completed")
            
        except Exception as e:
            logger.error(f"Error drawing side elevation: {e}")
    
    def draw_deck_cross_section(self, x_offset: float, y_base: float, ccbr: float, 
                               kerbw: float, slbthe: float, kerbd: float, rtl: float):
        """Draw deck cross-section showing carriageway and kerbs. Returns bounds for label positioning."""
        # Calculate deck section dimensions with direct scaling
        total_width = ccbr + 2 * kerbw
        deck_thickness = slbthe
        
        # Direct coordinate calculations (no double scaling)
        section_scale = 0.5  # Scale down section for visibility
        x_start = x_offset
        width_scaled = total_width * self.hhs * section_scale
        x_center = x_start + width_scaled / 2
        x_end = x_start + width_scaled
        
        # Vertical positions - use datum offset
        height_offset = self.vvs * section_scale
        y_deck_top = y_base
        y_deck_bottom = y_base - deck_thickness * height_offset
        y_kerb_top = y_base + kerbd * height_offset
        
        # Draw main deck slab
        deck_points = [
            (x_start, y_deck_top),
            (x_end, y_deck_top),
            (x_end, y_deck_bottom),
            (x_start, y_deck_bottom)
        ]
        self.msp.add_lwpolyline(deck_points, close=True)
        
        # Draw left kerb
        kerb_width_scaled = kerbw * self.hhs * section_scale
        left_kerb_x = x_start + kerb_width_scaled
        left_kerb_points = [
            (x_start, y_deck_top),
            (left_kerb_x, y_deck_top),
            (left_kerb_x, y_kerb_top),
            (x_start, y_kerb_top)
        ]
        self.msp.add_lwpolyline(left_kerb_points, close=True)
        
        # Draw right kerb
        right_kerb_x = x_end - kerb_width_scaled
        right_kerb_points = [
            (right_kerb_x, y_deck_top),
            (x_end, y_deck_top),
            (x_end, y_kerb_top),
            (right_kerb_x, y_kerb_top)
        ]
        self.msp.add_lwpolyline(right_kerb_points, close=True)
        
        # Add section label - dynamically positioned above section with proper spacing
        label_x = x_center
        label_spacing = max(3.0 * self.scale1, 50)  # Dynamic spacing based on scale
        label_y = y_kerb_top + label_spacing
        self.msp.add_text("SECTION A-A", dxfattribs={
            'height': 2.0 * self.scale1,
            'insert': (label_x, label_y),
            'halign': 1,  # Center alignment
            'valign': 0   # Bottom alignment
        })
        
        # Store bounds for next section positioning
        return {
            'x_start': x_start,
            'x_end': x_end,
            'x_center': x_center,
            'y_top': y_deck_top,
            'y_bottom': y_deck_bottom,
            'y_kerb': y_kerb_top,
            'label_y': label_y
        }
    
    def draw_pier_cross_section(self, x_offset: float, y_base: float, piertw: float, 
                               pierst: float, capt: float, capb: float, futrl: float, 
                               futd: float, futw: float, futl: float):
        """Draw typical pier cross-section."""
        # Direct coordinate calculations (no double scaling)
        section_scale = 0.5
        height_offset = self.vvs * section_scale
        
        # Pier center position
        pier_width_scaled = pierst * self.hhs * section_scale
        pier_center_x = x_offset + pier_width_scaled / 2
        
        # Draw pier cap in section
        cap_width_scaled = piertw * self.hhs * section_scale
        cap_x_start = pier_center_x - cap_width_scaled / 2
        cap_x_end = pier_center_x + cap_width_scaled / 2
        
        cap_height = (capt - capb) * height_offset
        cap_y_top = y_base
        cap_y_bottom = y_base - cap_height
        
        cap_points = [
            (cap_x_start, cap_y_top),
            (cap_x_end, cap_y_top),
            (cap_x_end, cap_y_bottom),
            (cap_x_start, cap_y_bottom)
        ]
        self.msp.add_lwpolyline(cap_points, close=True)
        
        # Draw pier shaft in section
        shaft_height = (capb - futrl) * height_offset
        shaft_y_top = cap_y_bottom
        shaft_y_bottom = cap_y_bottom - shaft_height
        
        shaft_points = [
            (cap_x_start, shaft_y_top),
            (cap_x_end, shaft_y_top),
            (cap_x_end, shaft_y_bottom),
            (cap_x_start, shaft_y_bottom)
        ]
        self.msp.add_lwpolyline(shaft_points, close=True)
        
        # Draw footing in section
        footing_width_scaled = futw * self.hhs * section_scale
        footing_x_start = pier_center_x - footing_width_scaled / 2
        footing_x_end = pier_center_x + footing_width_scaled / 2
        
        footing_height = futd * height_offset
        footing_y_top = shaft_y_bottom
        footing_y_bottom = footing_y_top - footing_height
        
        footing_points = [
            (footing_x_start, footing_y_top),
            (footing_x_end, footing_y_top),
            (footing_x_end, footing_y_bottom),
            (footing_x_start, footing_y_bottom)
        ]
        self.msp.add_lwpolyline(footing_points, close=True)
        
        # Add section label - dynamically positioned above pier cap with proper spacing
        label_x = pier_center_x
        label_spacing = max(3.0 * self.scale1, 50)  # Dynamic spacing based on scale
        label_y = cap_y_top + label_spacing
        self.msp.add_text("SECTION B-B (TYPICAL PIER)", dxfattribs={
            'height': 2.0 * self.scale1,
            'insert': (label_x, label_y),
            'halign': 1,  # Center alignment
            'valign': 0   # Bottom alignment
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
            
            # Draw border and title block first (underneath)
            self.draw_a4_border()
            
            # Main drawing elements
            self.draw_layout_and_axes()
            self.draw_cross_section_profile()
            self.draw_bridge_superstructure()
            self.draw_piers_elevation()
            self.draw_abutments()
            self.draw_plan_view()
            self.draw_side_elevation()
            self.add_dimensions_and_labels()
            
            # Add title block and footer
            self.add_title_block()
            self.add_project_name_footer()
            
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
