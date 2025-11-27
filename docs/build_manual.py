#!/usr/bin/env python3
"""
Bridge_GAD User Manual Generator

This script generates a professional PDF user manual from the markdown template.
"""

from datetime import date
import os
import sys

# Try to import pypandoc, if not available provide instructions
try:
    import pypandoc
    PANDOC_AVAILABLE = True
except ImportError:
    PANDOC_AVAILABLE = False
    pypandoc = None
    print("Warning: pypandoc not available. Manual generation will be limited.")
    print("To enable full PDF generation, install with: pip install pypandoc")

def get_version():
    """Extract version from the package __init__.py file."""
    version = "1.0.0"  # Default version
    
    try:
        # Look for version in src/bridge_gad/__init__.py
        init_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'bridge_gad', '__init__.py')
        if os.path.exists(init_path):
            with open(init_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('__version__'):
                        version = line.split('=')[1].strip().strip('"\'')
                        break
    except Exception as e:
        print(f"Warning: Could not read version from __init__.py: {e}")
    
    return version

def generate_manual():
    """Generate the user manual from template."""
    # Get the version
    version = get_version()
    print(f"Generating manual for Bridge_GAD v{version}")
    
    # Read the template
    template_path = os.path.join(os.path.dirname(__file__), 'manual_template.md')
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return False
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read().replace("VERSION", version)
    except Exception as e:
        print(f"Error reading template: {e}")
        return False
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate markdown output (always available)
    output_md = os.path.join(output_dir, "Bridge_GAD_User_Manual.md")
    try:
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Markdown manual generated: {output_md}")
    except Exception as e:
        print(f"Error writing markdown manual: {e}")
        return False
    
    # Generate PDF output if pypandoc is available
    if PANDOC_AVAILABLE and pypandoc:
        try:
            output_pdf = os.path.join(output_dir, "Bridge_GAD_User_Manual.pdf")
            pypandoc.convert_text(
                content,
                'pdf',
                format='md',
                outputfile=output_pdf,
                extra_args=['--standalone', '--pdf-engine=xelatex']
            )
            print(f"✅ PDF manual generated: {output_pdf}")
        except Exception as e:
            print(f"Warning: Could not generate PDF manual: {e}")
            print("You may need to install LaTeX for PDF generation.")
            return False
    else:
        print("ℹ️  PDF generation skipped (pypandoc not available)")
        print("To enable PDF generation:")
        print("1. Install pypandoc: pip install pypandoc")
        print("2. Install LaTeX distribution (e.g., MiKTeX, TeX Live)")
    
    return True

def main():
    """Main entry point."""
    print("=== Bridge_GAD User Manual Generator ===")
    print(f"Date: {date.today().strftime('%Y-%m-%d')}")
    print()
    
    success = generate_manual()
    
    if success:
        print("\n✅ Manual generation process completed!")
        return 0
    else:
        print("\n❌ Manual generation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())