"""
bridgecad_core.quantities — BOM extractor (concrete, steel, earthwork, surfacing).
M0 scaffold. Implementation: M1/M3 (after geometry + drawing modules deliver).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import BridgeProject


@dataclass
class BillItem:
    code: str
    description: str
    unit: str
    qty: float
    rate: float | None = None
    amount: float | None = None


@dataclass
class BillOfQuantities:
    items: list[BillItem] = field(default_factory=list)
    total_cost: float = 0.0

    def add(self, item: BillItem) -> None:
        self.items.append(item)


def extract_quantities(project: BridgeProject) -> BillOfQuantities:
    """Compute concrete/steel volumes from geometry. M0: returns empty BoQ."""
    return BillOfQuantities()


__all__ = ["BillItem", "BillOfQuantities", "extract_quantities"]
