"""Tests for structure/base.py — base relations (Task 3).

Ports the upstream ``structure/base`` package:

- ``ShapeRepetition`` <- ``ShapeRepetitionSGMStructureFeature.java``: cycles a
  pre-built feature list by ``base_index % len`` (l.94-99); the single-arg
  ``transform_surface_features`` returns the previous location's features
  unchanged (l.101-105).
- ``LogicalAND/OR/XOR`` <- ``Logical{AND,OR,XOR}SGMStructureFeature.java`` +
  ``AbstractLogicOperationSGMStructureFeature.java``: operate over feature lists
  from TWO prior cells via IDENTITY membership (Python ``in``/``is`` over
  ``SurfaceFeature``, which has identity equality), sharing instances.
    - AND (l.66-84): features in cell-one that are also (by identity) in cell-two.
    - OR  (l.74-97): cell-one features, then cell-two features not already present.
    - XOR (l.65-91): features in exactly one of the two.
  The base-location assignment (``AbstractLogicOperationSGMStructureFeature``
  ctor l.62-156) draws ``next_int(n+1)`` per location then ``next_int(n)`` per
  pick, looping until every feature is used and every location populated. The
  single-arg ``transform_surface_features`` raises (l.167-175,
  bug-catalog ``base-logic-singlearg-transform-throws``, REPLICATE).

DR7 witness: AND/OR/XOR over hand-built 2x2 source cells of SHARED instances
reproduce intersection/union/symmetric-difference BY IDENTITY, and a
value-equal-but-DISTINCT instance is treated as ABSENT.
"""

from __future__ import annotations

import pytest

from raven_matrix.model import (
    Fill,
    MatrixSize,
    Point,
    Shape,
    SurfaceFeature,
)
from raven_matrix.rng import JavaRandom
from raven_matrix.structure.base import (
    LogicalAND,
    LogicalOR,
    LogicalXOR,
    LogicOperation,
    ShapeRepetition,
)
from raven_matrix.transforms.geometric import Horizontal
from raven_matrix.transforms.logic import LogicLocationTransform

_CELL = 256


def _feature(shape: Shape = Shape.ELLIPSE, fill: Fill = Fill.WHITE) -> SurfaceFeature:
    """A SurfaceFeature with all required fields (width/height mandatory)."""
    return SurfaceFeature(
        shape=shape,
        fill=fill,
        scale=1.0,
        rotation=0.0,
        position=Point(128.0, 128.0),
        width=64.0,
        height=128.0,
    )


# ---------------------------------------------------------------------------
# ShapeRepetition
# ---------------------------------------------------------------------------

def test_shape_repetition_cycles_base_features_by_index_mod_len() -> None:
    """provide_base_surface_features returns base[idx % len] (l.94-99)."""
    transform = Horizontal(MatrixSize(3, 3))
    a, b, c = [_feature()], [_feature()], [_feature()]
    relation = ShapeRepetition(transform, [a, b, c])

    assert relation.provide_base_surface_features(0) is a
    assert relation.provide_base_surface_features(1) is b
    assert relation.provide_base_surface_features(2) is c
    # Wraps by modulo.
    assert relation.provide_base_surface_features(3) is a
    assert relation.provide_base_surface_features(4) is b


def test_shape_repetition_transform_returns_previous_unchanged() -> None:
    """transform_surface_features returns the previous-location list as-is."""
    transform = Horizontal(MatrixSize(3, 3))
    relation = ShapeRepetition(transform, [[_feature()]])
    previous = [_feature(Shape.RECTANGLE), _feature(Shape.TEE)]
    assert relation.transform_surface_features(previous) is previous


def test_shape_repetition_exposes_its_location_transform() -> None:
    transform = Horizontal(MatrixSize(3, 3))
    relation = ShapeRepetition(transform, [[_feature()]])
    assert relation.location_transform is transform


# ---------------------------------------------------------------------------
# Logic ops — base-location assignment (the constructor draws)
# ---------------------------------------------------------------------------

def test_logic_assignment_uses_every_feature_and_populates_every_location() -> None:
    """The assignment loop terminates only when all features used and all
    base locations populated (AbstractLogicOperationSGMStructureFeature ctor)."""
    transform = LogicLocationTransform(MatrixSize(3, 3))
    features = [_feature(Shape.ELLIPSE), _feature(Shape.RECTANGLE), _feature(Shape.TEE)]
    relation = LogicalAND(transform, features, JavaRandom(7))

    base_indices = range(len(transform.base_locations()))
    assigned_lists = [relation.provide_base_surface_features(i) for i in base_indices]

    # Every base location got a (possibly empty-then-refilled) list.
    assert all(lst is not None for lst in assigned_lists)
    # Every base location ends up populated (the loop's terminating condition).
    assert all(len(lst) >= 1 for lst in assigned_lists)
    # Every feature instance was used at least once, by identity.
    used = {id(f) for lst in assigned_lists for f in lst}
    assert used == {id(f) for f in features}


def test_logic_assignment_shares_instances_not_copies() -> None:
    """Assigned features are the SAME objects passed in (shared, by identity)."""
    transform = LogicLocationTransform(MatrixSize(3, 3))
    features = [_feature(Shape.ELLIPSE), _feature(Shape.RECTANGLE), _feature(Shape.TEE)]
    relation = LogicalOR(transform, features, JavaRandom(3))

    for i in range(len(transform.base_locations())):
        for f in relation.provide_base_surface_features(i):
            assert any(f is original for original in features)


def test_logic_assignment_is_deterministic_for_a_seed() -> None:
    """Same seed -> identical assignment (by identity positions)."""
    transform = LogicLocationTransform(MatrixSize(3, 3))
    features = [_feature(Shape.ELLIPSE), _feature(Shape.RECTANGLE), _feature(Shape.TEE)]

    def assignment(seed: int) -> list[list[int]]:
        rel = LogicalXOR(transform, features, JavaRandom(seed))
        return [
            [features.index(f) for f in rel.provide_base_surface_features(i)]
            for i in range(len(transform.base_locations()))
        ]

    assert assignment(11) == assignment(11)


def test_logic_assignment_no_duplicate_feature_per_location() -> None:
    """Each base location holds each feature at most once.

    bug-catalog base-logic-dedup-typemismatch (FIX-TO-PAPER): upstream guards
    the per-location add with ``list.contains(featureIndex)`` on a
    ``List<SGMSurfaceFeature>`` (an int vs feature-list type mismatch that is
    always false), so a location could receive the same feature twice. The port
    checks feature membership by value, so no location holds a duplicate.
    """
    transform = LogicLocationTransform(MatrixSize(3, 3))
    features = [_feature(Shape.ELLIPSE), _feature(Shape.RECTANGLE), _feature(Shape.TEE)]
    relation = LogicalAND(transform, features, JavaRandom(123))

    for i in range(len(transform.base_locations())):
        assigned = relation.provide_base_surface_features(i)
        ids = [id(f) for f in assigned]
        assert len(ids) == len(set(ids)), f"duplicate feature at base location {i}"


def test_logic_pool_must_be_value_distinct_or_raises() -> None:
    """A value-duplicate base pool fails fast (ValueError), not hangs.

    The assignment loop only terminates once every feature is placed. With value
    dedup, a value-equal feature can be blocked from every location yet never
    placed, so the loop would spin forever. The real generator never produces a
    value-duplicate pool (BaseSGMStructureFeatureGenerator.containsCheck), but the
    precondition is asserted at the boundary so a violation is a clear error
    rather than a hang.
    """
    transform = LogicLocationTransform(MatrixSize(3, 3))
    twin_a = _feature(Shape.ELLIPSE, Fill.WHITE)
    twin_b = _feature(Shape.ELLIPSE, Fill.WHITE)  # value-equal, distinct instance
    assert twin_a.value_equals(twin_b) and twin_a is not twin_b
    with pytest.raises(ValueError, match="value-distinct"):
        LogicalAND(transform, [twin_a, twin_b], JavaRandom(0))


# ---------------------------------------------------------------------------
# Logic ops — the two-cell combine (DR7 identity witness)
# ---------------------------------------------------------------------------

def _logic_relation(
    op: type[LogicOperation], features: list[SurfaceFeature]
) -> LogicOperation:
    """Build a logic relation; the seed only drives the unused base assignment."""
    return op(LogicLocationTransform(MatrixSize(3, 3)), features, JavaRandom(1))


def test_logical_and_intersection_by_identity() -> None:
    """AND = features of cell-one also present (by identity) in cell-two."""
    shared_x = _feature(Shape.ELLIPSE)
    shared_y = _feature(Shape.RECTANGLE)
    only_one = _feature(Shape.TEE)
    only_two = _feature(Shape.DIAMOND)

    relation = _logic_relation(LogicalAND, [shared_x, shared_y, only_one, only_two])
    cell_one = [shared_x, shared_y, only_one]
    cell_two = [shared_x, shared_y, only_two]

    result = relation.combine_surface_features(cell_one, cell_two)
    assert [id(f) for f in result] == [id(shared_x), id(shared_y)]


def test_logical_or_union_preserves_order_by_identity() -> None:
    """OR = cell-one, then cell-two features not already present by identity."""
    shared = _feature(Shape.ELLIPSE)
    only_one = _feature(Shape.RECTANGLE)
    only_two = _feature(Shape.TEE)

    relation = _logic_relation(LogicalOR, [shared, only_one, only_two])
    cell_one = [shared, only_one]
    cell_two = [shared, only_two]

    result = relation.combine_surface_features(cell_one, cell_two)
    assert [id(f) for f in result] == [id(shared), id(only_one), id(only_two)]


def test_logical_xor_symmetric_difference_by_identity() -> None:
    """XOR = features in exactly one of the two cells (by identity)."""
    shared = _feature(Shape.ELLIPSE)
    only_one = _feature(Shape.RECTANGLE)
    only_two = _feature(Shape.TEE)

    relation = _logic_relation(LogicalXOR, [shared, only_one, only_two])
    cell_one = [shared, only_one]
    cell_two = [shared, only_two]

    result = relation.combine_surface_features(cell_one, cell_two)
    # cell-one-only first (only_one), then cell-two-only (only_two); shared dropped.
    assert [id(f) for f in result] == [id(only_one), id(only_two)]


def test_value_equal_but_distinct_instance_is_absent_and() -> None:
    """DR7 witness: a value-equal-but-DISTINCT instance is NOT a member (AND)."""
    original = _feature(Shape.ELLIPSE, Fill.WHITE)
    twin = _feature(Shape.ELLIPSE, Fill.WHITE)  # value-equal, distinct object
    assert original.value_equals(twin)  # value-equal...
    assert original is not twin  # ...but a different instance.

    # The base pool must be value-distinct (precondition); the twin lives in the
    # combine cells, which is where the identity-vs-value distinction is tested.
    relation = _logic_relation(LogicalAND, [original, _feature(Shape.RECTANGLE)])
    # cell-one has the original; cell-two has only the value-equal twin.
    result = relation.combine_surface_features([original], [twin])
    # By identity the twin is absent, so the intersection is empty.
    assert result == []


def test_value_equal_but_distinct_instance_is_absent_xor() -> None:
    """DR7 witness: value-equal-but-distinct instances both survive XOR.

    Because membership is by identity, neither instance counts as present in the
    other cell, so both are emitted (a value-based XOR would drop both).
    """
    original = _feature(Shape.ELLIPSE, Fill.WHITE)
    twin = _feature(Shape.ELLIPSE, Fill.WHITE)
    assert original.value_equals(twin) and original is not twin

    # Pool must be value-distinct (precondition); the twin lives in the cells.
    relation = _logic_relation(LogicalXOR, [original, _feature(Shape.RECTANGLE)])
    result = relation.combine_surface_features([original], [twin])
    assert [id(f) for f in result] == [id(original), id(twin)]


def test_logic_single_arg_transform_raises() -> None:
    """The single-arg transform is the throwing special case (l.167-175)."""
    relation = _logic_relation(
        LogicalOR, [_feature(), _feature(Shape.TEE), _feature(Shape.DIAMOND)]
    )
    with pytest.raises(NotImplementedError):
        relation.transform_surface_features([_feature()])
