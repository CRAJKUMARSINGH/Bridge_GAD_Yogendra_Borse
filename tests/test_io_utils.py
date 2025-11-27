"""Tests for IO utilities."""

import tempfile
import yaml
from pathlib import Path
from bridge_gad.io_utils import read_config_yaml, save_config_yaml

def test_read_config_yaml():
    """Test reading configuration from YAML file."""
    # Create a temporary YAML file
    config_data = {
        "bridge": {
            "spans": 3,
            "span_lengths": [30.0, 35.0, 30.0]
        },
        "output": {
            "directory": "output",
            "format": "DXF"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)
    
    try:
        # Read the configuration
        result = read_config_yaml(temp_path)
        assert result == config_data
    finally:
        # Clean up
        temp_path.unlink()

def test_save_config_yaml():
    """Test saving configuration to YAML file."""
    config_data = {
        "bridge": {
            "spans": 2,
            "span_lengths": [25.0, 30.0]
        },
        "output": {
            "directory": "results",
            "format": "PDF"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        # Save the configuration
        save_config_yaml(config_data, temp_path)
        
        # Read it back to verify
        with open(temp_path, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data == config_data
    finally:
        # Clean up
        temp_path.unlink()

def test_read_config_yaml_empty():
    """Test reading empty YAML file."""
    # Create an empty temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        # Read the configuration
        result = read_config_yaml(temp_path)
        assert result == {}
    finally:
        # Clean up
        temp_path.unlink()