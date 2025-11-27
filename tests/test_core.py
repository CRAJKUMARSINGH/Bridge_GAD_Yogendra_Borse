import pytest
from bridge_gad.core import compute_load, total_cost
from bridge_gad.config import Settings

def test_compute_load_basic():
    """Basic sanity check for load computation."""
    nodes = ["A", "B", "C"]
    demand = [10, 20, 15]
    cfg = Settings()
    result = compute_load(nodes, demand, cfg)
    assert len(result) == 3

@pytest.mark.parametrize("nodes,demand,expected_length", [
    (["A", "B"], [10, 20], 2),
    (["A", "B", "C", "D"], [5, 10, 15, 20], 4),
])
def test_compute_load_param(nodes, demand, expected_length):
    """Check multiple scenarios."""
    from bridge_gad.core import compute_load
    from bridge_gad.config import Settings
    cfg = Settings()
    result = compute_load(nodes, demand, cfg)
    assert len(result) == expected_length

def test_total_cost():
    """Test the total_cost function."""
    route = [("A", 10), ("B", 20), ("C", 15)]
    cfg = Settings()
    
    # Calculate expected cost manually
    # For A (index 0): cost = alpha * 0 + beta * 10
    # For B (index 1): cost = alpha * 1 + beta * 20
    # For C (index 2): cost = alpha * 2 + beta * 15
    expected = (cfg.alpha * 0 + cfg.beta * 10) + \
               (cfg.alpha * 1 + cfg.beta * 20) + \
               (cfg.alpha * 2 + cfg.beta * 15)
    
    result = total_cost(route, cfg)
    assert result == expected

def test_compute_load_empty():
    """Test compute_load with empty inputs."""
    nodes = []
    demand = []
    cfg = Settings()
    
    result = compute_load(nodes, demand, cfg)
    assert result == []

def test_compute_load_mismatched_lengths():
    """Test compute_load with mismatched lengths."""
    nodes = ["A", "B"]
    demand = [10, 20, 30]  # One more demand than nodes
    cfg = Settings()
    
    with pytest.raises(ValueError):
        compute_load(nodes, demand, cfg)