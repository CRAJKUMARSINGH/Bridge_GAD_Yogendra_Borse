"""Tests for bridge geometry calculations."""

import pytest
from bridge_gad.geometry import compute_bending_moment, compute_shear_force, compute_deflection, compute_bridge_geometry

def test_compute_bending_moment():
    """Test bending moment calculation."""
    # For a simply supported beam with UDL:
    # M = wL²/8
    span = 10.0  # m
    load = 5.0   # kN/m
    expected = (5.0 * 10.0 ** 2) / 8.0  # 62.5 kN*m
    
    result = compute_bending_moment(span, load)
    assert result == expected

def test_compute_shear_force():
    """Test shear force calculation."""
    # For a simply supported beam with UDL:
    # V = wL/2
    load = 5.0   # kN/m
    span = 10.0  # m
    expected = (5.0 * 10.0) / 2.0  # 25.0 kN
    
    result = compute_shear_force(load, span)
    assert result == expected

def test_compute_deflection():
    """Test deflection calculation."""
    # For a simply supported beam with UDL:
    # δ = 5wL⁴ / (384EI)
    span = 10.0      # m
    load = 5.0       # kN/m
    E = 2.1e8        # kN/m²
    I = 0.0025       # m⁴
    expected = (5 * 5.0 * 10.0 ** 4) / (384 * 2.1e8 * 0.0025)  # ~0.000198 m
    
    result = compute_deflection(span, load, E, I)
    assert abs(result - expected) < 1e-10

def test_compute_bridge_geometry():
    """Test bridge geometry computation."""
    span_lengths = [20.0, 25.0, 20.0]
    deck_width = 12.0
    girder_spacing = 3.0
    
    result = compute_bridge_geometry(span_lengths, deck_width, girder_spacing)
    
    assert result["total_length"] == 65.0
    assert result["num_spans"] == 3
    assert result["span_lengths"] == span_lengths
    assert result["deck_width"] == deck_width
    assert result["num_girders"] == 5  # ceil(12.0/3.0) + 1 = 4 + 1 = 5
    assert result["girder_spacing"] == girder_spacing