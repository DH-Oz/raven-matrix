"""Tests for surface.py — generate_surface_feature (Task 2).

Ported from SGMSurfaceFeatureGenerator.java:134-202. The draw order under test:

  1. width   = next_int(3)  -> quarter*(n+1)             (l.134)
  2. height  = next_int(2)  -> ONLY when width is the smallest (1/4) size,
                              else fixed (no draw)        (l.137-143)
  3. swap    = next_boolean()  (always)                  (l.144)
  4. fill    = generate_fill -> next_int(3)              (l.158-161)
  5. shape   = next_int(6), or next_int(7) when Line enabled (l.164)

Pre-fill draws are 2 or 3 (3 only when the height draw fires).

Shape index -> class (live switch, l.165-202):
  0 Ellipse (l.167), 1 Rectangle (l.172), 2 Triangle (l.177), 3 Tee (l.182),
  4 Diamond (l.187), 5 Trapezoid (l.192). The commented-out case at l.197-201
  is a STALE `case 4` for Line that the live switch already uses for Diamond;
  Line participates only under line_shape_enabled, as a NEW index 6.

AC6.1: default flags never draw Line and use bound 6; line_shape_enabled widens
the draw to bound 7 and lets Line appear.
"""

from __future__ import annotations

from raven_matrix.compat import DEFAULT_FLAGS, CompatFlags
from raven_matrix.fillpattern import BASE_FILL_CATALOGUE
from raven_matrix.model import Point, Shape
from raven_matrix.rng import JavaRandom
from raven_matrix.surface import generate_surface_feature

_CELL = 256  # quarter = 64, half = 128


# --- shape index -> class, mirroring the live switch (l.165-202) ---
_SHAPE_BY_INDEX = {
    0: Shape.ELLIPSE,
    1: Shape.RECTANGLE,
    2: Shape.TRIANGLE,
    3: Shape.TEE,
    4: Shape.DIAMOND,
    5: Shape.TRAPEZOID,
    6: Shape.LINE,  # only reachable when line_shape_enabled
}


def _replay(seed: int, cell: int, *, line_enabled: bool) -> dict:
    """Independently replay the pinned draw sequence on a reference JavaRandom.

    Returns the drawn values plus the reference rng's final internal seed, so a
    test can assert the generator consumed exactly the same draws in the same
    order (same end state).
    """
    r = JavaRandom(seed)
    quarter = (cell / 2.0) / 2.0
    half = cell / 2.0
    width = (float(r.next_int(3)) * quarter) + quarter
    height_drew = False
    if width == 2 * quarter:
        height = 3 * quarter
    elif width == 3 * quarter:
        height = 2 * quarter
    else:
        height = (float(r.next_int(2)) * quarter) + half
        height_drew = True
    swap = r.next_boolean()
    if swap:
        width, height = height, width
    fill_index = r.next_int(3)
    shape_index = r.next_int(7 if line_enabled else 6)
    return {
        "width": width,
        "height": height,
        "height_drew": height_drew,
        "swap": swap,
        "fill": BASE_FILL_CATALOGUE[fill_index],
        "shape": _SHAPE_BY_INDEX[shape_index],
        "final_seed": r._seed,
    }


# ---------------------------------------------------------------------------
# Draw order / draw count, against a reference JavaRandom (both branches)
# Seed 0 -> width index 0 (smallest) -> 3 pre-fill draws.
# Seed 2 -> width index 1            -> 2 pre-fill draws.
# ---------------------------------------------------------------------------

def test_three_prefill_draws_branch_seed0() -> None:
    """Seed 0: smallest width fires the height draw (3 pre-fill draws)."""
    expected = _replay(0, _CELL, line_enabled=False)
    assert expected["height_drew"] is True  # this seed exercises the height draw

    rng = JavaRandom(0)
    feature = generate_surface_feature(rng, DEFAULT_FLAGS, _CELL)

    assert feature.width == expected["width"]
    assert feature.height == expected["height"]
    assert feature.fill is expected["fill"]
    assert feature.shape is expected["shape"]
    # Same end state proves the generator consumed exactly: width, height, swap,
    # fill, shape — the 3-pre-fill-draw sequence — in that order.
    assert rng._seed == expected["final_seed"]


def test_two_prefill_draws_branch_seed2() -> None:
    """Seed 2: larger width skips the height draw (2 pre-fill draws)."""
    expected = _replay(2, _CELL, line_enabled=False)
    assert expected["height_drew"] is False  # this seed skips the height draw

    rng = JavaRandom(2)
    feature = generate_surface_feature(rng, DEFAULT_FLAGS, _CELL)

    assert feature.width == expected["width"]
    assert feature.height == expected["height"]
    assert feature.fill is expected["fill"]
    assert feature.shape is expected["shape"]
    assert rng._seed == expected["final_seed"]


def test_fixed_rotation_zero_and_centre_position() -> None:
    """Rotation is 0; position is the cell centre (half, half); scale is 1.0."""
    feature = generate_surface_feature(JavaRandom(0), DEFAULT_FLAGS, _CELL)
    assert feature.rotation == 0
    assert feature.position == Point(_CELL / 2.0, _CELL / 2.0)
    assert feature.scale == 1.0


def test_width_never_equals_height_for_default_shapes() -> None:
    """The generator's draw forbids squares/circles (width != height)."""
    for seed in range(50):
        feature = generate_surface_feature(JavaRandom(seed), DEFAULT_FLAGS, _CELL)
        assert feature.width != feature.height, f"square at seed {seed}"


# ---------------------------------------------------------------------------
# AC6.1 — line_shape_enabled toggle
# ---------------------------------------------------------------------------

def test_default_flags_never_draw_line() -> None:
    """With default flags, Line is never produced across many seeds (bound 6)."""
    for seed in range(300):
        feature = generate_surface_feature(JavaRandom(seed), DEFAULT_FLAGS, _CELL)
        assert feature.shape is not Shape.LINE, f"Line drawn at seed {seed}"


def test_line_enabled_can_draw_line() -> None:
    """With line_shape_enabled, Line appears (seed 1 draws shape index 6)."""
    flags = CompatFlags(line_shape_enabled=True)
    expected = _replay(1, _CELL, line_enabled=True)
    assert expected["shape"] is Shape.LINE  # seed 1 is pinned to draw Line

    feature = generate_surface_feature(JavaRandom(1), flags, _CELL)
    assert feature.shape is Shape.LINE
    assert feature.width == expected["width"]


def test_line_enabled_changes_output_for_same_seed() -> None:
    """line_shape_enabled widens the shape draw to bound 7, changing the output.

    Pinned seed 1: the shape index is taken from next_int(6) (->Triangle, index
    2) under default flags vs next_int(7) (->Line, index 6) with the flag set.
    The produced shape therefore differs for the same seed — the observable
    effect of the wider draw bound. (The rng end-state can coincide because the
    rejection loop accepts the first candidate for both bounds; the meaningful,
    faithful difference is the chosen shape, not the internal seed.)
    """
    false_feature = generate_surface_feature(JavaRandom(1), DEFAULT_FLAGS, _CELL)
    true_feature = generate_surface_feature(
        JavaRandom(1), CompatFlags(line_shape_enabled=True), _CELL
    )
    assert false_feature.shape is not Shape.LINE
    assert true_feature.shape is Shape.LINE
    assert false_feature.shape is not true_feature.shape


def test_full_shape_mapping_matches_live_switch() -> None:
    """Every produced shape (default flags) is one of the six live-switch shapes.

    Guards the index->class mapping: no Line, and only the six live cases.
    """
    live_shapes = {
        Shape.ELLIPSE,
        Shape.RECTANGLE,
        Shape.TRIANGLE,
        Shape.TEE,
        Shape.DIAMOND,
        Shape.TRAPEZOID,
    }
    produced = {
        generate_surface_feature(JavaRandom(seed), DEFAULT_FLAGS, _CELL).shape
        for seed in range(300)
    }
    assert produced <= live_shapes
