"""Tests for the direction-digit factory (Task 4).

``make_location_transform`` maps the Matzen direction digit (Direction 1-5) to
the matching geometric transform class. Logic is selected by the structure
layer, not this digit map, so it is not reachable here. An out-of-range digit
raises ``ValueError``.
"""

from __future__ import annotations

import pytest

from raven_matrix.model import Direction, MatrixSize
from raven_matrix.transforms import (
    DiagonalBottomLeftTopRight,
    DiagonalTopLeftBottomRight,
    Horizontal,
    TopLeftCornerOut,
    Vertical,
    make_location_transform,
)


@pytest.mark.parametrize(
    "direction,expected_cls",
    [
        (Direction.HORIZONTAL, Horizontal),
        (Direction.VERTICAL, Vertical),
        (Direction.DIAGONAL_BL_TR, DiagonalBottomLeftTopRight),
        (Direction.DIAGONAL_TL_BR, DiagonalTopLeftBottomRight),
        (Direction.TOP_LEFT_CORNER_OUT, TopLeftCornerOut),
    ],
)
def test_factory_maps_each_direction_to_its_class(
    direction: Direction, expected_cls: type
) -> None:
    # 3x3 is odd-square, so every direction (including the diagonals) is valid.
    transform = make_location_transform(direction, MatrixSize(3, 3))
    assert type(transform) is expected_cls
    assert transform.size == MatrixSize(3, 3)


@pytest.mark.parametrize("bad_digit", [0, 6, -1])
def test_factory_rejects_out_of_range_digit(bad_digit: int) -> None:
    with pytest.raises(ValueError):
        make_location_transform(bad_digit, MatrixSize(3, 3))
