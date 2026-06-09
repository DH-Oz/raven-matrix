"""Tests for the two diagonal transforms + odd-square constraint (Task 3).

Verifies AC3.2 (base/next/parent on a valid 3x3 odd-square) and AC3.3 (the
constraint that diagonals require an odd, square grid).

Sequences are hand-derived from
``DiagonalBottomLeftTopRightSGMLocationTransform`` /
``DiagonalTopLeftBottomRightSGMLocationTransform``.
"""

from __future__ import annotations

import pytest

from raven_matrix.model import Location, MatrixSize
from raven_matrix.transforms.geometric import (
    DiagonalBottomLeftTopRight,
    DiagonalTopLeftBottomRight,
)


def _full_next_cycle(transform, start: Location) -> list[Location]:
    visited = [start]
    current = transform.next_location(start)
    while current != start:
        visited.append(current)
        current = transform.next_location(current)
    return visited


# ---------------------------------------------------------------------------
# DiagonalBottomLeftTopRight (3x3)
# ---------------------------------------------------------------------------

def test_bl_tr_base_locations_climb_the_main_diagonal() -> None:
    transform = DiagonalBottomLeftTopRight(MatrixSize(3, 3))
    assert transform.base_locations() == [
        Location(0, 0), Location(1, 1), Location(2, 2)
    ]


def test_bl_tr_next_moves_up_and_right_wrapping() -> None:
    transform = DiagonalBottomLeftTopRight(MatrixSize(3, 3))
    assert _full_next_cycle(transform, Location(0, 0)) == [
        Location(0, 0), Location(2, 1), Location(1, 2)
    ]


def test_bl_tr_parent_moves_down_and_left_wrapping() -> None:
    transform = DiagonalBottomLeftTopRight(MatrixSize(3, 3))
    assert transform.parent_location(Location(0, 0)) == Location(1, 2)
    assert transform.parent_location(Location(1, 1)) == Location(2, 0)
    assert transform.parent_location(Location(2, 2)) == Location(0, 1)


# ---------------------------------------------------------------------------
# DiagonalTopLeftBottomRight (3x3)
# ---------------------------------------------------------------------------

def test_tl_br_base_locations_descend_the_anti_diagonal() -> None:
    transform = DiagonalTopLeftBottomRight(MatrixSize(3, 3))
    assert transform.base_locations() == [
        Location(2, 0), Location(1, 1), Location(0, 2)
    ]


def test_tl_br_next_moves_down_and_right_wrapping() -> None:
    transform = DiagonalTopLeftBottomRight(MatrixSize(3, 3))
    assert _full_next_cycle(transform, Location(0, 0)) == [
        Location(0, 0), Location(1, 1), Location(2, 2)
    ]


def test_tl_br_parent_moves_up_and_left_wrapping() -> None:
    transform = DiagonalTopLeftBottomRight(MatrixSize(3, 3))
    assert transform.parent_location(Location(0, 0)) == Location(2, 2)
    assert transform.parent_location(Location(1, 1)) == Location(0, 0)
    assert transform.parent_location(Location(2, 2)) == Location(1, 1)


# ---------------------------------------------------------------------------
# AC3.3 — odd-AND-square constraint, both diagonals
# ---------------------------------------------------------------------------

DIAGONALS = [DiagonalBottomLeftTopRight, DiagonalTopLeftBottomRight]
INVALID_SIZES = [
    MatrixSize(2, 2),  # even square
    MatrixSize(3, 5),  # odd but non-square
    MatrixSize(4, 4),  # even square
]
VALID_SIZES = [MatrixSize(3, 3), MatrixSize(5, 5)]


@pytest.mark.parametrize("cls", DIAGONALS)
@pytest.mark.parametrize("size", INVALID_SIZES)
def test_diagonal_rejects_even_or_non_square(cls, size: MatrixSize) -> None:
    with pytest.raises(ValueError):
        cls(size)


@pytest.mark.parametrize("cls", DIAGONALS)
@pytest.mark.parametrize("size", VALID_SIZES)
def test_diagonal_accepts_odd_square(cls, size: MatrixSize) -> None:
    transform = cls(size)
    assert len(transform.base_locations()) == size.num_columns


# ---------------------------------------------------------------------------
# Full next_location cycle from every base — parity with axis / corner-out tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cls", DIAGONALS)
def test_diagonal_full_next_cycle_from_every_base_on_3x3(cls) -> None:
    """Every base location on a 3×3 diagonal must yield a cycle of length 3.

    Walks ``next_location`` from each base and asserts the cycle revisits the
    start after exactly ``num_rows`` steps. Matches the full-cycle coverage in
    the axis and corner-out test files.
    """
    size = MatrixSize(3, 3)
    transform = cls(size)
    for base in transform.base_locations():
        cycle = _full_next_cycle(transform, base)
        assert len(cycle) == size.num_rows, (
            f"{cls.__name__}: cycle from {base} has length {len(cycle)}, "
            f"expected {size.num_rows}"
        )
        # Confirm the cycle closes back to the starting base.
        assert transform.next_location(cycle[-1]) == base, (
            f"{cls.__name__}: next_location({cycle[-1]}) does not return to base {base}"
        )
