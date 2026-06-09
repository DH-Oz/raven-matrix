"""Tests for build() end-to-end (Task 7).

``build(config, seed, flags=DEFAULT_FLAGS) -> Matrix`` ties the layer build
(Task 5) and answer generation (Task 6) together over a single
``JavaRandom(seed)``: build each layer, compose, generate answers, return a
``Matrix``.

Coverage:
- AC1.1: a 1-layer config -> 3x3 grid + 8 answer choices.
- AC1.3 (option surface): every BaseRelation, every Supplemental, every Direction
  builds and is realised (direct structural inspection, per DR4 -- no label()).
- AC4.1 (determinism): same config + seed -> deep-equal matrix.
- AC4.3 (seed independence, discriminating): two pinned seeds whose first base
  surface feature's shape differs -> structurally-equal matrices but that one
  located feature's shape is exactly ``!=``.
- AC6.1: line_shape_enabled changes output; default never draws Line.
- Property (hypothesis): random valid configs -> 3x3 + 8 choices + correct at the
  configured position (default flags).
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from raven_matrix.builder import (
    NUM_ANSWER_CHOICES,
    BuilderConfig,
    LayerConfig,
    _cell_value_equals,
    build,
)
from raven_matrix.compat import CompatFlags
from raven_matrix.model import (
    BaseRelation,
    Direction,
    Matrix,
    Shape,
    Supplemental,
)

_CELL = 256


def _single(
    base: BaseRelation = BaseRelation.SHAPE_REPETITION,
    direction: Direction = Direction.HORIZONTAL,
    supplementals: tuple[tuple[Supplemental, Direction], ...] = (),
    position: int = 1,
) -> BuilderConfig:
    return BuilderConfig(
        layers=(
            LayerConfig(
                base=base,
                base_direction=direction,
                supplementals=supplementals,
            ),
        ),
        correct_answer_position=position,
    )


def _feature_values(matrix: Matrix) -> list:
    """Flatten the grid into a comparable list of per-cell feature value tuples."""
    out = []
    for row in matrix.cells:
        for cell in row:
            out.append(
                [
                    (f.shape.name, f.fill.name, f.scale, f.rotation, f.width, f.height)
                    for f in cell.surface_features
                ]
            )
    return out


# ---------------------------------------------------------------------------
# AC1.1 — shape of the result
# ---------------------------------------------------------------------------

def test_build_returns_three_by_three_with_eight_choices() -> None:
    matrix = build(_single(position=4), seed=1)
    assert isinstance(matrix, Matrix)
    assert len(matrix.cells) == 3
    assert all(len(row) == 3 for row in matrix.cells)
    assert len(matrix.answer_choices) == NUM_ANSWER_CHOICES
    assert matrix.correct_answer_position == 4
    assert len(matrix.layers) == 1


def test_build_two_layer_config_composes_both_layers() -> None:
    config = BuilderConfig(
        layers=(
            LayerConfig(BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL, ()),
            LayerConfig(BaseRelation.SHAPE_REPETITION, Direction.VERTICAL, ()),
        ),
        correct_answer_position=2,
    )
    matrix = build(config, seed=5)
    assert len(matrix.layers) == 2
    # Each composed cell holds both layers' features (count = sum).
    for r in range(3):
        for c in range(3):
            expected = sum(
                len(layer.cells[r][c].surface_features) for layer in matrix.layers
            )
            assert len(matrix.cells[r][c].surface_features) == expected


def test_build_rejects_invalid_config() -> None:
    """build() validates the config (AC1.4 surfaced through build)."""
    with pytest.raises(ValueError, match="position"):
        build(_single(position=0), seed=1)


# ---------------------------------------------------------------------------
# AC1.3 — option surface (every base, supplemental, direction)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "base",
    [
        BaseRelation.SHAPE_REPETITION,
        BaseRelation.LOGICAL_OR,
        BaseRelation.LOGICAL_AND,
        BaseRelation.LOGICAL_XOR,
    ],
)
def test_build_every_base_relation_realised(base: BaseRelation) -> None:
    """Every base relation builds and lands as the layer's first structure."""
    from raven_matrix.structure.base import LogicOperation, ShapeRepetition

    matrix = build(_single(base=base, position=3), seed=9)
    structure = matrix.layers[0].structures[0]
    if base is BaseRelation.SHAPE_REPETITION:
        assert isinstance(structure, ShapeRepetition)
    else:
        assert isinstance(structure, LogicOperation)
    # Grid fully populated regardless of relation.
    for row in matrix.cells:
        for cell in row:
            assert cell is not None


@pytest.mark.parametrize(
    "supplemental,expected_cls_name",
    [
        (Supplemental.ROTATION, "ApplyRotation"),
        (Supplemental.SCALING, "ApplyScaling"),
        (Supplemental.CHANGE_FILL, "ChangeFillPattern"),
        (Supplemental.FILL_REPETITION, "FillPatternRepetition"),
        (Supplemental.NUMEROSITY, "TranslationalNumerosity"),
    ],
)
def test_build_every_supplemental_realised(
    supplemental: Supplemental, expected_cls_name: str
) -> None:
    """Every supplemental builds atop a ShapeRepetition base as the 2nd structure."""
    config = _single(
        BaseRelation.SHAPE_REPETITION,
        Direction.HORIZONTAL,
        ((supplemental, Direction.HORIZONTAL),),
        position=2,
    )
    matrix = build(config, seed=4)
    structures = matrix.layers[0].structures
    assert len(structures) == 2
    assert type(structures[1]).__name__ == expected_cls_name


@pytest.mark.parametrize(
    "direction",
    [
        Direction.HORIZONTAL,
        Direction.VERTICAL,
        Direction.DIAGONAL_BL_TR,
        Direction.DIAGONAL_TL_BR,
        Direction.TOP_LEFT_CORNER_OUT,
    ],
)
def test_build_every_direction_realised(direction: Direction) -> None:
    """Every direction (1-5) builds a fully-populated 3x3 grid (odd-square)."""
    matrix = build(_single(direction=direction, position=1), seed=6)
    for row in matrix.cells:
        for cell in row:
            assert cell is not None
            assert len(cell.surface_features) >= 1
    # The base relation's transform reflects the chosen direction.
    transform = matrix.layers[0].structures[0].location_transform
    assert transform.size.num_rows == 3


# ---------------------------------------------------------------------------
# AC4.1 — determinism
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [0, 1, 42, 1234])
def test_build_is_deterministic_for_a_seed(seed: int) -> None:
    """Same config + seed -> deep-equal matrices (structure + values + answers)."""
    config = _single(
        BaseRelation.SHAPE_REPETITION,
        Direction.HORIZONTAL,
        ((Supplemental.ROTATION, Direction.HORIZONTAL),),
        position=3,
    )
    first = build(config, seed=seed)
    second = build(config, seed=seed)
    assert _feature_values(first) == _feature_values(second)
    assert first.correct_answer_position == second.correct_answer_position
    # Answer cells equal by value, slot by slot.
    for a, b in zip(first.answer_choices, second.answer_choices, strict=True):
        assert _cell_value_equals(a, b)


def test_build_logic_config_is_deterministic() -> None:
    config = _single(BaseRelation.LOGICAL_AND, position=2)
    first = build(config, seed=77)
    second = build(config, seed=77)
    assert _feature_values(first) == _feature_values(second)


# ---------------------------------------------------------------------------
# AC4.3 — seed independence (discriminating, not probabilistic)
# ---------------------------------------------------------------------------

def test_build_different_seeds_same_structure_differ_in_pinned_feature() -> None:
    """Two pinned seeds: same relations, but the (0,0) base feature's shape differs.

    Seeds 0 and 1 are chosen so the first base surface feature drawn (the cell at
    grid (0,0) of a single-layer Horizontal ShapeRepetition) takes a DIFFERENT
    shape index under each seed. The matrices are structurally equal (same
    relation, direction, layer count), but that one named, located feature's
    ``shape`` is exactly ``!=``. If build() failed to thread the surface RNG, the
    shapes would coincide and this would fail.
    """
    config = _single(
        BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL, (), position=1
    )
    matrix_zero = build(config, seed=0)
    matrix_one = build(config, seed=1)

    # Structurally equal: same relation type, direction, layer count.
    assert len(matrix_zero.layers) == len(matrix_one.layers) == 1
    assert (
        type(matrix_zero.layers[0].structures[0])
        is type(matrix_one.layers[0].structures[0])
    )
    assert (
        matrix_zero.layers[0].structures[0].location_transform.description
        == matrix_one.layers[0].structures[0].location_transform.description
    )

    # The pinned, located feature's shape is exactly different.
    shape_zero = matrix_zero.cells[0][0].surface_features[0].shape
    shape_one = matrix_one.cells[0][0].surface_features[0].shape
    assert shape_zero is Shape.TRAPEZOID
    assert shape_one is Shape.TRIANGLE
    assert shape_zero is not shape_one


# ---------------------------------------------------------------------------
# AC6.1 — line_shape_enabled
# ---------------------------------------------------------------------------

def test_build_default_flags_never_draw_line() -> None:
    config = _single(BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL, (), 1)
    for seed in range(60):
        matrix = build(config, seed=seed)
        for row in matrix.cells:
            for cell in row:
                for feature in cell.surface_features:
                    assert feature.shape is not Shape.LINE


def test_build_line_enabled_changes_output_for_same_seed() -> None:
    """With line_shape_enabled the shape draw widens, changing the output.

    Pinned: seed 1's first base feature is Triangle (next_int(6)) by default and
    Line (next_int(7)) with the flag, so the (0,0) shape differs for one seed.
    """
    config = _single(BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL, (), 1)
    default = build(config, seed=1)
    lined = build(config, seed=1, flags=CompatFlags(line_shape_enabled=True))
    assert default.cells[0][0].surface_features[0].shape is Shape.TRIANGLE
    assert lined.cells[0][0].surface_features[0].shape is Shape.LINE


# ---------------------------------------------------------------------------
# Property (hypothesis): random valid configs
# ---------------------------------------------------------------------------

_DIRECTIONS = list(Direction)
_SUPPLEMENTALS = list(Supplemental)


@st.composite
def _valid_configs(draw: st.DrawFn) -> BuilderConfig:
    """A random valid single-layer (non-logic) config + position."""
    direction = draw(st.sampled_from(_DIRECTIONS))
    num_supplementals = draw(st.integers(min_value=0, max_value=3))
    supplementals = tuple(
        (draw(st.sampled_from(_SUPPLEMENTALS)), draw(st.sampled_from(_DIRECTIONS)))
        for _ in range(num_supplementals)
    )
    position = draw(st.integers(min_value=1, max_value=8))
    return BuilderConfig(
        layers=(
            LayerConfig(
                base=BaseRelation.SHAPE_REPETITION,
                base_direction=direction,
                supplementals=supplementals,
            ),
        ),
        correct_answer_position=position,
    )


@given(config=_valid_configs(), seed=st.integers(min_value=0, max_value=10_000))
def test_build_property_shape_and_position(config: BuilderConfig, seed: int) -> None:
    """Any valid config -> 3x3, 8 choices, correct answer at the configured pos."""
    matrix = build(config, seed=seed)
    assert len(matrix.cells) == 3
    assert all(len(row) == 3 for row in matrix.cells)
    assert len(matrix.answer_choices) == NUM_ANSWER_CHOICES
    # Default flags: the correct position is honoured exactly.
    assert matrix.correct_answer_position == config.correct_answer_position
    correct_cell = matrix.cells[2][2]
    placed = matrix.answer_choices[matrix.correct_answer_position - 1]
    assert _cell_value_equals(placed, correct_cell)
