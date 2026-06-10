"""Unit tests for the pure ``config_from_controls`` option->config mapping.

This is the FCIS seam shared by the CLI and the marimo app: it maps the GUI-style
option choices (per-layer base relation + direction, supplemental slots) onto a
validated ``BuilderConfig``. Being pure, it is tested with plain assertions and no
mocks; invalid option sets must raise ``ValueError`` via the Phase-4 validation.
"""

from __future__ import annotations

import pytest

from raven_matrix.builder import BuilderConfig, LayerConfig, build
from raven_matrix.model import BaseRelation, Direction, Supplemental
from raven_matrix.ui_config import LayerControls, config_from_controls


def test_single_layer_shape_repetition_maps_to_config() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[],
        )
    ]

    config = config_from_controls(controls, correct_answer_position=1)

    assert config == BuilderConfig(
        layers=(
            LayerConfig(
                base=BaseRelation.SHAPE_REPETITION,
                base_direction=Direction.HORIZONTAL,
                supplementals=(),
            ),
        ),
        correct_answer_position=1,
    )


def test_supplementals_carry_their_directions() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.VERTICAL,
            supplementals=[
                (Supplemental.ROTATION, Direction.HORIZONTAL),
                (Supplemental.SCALING, Direction.VERTICAL),
            ],
        )
    ]

    config = config_from_controls(controls, correct_answer_position=3)

    layer = config.layers[0]
    assert layer.supplementals == (
        (Supplemental.ROTATION, Direction.HORIZONTAL),
        (Supplemental.SCALING, Direction.VERTICAL),
    )
    assert config.correct_answer_position == 3


def test_two_layer_config_preserves_order() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[],
        ),
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.VERTICAL,
            supplementals=[],
        ),
    ]

    config = config_from_controls(controls, correct_answer_position=2)

    assert len(config.layers) == 2
    assert config.layers[0].base_direction == Direction.HORIZONTAL
    assert config.layers[1].base_direction == Direction.VERTICAL


def test_resulting_config_is_buildable() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[(Supplemental.ROTATION, Direction.VERTICAL)],
        )
    ]

    config = config_from_controls(controls, correct_answer_position=4)
    matrix = build(config, seed=0)

    assert matrix.correct_answer_position == 4
    assert len(matrix.cells) == 3


def test_logic_base_with_supplementals_rejected() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.LOGICAL_OR,
            base_direction=Direction.HORIZONTAL,
            supplementals=[(Supplemental.ROTATION, Direction.HORIZONTAL)],
        )
    ]

    with pytest.raises(ValueError, match="logic base"):
        config_from_controls(controls, correct_answer_position=1)


def test_more_than_three_supplementals_rejected() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[
                (Supplemental.ROTATION, Direction.HORIZONTAL),
                (Supplemental.SCALING, Direction.HORIZONTAL),
                (Supplemental.NUMEROSITY, Direction.HORIZONTAL),
                (Supplemental.CHANGE_FILL, Direction.HORIZONTAL),
            ],
        )
    ]

    with pytest.raises(ValueError, match="supplemental"):
        config_from_controls(controls, correct_answer_position=1)


def test_position_out_of_range_rejected() -> None:
    controls = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[],
        )
    ]

    with pytest.raises(ValueError, match="correct_answer_position"):
        config_from_controls(controls, correct_answer_position=9)


def test_zero_layers_rejected() -> None:
    with pytest.raises(ValueError, match="1 or 2 layers"):
        config_from_controls([], correct_answer_position=1)
