"""Structure-feature relations: the logic that decides what each cell holds.

Re-exports the base relations (ShapeRepetition + logical AND/OR/XOR). Supplemental
relations are added by Task 4.
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

__all__ = [
    "BaseStructureFeature",
    "LogicOperation",
    "LogicalAND",
    "LogicalOR",
    "LogicalXOR",
    "ShapeRepetition",
]
