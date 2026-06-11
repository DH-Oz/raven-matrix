"""Tests for model.py — enums and frozen value dataclasses (Task 3).

Asserts structure only:
- Each enum has exactly the specified members (guards accidental additions/omissions).
- Fill has exactly 5 members; each value is a NamedTuple with r,g,b,a channels all
  in [0.0, 1.0]; all five RGBA tuples are mutually distinct.
- MatrixSize, Location, Point are value-equal for equal fields and hashable.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Shape
# ---------------------------------------------------------------------------


def test_shape_has_exactly_seven_members() -> None:
    from raven_matrix.model import Shape

    assert {m.name for m in Shape} == {
        "DIAMOND",
        "ELLIPSE",
        "LINE",
        "RECTANGLE",
        "TEE",
        "TRAPEZOID",
        "TRIANGLE",
    }


def test_shape_member_count() -> None:
    from raven_matrix.model import Shape

    assert len(Shape) == 7


# ---------------------------------------------------------------------------
# Fill — structural assertions only (no exact RGBA values pinned)
# ---------------------------------------------------------------------------


def test_fill_has_exactly_five_members() -> None:
    from raven_matrix.model import Fill

    assert len(Fill) == 5


def test_fill_member_names() -> None:
    from raven_matrix.model import Fill

    assert {m.name for m in Fill} == {"BLACK", "WHITE", "GREY10", "GREY40", "GREY75"}


def test_fill_values_are_distinct() -> None:
    """All five RGBA tuples must be mutually distinct."""
    from raven_matrix.model import Fill

    values = [m.value for m in Fill]
    assert len(set(values)) == 5


def test_fill_channels_in_unit_range() -> None:
    """Every r, g, b, a channel must be within [0.0, 1.0]."""
    from raven_matrix.model import Fill

    for member in Fill:
        v = member.value
        for channel_name, channel_val in (
            ("r", v.r),
            ("g", v.g),
            ("b", v.b),
            ("a", v.a),
        ):
            assert 0.0 <= channel_val <= 1.0, (
                f"Fill.{member.name}.{channel_name} = {channel_val} out of [0,1]"
            )


def test_fill_named_tuple_access() -> None:
    """Named-tuple fields are accessible by attribute name."""
    from raven_matrix.model import Fill

    for member in Fill:
        v = member.value
        # All four attributes must exist and be floats.
        assert isinstance(v.r, float)
        assert isinstance(v.g, float)
        assert isinstance(v.b, float)
        assert isinstance(v.a, float)


# ---------------------------------------------------------------------------
# BaseRelation
# ---------------------------------------------------------------------------


def test_base_relation_has_exactly_four_members() -> None:
    from raven_matrix.model import BaseRelation

    assert {m.name for m in BaseRelation} == {
        "SHAPE_REPETITION",
        "LOGICAL_OR",
        "LOGICAL_AND",
        "LOGICAL_XOR",
    }


def test_base_relation_member_count() -> None:
    from raven_matrix.model import BaseRelation

    assert len(BaseRelation) == 4


# ---------------------------------------------------------------------------
# Supplemental
# ---------------------------------------------------------------------------


def test_supplemental_has_exactly_five_members() -> None:
    from raven_matrix.model import Supplemental

    assert {m.name for m in Supplemental} == {
        "ROTATION",
        "SCALING",
        "CHANGE_FILL",
        "FILL_REPETITION",
        "NUMEROSITY",
    }


def test_supplemental_member_count() -> None:
    from raven_matrix.model import Supplemental

    assert len(Supplemental) == 5


# ---------------------------------------------------------------------------
# Direction
# ---------------------------------------------------------------------------


def test_direction_has_exactly_five_members() -> None:
    from raven_matrix.model import Direction

    assert {m.name for m in Direction} == {
        "HORIZONTAL",
        "VERTICAL",
        "DIAGONAL_BL_TR",
        "DIAGONAL_TL_BR",
        "TOP_LEFT_CORNER_OUT",
    }


def test_direction_member_count() -> None:
    from raven_matrix.model import Direction

    assert len(Direction) == 5


def test_direction_integer_values() -> None:
    from raven_matrix.model import Direction

    assert Direction.HORIZONTAL == 1
    assert Direction.VERTICAL == 2
    assert Direction.DIAGONAL_BL_TR == 3
    assert Direction.DIAGONAL_TL_BR == 4
    assert Direction.TOP_LEFT_CORNER_OUT == 5


# ---------------------------------------------------------------------------
# Frozen value dataclasses
# ---------------------------------------------------------------------------


def test_matrix_size_value_equality() -> None:
    from raven_matrix.model import MatrixSize

    assert MatrixSize(3, 3) == MatrixSize(3, 3)
    assert MatrixSize(3, 3) != MatrixSize(3, 4)


def test_matrix_size_hashable() -> None:
    from raven_matrix.model import MatrixSize

    assert {MatrixSize(3, 3)} == {MatrixSize(3, 3)}


def test_location_value_equality() -> None:
    from raven_matrix.model import Location

    assert Location(0, 0) == Location(0, 0)
    assert Location(1, 2) != Location(2, 1)


def test_location_hashable() -> None:
    from raven_matrix.model import Location

    assert {Location(1, 2)} == {Location(1, 2)}


def test_point_value_equality() -> None:
    from raven_matrix.model import Point

    assert Point(1.0, 2.0) == Point(1.0, 2.0)
    assert Point(1.0, 2.0) != Point(2.0, 1.0)


def test_point_hashable() -> None:
    from raven_matrix.model import Point

    assert {Point(0.5, 0.5)} == {Point(0.5, 0.5)}
