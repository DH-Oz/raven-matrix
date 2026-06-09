"""Tests for the Horizontal and Vertical location transforms (Task 2, AC3.2).

Sequences are hand-derived from the upstream
``HorizontalSGMLocationTransform`` / ``VerticalSGMLocationTransform`` logic on a
3x3 (square) grid, where every wrap value is unambiguous.

One regression test pins the fix-to-paper Vertical parent-wrap on a non-square
grid: upstream wraps the row to ``numColumns-1`` (a bug masked on square grids);
the port wraps to ``num_rows-1``. The non-square assertion fails against the
buggy code, proving the fix.
"""

from __future__ import annotations

import pytest

from raven_matrix.model import Location, MatrixSize
from raven_matrix.transforms.geometric import Horizontal, Vertical


def _full_next_cycle(transform, start: Location) -> list[Location]:
    """All locations from start, following next_location until it wraps back."""
    visited = [start]
    current = transform.next_location(start)
    while current != start:
        visited.append(current)
        current = transform.next_location(current)
    return visited


# ---------------------------------------------------------------------------
# Horizontal (3x3)
# ---------------------------------------------------------------------------

def test_horizontal_base_locations_are_first_column_of_each_row() -> None:
    transform = Horizontal(MatrixSize(3, 3))
    assert transform.base_locations() == [
        Location(0, 0), Location(1, 0), Location(2, 0)
    ]


def test_horizontal_next_walks_columns_and_wraps() -> None:
    transform = Horizontal(MatrixSize(3, 3))
    assert _full_next_cycle(transform, Location(0, 0)) == [
        Location(0, 0), Location(0, 1), Location(0, 2)
    ]
    # A non-zero row walks within its own row.
    assert _full_next_cycle(transform, Location(1, 0)) == [
        Location(1, 0), Location(1, 1), Location(1, 2)
    ]


def test_horizontal_parent_is_previous_column_wrapping_left() -> None:
    transform = Horizontal(MatrixSize(3, 3))
    assert transform.parent_location(Location(0, 0)) == Location(0, 2)
    assert transform.parent_location(Location(0, 1)) == Location(0, 0)
    assert transform.parent_location(Location(0, 2)) == Location(0, 1)


# ---------------------------------------------------------------------------
# Vertical (3x3)
# ---------------------------------------------------------------------------

def test_vertical_base_locations_are_first_row_of_each_column() -> None:
    transform = Vertical(MatrixSize(3, 3))
    assert transform.base_locations() == [
        Location(0, 0), Location(0, 1), Location(0, 2)
    ]


def test_vertical_next_walks_rows_and_wraps() -> None:
    transform = Vertical(MatrixSize(3, 3))
    assert _full_next_cycle(transform, Location(0, 0)) == [
        Location(0, 0), Location(1, 0), Location(2, 0)
    ]
    # A non-zero column walks within its own column.
    assert _full_next_cycle(transform, Location(0, 1)) == [
        Location(0, 1), Location(1, 1), Location(2, 1)
    ]


def test_vertical_parent_is_previous_row_wrapping_to_last_row() -> None:
    transform = Vertical(MatrixSize(3, 3))
    # Row 0 wraps to the last row (num_rows - 1 == 2 on a 3x3).
    assert transform.parent_location(Location(0, 0)) == Location(2, 0)
    assert transform.parent_location(Location(1, 0)) == Location(0, 0)
    assert transform.parent_location(Location(2, 0)) == Location(1, 0)


# ---------------------------------------------------------------------------
# Vertical fix-to-paper regression: non-square grid (4 rows, 2 columns)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("column", [0, 1])
def test_vertical_parent_wrap_uses_num_rows_on_non_square_grid(column: int) -> None:
    """The row wraps to num_rows-1 (==3), not the buggy num_columns-1 (==1)."""
    transform = Vertical(MatrixSize(4, 2))
    assert transform.parent_location(Location(0, column)) == Location(3, column)
