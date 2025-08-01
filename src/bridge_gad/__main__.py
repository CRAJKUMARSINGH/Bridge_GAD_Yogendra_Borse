import logging
import sys
import random
from pathlib import Path

import typer
import pandas as pd

from .config import Settings
from .core import compute_load
from .drawing import SlabBridgeGAD

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
    df = pd.read_excel(excel)
    path = SlabBridgeGAD(df).generate(out)
    typer.echo(f"Slab-bridge GAD → {path}")

@app.command("living")
def living(
    excel: Path = typer.Argument(..., exists=True, help="Excel file with spans"),
):
    """Launch interactive 3-D web GAD."""
    from .living_gad import run_living_gad
    run_living_gad(excel)

if __name__ == "__main__":
    app(prog_name="bridge-gad")
