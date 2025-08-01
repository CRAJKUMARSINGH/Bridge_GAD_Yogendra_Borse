import logging
import sys
from pathlib import Path

import typer

from .config import Settings
from .core import compute_load

app = typer.Typer()

@app.command(name="run")
def run(config: str = "config.yaml"):
    """Bridge-GAD runner."""
    cfg = Settings.from_yaml(Path(config))
    logging.basicConfig(
        level=cfg.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )
    import random
    random.seed(cfg.seed)

    nodes = ["A", "B", "C", "D"]  # demo data
    demand = [10, 20, 5, 15]

    result = compute_load(nodes, demand, cfg)
    for node, load in result:
        typer.echo(f"{node}: {load}")

if __name__ == "__main__":
    app(prog_name="bridge-gad")
