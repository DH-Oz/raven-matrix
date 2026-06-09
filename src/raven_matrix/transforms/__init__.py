"""Location transforms package: which cells share a feature, and in what order.

Re-exports the abstract base, the five geometric transforms, the Logic special
case, and the ``make_location_transform`` factory that maps the Matzen direction
digit (1-5) to a geometric transform class.
"""

from __future__ import annotations

from raven_matrix.model import Direction, MatrixSize

from .base import LocationTransform
from .geometric import (
    DiagonalBottomLeftTopRight,
    DiagonalTopLeftBottomRight,
    Horizontal,
    TopLeftCornerOut,
    Vertical,
)
from .logic import LogicLocationTransform

__all__ = [
    "DiagonalBottomLeftTopRight",
    "DiagonalTopLeftBottomRight",
    "Horizontal",
    "LocationTransform",
    "LogicLocationTransform",
    "TopLeftCornerOut",
    "Vertical",
    "make_location_transform",
]

# Direction digit (Matzen 1-5) -> geometric transform class. Logic is NOT in
# this map: it is selected by the structure layer when a logic base relation is
# chosen, never by a direction digit.
_DIRECTION_TO_TRANSFORM: dict[Direction, type[LocationTransform]] = {
    Direction.HORIZONTAL: Horizontal,
    Direction.VERTICAL: Vertical,
    Direction.DIAGONAL_BL_TR: DiagonalBottomLeftTopRight,
    Direction.DIAGONAL_TL_BR: DiagonalTopLeftBottomRight,
    Direction.TOP_LEFT_CORNER_OUT: TopLeftCornerOut,
}


def make_location_transform(
    direction: Direction | int, size: MatrixSize
) -> LocationTransform:
    """Build the geometric transform for a Matzen direction digit (1-5).

    ``direction`` may be a ``Direction`` member or its raw integer digit (the
    form parsed straight from an oracle ``Structure`` code). An out-of-range
    digit raises ``ValueError``.

    The ``Direction | int`` union is intentional: oracle ``Structure``-code
    direction digits arrive as raw ``int``s, so this factory owns the
    int→``Direction`` conversion and the out-of-range error. The contract will
    be revisited at the Phase 4 interface once the actual consumer exists.
    """
    # Normalise through Direction so an out-of-range int raises ValueError
    # rather than silently missing the dict.
    key = Direction(direction)
    return _DIRECTION_TO_TRANSFORM[key](size)
