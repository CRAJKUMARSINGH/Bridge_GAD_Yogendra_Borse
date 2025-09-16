import logging
import sys
import random
from pathlib import Path
from typing import Optional

import typer
import pandas as pd

from .config import Settings
from .core import compute_load
from .drawing import SlabBridgeGAD
from .bridge_generator import generate_bridge_gad

app = typer.Typer()

@app.command()
def run(
    config: Path = typer.Option('config.yaml', '--config', '-c', exists=True),
):
    """Run Bridge-GAD with the given YAML config."""
    cfg = Settings.from_yaml(config)
    logging.basicConfig(
        level=cfg.log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stderr,
    )
    random.seed(cfg.seed)

    nodes = ['A', 'B', 'C', 'D']  # demo data
    demand = [10, 20, 5, 15]

    result = compute_load(nodes, demand, cfg)
    for node, load in result:
        typer.echo(f'{node}: {load}')

@app.command("gad")
def gad(
    excel: Path = typer.Argument(..., exists=True, help="Excel file with spans"),
    out: Path = typer.Option(Path("slab_bridge_gad.dxf"), help="Output DXF"),
):
    """Generate slab-bridge general-arrangement drawing."""
    df = pd.read_excel(excel, engine='openpyxl')
    path = SlabBridgeGAD(df).generate(out)
    typer.echo(f"Slab-bridge GAD → {path}")

@app.command("lisp")
def lisp(
    excel: Path = typer.Argument(..., exists=True, help="Excel file with Lisp parameters"),
    out: Path = typer.Option(Path("lisp_bridge.dxf"), help="Output DXF file"),
):
    """Generate bridge GAD using Lisp parameters from Excel."""
    from .lisp_mirror import draw_lisp_bridge
    try:
        output_path = draw_lisp_bridge(excel, out)
        typer.echo(f"Lisp bridge GAD → {output_path}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command("generate")
def generate(
    excel_file: Path = typer.Argument(..., exists=True, help="Excel file with bridge parameters"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path (extension determines format)"),
    config: Path = typer.Option(None, "--config", "-c", help="Configuration YAML file"),
    formats: Optional[str] = typer.Option(None, "--formats", help="Comma-separated list of output formats (dxf,pdf,html,svg,png)"),
    show_canvas: bool = typer.Option(False, "--canvas", help="Also create and open HTML canvas visualization"),
):
    """Generate complete bridge GAD from Excel parameters with multiple format support."""
    try:
        if output is None:
            output = excel_file.parent / f"{excel_file.stem}_bridge_gad.dxf"
        
        # Generate the main bridge drawing first
        from .bridge_generator import BridgeGADGenerator
        generator = BridgeGADGenerator()
        
        if not generator.generate_complete_drawing(excel_file, output):
            raise RuntimeError("Failed to generate bridge drawing")
        
        typer.echo(f"✅ Primary output generated: {output}")
        
        # Handle multiple formats if specified
        if formats or show_canvas:
            from .output_formats import create_multi_format_output
            
            format_list = []
            if formats:
                format_list.extend([f.strip() for f in formats.split(',')])
            if show_canvas and 'html' not in format_list:
                format_list.append('html')
            
            if format_list:
                typer.echo(f"🔄 Creating additional formats: {', '.join(format_list)}")
                results = create_multi_format_output(generator, output.with_suffix(''), format_list)
                
                for fmt, result_path in results.items():
                    if result_path:
                        typer.echo(f"✅ {fmt.upper()} output: {result_path}")
                        
                        # Open HTML canvas in browser if requested
                        if fmt == 'html' and show_canvas:
                            import webbrowser
                            webbrowser.open(f'file://{result_path.absolute()}')
                            typer.echo(f"🌐 Canvas visualization opened in browser")
                    else:
                        typer.echo(f"❌ Failed to create {fmt.upper()} output")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """Start the FastAPI web server."""
    try:
        import uvicorn
        from .api import app as fastapi_app
        
        typer.echo(f"🚀 Starting Bridge GAD API server at http://{host}:{port}")
        uvicorn.run(fastapi_app, host=host, port=port, reload=reload)
        
    except ImportError:
        typer.echo("❌ Error: uvicorn is required to run the server. Install with: pip install uvicorn", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error starting server: {e}", err=True)
        raise typer.Exit(1)

@app.command("canvas")
def canvas(
    excel_file: Path = typer.Argument(..., exists=True, help="Excel file with bridge parameters"),
    output: Path = typer.Option(None, "--output", "-o", help="HTML output file path"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open in browser automatically"),
):
    """Create interactive HTML canvas visualization of the bridge."""
    try:
        if output is None:
            output = excel_file.parent / f"{excel_file.stem}_bridge_canvas.html"
        
        # Generate bridge and create canvas
        from .bridge_generator import BridgeGADGenerator
        from .output_formats import MultiFormatExporter
        
        generator = BridgeGADGenerator()
        generator.setup_document()
        
        if not generator.read_variables_from_excel(excel_file):
            raise RuntimeError("Failed to read Excel parameters")
        
        # Generate the drawing components
        generator.draw_layout_and_axes()
        generator.draw_bridge_superstructure()
        generator.draw_piers_elevation()
        generator.draw_abutments()
        generator.draw_plan_view()
        generator.add_dimensions_and_labels()
        
        # Export as HTML canvas
        exporter = MultiFormatExporter(generator)
        result_path = exporter.export(output, 'html')
        
        typer.echo(f"✅ Interactive canvas created: {result_path}")
        
        if open_browser:
            import webbrowser
            webbrowser.open(f'file://{result_path.absolute()}')
            typer.echo(f"🌐 Canvas visualization opened in browser")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command("pdf")
def pdf(
    excel_file: Path = typer.Argument(..., exists=True, help="Excel file with bridge parameters"),
    output: Path = typer.Option(None, "--output", "-o", help="PDF output file path"),
):
    """Generate PDF drawing of the bridge."""
    try:
        if output is None:
            output = excel_file.parent / f"{excel_file.stem}_bridge_drawing.pdf"
        
        # Generate bridge and create PDF
        from .bridge_generator import BridgeGADGenerator
        from .output_formats import MultiFormatExporter
        
        generator = BridgeGADGenerator()
        generator.setup_document()
        
        if not generator.read_variables_from_excel(excel_file):
            raise RuntimeError("Failed to read Excel parameters")
        
        # Generate the drawing components
        generator.draw_layout_and_axes()
        generator.draw_bridge_superstructure()
        generator.draw_piers_elevation()
        generator.draw_abutments()
        generator.draw_plan_view()
        generator.add_dimensions_and_labels()
        
        # Export as PDF
        exporter = MultiFormatExporter(generator)
        result_path = exporter.export(output, 'pdf')
        
        typer.echo(f"✅ PDF drawing created: {result_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command("version")
def version():
    """Show version information."""
    from . import __version__
    typer.echo(f"Bridge GAD Generator v{__version__}")

@app.command("living")
def living(
    excel: Path = typer.Argument(..., exists=True, help="Excel file with spans"),
):
    """Launch interactive 3-D web GAD."""
    try:
        from .living_gad import run_living_gad
        run_living_gad(excel)
    except ImportError:
        typer.echo("❌ Error: living_gad module not available", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app(prog_name="bridge-gad")
