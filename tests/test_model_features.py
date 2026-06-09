"""Tests for model.py — SurfaceFeature identity semantics and contains_check (Task 4).

AC1.5: value-equal-but-distinct SurfaceFeatures are treated as distinct under
identity (==, list `in`), but value_equals() and contains_check() find them.
"""

from __future__ import annotations


def _make_feature(shape=None, fill=None, scale=1.0, rotation=0.0, x=0.0, y=0.0):
    """Build a SurfaceFeature with sensible defaults."""
    from raven_matrix.model import Fill, Point, Shape, SurfaceFeature

    return SurfaceFeature(
        shape=shape or Shape.DIAMOND,
        fill=fill or Fill.BLACK,
        scale=scale,
        rotation=rotation,
        position=Point(x, y),
    )


# ---------------------------------------------------------------------------
# AC1.5 — identity semantics
# ---------------------------------------------------------------------------

def test_value_equal_features_are_identity_unequal() -> None:
    """Two SurfaceFeatures with identical field values must not be == (identity)."""
    a = _make_feature()
    b = _make_feature()
    assert a is not b
    assert a != b  # default identity ==


def test_value_equal_feature_not_in_list_by_identity() -> None:
    """list `in` uses == (identity), so b is not found in [a] even when value-equal."""
    a = _make_feature()
    b = _make_feature()
    assert b not in [a]


def test_value_equals_true_for_value_equal_distinct_instances() -> None:
    """value_equals() must return True for two identical-field distinct objects."""
    a = _make_feature()
    b = _make_feature()
    assert a is not b
    assert a.value_equals(b)


def test_value_equals_false_when_shape_differs() -> None:
    from raven_matrix.model import Shape
    a = _make_feature(shape=Shape.DIAMOND)
    b = _make_feature(shape=Shape.ELLIPSE)
    assert not a.value_equals(b)


def test_value_equals_false_when_fill_differs() -> None:
    from raven_matrix.model import Fill
    a = _make_feature(fill=Fill.BLACK)
    b = _make_feature(fill=Fill.WHITE)
    assert not a.value_equals(b)


def test_value_equals_false_when_scale_differs() -> None:
    a = _make_feature(scale=1.0)
    b = _make_feature(scale=2.0)
    assert not a.value_equals(b)


def test_value_equals_false_when_rotation_differs() -> None:
    a = _make_feature(rotation=0.0)
    b = _make_feature(rotation=45.0)
    assert not a.value_equals(b)


def test_value_equals_false_when_position_differs() -> None:
    a = _make_feature(x=0.0, y=0.0)
    b = _make_feature(x=1.0, y=0.0)
    assert not a.value_equals(b)


# ---------------------------------------------------------------------------
# AC1.5 — contains_check
# ---------------------------------------------------------------------------

def test_contains_check_true_for_value_equal_distinct_instances() -> None:
    from raven_matrix.model import contains_check
    a = _make_feature()
    b = _make_feature()
    assert a is not b
    assert contains_check([a], b)


def test_contains_check_false_when_no_value_equal_element() -> None:
    from raven_matrix.model import Fill, Shape, contains_check
    a = _make_feature(shape=Shape.DIAMOND, fill=Fill.BLACK)
    b = _make_feature(shape=Shape.ELLIPSE, fill=Fill.WHITE)
    assert not contains_check([a], b)


def test_contains_check_skips_none_elements_without_error() -> None:
    from raven_matrix.model import contains_check
    a = _make_feature()
    b = _make_feature()
    # None in the list must not raise; value-equal b is still found.
    assert contains_check([None, a], b)


def test_contains_check_none_only_list_returns_false() -> None:
    from raven_matrix.model import contains_check
    b = _make_feature()
    assert not contains_check([None, None], b)


def test_contains_check_empty_list_returns_false() -> None:
    from raven_matrix.model import contains_check
    b = _make_feature()
    assert not contains_check([], b)


# ---------------------------------------------------------------------------
# AC1.5 — hashability by identity (documents the list-based-dedup rule)
# ---------------------------------------------------------------------------

def test_surface_feature_is_hashable_by_identity() -> None:
    """SurfaceFeature must be usable as a dict key / set member."""
    a = _make_feature()
    d: dict = {a: "present"}
    assert d[a] == "present"


def test_two_value_equal_features_occupy_two_distinct_set_slots() -> None:
    """Documents that dedup must stay list-based, not set-based.

    If value-equal features hashed to the same slot they would collapse to one
    entry, breaking determinism.  Identity hash ensures they stay separate.
    """
    a = _make_feature()
    b = _make_feature()
    s = {a, b}
    assert len(s) == 2


# ---------------------------------------------------------------------------
# Container shape checks
# ---------------------------------------------------------------------------

def test_cell_holds_mutable_feature_list() -> None:
    from raven_matrix.model import Cell, Location
    loc = Location(0, 0)
    feat = _make_feature()
    cell = Cell(surface_features=[feat], location=loc)
    # List is mutable — append must succeed.
    extra = _make_feature()
    cell.surface_features.append(extra)
    assert len(cell.surface_features) == 2


def test_layer_holds_cells_grid_and_structures() -> None:
    from raven_matrix.model import Cell, Layer, Location
    cell = Cell(surface_features=[], location=Location(0, 0))
    layer = Layer(cells=[[cell]], structures=[])
    assert layer.cells[0][0] is cell
    assert layer.structures == []


def test_matrix_holds_cells_answer_choices_and_layers() -> None:
    from raven_matrix.model import Cell, Layer, Location, Matrix
    cell = Cell(surface_features=[], location=Location(0, 0))
    layer = Layer(cells=[[cell]], structures=[])
    matrix = Matrix(
        cells=[[cell]],
        answer_choices=[cell],
        correct_answer_position=1,
        layers=[layer],
    )
    assert matrix.correct_answer_position == 1
    assert len(matrix.answer_choices) == 1
    assert len(matrix.layers) == 1
