import asyncio
import pygame
import math
import platform
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bridge Drawing App")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Font
font = pygame.font.SysFont("arial", 16)

# View controls
zoom = 1.0
min_zoom, max_zoom = 0.5, 2.0
pan_x, pan_y = 0, 0

# Input state
input_mode = True
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
    "Enter cross-section points (x,y) or 'done': "
]
input_data = []

# Hardcoded data (for Pyodide or default)
scale1 = 1.0
scale2 = 1.0
skew = 15.0
datum = 100.0
toprl = 110.0
left = 0.0
right = 100.0
xincr = 10.0
yincr = 1.0
noch = 5
cs_data = [(0.0, 100.5), (20.0, 101.0), (40.0, 100.8), (60.0, 101.2), (80.0, 100.7)]
nspan = 1
lbridge = 100.0
abtl = 0.0
RTL = 105.0
Sofl = 104.0
kerbw = 1.0
kerbd = 0.5
ccbr = 8.0
slbthc = 0.3
slbthe = 0.25
slbtht = 0.15
capt = 103.0
capb = 102.5
capw = 2.0
piertw = 1.5
battr = 12.0
pierst = 10.0
piern = 1
span1 = 50.0
futrl = 99.0
futd = 1.0
futw = 3.0
futl = 5.0
dwth = 0.5
alcw = 2.0
alcd = 0.5
alfb = 6.0
alfbl = 101.5
altb = 12.0
altbl = 100.5
alfo = 1.0
alfd = 1.0
albb = 6.0
albbl = 101.5

# Derived variables
def init_derived():
    global hs, vs, vvs, hhs, skew1, s, c, tn, sc, spane, RTL2, ccbrsq, kerbwsq, abtlen
    hs = 1.0
    vs = 1.0
    vvs = 50.0 * zoom
    hhs = 50.0 * zoom
    skew1 = skew * 0.0174532
    s = math.sin(skew1)
    c = math.cos(skew1)
    tn = s / c if c != 0 else 0
    sc = scale1 / scale2
    spane = abtl + span1
    RTL2 = RTL - 30 * sc
    ccbrsq = ccbr / c if c != 0 else ccbr
    kerbwsq = kerbw / c if c != 0 else kerbw
    abtlen = ccbrsq + 2 * kerbwsq

def vpos(a, for_dxf=False):
    a = (1000 if for_dxf else vvs) * (a - datum)
    return (0 if for_dxf else HEIGHT) - a + (0 if for_dxf else pan_y)

def hpos(a, for_dxf=False):
    a = (1000 if for_dxf else hhs) * (a - left)
    return a + (0 if for_dxf else 50 + pan_x)

def v2pos(a, for_dxf=False):
    a = (1000 if for_dxf else vvs) * (a - datum) * sc
    return (0 if for_dxf else HEIGHT) - a + (0 if for_dxf else pan_y)

def h2pos(a, for_dxf=False):
    a = (1000 if for_dxf else hhs) * (a - left) * sc
    return a + (0 if for_dxf else 50 + pan_x)

def pt(a, b, for_dxf=False):
    return (hpos(a, for_dxf), vpos(b, for_dxf))

def p2t(a, b, for_dxf=False):
    return (h2pos(a, for_dxf), v2pos(b, for_dxf))

def rotate_point(point, center, angle, for_dxf=False):
    angle_rad = math.radians(angle)
    x, y = point[0] - center[0], point[1] - center[1]
    new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return (new_x + center[0], new_y + center[1])

def layout(screen=None, doc=None, pdf=None):
    d1 = 20
    pta1 = pt(left, datum)
    ptb1 = pt(left, datum - d1 * scale1)
    pta2 = pt(right, datum)
    ptb2 = pt(right, datum - d1 * scale1)
    ptc1 = pt(left, datum - 2 * d1 * scale1)
    ptc2 = pt(right, datum - 2 * d1 * scale1)
    ptd1 = pt(left, toprl)

    if screen:
        pygame.draw.line(screen, BLACK, pta1, pta2, 2)
        pygame.draw.line(screen, BLACK, ptb1, ptb2, 1)
        pygame.draw.line(screen, BLACK, ptc1, ptc2, 1)
        pygame.draw.line(screen, BLACK, ptc1, ptd1, 2)
    if doc:
        msp = doc.modelspace()
        msp.add_line(pta1, pta2)
        msp.add_line(ptb1, ptb2)
        msp.add_line(ptc1, ptc2)
        msp.add_line(ptc1, ptd1)
    if pdf:
        pdf.setLineWidth(2 if pta1 == pta2 or ptc1 == ptd1 else 1)
        pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)
        pdf.line(ptb1[0]/mm, ptb1[1]/mm, ptb2[0]/mm, ptb2[1]/mm)
        pdf.line(ptc1[0]/mm, ptc1[1]/mm, ptc2[0]/mm, ptc2[1]/mm)
        pdf.line(ptc1[0]/mm, ptc1[1]/mm, ptd1[0]/mm, ptd1[1]/mm)

    ptb3 = pt(left - 25 * scale1, datum - 0.5 * d1 * scale1)
    if screen:
        text = font.render("BED LEVEL", True, BLACK)
        screen.blit(text, ptb3)
    if doc:
        msp.add_text("BED LEVEL", dxfattribs={'height': 2.5}).set_placement(ptb3)
    if pdf:
        pdf.drawString(ptb3[0]/mm, ptb3[1]/mm, "BED LEVEL")

    ptb3 = pt(left - 25 * scale1, datum - 1.5 * d1 * scale1)
    if screen:
        text = font.render("CHAINAGE", True, BLACK)
        screen.blit(text, ptb3)
    if doc:
        msp.add_text("CHAINAGE", dxfattribs={'height': 2.5}).set_placement(ptb3)
    if pdf:
        pdf.drawString(ptb3[0]/mm, ptb3[1]/mm, "CHAINAGE")

    d2 = 2.5
    pta1 = pt(left - d2 * scale1, datum)
    pta2 = pt(left + d2 * scale1, datum)
    if screen:
        pygame.draw.line(screen, GRAY, pta1, pta2, 1)
    if doc:
        msp.add_line(pta1, pta2)
    if pdf:
        pdf.setLineWidth(1)
        pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)

    nov = int(toprl - datum)
    for i in range(nov + 1):
        lvl = datum + i * yincr
        pta1 = pt(left - 13 * scale1, lvl)
        if screen:
            text = font.render(f"{lvl:.3f}", True, BLACK)
            screen.blit(text, (pta1[0] - 40, pta1[1] - 8))
        if doc:
            msp.add_text(f"{lvl:.3f}", dxfattribs={'height': 2.5}).set_placement((pta1[0] - 40, pta1[1] - 2.5))
        if pdf:
            pdf.drawString((pta1[0] - 40)/mm, (pta1[1] - 2)/mm, f"{lvl:.3f}")
        if i > 0:
            pta1 = pt(left - d2 * scale1, lvl)
            pta2 = pt(left + d2 * scale1, lvl)
            if screen:
                pygame.draw.line(screen, GRAY, pta1, pta2, 1)
            if doc:
                msp.add_line(pta1, pta2)
            if pdf:
                pdf.setLineWidth(1)
                pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)

    noh = right - left
    n = int(noh / xincr)
    d4 = 2 * d1
    d5 = d4 - 2.0
    d8 = d4 - 4.0
    for a in range(1, n + 1):
        ch = left + a * xincr
        b1 = f"{ch:.3f}"
        pta1 = pt(ch, datum - d8 * scale1)
        if screen:
            text = font.render(b1, True, BLACK)
            text = pygame.transform.rotate(text, 90)
            screen.blit(text, (pta1[0], pta1[1] - 20))
        if doc:
            msp.add_text(b1, dxfattribs={'height': 2.5, 'rotation': 90}).set_placement((pta1[0], pta1[1] - 5))
        if pdf:
            pdf.saveState()
            pdf.translate(pta1[0]/mm, (pta1[1] - 5)/mm)
            pdf.rotate(90)
            pdf.drawString(0, 0, b1)
            pdf.restoreState()
        pta1 = pt(ch, datum - d4 * scale1)
        pta2 = pt(ch, datum - d5 * scale1)
        if screen:
            pygame.draw.line(screen, GRAY, pta1, pta2, 1)
        if doc:
            msp.add_line(pta1, pta2)
        if pdf:
            pdf.setLineWidth(1)
            pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)

def cs(screen=None, doc=None, pdf=None):
    ptb3 = None
    for a, (x, y) in enumerate(cs_data, 1):
        b1 = f"{x:.3f}"
        b2 = f"{y:.3f}"
        xx = hpos(x)
        d4 = 40.0
        d5 = d4 - 2.0
        d8 = d4 - 4.0
        d9 = 20.0 - 4.0
        pta1 = (xx + 0.9 * scale1, vpos(datum - d8 * scale1))
        pta2 = (xx + 0.9 * scale1, vpos(datum - d9 * scale1))
        if screen:
            text = font.render(b2, True, BLACK)
            text = pygame.transform.rotate(text, 90)
            screen.blit(text, (pta2[0], pta2[1] - 20))
        if doc:
            msp = doc.modelspace()
            msp.add_text(b2, dxfattribs={'height': 2.5, 'rotation': 90}).set_placement((pta2[0], pta2[1] - 5))
        if pdf:
            pdf.saveState()
            pdf.translate(pta2[0]/mm, (pta2[1] - 5)/mm)
            pdf.rotate(90)
            pdf.drawString(0, 0, b2)
            pdf.restoreState()
        b = (x - left) % xincr
        if b != 0.0:
            if screen:
                text = font.render(b1, True, BLACK)
                text = pygame.transform.rotate(text, 90)
                screen.blit(text, (pta1[0], pta1[1] - 20))
            if doc:
                msp.add_text(b1, dxfattribs={'height': 2.5, 'rotation': 90}).set_placement((pta1[0], pta1[1] - 5))
            if pdf:
                pdf.saveState()
                pdf.translate(pta1[0]/mm, (pta1[1] - 5)/mm)
                pdf.rotate(90)
                pdf.drawString(0, 0, b1)
                pdf.restoreState()
            pta1 = (xx, vpos(datum - d4 * scale1))
            pta2 = (xx, vpos(datum - d5 * scale1))
            if screen:
                pygame.draw.line(screen, GRAY, pta1, pta2, 1)
            if doc:
                msp.add_line(pta1, pta2)
            if pdf:
                pdf.setLineWidth(1)
                pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)
        pta5 = (xx, vpos(datum - 2 * scale1))
        pta6 = (xx, vpos(datum))
        if screen:
            pygame.draw.line(screen, BLACK, pta5, pta6, 1)
        if doc:
            msp.add_line(pta5, pta6)
        if pdf:
            pdf.setLineWidth(1)
            pdf.line(pta5[0]/mm, pta5[1]/mm, pta6[0]/mm, pta6[1]/mm)
        ptb4 = pt(x, y)
        if a > 1:
            if screen:
                pygame.draw.line(screen, BLACK, ptb3, ptb4, 2)
            if doc:
                msp.add_line(ptb3, ptb4)
            if pdf:
                pdf.setLineWidth(2)
                pdf.line(ptb3[0]/mm, ptb3[1]/mm, ptb4[0]/mm, ptb4[1]/mm)
        ptb3 = ptb4

def pier(screen=None, doc=None, pdf=None):
    yc = datum - 30.0
    plan_y_offset = 400
    if doc or pdf:
        plan_y_offset = 400 * 1000 / vvs

    # Elevation: Superstructure
    x1 = hpos(span1)
    y1 = vpos(RTL)
    x2 = hpos(spane)
    y2 = vpos(Sofl)
    pta1 = (x1 + (25 * 1000 / hhs if doc or pdf else 25), y1)
    pta2 = (x2 - (25 * 1000 / hhs if doc or pdf else 25), y2)
    if screen:
        pygame.draw.rect(screen, BLACK, (pta1[0], min(pta1[1], pta2[1]), pta2[0] - pta1[0], abs(pta2[1] - pta1[1])), 1)
    if doc:
        msp = doc.modelspace()
        msp.add_lwpolyline([pta1, (pta2[0], pta1[1]), pta2, (pta1[0], pta2[1]), pta1], close=True)
    if pdf:
        pdf.setLineWidth(1)
        pdf.rect(pta1[0]/mm, min(pta1[1], pta2[1])/mm, (pta2[0] - pta1[0])/mm, abs(pta2[1] - pta1[1])/mm, stroke=1, fill=0)

    # Elevation: Pier cap
    capwsq = capw / c if c != 0 else capw
    x1 = spane - capwsq / 2
    x2 = x1 + capwsq
    y1 = capt
    y2 = capb
    pta1 = pt(x1, y1)
    pta2 = pt(x2, y2)
    if screen:
        pygame.draw.rect(screen, BLACK, (pta1[0], min(pta1[1], pta2[1]), pta2[0] - pta1[0], abs(pta2[1] - pta2[1])), 1)
    if doc:
        msp.add_lwpolyline([pta1, (pta2[0], pta1[1]), pta2, (pta1[0], pta2[1]), pta1], close=True)
    if pdf:
        pdf.setLineWidth(1)
        pdf.rect(pta1[0]/mm, min(pta1[1], pta2[1])/mm, (pta2[0] - pta1[0])/mm, abs(pta2[1] - pta2[1])/mm, stroke=1, fill=0)

    # Elevation: Pier
    piertwsq = piertw / c if c != 0 else piertw
    x1 = spane - piertwsq / 2
    x3 = x1 + piertwsq
    y2 = futrl + futd
    ofset = (capb - y2) / battr
    ofsetsq = ofset / c if c != 0 else ofset
    x2 = x1 - ofsetsq
    x4 = x3 + ofsetsq
    y4 = y2
    pta1 = pt(x1, capb)
    pta2 = pt(x2, y2)
    pta3 = pt(x3, capb)
    pta4 = pt(x4, y4)
    if screen:
        pygame.draw.line(screen, BLACK, pta1, pta2, 2)
        pygame.draw.line(screen, BLACK, pta3, pta4, 2)
    if doc:
        msp.add_line(pta1, pta2)
        msp.add_line(pta3, pta4)
    if pdf:
        pdf.setLineWidth(2)
        pdf.line(pta1[0]/mm, pta1[1]/mm, pta2[0]/mm, pta2[1]/mm)
        pdf.line(pta3[0]/mm, pta3[1]/mm, pta4[0]/mm, pta4[1]/mm)

    # Elevation: Footing
    futwsq = futw / c if c != 0 else futw
    x5 = spane - futwsq / 2
    x6 = x5 + futwsq
    y6 = futrl
    y5 = y4
    pta5 = pt(x5, y5)
    pta6 = pt(x6, y6)
    if screen:
        pygame.draw.rect(screen, BLACK, (pta5[0], min(pta5[1], pta6[1]), pta6[0] - pta5[0], abs(pta6[1] - pta5[1])), 1)
    if doc:
        msp.add_lwpolyline([pta5, (pta6[0], pta5[1]), pta6, (pta5[0], pta6[1]), pta5], close=True)
    if pdf:
        pdf.setLineWidth(1)
        pdf.rect(pta5[0]/mm, min(pta5[1], pta6[1])/mm, (pta6[0] - pta5[0])/mm, abs(pta6[1] - pta5[1])/mm, stroke=1, fill=0)

    # Plan: Footing
    x7 = spane - futw / 2
    x8 = x7 + futw
    y7 = yc + futl / 2
    y8 = y7 - futl
    pta7 = pt(x7, y7)
    pta8 = pt(x8, y8)
    rect_points = [pta7, (pta7[0], pta8[1]), pta8, (pta8[0], pta7[1])]
    center = pt(spane, yc)
    rotated_points = [rotate_point(p, center, skew) for p in rect_points]
    if screen:
        pygame.draw.polygon(screen, BLACK, [(p[0], p[1] + plan_y_offset) for p in rotated_points], 1)
    if doc:
        msp.add_lwpolyline([(p[0], p[1] + plan_y_offset) for p in rotated_points], close=True)
    if pdf:
        pdf.setLineWidth(1)
        path = pdf.beginPath()
        for i, p in enumerate(rotated_points):
            x, y = p[0]/mm, (p[1] + plan_y_offset)/mm
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.close()
        pdf.drawPath(path, stroke=1, fill=0)

    # Plan: Pier
    pierstsq = pierst / c + abs(piertw * tn) if c != 0 else pierst
    x1 = spane - piertw / 2
    x3 = x1 + piertw
    x2 = x1 - ofset
    x4 = x3 + ofset
    y9 = yc + pierstsq / 2
    y10 = y9 - pierstsq
    pta9 = pt(x2, y9)
    pta10 = pt(x2, y10)
    pta11 = pt(x1, y9)
    pta12 = pt(x1, y10)
    pta13 = pt(x3, y9)
    pta14 = pt(x3, y10)
    pta15 = pt(x4, y9)
    pta16 = pt(x4, y10)
    lines = [(pta9, pta10), (pta11, pta12), (pta13, pta14), (pta15, pta16)]
    y17 = y9 + piertw / 2
    y18 = y17 + ofset
    y19 = y10 - piertw / 2
    y20 = y19 - ofset
    pta17 = pt(spane, y17)
    pta18 = pt(spane, y18)
    pta19 = pt(spane, y19)
    pta20 = pt(spane, y20)
    arcs = [(pta9, pta18, pta15), (pta11, pta17, pta13), (pta12, pta19, pta14), (pta10, pta20, pta16)]
    for start, mid, end in arcs:
        start = rotate_point(start, center, skew)
        end = rotate_point(end, center, skew)
        if screen:
            pygame.draw.line(screen, BLACK, (start[0], start[1] + plan_y_offset), (end[0], end[1] + plan_y_offset), 1)
        if doc:
            msp.add_line((start[0], start[1] + plan_y_offset), (end[0], end[1] + plan_y_offset))
        if pdf:
            pdf.setLineWidth(1)
            pdf.line(start[0]/mm, (start[1] + plan_y_offset)/mm, end[0]/mm, (end[1] + plan_y_offset)/mm)
    for p1, p2 in lines:
        p1 = rotate_point(p1, center, skew)
        p2 = rotate_point(p2, center, skew)
        if screen:
            pygame.draw.line(screen, BLACK, (p1[0], p1[1] + plan_y_offset), (p2[0], p2[1] + plan_y_offset), 1)
        if doc:
            msp.add_line((p1[0], p1[1] + plan_y_offset), (p2[0], p2[1] + plan_y_offset))
        if pdf:
            pdf.setLineWidth(1)
            pdf.line(p1[0]/mm, (p1[1] + plan_y_offset)/mm, p2[0]/mm, (p2[1] + plan_y_offset)/mm)

def abt1(screen=None, doc=None, pdf=None):
    plan_y_offset = 400 if screen else 400 * 1000 / vvs
    yc = datum - 30.0

    # Elevation
    x1 = abtl
    alcwsq = alcw
    x3 = x1 + alcwsq
    capb = capt - alcd
    p1 = (capb - alfbl) / alfb
    p1sq = p1
    x5 = x3 + p1sq
    p2 = (alfbl - altbl) / altb
    p2sq = p2
    x6 = x5 + p2sq
    alfosq = alfo
    x7 = x6 + alfosq
    y8 = altbl - alfd
    dwthsq = dwth
    x14 = x1 - dwthsq
    p3 = (capb - albbl) / albb
    p3sq = p3
    x12 = x14 - p3sq
    x10 = x12 - alfosq
    pt1 = pt(x1, RTL)
    pt2 = pt(x1, capt)
    pt3 = pt(x3, capt)
    pt4 = pt(x3, capb)
    pt5 = pt(x5, alfbl)
    pt6 = pt(x6, altbl)
    pt7 = pt(x7, altbl)
    pt8 = pt(x7, y8)
    pt9 = pt(x10, y8)
    pt10 = pt(x10, altbl)
    pt11 = pt(x12, altbl)
    pt12 = pt(x12, albbl)
    pt13 = pt(x14, capb)
    pt14 = pt(x14, RTL)
    pt15 = pt(x12, RTL)
    points = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8, pt9, pt10, pt11, pt12, pt13, pt14, pt1]
    if screen:
        pygame.draw.polygon(screen, BLACK, points, 1)
        pygame.draw.line(screen, BLACK, pt13, pt4, 1)
        pygame.draw.line(screen, BLACK, pt10, pt7, 1)
        pygame.draw.line(screen, BLACK, pt12, pt15, 1)
        pygame.draw.line(screen, BLACK, pt15, pt14, 1)
    if doc:
        msp = doc.modelspace()
        msp.add_lwpolyline(points, close=True)
        msp.add_line(pt13, pt4)
        msp.add_line(pt10, pt7)
        msp.add_line(pt12, pt15)
        msp.add_line(pt15, pt14)
    if pdf:
        pdf.setLineWidth(1)
        path = pdf.beginPath()
        for i, p in enumerate(points):
            if i == 0:
                path.moveTo(p[0]/mm, p[1]/mm)
            else:
                path.lineTo(p[0]/mm, p[1]/mm)
        path.close()
        pdf.drawPath(path, stroke=1, fill=0)
        pdf.line(pt13[0]/mm, pt13[1]/mm, pt4[0]/mm, pt4[1]/mm)
        pdf.line(pt10[0]/mm, pt10[1]/mm, pt7[0]/mm, pt7[1]/mm)
        pdf.line(pt12[0]/mm, pt12[1]/mm, pt15[0]/mm, pt15[1]/mm)
        pdf.line(pt15[0]/mm, pt15[1]/mm, pt14[0]/mm, pt14[1]/mm)

    # Plan
    y20 = yc + abtlen / 2
    y21 = y20 - abtlen
    y16 = y20 + 0.15
    y17 = y21 - 0.15
    footl = (y16 - y17) / 2
    x = footl * s
    y = footl * (1 - c)
    pt16 = pt(x10 - x, y16 - y)
    pt17 = pt(x10 + x, y17 + y)
    pt18 = pt(x7 - x, y16 - y)
    pt19 = pt(x7 + x, y17 + y)
    center = pt((x10 + x7) / 2, yc)
    rect_points = [pt16, pt17, pt19, pt18]
    rotated_points = [rotate_point(p, center, skew) for p in rect_points]
    if screen:
        pygame.draw.polygon(screen, BLACK, [(p[0], p[1] + plan_y_offset) for p in rotated_points], 1)
    if doc:
        msp.add_lwpolyline([(p[0], p[1] + plan_y_offset) for p in rotated_points], close=True)
    if pdf:
        pdf.setLineWidth(1)
        path = pdf.beginPath()
        for i, p in enumerate(rotated_points):
            x, y = p[0]/mm, (p[1] + plan_y_offset)/mm
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.close()
        pdf.drawPath(path, stroke=1, fill=0)

    xx = abtlen / 2
    x = xx * s
    y = xx * (1 - c)
    y20 -= y
    y21 += y
    pt20 = pt(x12 - x, y20)
    pt21 = pt(x12 + x, y21)
    pt22 = pt(x14 - x, y20)
    pt23 = pt(x14 + x, y21)
    pt24 = pt(x1 - x, y20)
    pt25 = pt(x1 + x, y21)
    pt26 = pt(x3 - x, y20)
    pt27 = pt(x3 + x, y21)
    pt28 = pt(x5 - x, y20)
    pt29 = pt(x5 + x, y21)
    pt30 = pt(x6 - x, y20)
    pt31 = pt(x6 + x, y21)
    lines = [(pt20, pt21), (pt22, pt23), (pt24, pt25), (pt26, pt27), (pt28, pt29), (pt30, pt31), (pt21, pt31), (pt20, pt30)]
    for p1, p2 in lines:
        p1 = rotate_point(p1, center, skew)
        p2 = rotate_point(p2, center, skew)
        if screen:
            pygame.draw.line(screen, BLACK, (p1[0], p1[1] + plan_y_offset), (p2[0], p2[1] + plan_y_offset), 1)
        if doc:
            msp.add_line((p1[0], p1[1] + plan_y_offset), (p2[0], p2[1] + plan_y_offset))
        if pdf:
            pdf.setLineWidth(1)
            pdf.line(p1[0]/mm, (p1[1] + plan_y_offset)/mm, p2[0]/mm, (p2[1] + plan_y_offset)/mm)

def setup():
    global scale1, scale2, skew, datum, toprl, left, right, xincr, yincr, noch, cs_data
    if input_data and len(input_data) >= 10:
        try:
            scale1 = float(input_data[0])
            scale2 = float(input_data[1])
            skew = float(input_data[2])
            datum = float(input_data[3])
            toprl = float(input_data[4])
            left = float(input_data[5])
            right = float(input_data[6])
            xincr = float(input_data[7])
            yincr = float(input_data[8])
            noch = int(input_data[9])
            cs_data = []
            for i in range(10, len(input_data)):
                x, y = map(float, input_data[i].split(","))
                cs_data.append((x, y))
        except (ValueError, IndexError):
            pass
    init_derived()
    screen.fill(WHITE)
    layout(screen=screen)
    cs(screen=screen)
    pier(screen=screen)
    abt1(screen=screen)

def save_dxf():
    doc = ezdxf.new(dxfversion='R2010')
    layout(doc=doc)
    cs(doc=doc)
    pier(doc=doc)
    abt1(doc=doc)
    doc.saveas("bridge_output.dxf")

def save_pdf():
    pdf = canvas.Canvas("bridge_output.pdf", pagesize=(1200/mm, 800/mm))
    layout(pdf=pdf)
    cs(pdf=pdf)
    pier(pdf=pdf)
    abt1(pdf=pdf)
    pdf.showPage()
    pdf.save()

def handle_input(event):
    global input_mode, input_text, input_field, input_data
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            if input_text:
                input_data.append(input_text)
                input_text = ""
                input_field += 1
                if input_field == 10 and input_data[-1].lower() == "done":
                    input_mode = False
                    setup()
            if input_field >= len(input_labels):
                input_mode = False
                setup()
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
        elif event.unicode.isprintable():
            input_text += event.unicode

def render_input_screen():
    """Render the input screen."""
    screen.fill(WHITE)
    
    # Title
    title_text = font.render("Bridge GAD Generator - Input Mode", True, BLACK)
    screen.blit(title_text, (50, 50))
    
    # Current input field
    if input_field < len(input_labels):
        label = input_labels[input_field]
        text = font.render(f"{label}{input_text}", True, BLACK)
        screen.blit(text, (50, 100))
    
    # Display entered data
    y_offset = 150
    for i, data in enumerate(input_data):
        if i < 15:  # Limit display to avoid overflow
            text = font.render(f"{i+1}: {data}", True, GRAY)
            screen.blit(text, (50, y_offset))
            y_offset += 25

def render_drawing():
    """Render the bridge drawing."""
    screen.fill(WHITE)
    
    # Draw the bridge components
    init_derived()
    layout(screen=screen)
    cs(screen=screen)
    pier(screen=screen)
    abt1(screen=screen)
    
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

def update_loop():
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
                elif event.key == pygame.K_d and platform.system() != "Emscripten":
                    save_dxf()
                elif event.key == pygame.K_p and platform.system() != "Emscripten":
                    save_pdf()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom = min(max_zoom, zoom * 1.1)
                    init_derived()
                elif event.button == 5:
                    zoom = max(min_zoom, zoom / 1.1)
                    init_derived()
                elif event.button == 1:
                    mouse_dragging = True
                    start_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION and mouse_dragging:
                pan_x = start_pan_x + (event.pos[0] - start_pos[0])
                pan_y = start_pan_y + (event.pos[1] - start_pos[1])
    # Proper rendering logic here
    if input_mode:
        render_input_screen()
    else:
        render_drawing()
    
    pygame.display.flip()
    clock.tick(FPS)
    return True

async def main():
    setup()
    running = True
    while running:
        running = update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())

