"""Tests for builder.py config dataclasses + validation + layer build (Task 5).

Ports the config-driven layer build (the headless reconstruction of the GUI
``SGMBuilderFrame.generateMatrix`` option surface plus ``SGMLayer`` traversal):

- ``LayerConfig`` / ``BuilderConfig`` are frozen dataclasses carrying parsed
  ``BaseRelation`` / ``Direction`` / ``Supplemental`` ENUMS (never raw digits).
- ``validate_config`` enforces the GUI constraints (AC1.4): 1-2 layers, <=3
  supplementals per layer, ``1 <= correct_answer_position <= 8``, and a logic
  base relation forbids supplementals
  (``gen-supplemental-disabled-when-logic-base``, SGMLayerGenerator.java:102-113).
- ``build_layer(layer_config, size, cell_pixel_size, rng, flags)`` mirrors
  ``SGMLayer`` (SGMLayer.java:132-356): seed base cells, walk the transform to
  derive the rest (geometric), or fill the 2x2 logic seed and combine two prior
  cells (logic), then apply each supplemental in config order.
- ``compose_layers(layers, size)`` mirrors the per-cell ``combineWith``
  concatenation (SGMMatrix.java:198-228).

The MANDATORY logic-termination test lives here: a build over an OR/AND/XOR
config TERMINATES and the generated base pool is pairwise value-distinct
(BaseSGMStructureFeatureGenerator.java:204-221 + containsCheck l.306-323).
"""

from __future__ import annotations

import pytest

from raven_matrix.builder import (
    BuilderConfig,
    LayerConfig,
    build_layer,
    compose_layers,
    validate_config,
)
from raven_matrix.compat import DEFAULT_FLAGS
from raven_matrix.model import (
    BaseRelation,
    Direction,
    MatrixSize,
    Supplemental,
)
from raven_matrix.rng import JavaRandom

_SIZE = MatrixSize(3, 3)
_CELL = 256


def _layer(
    base: BaseRelation = BaseRelation.SHAPE_REPETITION,
    direction: Direction = Direction.HORIZONTAL,
    supplementals: tuple[tuple[Supplemental, Direction], ...] = (),
) -> LayerConfig:
    return LayerConfig(base=base, base_direction=direction, supplementals=supplementals)


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


def test_layer_config_carries_parsed_enums() -> None:
    """LayerConfig holds Direction/BaseRelation/Supplemental enums, not digits."""
    layer = _layer(
        BaseRelation.SHAPE_REPETITION,
        Direction.VERTICAL,
        ((Supplemental.ROTATION, Direction.HORIZONTAL),),
    )
    assert layer.base is BaseRelation.SHAPE_REPETITION
    assert layer.base_direction is Direction.VERTICAL
    assert layer.supplementals == ((Supplemental.ROTATION, Direction.HORIZONTAL),)


def test_builder_config_is_frozen() -> None:
    config = BuilderConfig(layers=(_layer(),), correct_answer_position=1)
    # A non-constant attribute name avoids both a static read-only-property error
    # (ty) and B010 (ruff) while still exercising the runtime FrozenInstanceError.
    attr = "correct_answer_position"
    with pytest.raises((AttributeError, TypeError)):
        setattr(config, attr, 2)


# ---------------------------------------------------------------------------
# Validation (AC1.4)
# ---------------------------------------------------------------------------


def test_validate_accepts_a_minimal_single_layer_config() -> None:
    validate_config(BuilderConfig(layers=(_layer(),), correct_answer_position=1))


def test_validate_rejects_zero_layers() -> None:
    with pytest.raises(ValueError, match="1.*2 layers|layers"):
        validate_config(BuilderConfig(layers=(), correct_answer_position=1))


def test_validate_rejects_three_layers() -> None:
    with pytest.raises(ValueError, match="layers"):
        validate_config(
            BuilderConfig(
                layers=(_layer(), _layer(), _layer()), correct_answer_position=1
            )
        )


def test_validate_rejects_more_than_three_supplementals() -> None:
    four = (
        (Supplemental.ROTATION, Direction.HORIZONTAL),
        (Supplemental.SCALING, Direction.HORIZONTAL),
        (Supplemental.CHANGE_FILL, Direction.HORIZONTAL),
        (Supplemental.FILL_REPETITION, Direction.HORIZONTAL),
    )
    with pytest.raises(ValueError, match="supplemental"):
        validate_config(
            BuilderConfig(
                layers=(_layer(supplementals=four),), correct_answer_position=1
            )
        )


@pytest.mark.parametrize("position", [0, 9, -1, 100])
def test_validate_rejects_out_of_range_position(position: int) -> None:
    with pytest.raises(ValueError, match="position"):
        validate_config(
            BuilderConfig(layers=(_layer(),), correct_answer_position=position)
        )


@pytest.mark.parametrize(
    "logic_base",
    [BaseRelation.LOGICAL_OR, BaseRelation.LOGICAL_AND, BaseRelation.LOGICAL_XOR],
)
def test_validate_rejects_logic_base_with_supplementals(
    logic_base: BaseRelation,
) -> None:
    """A logic base forbids supplementals (SGMLayerGenerator.java:102-113)."""
    layer = _layer(
        logic_base,
        Direction.HORIZONTAL,
        ((Supplemental.ROTATION, Direction.HORIZONTAL),),
    )
    with pytest.raises(ValueError, match="logic"):
        validate_config(BuilderConfig(layers=(layer,), correct_answer_position=1))


def test_validate_allows_logic_base_without_supplementals() -> None:
    layer = _layer(BaseRelation.LOGICAL_AND, Direction.HORIZONTAL, ())
    validate_config(BuilderConfig(layers=(layer,), correct_answer_position=1))


# ---------------------------------------------------------------------------
# build_layer — geometric (ShapeRepetition)
# ---------------------------------------------------------------------------


def test_build_layer_fills_every_cell_shape_repetition() -> None:
    """A ShapeRepetition layer populates all 9 cells of a 3x3 grid."""
    layer = build_layer(_layer(), _SIZE, _CELL, JavaRandom(1), DEFAULT_FLAGS)
    assert len(layer.cells) == 3
    assert all(len(row) == 3 for row in layer.cells)
    for row in layer.cells:
        for cell in row:
            assert cell is not None
            assert len(cell.surface_features) >= 1


def test_build_layer_horizontal_repeats_features_along_rows() -> None:
    """Horizontal ShapeRepetition: each row's three cells share feature values."""
    layer = build_layer(_layer(), _SIZE, _CELL, JavaRandom(5), DEFAULT_FLAGS)
    for row in layer.cells:
        base_features = row[0].surface_features
        for cell in row[1:]:
            assert len(cell.surface_features) == len(base_features)
            for got, want in zip(cell.surface_features, base_features, strict=True):
                assert got.value_equals(want)


def test_build_layer_is_deterministic_for_a_seed() -> None:
    """Same config + seed -> identical layer feature values."""

    def shapes(seed: int) -> list[list[list[str]]]:
        layer = build_layer(_layer(), _SIZE, _CELL, JavaRandom(seed), DEFAULT_FLAGS)
        return [
            [[f.shape.name for f in cell.surface_features] for cell in row]
            for row in layer.cells
        ]

    assert shapes(42) == shapes(42)


# ---------------------------------------------------------------------------
# build_layer — supplementals stacked on a geometric base
# ---------------------------------------------------------------------------


def test_build_layer_applies_rotation_supplemental() -> None:
    """A ROTATION supplemental over a horizontal base accumulates +45 per step."""
    layer = build_layer(
        _layer(
            BaseRelation.SHAPE_REPETITION,
            Direction.HORIZONTAL,
            ((Supplemental.ROTATION, Direction.HORIZONTAL),),
        ),
        _SIZE,
        _CELL,
        JavaRandom(3),
        DEFAULT_FLAGS,
    )
    # Each row: column 0 is base (rotation 0), then +45, +90 along the row.
    for row in layer.cells:
        rotations = [row[c].surface_features[0].rotation for c in range(3)]
        assert rotations[0] == 0
        assert rotations[1] == 45
        assert rotations[2] == 90


# ---------------------------------------------------------------------------
# build_layer — logic base (MANDATORY termination + value-distinct pool)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "logic_base",
    [BaseRelation.LOGICAL_OR, BaseRelation.LOGICAL_AND, BaseRelation.LOGICAL_XOR],
)
def test_build_layer_logic_terminates_and_fills_grid(
    logic_base: BaseRelation,
) -> None:
    """A logic-op layer build TERMINATES (no hang) and fills all 9 cells.

    Regression guard for the non-termination bug: the base pool must be value-
    distinct (BaseSGMStructureFeatureGenerator.containsCheck) or the assignment
    loop spins forever. This test would hang, not fail, on a regression.
    """
    layer = build_layer(
        _layer(logic_base, Direction.HORIZONTAL, ()),
        _SIZE,
        _CELL,
        JavaRandom(9),
        DEFAULT_FLAGS,
    )
    assert len(layer.cells) == 3
    for row in layer.cells:
        for cell in row:
            assert cell is not None  # every cell populated (including derived)


@pytest.mark.parametrize(
    "logic_base",
    [BaseRelation.LOGICAL_OR, BaseRelation.LOGICAL_AND, BaseRelation.LOGICAL_XOR],
)
def test_build_layer_logic_base_pool_is_value_distinct(
    logic_base: BaseRelation,
) -> None:
    """The generated logic base pool is pairwise value-distinct (DR cross-cut #1).

    Inspect the 2x2 seed cells: the union of their base surface features is the
    assigned pool, which must contain no two value-equal features. (If it did,
    base.py's LogicOperation precondition would have raised ValueError.)
    """
    layer = build_layer(
        _layer(logic_base, Direction.HORIZONTAL, ()),
        _SIZE,
        _CELL,
        JavaRandom(13),
        DEFAULT_FLAGS,
    )
    pool: list = []
    for loc in ((0, 0), (0, 1), (1, 0), (1, 1)):
        for feature in layer.cells[loc[0]][loc[1]].surface_features:
            if feature not in pool:  # identity dedup to gather unique instances
                pool.append(feature)
    for i, a in enumerate(pool):
        for b in pool[i + 1 :]:
            assert not a.value_equals(b), "logic base pool has a value-duplicate"


def test_build_layer_logic_never_calls_next_or_parent_on_logic_transform() -> None:
    """build_layer must NOT drive the Logic transform via next/parent (partial).

    LogicLocationTransform.next_location / parent_location raise
    NotImplementedError. The logic branch consumes the 2x2 seed directly. If the
    builder mistakenly walked the transform, this build would raise.
    """
    layer = build_layer(
        _layer(BaseRelation.LOGICAL_XOR, Direction.HORIZONTAL, ()),
        _SIZE,
        _CELL,
        JavaRandom(2),
        DEFAULT_FLAGS,
    )
    # Reached here without NotImplementedError -> next/parent were never called.
    assert layer.cells[2][2] is not None


# ---------------------------------------------------------------------------
# compose_layers (AC1.2 — concatenation)
# ---------------------------------------------------------------------------


def test_compose_single_layer_passes_features_through() -> None:
    layer = build_layer(_layer(), _SIZE, _CELL, JavaRandom(7), DEFAULT_FLAGS)
    composed = compose_layers([layer], _SIZE)
    for r in range(3):
        for c in range(3):
            assert len(composed[r][c].surface_features) == len(
                layer.cells[r][c].surface_features
            )


def test_compose_two_layers_concatenates_per_cell() -> None:
    """AC1.2: a composed cell holds both layers' features (count = sum)."""
    rng = JavaRandom(11)
    layer_one = build_layer(_layer(), _SIZE, _CELL, rng, DEFAULT_FLAGS)
    layer_two = build_layer(
        _layer(BaseRelation.SHAPE_REPETITION, Direction.VERTICAL, ()),
        _SIZE,
        _CELL,
        rng,
        DEFAULT_FLAGS,
    )
    composed = compose_layers([layer_one, layer_two], _SIZE)
    for r in range(3):
        for c in range(3):
            assert len(composed[r][c].surface_features) == (
                len(layer_one.cells[r][c].surface_features)
                + len(layer_two.cells[r][c].surface_features)
            )
            assert composed[r][c].location == layer_one.cells[r][c].location
