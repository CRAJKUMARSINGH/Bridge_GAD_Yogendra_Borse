import pandas as pd

# Create MODIFIED bridge parameters - different from the original
data = [
    [100, "SCALE1", "Scale1 - Drawing scale for plans and elevations"],
    [50, "SCALE2", "Scale2 - Drawing scale for sections"],
    [15.00, "SKEW", "Degree Of Skew In Plan Of The Bridge"],  # Modified: Added skew
    [95.00, "DATUM", "Datum level for the drawing"],  # Modified: Lower datum
    [108.50, "TOPRL", "Top RL Of The Bridge"],  # Modified: Lower bridge
    [0.00, "LEFT", "Left Most Chainage Of The Bridge"],
    [60.00, "RIGHT", "Right Most Chainage Of The Bridge"],  # Modified: Longer bridge
    [12.00, "XINCR", "Chainage Increment In X Direction"],  # Modified: Different increment
    [1.00, "YINCR", "Elevation Increment In Y Direction"],
    [16, "NOCH", "Total No. Of Chainages On C/S"],  # Modified: Different count
    [3, "NSPAN", "Number of Spans"],  # Modified: 3 spans instead of 4
    [60.00, "LBRIDGE", "Length Of Bridge"],  # Modified: 60m bridge
    [0.00, "ABTL", "Read Chainage Of Left Abutment"],
    [108.50, "RTL", "Road Top Level"],  # Modified: Match TOPRL
    [107.50, "SOFL", "Soffit Level"],  # Modified: 1m depth
    [0.30, "KERBW", "Width Of Kerb At Deck Top"],  # Modified: Wider kerb
    [0.30, "KERBD", "Depth Of Kerb Above Deck Top"],  # Modified: Deeper kerb
    [14.00, "CCBR", "Clear Carriageway Width Of Bridge"],  # Modified: Wider carriageway
    [1.20, "SLBTHC", "Thickness Of Slab At Centre"],  # Modified: Thicker slab
    [1.00, "SLBTHE", "Thickness Of Slab At Edge"],  # Modified: Thicker edge
    [0.90, "SLBTHT", "Thickness Of Slab At Tip"],  # Modified: Thicker tip
    [107.50, "CAPT", "Pier Cap Top RL"],  # Modified: Match soffit
    [106.80, "CAPB", "Pier Cap Bottom RL = Pier Top"],  # Modified: Thicker cap
    [1.50, "CAPW", "Cap Width"],  # Modified: Wider cap
    [1.50, "PIERTW", "Pier Top Width"],  # Modified: Wider pier
    [12.00, "BATTR", "Pier Batter"],  # Modified: Steeper batter
    [15.00, "PIERST", "Straight Length Of Pier"],  # Modified: Longer pier
    [1.00, "PIERN", "Sr No Of Pier"],
    [20.00, "SPAN1", "Span Individual Length"],  # Modified: 20m spans
    [92.00, "FUTRL", "Founding RL Of Pier Found"],  # Modified: Lower founding
    [1.50, "FUTD", "Depth Of Footing"],  # Modified: Deeper footing
    [6.00, "FUTW", "Width Of Rect Footing"],  # Modified: Wider footing
    [15.00, "FUTL", "Length Of Footing Along Current Direction"],  # Modified: Longer
    [15.00, "ABTLEN", "Length Of Abutment Along Current Direction at cap level"],  # Modified
    [0.40, "DWTH", "Dirtwall Thickness"],  # Modified: Thicker dirtwall
    [1.00, "ALCW", "Abutment Left Cap Width Excluding D/W"],  # Modified: Wider
    [1.50, "ALCD", "Abutment Left Cap Depth"],  # Modified: Deeper
    [8.00, "ALFB", "Abt Left Front Batter (1 HOR : 8 VER)"],  # Modified: Steeper
    [98.00, "ALFBL", "Abt Left Front Batter RL"],  # Modified: Lower
    [97.75, "ALFBR", "Abt RIGHT Front Batter RL"],  # Modified: Lower
    [6.00, "ALTB", "Abt Left Toe Batter (1 HOR : 6 VER)"],  # Modified: Steeper
    [98.00, "ALTBL", "Abt Left Toe Batter Level Footing Top"],  # Modified: Lower
    [97.75, "ALTBR", "Abt RIGHT Toe Batter Level Footing Top"],  # Modified: Lower
    [2.00, "ALFO", "Abutment Left Front Offset To Footing"],  # Modified: Larger offset
    [1.50, "ALFD", "Abt Left Footing Depth"],  # Modified: Deeper
    [4.00, "ALBB", "Abt Left Back Batter"],  # Modified: Steeper
    [98.00, "ALBBL", "Abt Left Back Batter RL"],  # Modified: Lower
    [97.75, "ALBBR", "Abt RIGHT Back Batter RL"],  # Modified: Lower
    [4.00, "LASLAB", "Length of approach slab"],  # Modified: Longer
    [15.00, "APWTH", "Width of approach slab"],  # Modified: Wider
    [0.50, "APTHK", "Thickness of approach slab"],  # Modified: Thicker
    [0.10, "WCTH", "Thickness of wearing course"]  # Modified: Thicker
]

# Create DataFrame
df = pd.DataFrame(data, columns=['Value', 'Variable', 'Description'])

# Save to Excel
df.to_excel('modified_bridge.xlsx', index=False, header=False)
print("Modified bridge parameters created: modified_bridge.xlsx")
print("Key modifications:")
print("- 15° skew bridge (was 0°)")
print("- 3 spans of 20m each (was 4 spans of 10.8m)")
print("- Total length: 60m (was 43.2m)")
print("- Wider carriageway: 14m (was 11.1m)")
print("- Thicker deck slab: 1.2m center (was 0.9m)")
print("- Steeper pier batter and larger footings")
print("- Different scale ratios for more detailed sections")
