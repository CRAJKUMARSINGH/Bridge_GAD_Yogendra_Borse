"""Load-balancing / routing utilities.

Moved from core.py (BOLT-003 fix) — these functions are unrelated to bridge
drawing and belong in their own module.

FIXES: BOLT-003, QODER-004
"""

import logging
from typing import List, Tuple

from .config import Settings

logger = logging.getLogger(__name__)


def compute_load(nodes: List[str], demand: List[int], cfg: Settings) -> List[Tuple[str, int]]:
    """Greedy assignment + 2-opt refinement.

    Args:
        nodes:  List of node identifiers.
        demand: Load demand per node (must be same length as nodes).
        cfg:    Settings containing alpha/beta cost weights.

    Returns:
        Sorted list of (node, demand) tuples after 2-opt refinement.
    """
    if len(nodes) != len(demand):
        raise ValueError("nodes and demand must be same length")
    pairs = list(zip(nodes, demand))
    pairs.sort(key=lambda x: x[1], reverse=True)
    logger.debug("Initial greedy assignment: %s", pairs)
    return two_opt(pairs, cfg)


def two_opt(route: List[Tuple[str, int]], cfg: Settings) -> List[Tuple[str, int]]:
    """2-opt local search for load balancing.

    Note: O(n²) per improvement pass — suitable for n < 50.
    For larger inputs consider or-opt / simulated annealing.
    """
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 1):
            for j in range(i + 1, len(route)):
                new_route = route[:i] + route[i:j][::-1] + route[j:]
                if total_cost(new_route, cfg) < total_cost(route, cfg):
                    route = new_route
                    improved = True
    return route


def total_cost(route: List[Tuple[str, int]], cfg: Settings) -> float:
    """Latency surrogate: alpha * distance + beta * load."""
    cost = 0.0
    for idx, (_node, load) in enumerate(route):
        dist = idx  # placeholder distance metric
        cost += cfg.alpha * dist + cfg.beta * load
    return cost
