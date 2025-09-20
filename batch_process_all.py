#!/usr/bin/env python3
"""
Batch processing script for all SweetWilledInputFile files
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def process_all_files():
    """Process all SweetWilledInputFile files and generate outputs."""
    # Create output directory
    output_dir = Path("COMBINED_OUTPUT")
    output_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for different output types
    dxf_dir = output_dir / "DXF_FILES"
    pdf_dir = output_dir / "PDF_FILES"
    dxf_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    
    # List of all SweetWilledInputFile files
    sweet_willed_files = [
        "SweetWilledInputFile-01.csv",
        "SweetWilledInputFile-02.csv", 
        "SweetWilledInputFile-03.csv"
        # Note: We only created 3 files for demonstration
    ]
    
    print("Processing all SweetWilledInputFile files...")
    print("=" * 50)
    
    processed_files = 0
    
    # Import the main application
    import simple_bridge_app
    
    for i, filename in enumerate(sweet_willed_files, 1):
        if os.path.exists(filename):
            print(f"Processing {filename} ({i}/{len(sweet_willed_files)})...")
            
            try:
                # Load parameters from CSV file
                if simple_bridge_app.load_bridge_parameters_from_csv(filename):
                    print(f"  ✓ Loaded parameters from {filename}")
                    
                    # Generate timestamp for unique filenames
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    # Generate DXF output
                    dxf_filename = f"bridge_drawing_{i:02d}_{timestamp}.dxf"
                    print(f"  Generating DXF: {dxf_filename}")
                    
                    # Use the existing save_dxf function
                    simple_bridge_app.save_dxf()
                    
                    # Rename the generated DXF file
                    if os.path.exists("enhanced_bridge_" + timestamp + ".dxf"):
                        os.rename("enhanced_bridge_" + timestamp + ".dxf", dxf_filename)
                    elif os.path.exists("enhanced_bridge_*.dxf"):
                        # Find the latest DXF file
                        import glob
                        dxf_files = glob.glob("enhanced_bridge_*.dxf")
                        if dxf_files:
                            latest_dxf = max(dxf_files, key=os.path.getctime)
                            os.rename(latest_dxf, dxf_filename)
                    
                    # Move DXF file to output directory
                    if os.path.exists(dxf_filename):
                        shutil.move(dxf_filename, dxf_dir / dxf_filename)
                        print(f"  ✓ Saved DXF to {dxf_dir / dxf_filename}")
                    
                    # Generate PDF output
                    pdf_filename = f"bridge_drawing_{i:02d}_{timestamp}.pdf"
                    print(f"  Generating PDF: {pdf_filename}")
                    
                    # Use the existing save_pdf function
                    simple_bridge_app.save_pdf()
                    
                    # Rename the generated PDF file
                    if os.path.exists("simple_bridge_" + timestamp + ".pdf"):
                        os.rename("simple_bridge_" + timestamp + ".pdf", pdf_filename)
                    elif os.path.exists("simple_bridge_*.pdf"):
                        # Find the latest PDF file
                        import glob
                        pdf_files = glob.glob("simple_bridge_*.pdf")
                        if pdf_files:
                            latest_pdf = max(pdf_files, key=os.path.getctime)
                            os.rename(latest_pdf, pdf_filename)
                    
                    # Move PDF file to output directory
                    if os.path.exists(pdf_filename):
                        shutil.move(pdf_filename, pdf_dir / pdf_filename)
                        print(f"  ✓ Saved PDF to {pdf_dir / pdf_filename}")
                    
                    processed_files += 1
                    print(f"  ✓ Completed processing {filename}")
                else:
                    print(f"  ✗ Failed to load parameters from {filename}")
                    
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                
            print()
    
    print("=" * 50)
    print(f"Processing complete! Processed {processed_files} files.")
    print(f"Output files saved to: {output_dir}")
    print(f"DXF files in: {dxf_dir}")
    print(f"PDF files in: {pdf_dir}")
    
    return processed_files

def create_combined_pdf():
    """Create a combined PDF with all outputs."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Create combined PDF
        combined_pdf = "COMBINED_OUTPUT/COMBINED_BRIDGE_DRAWINGS.pdf"
        doc = SimpleDocTemplate(combined_pdf, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        title = Paragraph("Bridge GAD Generator - Combined Output Report", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 20))
        
        subtitle = Paragraph("Comprehensive Bridge Engineering Drawings", styles["Heading2"])
        story.append(subtitle)
        story.append(Spacer(1, 20))
        
        date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"])
        story.append(date_text)
        story.append(Spacer(1, 20))
        
        # Add section for each processed file
        sweet_willed_files = [
            "SweetWilledInputFile-01.csv",
            "SweetWilledInputFile-02.csv", 
            "SweetWilledInputFile-03.csv"
        ]
        
        for i, filename in enumerate(sweet_willed_files, 1):
            if os.path.exists(filename):
                story.append(PageBreak())
                section_title = Paragraph(f"Drawing Set {i}: {filename}", styles["Heading1"])
                story.append(section_title)
                story.append(Spacer(1, 20))
                
                # Add description
                desc = Paragraph("This section contains the bridge engineering drawings generated from the input parameters.", styles["Normal"])
                story.append(desc)
                story.append(Spacer(1, 20))
                
                # Add parameter summary
                param_title = Paragraph("Input Parameters Summary:", styles["Heading2"])
                story.append(param_title)
                story.append(Spacer(1, 10))
                
                # Read and summarize parameters
                try:
                    with open(filename, 'r') as f:
                        lines = f.readlines()
                        if len(lines) > 5:  # Skip header
                            for line in lines[1:6]:  # Show first 5 parameter lines
                                parts = line.strip().split(',')
                                if len(parts) >= 3:
                                    param_text = Paragraph(f"<b>{parts[1]}</b>: {parts[0]} - {parts[2]}", styles["Normal"])
                                    story.append(param_text)
                except Exception as e:
                    error_text = Paragraph(f"Error reading parameters: {e}", styles["Normal"])
                    story.append(error_text)
                
                story.append(Spacer(1, 20))
                story.append(Paragraph("Generated Files:", styles["Heading2"]))
                story.append(Spacer(1, 10))
                
                # List generated files
                dxf_file = f"bridge_drawing_{i:02d}_*.dxf"
                pdf_file = f"bridge_drawing_{i:02d}_*.pdf"
                
                dxf_text = Paragraph(f"• DXF Drawing: {dxf_file}", styles["Normal"])
                story.append(dxf_text)
                pdf_text = Paragraph(f"• PDF Drawing: {pdf_file}", styles["Normal"])
                story.append(pdf_text)
        
        story.append(PageBreak())
        final_text = Paragraph("End of Report", styles["Title"])
        story.append(final_text)
        
        # Build PDF
        doc.build(story)
        print(f"✓ Combined PDF created: {combined_pdf}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating combined PDF: {e}")
        return False

def main():
    """Main function to process all files and create combined output."""
    print("Bridge GAD Generator - Batch Processing Tool")
    print("=" * 50)
    
    # Process all files
    processed = process_all_files()
    
    if processed > 0:
        # Create combined PDF report
        print("\nCreating combined PDF report...")
        if create_combined_pdf():
            print("✓ Combined PDF report created successfully")
        else:
            print("✗ Failed to create combined PDF report")
    else:
        print("No files were processed successfully.")
        return 1
    
    print("\n" + "=" * 50)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 50)
    print("Output files are located in the COMBINED_OUTPUT directory:")
    print("- DXF_FILES/: Individual DXF drawing files")
    print("- PDF_FILES/: Individual PDF drawing files")
    print("- COMBINED_BRIDGE_DRAWINGS.pdf: Combined report")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())