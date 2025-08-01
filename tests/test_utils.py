"""
Test utilities for the Bridge GAD Generator.

This module provides utility functions to assist with testing the bridge drawing
functionality, including creating test data and verifying DXF output.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import ezdxf
import pandas as pd
from ezdxf.document import Drawing
from ezdxf.entities import DXFGraphic


def create_test_excel(
    file_path: Union[str, Path],
    data: Optional[Dict[str, List[Union[float, int, str]]]] = None,
) -> Path:
    """
    Create a test Excel file with the given data.

    Args:
        file_path: Path where the Excel file will be created
        data: Dictionary containing the data to write to the Excel file.
              If None, default test data will be used.

    Returns:
        Path to the created Excel file
    """
    if data is None:
        data = {
            "Span": [1, 2, 3],
            "Length (m)": [30.0, 35.0, 30.0],
            "Width (m)": [10.0, 10.0, 10.0],
            "Pier Type": ["Abutment", "Pier", "Abutment"],
        }

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return Path(file_path)


def create_test_config(
    file_path: Union[str, Path],
    config_data: Optional[Dict] = None,
) -> Path:
    """
    Create a test config YAML file.

    Args:
        file_path: Path where the config file will be created
        config_data: Dictionary containing the config data.
                   If None, default test config will be used.

    Returns:
        Path to the created config file
    """
    if config_data is None:
        config_data = {
            "drawing": {
                "paper_size": "A1",
                "orientation": "landscape",
                "title": "Test Bridge Drawing",
                "scale": 100,
                "layers": [
                    {"name": "BRIDGE", "color": 7, "linetype": "CONTINUOUS"},
                    {"name": "DIMENSIONS", "color": 1, "linetype": "CONTINUOUS"},
                ],
            },
            "bridge": {
                "deck_width": 10.0,
                "num_spans": 3,
                "span_lengths": [30.0, 35.0, 30.0],
                "pier_width": 1.5,
                "pier_height": 10.0,
                "abutment_width": 2.0,
                "abutment_height": 8.0,
                "girder_depth": 1.5,
                "girder_spacing": 2.0,
                "num_girders": 5,
            },
            "display": {
                "show_dimensions": True,
                "show_annotations": True,
                "show_grid": True,
                "show_centerline": True,
            },
        }

    import yaml

    with open(file_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False)

    return Path(file_path)


def verify_dxf_file(dxf_path: Union[str, Path]) -> bool:
    """
    Verify that a DXF file exists and can be loaded.

    Args:
        dxf_path: Path to the DXF file to verify

    Returns:
        bool: True if the DXF file is valid, False otherwise
    """
    try:
        doc = ezdxf.readfile(str(dxf_path))
        return doc is not None
    except Exception:
        return False


def count_entities_by_layer(doc: Drawing, layer_name: str) -> int:
    """
    Count the number of entities on a specific layer in a DXF document.

    Args:
        doc: The DXF document to search
        layer_name: Name of the layer to count entities for

    Returns:
        int: Number of entities on the specified layer
    """
    return sum(1 for e in doc.modelspace() if e.dxf.layer == layer_name)


def get_entity_bounds(entity: DXFGraphic) -> tuple:
    """
    Get the bounding box of a DXF entity.

    Args:
        entity: The DXF entity to get bounds for

    Returns:
        tuple: (min_x, min_y, max_x, max_y) bounding box coordinates
    """
    try:
        bbox = entity.bbox()
        return (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
    except AttributeError:
        # Some entities might not have a bbox() method
        return (0, 0, 0, 0)


def create_temp_file(suffix: str = "", content: str = None) -> str:
    """
    Create a temporary file with optional content.

    Args:
        suffix: File suffix (e.g., '.txt', '.dxf')
        content: Optional content to write to the file

    Returns:
        str: Path to the created temporary file
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        if content:
            f.write(content.encode("utf-8"))
        return f.name


class DXFTestMixin:
    """Mixin class with DXF testing utilities."""

    def assertLayerExists(self, doc: Drawing, layer_name: str):
        """Assert that a layer exists in the DXF document."""
        self.assertIn(layer_name, doc.layers)

    def assertEntityCountOnLayer(
        self, doc: Drawing, layer_name: str, expected_count: int
    ):
        """Assert the number of entities on a specific layer."""
        actual_count = count_entities_by_layer(doc, layer_name)
        self.assertEqual(
            actual_count,
            expected_count,
            f"Expected {expected_count} entities on layer '{layer_name}', "
            f"found {actual_count}",
        )

    def assertEntityTypeOnLayer(
        self, doc: Drawing, layer_name: str, entity_type: str, min_count: int = 1
    ):
        """Assert that at least min_count entities of type exist on the layer."""
        count = sum(
            1
            for e in doc.modelspace()
            if e.dxf.layer == layer_name and e.dxftype() == entity_type
        )
        self.assertGreaterEqual(
            count,
            min_count,
            f"Expected at least {min_count} {entity_type} entities on layer "
            f"'{layer_name}', found {count}",
        )
