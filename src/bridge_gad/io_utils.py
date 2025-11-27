import pandas as pd
from typing import Dict
from pathlib import Path
from typing import Any
import yaml

def read_input_excel(path: str) -> pd.DataFrame:
    """Read bridge input parameters from Excel."""
    return pd.read_excel(path)

def save_results_to_excel(results: Dict[str, float], output_path: str) -> None:
    """Save computed results to Excel."""
    df = pd.DataFrame([results])
    df.to_excel(output_path, index=False)

def read_config_yaml(path: Path) -> Dict[str, Any]:
    """Read configuration from YAML file.
    
    Args:
        path: Path to the YAML configuration file
        
    Returns:
        Dictionary with configuration parameters
    """
    with open(path, 'r') as file:
        return yaml.safe_load(file) or {}

def save_config_yaml(config: Dict[str, Any], path: Path) -> None:
    """Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        path: Path to save the YAML file
    """
    with open(path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)