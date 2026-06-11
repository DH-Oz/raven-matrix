"""Tests for fillpattern.py — base fill catalogue + generate_fill (Task 1).

Ported from SGMFillPatternGenerator.java:60-86 (the single-arg overload): a
nextInt(3) over the catalogue [White, Grey75, Black] (cases 0/1/2 at lines
74-83).  The supplemental cycles (CHANGE_FILL_CYCLE, FILL_REP_CYCLE) are pinned
here verbatim for the Task-4 supplementals to consume.
"""

from __future__ import annotations

from raven_matrix.fillpattern import (
    BASE_FILL_CATALOGUE,
    CHANGE_FILL_CYCLE,
    FILL_REP_CYCLE,
    generate_fill,
)
from raven_matrix.model import Fill
from raven_matrix.rng import JavaRandom

# ---------------------------------------------------------------------------
# Base catalogue order — SGMFillPatternGenerator.java:74-83 (case 0/1/2)
# ---------------------------------------------------------------------------


def test_base_catalogue_order_is_white_grey75_black() -> None:
    """The nextInt(3) catalogue is exactly [White, Grey75, Black] (l.74-83)."""
    assert BASE_FILL_CATALOGUE == [Fill.WHITE, Fill.GREY75, Fill.BLACK]


def test_generate_fill_returns_catalogue_element_at_drawn_index() -> None:
    """generate_fill(rng) == BASE_FILL_CATALOGUE[rng.next_int(3)] for a seed.

    Replay a separate reference JavaRandom to know the drawn index, then assert
    the generator returns the catalogue element at that index.
    """
    for seed in (0, 1, 2, 7, 42):
        reference = JavaRandom(seed)
        expected_index = reference.next_int(3)
        expected = BASE_FILL_CATALOGUE[expected_index]

        actual = generate_fill(JavaRandom(seed))

        assert actual is expected, (
            f"seed={seed}: drew index {expected_index} -> {expected}, got {actual}"
        )


def test_generate_fill_consumes_exactly_one_draw() -> None:
    """generate_fill advances the rng by exactly one next_int(3) draw."""
    rng = JavaRandom(0)
    reference = JavaRandom(0)
    generate_fill(rng)
    reference.next_int(3)
    assert rng._seed == reference._seed


# ---------------------------------------------------------------------------
# Supplemental cycles — pinned verbatim from the supplemental generators
# (consumed by Task 4: ChangeFillPattern / FillPatternRepetition)
# ---------------------------------------------------------------------------


def test_change_fill_cycle_order() -> None:
    """ChangeFill cycle = [White, Grey75, Grey40, Grey10, Black] (5 fills)."""
    assert CHANGE_FILL_CYCLE == [
        Fill.WHITE,
        Fill.GREY75,
        Fill.GREY40,
        Fill.GREY10,
        Fill.BLACK,
    ]


def test_fill_rep_cycle_order() -> None:
    """FillRep base cycle = [White, Black, Grey75]."""
    assert FILL_REP_CYCLE == [Fill.WHITE, Fill.BLACK, Fill.GREY75]
