import pandas as pd

# Create LARGE SKEWED BRIDGE parameters - showcase full capabilities
data = [
    [150, "SCALE1", "Scale1 - Drawing scale for plans and elevations"],
    [100, "SCALE2", "Scale2 - Drawing scale for sections"],
    [25.00, "SKEW", "Degree Of Skew In Plan Of The Bridge"],  # Large skew
    [90.00, "DATUM", "Datum level for the drawing"],  
    [115.50, "TOPRL", "Top RL Of The Bridge"],  # High bridge
    [0.00, "LEFT", "Left Most Chainage Of The Bridge"],
    [120.00, "RIGHT", "Right Most Chainage Of The Bridge"],  # Very long bridge
    [15.00, "XINCR", "Chainage Increment In X Direction"],  
    [2.00, "YINCR", "Elevation Increment In Y Direction"], # Coarser grid
    [9, "NOCH", "Total No. Of Chainages On C/S"],  
    [5, "NSPAN", "Number of Spans"],  # 5 spans
    [120.00, "LBRIDGE", "Length Of Bridge"],  # 120m total
    [0.00, "ABTL", "Read Chainage Of Left Abutment"],
    [115.50, "RTL", "Road Top Level"],  
    [113.00, "SOFL", "Soffit Level"],  # 2.5m depth
    [0.40, "KERBW", "Width Of Kerb At Deck Top"],  # Large kerb
    [0.35, "KERBD", "Depth Of Kerb Above Deck Top"],  
    [18.00, "CCBR", "Clear Carriageway Width Of Bridge"],  # Wide carriageway
    [1.50, "SLBTHC", "Thickness Of Slab At Centre"],  # Very thick slab
    [1.20, "SLBTHE", "Thickness Of Slab At Edge"],  
    [1.00, "SLBTHT", "Thickness Of Slab At Tip"],  
    [113.00, "CAPT", "Pier Cap Top RL"],  
    [112.00, "CAPB", "Pier Cap Bottom RL = Pier Top"],  # Thick cap
    [2.00, "CAPW", "Cap Width"],  # Wide cap
    [2.00, "PIERTW", "Pier Top Width"],  # Wide pier
    [15.00, "BATTR", "Pier Batter"],  # Steep batter
    [20.00, "PIERST", "Straight Length Of Pier"],  # Long pier
    [1.00, "PIERN", "Sr No Of Pier"],
    [24.00, "SPAN1", "Span Individual Length"],  # 24m spans
    [85.00, "FUTRL", "Founding RL Of Pier Found"],  # Deep founding
    [2.50, "FUTD", "Depth Of Footing"],  # Deep footing
    [8.00, "FUTW", "Width Of Rect Footing"],  # Large footing
    [20.00, "FUTL", "Length Of Footing Along Current Direction"], 
    [20.00, "ABTLEN", "Length Of Abutment Along Current Direction at cap level"],  
    [0.60, "DWTH", "Dirtwall Thickness"],  # Thick dirtwall
    [1.50, "ALCW", "Abutment Left Cap Width Excluding D/W"],  
    [2.00, "ALCD", "Abutment Left Cap Depth"],  # Deep cap
    [6.00, "ALFB", "Abt Left Front Batter (1 HOR : 6 VER)"],  # Steep
    [95.00, "ALFBL", "Abt Left Front Batter RL"],  
    [94.50, "ALFBR", "Abt RIGHT Front Batter RL"],  
    [4.00, "ALTB", "Abt Left Toe Batter (1 HOR : 4 VER)"],  # Very steep
    [95.00, "ALTBL", "Abt Left Toe Batter Level Footing Top"],  
    [94.50, "ALTBR", "Abt RIGHT Toe Batter Level Footing Top"],  
    [3.00, "ALFO", "Abutment Left Front Offset To Footing"],  # Large offset
    [2.00, "ALFD", "Abt Left Footing Depth"],  # Deep footing
    [3.00, "ALBB", "Abt Left Back Batter"],  
    [95.00, "ALBBL", "Abt Left Back Batter RL"],  
    [94.50, "ALBBR", "Abt RIGHT Back Batter RL"],  
    [5.00, "LASLAB", "Length of approach slab"],  # Long approach
    [20.00, "APWTH", "Width of approach slab"],  # Wide approach
    [0.60, "APTHK", "Thickness of approach slab"],  # Thick approach
    [0.15, "WCTH", "Thickness of wearing course"]  # Thick wearing course
]

# Create DataFrame
df = pd.DataFrame(data, columns=['Value', 'Variable', 'Description'])

# Save to Excel
df.to_excel('large_bridge.xlsx', index=False, header=False)
print("Large bridge parameters created: large_bridge.xlsx")
print("SHOWCASE FEATURES:")
print("- 25° skew bridge (major skew)")
print("- 5 spans of 24m each = 120m total length")
print("- 18m wide carriageway (highway standard)")
print("- 1.5m thick deck slab (heavy duty)")
print("- 2.5m deep superstructure")
print("- Large piers and footings for major bridge")
print("- Deep founding level (85m RL)")
print("- Professional highway bridge proportions")
