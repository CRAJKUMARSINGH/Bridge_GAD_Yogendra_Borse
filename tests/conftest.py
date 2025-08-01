"""
Configuration file for pytest.
This file is automatically discovered by pytest and used for test configuration.
"""
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
import tempfile
import shutil

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (dependencies may be required)",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow-running",
    )

# Fixtures
@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def temp_dir():
    """Fixture to provide a temporary directory for test outputs."""
    temp_dir = Path(tempfile.mkdtemp(prefix="bridge_gad_test_"))
    yield temp_dir
    # Cleanup after tests
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def sample_config_path(test_data_dir: Path) -> Path:
    """Return the path to the sample config file."""
    return test_data_dir / "test_config.yaml"

@pytest.fixture(scope="session")
def sample_excel_path(test_data_dir: Path) -> Path:
    """Return the path to the sample Excel file."""
    return test_data_dir / "test_input.xlsx"

@pytest.fixture(scope="session")
def output_dxf_path(test_data_dir: Path) -> Path:
    """Return the path to the output DXF file."""
    return test_data_dir / "output.dxf"

@pytest.fixture(scope="session")
def ensure_test_data_dir(test_data_dir: Path) -> Path:
    """Ensure the test data directory exists and return its path."""
    test_data_dir.mkdir(exist_ok=True)
    return test_data_dir

@pytest.fixture(scope="module")
def mock_settings():
    """Return a mock settings object for testing."""
    from unittest.mock import MagicMock
    
    mock_settings = MagicMock()
    mock_settings.drawing.paper_size = "A1"
    mock_settings.drawing.orientation = "landscape"
    mock_settings.drawing.title = "Test Bridge"
    mock_settings.drawing.scale = 100
    
    return mock_settings

@pytest.fixture(scope="module")
def sample_bridge_parameters():
    """Return sample bridge parameters for testing."""
    from bridge_gad.__main__ import BridgeParameters
    
    return BridgeParameters(
        deck_width=10.0,
        num_spans=3,
        span_lengths=[30.0, 35.0, 30.0],
        pier_width=1.5,
        pier_height=10.0,
        abutment_width=2.0,
        abutment_height=8.0,
        girder_depth=1.5,
        girder_spacing=2.0,
        num_girders=5
    )

@pytest.fixture(scope="module")
def sample_drawing_settings():
    """Return sample drawing settings for testing."""
    from bridge_gad.__main__ import DrawingSettings
    
    return DrawingSettings(
        paper_size='A1',
        orientation='landscape',
        title='Test Bridge',
        scale=100
    )

@pytest.fixture(scope="session")
def default_settings():
    """Fixture to provide default settings."""
    from bridge_gad.config import Settings
    return Settings()

@pytest.fixture(scope="session")
def test_config_file(test_data_dir):
    """Fixture to provide a path to a test config file."""
    return test_data_dir / "test_config.yaml"

@pytest.fixture(scope="session")
def test_excel_file(test_data_dir):
    """Fixture to provide a path to a test Excel file."""
    return test_data_dir / "test_bridge_data.xlsx"

@pytest.fixture
def bridge_drawing(default_settings):
    """Fixture to provide a BridgeDrawing instance with default settings."""
    from bridge_gad.core import BridgeDrawing
    return BridgeDrawing(settings=default_settings)

@pytest.fixture(scope="session")
def sample_bridge_data():
    """Fixture to provide sample bridge data for testing."""
    return {
        'spans': 3,
        'span_lengths': [30.0, 35.0, 30.0],
        'deck_width': 10.5,
        'girder_spacing': 2.5,
        'girder_depth': 1.5,
        'abutment_width': 1.2,
        'pier_width': 1.0,
        'pier_height': 5.0
    }

# Add command line options
def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    skip_slow = not config.getoption("--run-slow")
    skip_integration = not config.getoption("--run-integration")
    
    skip_markers = []
    
    if skip_slow:
        skip_markers.append(pytest.mark.skip(reason="need --run-slow option to run"))
    
    if skip_integration:
        skip_markers.append(pytest.mark.skip(reason="need --run-integration option to run"))
    
    for item in items:
        if "slow" in item.keywords and skip_slow:
            item.add_marker(skip_markers[0])
        if "integration" in item.keywords and skip_integration:
            item.add_marker(skip_markers[-1])
