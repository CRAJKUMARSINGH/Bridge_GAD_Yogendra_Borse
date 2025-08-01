from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field
import yaml

class Settings(BaseModel):
    alpha: float = Field(0.85, ge=0, le=1)
    beta: float = Field(0.15, ge=0, le=1)
    max_hops: int = Field(8, ge=1)
    log_level: str = "INFO"
    seed: int = 42

    @classmethod
    def from_yaml(cls, path: Path) -> 'Settings':
        with path.open() as f:
            data = yaml.safe_load(f)
        return cls(**data)

# Optional bridge-specific config
class BridgeConfig(BaseModel):
    span_length: float = 30.0
    width: float = 12.0
