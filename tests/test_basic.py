"""
Basic tests for Bridge GAD Generator.
"""
import pytest
from pathlib import Path
import tempfile

from bridge_gad import __version__
from bridge_gad.config import Settings
from bridge_gad.core import compute_load
from bridge_gad.drawing import BridgeDrawing, generate_bridge_drawing


def test_version():
    """Test that version is defined."""
    assert __version__ is not None


def test_settings_loading():
    """Test that default settings can be loaded."""
    settings = Settings()
    assert settings is not None
    assert settings.bridge.spans == 3
    assert settings.drawing.paper_size == "A3"


def test_bridge_drawing_initialization():
    """Test that BridgeDrawing can be initialized."""
    drawing = BridgeDrawing()
    assert drawing is not None
    assert drawing.settings is not None


def test_generate_bridge_drawing(tmp_path):
    """Test that a bridge drawing can be generated."""
    # Create a temporary Excel file for testing
    import pandas as pd
    
    # Create a simple Excel file with test data
    test_data = {
        'Parameter': ['SPAN1', 'SPAN2', 'SPAN3'],
        'Value': [30.0, 35.0, 30.0]
    }
    df = pd.DataFrame(test_data)
    
    excel_file = tmp_path / "test_bridge_data.xlsx"
    df.to_excel(excel_file, index=False)
    
    # Generate the drawing
    output_file = tmp_path / "test_output.dxf"
    result_path = generate_bridge_drawing(
        excel_file=excel_file,
        output_path=output_file
    )
    
    # Verify the output file was created
    assert result_path.exists()
    assert result_path == output_file


def test_optimization():
    """Test that bridge optimization runs without errors."""
    from bridge_gad.optimize import optimize_bridge_design
    
    # Get default settings
    settings = Settings()
    
    # Run optimization with default settings
    result = optimize_bridge_design(settings)
    
    # Check that we got results
    assert result is not None
    assert 'span_lengths' in result
    assert len(result['span_lengths']) == settings.bridge.spans
    
    # Check that the optimized values are within reasonable bounds
    for length in result['span_lengths']:
        assert 10.0 <= length <= 100.0  # From optimization constraints
    
    assert 2.0 <= result['girder_spacing'] <= 6.0
    assert 0.5 <= result['girder_depth'] <= 3.0
    assert 0.15 <= result['deck_thickness'] <= 0.3


def test_compute_load_smoke():
    from bridge_gad.config import Settings
    from bridge_gad.core import compute_load

    cfg = Settings(alpha=0.5, beta=0.5, max_hops=4, seed=7)
    nodes = ["x", "y", "z"]
    demand = [3, 2, 5]
    out = compute_load(nodes, demand, cfg)
    assert len(out) == 3
    assert sum(d for _, d in out) == 10
