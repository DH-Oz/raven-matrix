"""Tests for the Logic location transform (Task 4, AC3.3).

The Logic transform seeds the 2x2 top-left block and refuses to traverse: both
``next_location`` and ``parent_location`` raise ``NotImplementedError`` (the
upstream ``UnsupportedOperationException`` special case). It requires at least a
3x3 grid.
"""

from __future__ import annotations

import pytest

from raven_matrix.model import Location, MatrixSize
from raven_matrix.transforms.logic import LogicLocationTransform


def test_base_locations_are_the_top_left_2x2_block() -> None:
    transform = LogicLocationTransform(MatrixSize(3, 3))
    assert transform.base_locations() == [
        Location(0, 0),
        Location(0, 1),
        Location(1, 0),
        Location(1, 1),
    ]


def test_next_location_is_not_supported() -> None:
    transform = LogicLocationTransform(MatrixSize(3, 3))
    with pytest.raises(NotImplementedError):
        transform.next_location(Location(0, 0))


def test_parent_location_is_not_supported() -> None:
    transform = LogicLocationTransform(MatrixSize(3, 3))
    with pytest.raises(NotImplementedError):
        transform.parent_location(Location(1, 1))


@pytest.mark.parametrize(
    "size",
    [
        MatrixSize(2, 3),  # too few rows
        MatrixSize(3, 2),  # too few columns
        MatrixSize(2, 2),  # both too small
    ],
)
def test_rejects_grids_smaller_than_3x3(size: MatrixSize) -> None:
    with pytest.raises(ValueError):
        LogicLocationTransform(size)


def test_accepts_3x3_and_larger() -> None:
    # No raise for the minimum and a larger grid.
    assert LogicLocationTransform(MatrixSize(3, 3)).base_locations()
    assert LogicLocationTransform(MatrixSize(5, 4)).base_locations()
