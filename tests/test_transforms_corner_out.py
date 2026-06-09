"""Value-pinned tests for the TopLeftCornerOut location transform (Task 1, AC3.1).

The 8 matrix sizes and their full traversal + parent sequences are the
executable spec, ported from
``Test/.../locationtransform/TopLeftCornerOutSGMLocationTransformTest.java``.
Each entry is ``(row, column)``; the traversal starts at the base ``(0, 0)`` and
follows ``next_location`` until it wraps back to ``(0, 0)``. The parent sequence
is the ``parent_location`` of each non-base visited cell, in traversal order.

Both sequences were cross-checked against the JUnit source before pinning.
"""

from __future__ import annotations

import pytest

from raven_matrix.model import Location, MatrixSize
from raven_matrix.transforms.geometric import TopLeftCornerOut

# (rows, cols): (full traversal as (r, c) tuples, parent sequence as (r, c) tuples)
PINNED: dict[tuple[int, int], tuple[list[tuple[int, int]], list[tuple[int, int]]]] = {
    (3, 3): (
        [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (2, 1), (1, 2), (2, 2)],
        [(0, 0), (0, 0), (1, 0), (0, 1), (0, 1), (1, 1), (0, 2), (1, 2)],
    ),
    (1, 1): (
        [(0, 0)],
        [],
    ),
    (1, 4): (
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 0), (0, 1), (0, 2)],
    ),
    (4, 1): (
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, 0), (1, 0), (2, 0)],
    ),
    (2, 4): (
        [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3)],
        [(0, 0), (0, 0), (0, 1), (0, 1), (0, 2), (0, 2), (0, 3)],
    ),
    (4, 2): (
        [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (3, 0), (2, 1), (3, 1)],
        [(0, 0), (0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (2, 1)],
    ),
    (3, 5): (
        [
            (0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (2, 1), (1, 2),
            (0, 3), (2, 2), (1, 3), (0, 4), (2, 3), (1, 4), (2, 4),
        ],
        [
            (0, 0), (0, 0), (1, 0), (0, 1), (0, 1), (1, 1), (0, 2), (0, 2),
            (1, 2), (0, 3), (0, 3), (1, 3), (0, 4), (1, 4),
        ],
    ),
    (10, 3): (
        [
            (0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (3, 0), (2, 1),
            (1, 2), (4, 0), (3, 1), (2, 2), (5, 0), (4, 1), (3, 2), (6, 0),
            (5, 1), (4, 2), (7, 0), (6, 1), (5, 2), (8, 0), (7, 1), (6, 2),
            (9, 0), (8, 1), (7, 2), (9, 1), (8, 2), (9, 2),
        ],
        [
            (0, 0), (0, 0), (1, 0), (0, 1), (0, 1), (2, 0), (1, 1), (0, 2),
            (3, 0), (2, 1), (1, 2), (4, 0), (3, 1), (2, 2), (5, 0), (4, 1),
            (3, 2), (6, 0), (5, 1), (4, 2), (7, 0), (6, 1), (5, 2), (8, 0),
            (7, 1), (6, 2), (8, 1), (7, 2), (8, 2),
        ],
    ),
}

SIZES = list(PINNED.keys())


def _walk(transform: TopLeftCornerOut, base: Location) -> list[Location]:
    """Visited locations: base, then next_location until it wraps to base."""
    visited = [base]
    current = transform.next_location(base)
    while current != base:
        visited.append(current)
        current = transform.next_location(current)
    return visited


@pytest.mark.parametrize("size", SIZES)
def test_base_location_is_top_left_corner(size: tuple[int, int]) -> None:
    rows, cols = size
    transform = TopLeftCornerOut(MatrixSize(rows, cols))
    assert transform.base_locations() == [Location(0, 0)]


@pytest.mark.parametrize("size", SIZES)
def test_traversal_matches_pinned_sequence(size: tuple[int, int]) -> None:
    rows, cols = size
    expected_traversal, _ = PINNED[size]
    transform = TopLeftCornerOut(MatrixSize(rows, cols))

    visited = _walk(transform, Location(0, 0))

    assert visited == [Location(r, c) for r, c in expected_traversal]


@pytest.mark.parametrize("size", SIZES)
def test_traversal_wraps_back_to_base(size: tuple[int, int]) -> None:
    rows, cols = size
    transform = TopLeftCornerOut(MatrixSize(rows, cols))

    visited = _walk(transform, Location(0, 0))
    # next_location of the final visited cell returns to the base.
    assert transform.next_location(visited[-1]) == Location(0, 0)


@pytest.mark.parametrize("size", SIZES)
def test_parent_of_each_non_base_cell_matches_pinned_sequence(
    size: tuple[int, int],
) -> None:
    rows, cols = size
    expected_traversal, expected_parents = PINNED[size]
    transform = TopLeftCornerOut(MatrixSize(rows, cols))

    non_base = [Location(r, c) for r, c in expected_traversal[1:]]
    parents = [transform.parent_location(loc) for loc in non_base]

    assert parents == [Location(r, c) for r, c in expected_parents]


def test_parent_of_base_location_raises() -> None:
    transform = TopLeftCornerOut(MatrixSize(3, 3))
    with pytest.raises(ValueError):
        transform.parent_location(Location(0, 0))
