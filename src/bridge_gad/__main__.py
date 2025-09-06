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
    output: Path = typer.Option(None, "--output", "-o", help="Output DXF file path"),
    config: Path = typer.Option(None, "--config", "-c", help="Configuration YAML file"),
):
    """Generate complete bridge GAD from Excel parameters."""
    try:
        if output is None:
            output = excel_file.parent / f"{excel_file.stem}_bridge_gad.dxf"
        
        result_path = generate_bridge_gad(excel_file, output)
        typer.echo(f"✅ Bridge GAD generated successfully: {result_path}")
        
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
