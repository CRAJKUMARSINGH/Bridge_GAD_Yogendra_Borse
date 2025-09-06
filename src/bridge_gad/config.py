from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field
import yaml

# Bridge-specific config
class BridgeConfig(BaseModel):
    spans: int = 3
    span_lengths: List[float] = [30.0, 35.0, 30.0]
    deck_width: float = 12.0
    girder_spacing: float = 3.0
    girder_depth: float = 1.5
    deck_thickness: float = 0.2

# Drawing-specific config
class DrawingConfig(BaseModel):
    paper_size: str = "A3"
    scale: float = 100.0
    line_weight: float = 0.35
    text_height: float = 2.5

# Output configuration
class OutputConfig(BaseModel):
    directory: str = "output"
    format: str = "DXF"
    layers: Dict[str, str] = {
        "outline": "BRIDGE_OUTLINE",
        "dimensions": "DIMENSIONS",
        "text": "TEXT",
        "centerline": "CENTERLINE"
    }

class Settings(BaseModel):
    alpha: float = Field(0.85, ge=0, le=1)
    beta: float = Field(0.15, ge=0, le=1)
    max_hops: int = Field(8, ge=1)
    log_level: str = "INFO"
    seed: int = 42
    bridge: BridgeConfig = BridgeConfig()
    drawing: DrawingConfig = DrawingConfig()
    output: OutputConfig = OutputConfig()

    @classmethod
    def from_yaml(cls, path: Path) -> 'Settings':
        with path.open() as f:
            data = yaml.safe_load(f)
        return cls(**data)

def load_settings(config_path: Path = None) -> Settings:
    """Load settings from configuration file or use defaults."""
    if config_path and config_path.exists():
        return Settings.from_yaml(config_path)
    return Settings()
