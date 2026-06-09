"""Tests for structure/supplemental.py — supplemental relations (Task 4).

Ports the upstream ``structure/supplemental`` package. Each supplemental has two
hooks (``AbstractSupplementalSGMStructureFeature``): ``provide_base_surface_features
(base_index, existing)`` for base cells, and ``transform_surface_features(previous,
existing)`` for derived cells (``previous`` = the parent cell's features,
``existing`` = what the base relation already placed at this cell).

Pinned params (SupplementalSGMStructureFeatureGenerator.java):
- ApplyRotation: rotate amount 45, ADDITIVE (l.234-235; ApplyRotation...java:95-96).
- ApplyScaling: scale amount 0.66, MULTIPLICATIVE (l.213; ApplyScaling...java:85).
- ChangeFillPattern: cycle [White,Grey75,Grey40,Grey10,Black] (l.255-259); base
  -> cycle[0], derived -> cycle[(index_of(parent.fill)+1) % len]
  (ChangeFill...java:83,102-105).
- FillPatternRepetition: cycle [White,Black,Grey75] (l.224-226); base ->
  cycle[idx % len], derived inherit parent fill (FillRep...java:108-110,128).
- TranslationalNumerosity: initial 1-2 copies at base, len(previous)+1 at derived;
  numPositions/positionStepSize/scaling per the ctor (Numerosity...java:100-123),
  base scale OVERWRITE = scaling, derived scale MULTIPLY = scaling*scale
  (l.153 vs l.201).
"""

from __future__ import annotations

import math

from raven_matrix.fillpattern import CHANGE_FILL_CYCLE, FILL_REP_CYCLE
from raven_matrix.model import (
    Fill,
    MatrixSize,
    Point,
    Shape,
    SurfaceFeature,
)
from raven_matrix.structure.supplemental import (
    ApplyRotation,
    ApplyScaling,
    ChangeFillPattern,
    FillPatternRepetition,
    TranslationalNumerosity,
)
from raven_matrix.transforms.geometric import Horizontal

_CELL = 256
_CENTRE = Point(128.0, 128.0)


def _feature(
    *,
    shape: Shape = Shape.ELLIPSE,
    fill: Fill = Fill.WHITE,
    scale: float = 1.0,
    rotation: float = 0.0,
    position: Point = _CENTRE,
    width: float = 64.0,
    height: float = 128.0,
) -> SurfaceFeature:
    return SurfaceFeature(
        shape=shape,
        fill=fill,
        scale=scale,
        rotation=rotation,
        position=position,
        width=width,
        height=height,
    )


def _horizontal() -> Horizontal:
    return Horizontal(MatrixSize(3, 3))


# ---------------------------------------------------------------------------
# ApplyRotation — additive, 45 degrees
# ---------------------------------------------------------------------------

def test_rotation_base_passes_existing_through() -> None:
    """Repetition base hook returns the existing features unchanged (l.82-87)."""
    relation = ApplyRotation(_horizontal(), 45)
    existing = [_feature()]
    assert relation.provide_base_surface_features(0, existing) is existing


def test_rotation_derived_is_additive_over_parent() -> None:
    """derived.rotation = rotate_amount + parent.rotation (ApplyRotation...java:95)."""
    relation = ApplyRotation(_horizontal(), 45)
    previous = [_feature(rotation=45.0)]
    existing = [_feature(rotation=0.0)]

    result = relation.transform_surface_features(previous, existing)

    assert len(result) == 1
    assert result[0].rotation == 90.0  # 45 + 45
    # Operates on a fresh clone, not the existing instance.
    assert result[0] is not existing[0]


def test_rotation_chain_accumulates() -> None:
    """Across a 3-cell chain rotation accrues 45 each step (0 -> 45 -> 90)."""
    relation = ApplyRotation(_horizontal(), 45)
    cell0 = [_feature(rotation=0.0)]
    cell1 = relation.transform_surface_features(cell0, [_feature(rotation=0.0)])
    cell2 = relation.transform_surface_features(cell1, [_feature(rotation=0.0)])
    assert cell1[0].rotation == 45.0
    assert cell2[0].rotation == 90.0


# ---------------------------------------------------------------------------
# ApplyScaling — multiplicative, 0.66
# ---------------------------------------------------------------------------

def test_scaling_derived_is_multiplicative_over_parent() -> None:
    """derived.scale = scale_amount * parent.scale (ApplyScaling...java:85)."""
    relation = ApplyScaling(_horizontal(), 0.66)
    previous = [_feature(scale=1.0)]
    existing = [_feature(scale=1.0)]

    result = relation.transform_surface_features(previous, existing)

    assert result[0].scale == 0.66
    assert result[0] is not existing[0]


def test_scaling_chain_multiplies() -> None:
    """Across a 3-cell chain scale multiplies by 0.66 each step."""
    relation = ApplyScaling(_horizontal(), 0.66)
    cell0 = [_feature(scale=1.0)]
    cell1 = relation.transform_surface_features(cell0, [_feature(scale=1.0)])
    cell2 = relation.transform_surface_features(cell1, [_feature(scale=1.0)])
    assert cell1[0].scale == 0.66
    assert cell2[0].scale == 0.66 * 0.66


# ---------------------------------------------------------------------------
# ChangeFillPattern — cycle [White,Grey75,Grey40,Grey10,Black]
# ---------------------------------------------------------------------------

def test_change_fill_base_uses_cycle_zero() -> None:
    """Base cells all take cycle[0] = White (ChangeFill...java:83)."""
    relation = ChangeFillPattern(_horizontal(), CHANGE_FILL_CYCLE)
    existing = [_feature(fill=Fill.BLACK)]
    result = relation.provide_base_surface_features(0, existing)
    assert result[0].fill is CHANGE_FILL_CYCLE[0]
    assert result[0].fill is Fill.WHITE
    assert result[0] is not existing[0]  # cloned


def test_change_fill_derived_advances_cycle() -> None:
    """derived.fill = cycle[(index_of(parent.fill)+1) % len] (java:102-105)."""
    relation = ChangeFillPattern(_horizontal(), CHANGE_FILL_CYCLE)
    # parent fill White (index 0) -> derived Grey75 (index 1)
    previous = [_feature(fill=Fill.WHITE)]
    existing = [_feature(fill=Fill.WHITE)]
    result = relation.transform_surface_features(previous, existing)
    assert result[0].fill is Fill.GREY75


def test_change_fill_wraps_at_end_of_cycle() -> None:
    """Edge: parent fill Black (last index) wraps to cycle[0] = White."""
    relation = ChangeFillPattern(_horizontal(), CHANGE_FILL_CYCLE)
    previous = [_feature(fill=Fill.BLACK)]  # index 4 (last)
    existing = [_feature(fill=Fill.BLACK)]
    result = relation.transform_surface_features(previous, existing)
    assert result[0].fill is Fill.WHITE  # (4 + 1) % 5 == 0


def test_change_fill_full_cycle_progression() -> None:
    """Walking the cycle from White visits every fill then wraps."""
    relation = ChangeFillPattern(_horizontal(), CHANGE_FILL_CYCLE)
    fill = Fill.WHITE
    seen = [fill]
    for _ in range(len(CHANGE_FILL_CYCLE)):
        result = relation.transform_surface_features(
            [_feature(fill=fill)], [_feature(fill=fill)]
        )
        fill = result[0].fill
        seen.append(fill)
    # 5 advances from White returns to White; all five fills appear.
    assert seen == [
        Fill.WHITE,
        Fill.GREY75,
        Fill.GREY40,
        Fill.GREY10,
        Fill.BLACK,
        Fill.WHITE,
    ]


# ---------------------------------------------------------------------------
# FillPatternRepetition — cycle [White,Black,Grey75]
# ---------------------------------------------------------------------------

def test_fill_rep_base_cycles_by_index() -> None:
    """Base cells take cycle[idx % len] (FillRep...java:108-110)."""
    relation = FillPatternRepetition(_horizontal(), FILL_REP_CYCLE)
    existing = [_feature(fill=Fill.GREY40)]
    assert relation.provide_base_surface_features(0, existing)[0].fill is Fill.WHITE
    assert relation.provide_base_surface_features(1, existing)[0].fill is Fill.BLACK
    assert relation.provide_base_surface_features(2, existing)[0].fill is Fill.GREY75
    # Wraps.
    assert relation.provide_base_surface_features(3, existing)[0].fill is Fill.WHITE


def test_fill_rep_derived_inherits_parent_fill() -> None:
    """derived.fill = parent.fill (FillRep...java:128)."""
    relation = FillPatternRepetition(_horizontal(), FILL_REP_CYCLE)
    previous = [_feature(fill=Fill.BLACK)]
    existing = [_feature(fill=Fill.WHITE)]
    result = relation.transform_surface_features(previous, existing)
    assert result[0].fill is Fill.BLACK
    assert result[0] is not existing[0]  # cloned


# ---------------------------------------------------------------------------
# TranslationalNumerosity — count + layout
# ---------------------------------------------------------------------------

def _expected_num_positions(size: MatrixSize, initial: int) -> int:
    """Non-TopLeftCornerOut formula: ceil(sqrt(maxDim + (initial - 1)))."""
    max_dim = max(size.num_rows, size.num_columns)
    return math.ceil(math.sqrt(max_dim + (initial - 1)))


def test_numerosity_base_produces_initial_copies() -> None:
    """Base hook makes initial_numerosity clones of existing[0] (java:142-146)."""
    size = MatrixSize(3, 3)
    relation = TranslationalNumerosity(_horizontal(), _CELL, size, initial_numerosity=2)
    existing = [_feature()]
    result = relation.provide_base_surface_features(0, existing)
    assert len(result) == 2
    assert all(f is not existing[0] for f in result)  # all clones


def test_numerosity_empty_existing_returns_empty_fail_safe() -> None:
    """Empty ``existing`` yields no copies instead of an IndexError (fail-safe).

    Mirrors the upstream null guard
    (TranslationalNumerositySGMStructureFeature.java:131,170) and extends it to
    the empty case, plus guards the transform path the upstream leaves unguarded
    (catalog ``numerosity-transform-null-deref``, flag-and-decide -> fail-safe).
    Unreachable on the single-layer path, but a multi-layer/impoverished config
    could pass an empty list.
    """
    size = MatrixSize(3, 3)
    relation = TranslationalNumerosity(
        _horizontal(), _CELL, size, initial_numerosity=2
    )
    assert relation.provide_base_surface_features(0, []) == []
    assert relation.transform_surface_features([_feature()], []) == []


def test_numerosity_base_scale_is_overwrite() -> None:
    """Base path OVERWRITES scale to the computed scaling (java:153)."""
    size = MatrixSize(3, 3)
    initial = 1
    relation = TranslationalNumerosity(
        _horizontal(), _CELL, size, initial_numerosity=initial
    )
    num_positions = _expected_num_positions(size, initial)
    expected_scaling = 0.75 / num_positions
    existing = [_feature(scale=1.0)]
    result = relation.provide_base_surface_features(0, existing)
    assert result[0].scale == expected_scaling


def test_numerosity_derived_count_is_previous_plus_one() -> None:
    """Derived count = len(previous) + 1 (the <= bound, java:190)."""
    size = MatrixSize(3, 3)
    relation = TranslationalNumerosity(_horizontal(), _CELL, size, initial_numerosity=1)
    previous = [_feature(), _feature()]  # 2 features at previous location
    existing = [_feature()]
    result = relation.transform_surface_features(previous, existing)
    assert len(result) == 3  # 2 + 1


def test_numerosity_derived_scale_is_multiplicative() -> None:
    """Derived path MULTIPLIES scale by scaling (java:201)."""
    size = MatrixSize(3, 3)
    initial = 1
    relation = TranslationalNumerosity(
        _horizontal(), _CELL, size, initial_numerosity=initial
    )
    num_positions = _expected_num_positions(size, initial)
    scaling = 0.75 / num_positions
    previous = [_feature()]
    existing = [_feature(scale=2.0)]
    result = relation.transform_surface_features(previous, existing)
    # 2 clones, each scale = scaling * existing.scale.
    assert len(result) == 2
    assert all(f.scale == scaling * 2.0 for f in result)


def test_numerosity_lays_out_positions_on_grid() -> None:
    """Positions step by positionStepSize, wrapping columns at numPositions."""
    size = MatrixSize(3, 3)
    initial = 2
    relation = TranslationalNumerosity(
        _horizontal(), _CELL, size, initial_numerosity=initial
    )
    num_positions = _expected_num_positions(size, initial)
    step = _CELL / (num_positions + 1)
    existing = [_feature()]
    result = relation.provide_base_surface_features(0, existing)
    # First feature at (col 0, row 0) -> ((0+1)*step, (0+1)*step).
    assert result[0].position == Point(step, step)


def test_numerosity_topleftcornerout_uses_other_formula() -> None:
    """TopLeftCornerOut numPositions = ceil(sqrt(rows + cols - 1)) (java:107-109)."""
    from raven_matrix.transforms.geometric import TopLeftCornerOut

    size = MatrixSize(3, 3)
    transform = TopLeftCornerOut(size)
    relation = TranslationalNumerosity(transform, _CELL, size, initial_numerosity=1)
    expected_num_positions = math.ceil(
        math.sqrt(size.num_rows + size.num_columns - 1)
    )
    expected_scaling = 0.75 / expected_num_positions
    existing = [_feature(scale=1.0)]
    result = relation.provide_base_surface_features(0, existing)
    assert result[0].scale == expected_scaling
