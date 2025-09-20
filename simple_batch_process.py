#!/usr/bin/env python3
"""
Simple batch processing script for all SweetWilledInputFile files
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def process_file(filename, file_index):
    """Process a single SweetWilledInputFile and generate outputs."""
    try:
        # Import the main application
        import simple_bridge_app
        
        print(f"Processing {filename}...")
        
        # Load parameters from CSV file
        if simple_bridge_app.load_bridge_parameters_from_csv(filename):
            print(f"  ✓ Loaded parameters from {filename}")
            
            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Generate DXF output
            print(f"  Generating DXF output...")
            simple_bridge_app.save_dxf()
            
            # Find and rename the generated DXF file
            dxf_files = list(Path('.').glob('enhanced_bridge_*.dxf'))
            if dxf_files:
                latest_dxf = max(dxf_files, key=os.path.getctime)
                new_dxf_name = f"bridge_drawing_{file_index:02d}_{timestamp}.dxf"
                os.rename(latest_dxf, new_dxf_name)
                print(f"  ✓ Generated DXF: {new_dxf_name}")
            
            # Generate PDF output
            print(f"  Generating PDF output...")
            simple_bridge_app.save_pdf()
            
            # Find and rename the generated PDF file
            pdf_files = list(Path('.').glob('simple_bridge_*.pdf'))
            if pdf_files:
                latest_pdf = max(pdf_files, key=os.path.getctime)
                new_pdf_name = f"bridge_drawing_{file_index:02d}_{timestamp}.pdf"
                os.rename(latest_pdf, new_pdf_name)
                print(f"  ✓ Generated PDF: {new_pdf_name}")
            
            return True
        else:
            print(f"  ✗ Failed to load parameters from {filename}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing {filename}: {e}")
        return False

def main():
    """Main function to process all files."""
    print("Bridge GAD Generator - Simple Batch Processing")
    print("=" * 50)
    
    # List of all SweetWilledInputFile files
    sweet_willed_files = [
        "SweetWilledInputFile-01.csv",
        "SweetWilledInputFile-02.csv", 
        "SweetWilledInputFile-03.csv",
        "SweetWilledInputFile-04.csv",
        "SweetWilledInputFile-05.csv",
        "SweetWilledInputFile-06.csv",
        "SweetWilledInputFile-07.csv",
        "SweetWilledInputFile-08.csv",
        "SweetWilledInputFile-09.csv",
        "SweetWilledInputFile-10.csv"
    ]
    
    # Create output directories
    dxf_dir = Path("DXF_OUTPUT")
    pdf_dir = Path("PDF_OUTPUT")
    dxf_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    
    processed_files = 0
    
    for i, filename in enumerate(sweet_willed_files, 1):
        if os.path.exists(filename):
            if process_file(filename, i):
                processed_files += 1
                # Move generated files to appropriate directories
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dxf_files = list(Path('.').glob(f'bridge_drawing_{i:02d}_*.dxf'))
                pdf_files = list(Path('.').glob(f'bridge_drawing_{i:02d}_*.pdf'))
                
                for dxf_file in dxf_files:
                    shutil.move(str(dxf_file), dxf_dir / dxf_file.name)
                    print(f"  Moved DXF to {dxf_dir / dxf_file.name}")
                
                for pdf_file in pdf_files:
                    shutil.move(str(pdf_file), pdf_dir / pdf_file.name)
                    print(f"  Moved PDF to {pdf_dir / pdf_file.name}")
        else:
            print(f"File not found: {filename}")
            # Create the missing file with default parameters
            create_default_input_file(filename)
            print(f"  Created default file: {filename}")
            if process_file(filename, i):
                processed_files += 1
                # Move generated files to appropriate directories
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dxf_files = list(Path('.').glob(f'bridge_drawing_{i:02d}_*.dxf'))
                pdf_files = list(Path('.').glob(f'bridge_drawing_{i:02d}_*.pdf'))
                
                for dxf_file in dxf_files:
                    shutil.move(str(dxf_file), dxf_dir / dxf_file.name)
                    print(f"  Moved DXF to {dxf_dir / dxf_file.name}")
                
                for pdf_file in pdf_files:
                    shutil.move(str(pdf_file), pdf_dir / pdf_file.name)
                    print(f"  Moved PDF to {pdf_dir / pdf_file.name}")
    
    print("\n" + "=" * 50)
    print(f"Batch processing complete!")
    print(f"Successfully processed {processed_files} files out of {len(sweet_willed_files)}")
    print(f"DXF files saved to: {dxf_dir}")
    print(f"PDF files saved to: {pdf_dir}")
    
    # Create a summary report
    create_summary_report(processed_files, sweet_willed_files)
    
    return 0 if processed_files > 0 else 1

def create_default_input_file(filename):
    """Create a default input file with sample parameters."""
    # Use parameters from existing files as template
    default_params = [
        "100.0,SCALE1,Scale factor for plan and elevation",
        "50.0,SCALE2,Scale factor for sections",
        "0.0,SKEW,Skew angle in degrees",
        "100.0,DATUM,Datum level",
        "110.0,TOPRL,Top level on Y axis",
        "0.0,LEFT,Starting chainage of X axis",
        "30.0,RIGHT,End chainage of X axis",
        "5.0,XINCR,Interval of distances on X axis",
        "1.0,YINCR,Interval of levels on Y axis",
        "6,NOCH,Total number of chainages",
        "1,NSPAN,Number of spans",
        "30.0,LBRIDGE,Length of bridge",
        "0.0,ABTL,Chainage of left abutment",
        "105.0,RTL,Road top level",
        "103.0,Sofl,Soffit level",
        "0.3,KERBW,Width of kerb",
        "0.2,KERBD,Depth of kerb",
        "7.5,CCBR,Clear carriageway width",
        "0.2,SLBTHC,Thickness of slab at center",
        "0.15,SLBTHE,Thickness of slab at edge",
        "0.1,SLBTHT,Thickness of slab at tip",
        "104.0,CAPT,Pier cap top RL",
        "103.5,CAPB,Pier cap bottom RL",
        "1.2,CAPW,Cap width",
        "1.0,PIERTW,Pier top width",
        "10.0,BATTR,Pier batter",
        "8.0,PIERST,Straight length of pier",
        "1,PIERN,Pier serial number",
        "30.0,SPAN1,Span individual length",
        "95.0,FUTRL,Founding RL",
        "1.0,FUTD,Depth of footing",
        "3.0,FUTW,Width of footing",
        "6.0,FUTL,Length of footing",
        "0.3,DWTH,Dirtwall thickness",
        "1.0,ALCW,Abutment left cap width",
        "1.0,ALCD,Abutment left cap depth",
        "10.0,ALFB,Abutment left front batter",
        "101.0,ALFBL,Abutment left front batter RL",
        "10.0,ALTB,Abutment left toe batter",
        "100.5,ALTBL,Abutment left toe batter level",
        "0.5,ALFO,Abutment left front offset",
        "1.0,ALFD,Abutment left footing depth",
        "8.0,ALBB,Abutment left back batter",
        "101.5,ALBBL,Abutment left back batter RL",
        "101.0,ALFBR,Abutment right front batter RL",
        "100.5,ALTBR,Abutment right toe batter level",
        "101.5,ALBBR,Abutment right back batter RL",
        "95.0,ARFL,Abutment right footing level"
    ]
    
    with open(filename, 'w') as f:
        f.write("Value,Variable,Description\n")
        for param in default_params:
            f.write(param + "\n")
    
    print(f"Created default input file: {filename}")


def create_summary_report(processed_count, file_list):
    """Create a simple summary report."""
    try:
        with open("PROCESSING_SUMMARY.txt", "w") as f:
            f.write("Bridge GAD Generator - Processing Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Processing completed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Files processed successfully: {processed_count}/{len(file_list)}\n\n")
            
            f.write("Input Files:\n")
            for filename in file_list:
                status = "[OK] Processed" if os.path.exists(filename) else "[ERROR] Not found"
                f.write(f"  {filename}: {status}\n")
            
            f.write("\nOutput Directories:\n")
            f.write(f"  DXF Files: DXF_OUTPUT/\n")
            f.write(f"  PDF Files: PDF_OUTPUT/\n")
            
            f.write("\nGenerated Files:\n")
            # List DXF files
            dxf_dir = Path("DXF_OUTPUT")
            if dxf_dir.exists():
                dxf_files = list(dxf_dir.glob("*.dxf"))
                f.write("  DXF Files:\n")
                for dxf_file in dxf_files:
                    f.write(f"    {dxf_file.name}\n")
            
            # List PDF files
            pdf_dir = Path("PDF_OUTPUT")
            if pdf_dir.exists():
                pdf_files = list(pdf_dir.glob("*.pdf"))
                f.write("  PDF Files:\n")
                for pdf_file in pdf_files:
                    f.write(f"    {pdf_file.name}\n")
        
        print(f"Summary report saved as PROCESSING_SUMMARY.txt")
        
    except Exception as e:
        print(f"Error creating summary report: {e}")

if __name__ == "__main__":
    sys.exit(main())