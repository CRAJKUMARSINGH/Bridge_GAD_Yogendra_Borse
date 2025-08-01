import pandas as pd

# Create the Excel file with required Lisp parameters
data = {
    'Parameter': [
        'LBRIDGE',    # Total bridge length
        'NSPAN',      # Number of spans
        'SPAN1',      # Length of span 1
        'SPAN2',      # Length of span 2
        'CCBR',       # Carriageway width
        'TOPRL',      # Top road level
        'SOFL',       # Soffit level
        'KERBW',      # Kerb width
        'KERBD',      # Kerb depth
        'CAPW',       # Cap width
        'FUTW',       # Footing width
        'FUTL',       # Footing length
        'FUTD',       # Footing depth
        'LASLAB'      # Approach slab length
    ],
    'Value': [
        20.0,  # LBRIDGE: Total bridge length
        2,     # NSPAN: Number of spans
        10.0,  # SPAN1: Length of span 1
        10.0,  # SPAN2: Length of span 2
        12.0,  # CCBR: Carriageway width
        100.0, # TOPRL: Top road level
        98.5,  # SOFL: Soffit level
        0.3,   # KERBW: Kerb width
        0.2,   # KERBD: Kerb depth
        1.2,   # CAPW: Cap width
        1.8,   # FUTW: Footing width
        10.0,  # FUTL: Footing length
        0.5,   # FUTD: Footing depth
        3.0    # LASLAB: Approach slab length
    ],
    'Units': ['m', '', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm']
}

# Create DataFrame and save to Excel
df = pd.DataFrame(data)
df.to_excel('lisp_params.xlsx', index=False)
print("Created lisp_params.xlsx with required Lisp bridge parameters")
