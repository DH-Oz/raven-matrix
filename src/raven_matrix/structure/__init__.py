"""Structure-feature relations: the logic that decides what each cell holds.

Re-exports the base relations (ShapeRepetition + logical AND/OR/XOR) and the five
supplemental relations (rotation, scaling, fill change/repetition, numerosity).
"""

from __future__ import annotations

from .base import (
    BaseStructureFeature,
    LogicalAND,
    LogicalOR,
    LogicalXOR,
    LogicOperation,
    ShapeRepetition,
)
from .supplemental import (
    ApplyRotation,
    ApplyScaling,
    ChangeFillPattern,
    FillPatternRepetition,
    SupplementalStructureFeature,
    TranslationalNumerosity,
)

__all__ = [
    "ApplyRotation",
    "ApplyScaling",
    "BaseStructureFeature",
    "ChangeFillPattern",
    "FillPatternRepetition",
    "LogicOperation",
    "LogicalAND",
    "LogicalOR",
    "LogicalXOR",
    "ShapeRepetition",
    "SupplementalStructureFeature",
    "TranslationalNumerosity",
]
