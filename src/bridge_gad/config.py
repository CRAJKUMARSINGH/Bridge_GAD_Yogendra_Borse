from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field
import yaml

class Settings(BaseModel):
    alpha: float = Field(ge=0.0, le=1.0)
    beta: float = Field(ge=0.0, le=1.0)
    max_hops: int = Field(ge=1)
    log_level: str = "INFO"
    seed: int = 42

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with path.open() as f:
            raw: Dict[str, Any] = yaml.safe_load(f)
        return cls(**raw)
