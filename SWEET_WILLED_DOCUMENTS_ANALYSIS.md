# SweetWilledDocument Files Analysis

## Overview

This document provides an analysis of all SweetWilledDocument files available in the BridgeGAD-00 project, detailing their parameters and variations.

## File List

1. SweetWilledDocument-01.xlsx
2. SweetWilledDocument-02.xlsx
3. SweetWilledDocument-03.xlsx
4. SweetWilledDocument-04.xlsx
5. SweetWilledDocument-07.xlsx
6. SweetWilledDocument-08.xlsx
7. SweetWilledDocument-09.xlsx
8. SweetWilledDocument-10.xlsx

## Parameter Analysis

### Common Parameters Across Files

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| SCALE1 | Plan/elevation scale | 100-250 |
| SCALE2 | Section scale | 50-200 |
| SKEW | Skew angle in degrees | 0-30 |
| DATUM | Datum level (m) | 90-100 |
| LEFT | Left chainage (m) | 0 |
| RIGHT | Right chainage (m) | 20-80 |
| XINCR | X increment for chainage (m) | 5-20 |
| YINCR | Y increment for levels (m) | 1-3 |
| NSPAN | Number of spans | 1-5 |
| SPAN1 | Span length (m) | 15-20 |
| LBRIDGE | Total bridge length (m) | 20-80 |
| ABTL | Abutment left position (m) | 0 |
| RTL | Road top level (m) | 105-120 |
| SOFL | Soffit level (m) | 102-115 |
| CCBR | Carriageway width (m) | 7.5-14 |
| KERBW | Kerb width (m) | 0.3-0.35 |
| KERBD | Kerb depth (m) | 0.2-0.25 |
| SLBTHE | Slab thickness at edge (m) | 0.15-0.9 |
| APTHK | Approach slab thickness (m) | 0.2-0.45 |
| LASLAB | Length of approach slab (m) | 4-5 |
| WCTH | Wearing course thickness (m) | 0.075-0.12 |
| CAPT | Cap top level (m) | 104-118 |
| CAPB | Cap bottom level (m) | 102.5-115.5 |
| CAPW | Cap width (m) | 1.0-2.0 |
| PIERTW | Pier thickness width (m) | 1.0-2.0 |
| PIERST | Pier thickness length (m) | 8-18 |
| BATTR | Batter ratio | 6-15 |
| PIERN | Pier number | 1 |
| FUTRL | Foundation level (m) | 90-95 |
| FUTD | Foundation depth (m) | 1.0-2.5 |
| FUTW | Foundation width (m) | 3.0-6.0 |
| FUTL | Foundation length (m) | 6-12 |
| ABTLEN | Abutment length (m) | 15-18 |
| APWTH | Approach width (m) | 15-18 |
| DWTH | Dirt wall thickness (m) | 0.3-0.5 |
| ALCW | Abutment left cap width (m) | 1.0-1.2 |
| ALCD | Abutment left cap depth (m) | 1.0-2.0 |
| ALFB | Abutment left front batter | 10-15 |
| ALFBL | Abutment left front batter level (m) | 101-103 |
| ALTB | Abutment left toe batter | 10-15 |
| ALTBL | Abutment left toe batter level (m) | 100.5-101.5 |
| ALFO | Abutment left front offset (m) | 0.5-1.0 |
| ALFD | Abutment left footing depth (m) | 1.0-2.5 |
| ALBB | Abutment left back batter | 6-8 |
| ALBBL | Abutment left back batter level (m) | 101.5-103.5 |
| ALFL | Abutment left footing level (m) | 90-95 |
| ARFL | Abutment right footing level (m) | 91-96 |
| ALFBR | Abutment left front batter right | 96-102.5 |
| ALTBR | Abutment left toe batter right | 101-101.5 |
| ALBBR | Abutment left back batter right | 102.5-103.5 |

## File-Specific Observations

### SweetWilledDocument-01.xlsx
- Simple parameter format with Parameter,Value,Description structure
- Basic bridge parameters for a small slab bridge
- Span length: 20.0m
- Deck width: 7.5m

### SweetWilledDocument-02.xlsx
- Detailed engineering parameters format with Value,Variable,Description structure
- More comprehensive parameter set
- Span length: 15m
- Bridge length: 60m
- 4 spans

### SweetWilledDocument-03.xlsx
- Extended parameter set with larger bridge dimensions
- Span length: 16m
- Bridge length: 80m
- 5 spans
- Increased foundation dimensions

### SweetWilledDocument-04.xlsx to SweetWilledDocument-10.xlsx
- Similar parameter structure to files 2 and 3
- Varying bridge dimensions and configurations
- Different skew angles and scale factors

## Key Parameter Relationships

### Span Configuration
- LBRIDGE = SPAN1 × NSPAN (for equal spans)
- ABTL = 0 (typically)
- RIGHT = LEFT + LBRIDGE

### Structural Dimensions
- CAPT ≈ RTL - small offset
- CAPB ≈ CAPT - cap thickness
- SOFL ≈ CAPB - pier dimensions
- FUTRL = foundation level (typically below datum)

### Geometry Relationships
- ABTLEN = CCBR + 2×KERBW (abutment length)
- Pier dimensions relate to load requirements
- Skew angle affects plan geometry calculations

## Usage Guidelines

1. **File Format**: All files are actually CSV format despite .xlsx extension
2. **Loading**: Use appropriate CSV parsing methods
3. **Validation**: Check parameter consistency (e.g., LBRIDGE vs NSPAN×SPAN1)
4. **Units**: All dimensions in meters unless otherwise specified
5. **Coordinate System**: Based on datum level and chainage system

## Validation Rules

1. SPAN1 > 0
2. CCBR > 0
3. 0 ≤ SKEW ≤ 45 degrees
4. FUTRL < CAPB (foundation below cap)
5. SOFL < CAPB (soffit below cap)
6. RTL > SOFL (road above soffit)

This analysis provides a comprehensive overview of the parameter variations across the SweetWilledDocument files, enabling proper handling and validation in the BridgeGAD application.