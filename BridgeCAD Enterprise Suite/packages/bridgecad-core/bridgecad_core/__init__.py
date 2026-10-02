"""
BridgeCAD Enterprise — Core Domain Package.

M0 scaffold: module files exist but implementation is scheduled for M1.
Submodules:
  - types: 200+ enums (bridge category, superstructure, pier, foundation, materials, ...)
  - models: Pydantic V2 aggregate BridgeProject (14 sheets mapped)
  - geometry.{plan, long_section, cross_section, foundation}: pure math
  - standards.{irc_sp55, irc_05, irc_21, morth_specs}
  - validation: 150 check_*() functions
  - quantities: concrete/steel BOM extractor
  - costs: unit-rate cost estimator
"""

from . import types  # noqa: F401
from . import models  # noqa: F401
from . import validation  # noqa: F401
from . import quantities  # noqa: F401
from . import costs  # noqa: F401

__version__ = "0.1.0-rc1"
__all__ = ["types", "models", "validation", "quantities", "costs"]
