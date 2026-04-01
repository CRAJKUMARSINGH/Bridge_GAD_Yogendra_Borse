"""Phase 6 — Auto Calculation Engine.

Implements:
  - Dependency graph evaluation (topological sort)
  - Reactive recalculation on parameter change
  - Deterministic ordering
  - Formula sandbox (safe eval with restricted builtins)

Usage:
    engine = CalcEngine()
    engine.set("SPAN1", 12.0)
    engine.set("NSPAN", 3)
    engine.register_formula("LBRIDGE", "SPAN1 * NSPAN")
    results = engine.recalculate()
    # results["LBRIDGE"] == 36.0
"""

from __future__ import annotations

import logging
import math
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ── Safe builtins for formula sandbox ────────────────────────────────────────
_SAFE_BUILTINS: Dict[str, Any] = {
    "__builtins__": {},
    "abs": abs, "round": round, "min": min, "max": max,
    "int": int, "float": float, "bool": bool,
    "sqrt": math.sqrt, "ceil": math.ceil, "floor": math.floor,
    "pi": math.pi, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "exp": math.exp,
    "pow": math.pow,
}


class CalcEngine:
    """Reactive parameter calculation engine with dependency tracking."""

    def __init__(self) -> None:
        self._values: Dict[str, float] = {}
        self._formulas: Dict[str, str] = {}          # name → formula string
        self._callbacks: Dict[str, Callable] = {}    # name → callable
        self._dirty: Set[str] = set()

    # ── Value management ──────────────────────────────────────────────────────

    def set(self, name: str, value: float) -> None:
        """Set a raw parameter value and mark dependents dirty."""
        name = name.upper()
        if self._values.get(name) != value:
            self._values[name] = value
            self._dirty.add(name)
            # Mark all formulas that depend on this name as dirty
            for fname, formula in self._formulas.items():
                if name in formula.upper():
                    self._dirty.add(fname)

    def get(self, name: str, default: float = 0.0) -> float:
        """Get a parameter value (raw or computed)."""
        return self._values.get(name.upper(), default)

    def load(self, params: Dict[str, Any]) -> None:
        """Bulk-load parameters from a dict."""
        for k, v in params.items():
            try:
                self.set(k, float(v))
            except (TypeError, ValueError):
                pass

    # ── Formula registration ──────────────────────────────────────────────────

    def register_formula(self, name: str, formula: str) -> None:
        """Register a formula string for a derived parameter.

        Formula may reference other parameter names (case-insensitive).
        Example: register_formula("LBRIDGE", "SPAN1 * NSPAN")
        """
        self._formulas[name.upper()] = formula
        self._dirty.add(name.upper())

    def register_callback(self, name: str, fn: Callable[[float], None]) -> None:
        """Register a callback fired when a parameter value changes."""
        self._callbacks[name.upper()] = fn

    # ── Dependency graph ──────────────────────────────────────────────────────

    def _build_dep_graph(self) -> Dict[str, Set[str]]:
        """Build adjacency map: formula_name → set of names it depends on."""
        graph: Dict[str, Set[str]] = {}
        all_names = set(self._values.keys()) | set(self._formulas.keys())
        for fname, formula in self._formulas.items():
            deps: Set[str] = set()
            for token in formula.upper().split():
                clean = token.strip("()+-*/,")
                if clean in all_names and clean != fname:
                    deps.add(clean)
            graph[fname] = deps
        return graph

    def _topological_order(self) -> List[str]:
        """Return formula names in safe evaluation order (Kahn's algorithm)."""
        graph = self._build_dep_graph()
        in_degree: Dict[str, int] = {n: 0 for n in graph}
        dependents: Dict[str, List[str]] = {n: [] for n in graph}

        for node, deps in graph.items():
            for dep in deps:
                if dep in graph:
                    in_degree[node] += 1
                    dependents[dep].append(node)

        queue = [n for n, d in in_degree.items() if d == 0]
        order: List[str] = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for dep in dependents.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        if len(order) < len(graph):
            logger.warning("Circular dependency detected in formulas — partial evaluation")
        return order

    # ── Recalculation ─────────────────────────────────────────────────────────

    def recalculate(self, force: bool = False) -> Dict[str, float]:
        """Evaluate all dirty (or all, if force=True) formulas in dependency order.

        Returns the full parameter dict after recalculation.
        """
        order = self._topological_order()
        for name in order:
            if not force and name not in self._dirty:
                continue
            formula = self._formulas.get(name)
            if not formula:
                continue
            try:
                # Build eval namespace: current values + safe math
                ns = {**_SAFE_BUILTINS, **{k: v for k, v in self._values.items()}}
                result = float(eval(formula.upper(), ns))  # noqa: S307
                old = self._values.get(name)
                self._values[name] = result
                self._dirty.discard(name)
                if old != result and name in self._callbacks:
                    try:
                        self._callbacks[name](result)
                    except Exception as cb_err:
                        logger.warning("Callback error for %s: %s", name, cb_err)
                logger.debug("Calc %s = %s (formula: %s)", name, result, formula)
            except Exception as exc:
                logger.warning("Formula eval failed for %s (%s): %s", name, formula, exc)

        self._dirty.clear()
        return dict(self._values)

    # ── Built-in bridge formulas ──────────────────────────────────────────────

    @classmethod
    def with_bridge_defaults(cls) -> "CalcEngine":
        """Return a CalcEngine pre-loaded with standard bridge derived formulas."""
        engine = cls()
        engine.register_formula("LBRIDGE", "SPAN1 * NSPAN")
        engine.register_formula("RIGHT",   "LEFT + LBRIDGE")
        engine.register_formula("CAPT",    "TOPRL + 0.5")
        engine.register_formula("CAPB",    "TOPRL - 0.7")
        engine.register_formula("SOFL",    "TOPRL - SLBTHE")
        engine.register_formula("FUTRL",   "DATUM - 5.0")
        return engine

    def summary(self) -> str:
        lines = [f"  {k} = {v}" for k, v in sorted(self._values.items())]
        return "CalcEngine state:\n" + "\n".join(lines)
