"""Tests for builder.py answer + distractor generation (Task 6).

Ports ``SGMMatrix.java`` ~242-572: the correct answer is the composited
bottom-right cell ``(2,2)``; up to 7 distractors come from four strategies
(``nextInt(4)`` for >=2 layers, ``nextInt(3)+1`` for one layer); dedup is at the
CELL level by VALUE; remaining slots are blank-padded.

Cell-level dedup helpers (DR7, cross-cut #4):
- ``_cell_value_equals`` mirrors ``SGMCell.equals`` (SGMBaseCell.java:202): equal
  feature count AND mutual value-containment via the Phase-2 feature-list
  ``contains_check``.
- ``_contains_cell`` mirrors ``SGMMatrix.containsCheck`` (SGMMatrix.java:575,
  used at l.492): True iff some non-blank choice ``_cell_value_equals`` the
  candidate.

``MAX_DUPLICATES_IN_A_ROW = 500`` (SGMMatrix.java:142). No ``set`` in any output
path -- list-based dedup only.
"""

from __future__ import annotations

import pytest

from raven_matrix.builder import (
    NUM_ANSWER_CHOICES,
    BuilderConfig,
    LayerConfig,
    _cell_value_equals,
    _contains_cell,
    build_layer,
    compose_layers,
    generate_answer_choices,
)
from raven_matrix.compat import DEFAULT_FLAGS, CompatFlags
from raven_matrix.model import (
    BaseRelation,
    Cell,
    Direction,
    Fill,
    Layer,
    Location,
    MatrixSize,
    Point,
    Shape,
    SurfaceFeature,
)
from raven_matrix.rng import JavaRandom

_SIZE = MatrixSize(3, 3)
_CELL = 256


def _feature(
    shape: Shape = Shape.ELLIPSE,
    fill: Fill = Fill.WHITE,
    scale: float = 1.0,
) -> SurfaceFeature:
    return SurfaceFeature(
        shape=shape,
        fill=fill,
        scale=scale,
        rotation=0.0,
        position=Point(128.0, 128.0),
        width=64.0,
        height=128.0,
    )


def _cell(features: list[SurfaceFeature], location: Location | None = None) -> Cell:
    return Cell(surface_features=features, location=location or Location(2, 2))


def _single_layer_config(
    base: BaseRelation = BaseRelation.SHAPE_REPETITION,
    direction: Direction = Direction.HORIZONTAL,
    position: int = 1,
) -> BuilderConfig:
    return BuilderConfig(
        layers=(LayerConfig(base=base, base_direction=direction, supplementals=()),),
        correct_answer_position=position,
    )


def _build_cells_and_layers(
    config: BuilderConfig, rng: JavaRandom
) -> tuple[list[list[Cell]], list]:
    layers = [
        build_layer(layer_cfg, _SIZE, _CELL, rng, DEFAULT_FLAGS)
        for layer_cfg in config.layers
    ]
    cells = compose_layers(layers, _SIZE)
    return cells, layers


# ---------------------------------------------------------------------------
# _cell_value_equals — direct unit coverage (SGMBaseCell.equals)
# ---------------------------------------------------------------------------

def test_cell_value_equals_value_equal_but_distinct_instances() -> None:
    """Two cells with value-equal (distinct) feature lists are equal."""
    a = _cell([_feature(Shape.ELLIPSE), _feature(Shape.TEE)])
    b = _cell([_feature(Shape.ELLIPSE), _feature(Shape.TEE)])
    assert a.surface_features[0] is not b.surface_features[0]
    assert _cell_value_equals(a, b)


def test_cell_value_equals_differing_feature_count_not_equal() -> None:
    a = _cell([_feature(Shape.ELLIPSE)])
    b = _cell([_feature(Shape.ELLIPSE), _feature(Shape.TEE)])
    assert not _cell_value_equals(a, b)


def test_cell_value_equals_differing_values_not_equal() -> None:
    a = _cell([_feature(Shape.ELLIPSE, Fill.WHITE)])
    b = _cell([_feature(Shape.ELLIPSE, Fill.BLACK)])
    assert not _cell_value_equals(a, b)


def test_cell_value_equals_ignores_order() -> None:
    """Equality is by mutual containment, so feature order does not matter."""
    a = _cell([_feature(Shape.ELLIPSE), _feature(Shape.TEE)])
    b = _cell([_feature(Shape.TEE), _feature(Shape.ELLIPSE)])
    assert _cell_value_equals(a, b)


def test_cell_value_equals_two_empty_cells_equal() -> None:
    assert _cell_value_equals(_cell([]), _cell([]))


# ---------------------------------------------------------------------------
# _contains_cell — SGMMatrix.containsCheck (skips None/blank)
# ---------------------------------------------------------------------------

def test_contains_cell_finds_value_equal_choice() -> None:
    candidate = _cell([_feature(Shape.ELLIPSE)])
    choices: list[Cell | None] = [_cell([_feature(Shape.ELLIPSE)])]
    assert _contains_cell(choices, candidate)


def test_contains_cell_skips_none_entries() -> None:
    candidate = _cell([_feature(Shape.ELLIPSE)])
    choices: list[Cell | None] = [None, None]
    assert not _contains_cell(choices, candidate)


def test_contains_cell_absent_when_no_value_match() -> None:
    candidate = _cell([_feature(Shape.ELLIPSE)])
    choices: list[Cell | None] = [_cell([_feature(Shape.TEE)])]
    assert not _contains_cell(choices, candidate)


# ---------------------------------------------------------------------------
# generate_answer_choices — shape of the output (part of AC1.1)
# ---------------------------------------------------------------------------

def test_generates_eight_answer_choices() -> None:
    rng = JavaRandom(1)
    config = _single_layer_config(position=3)
    cells, layers = _build_cells_and_layers(config, rng)
    choices, correct_position = generate_answer_choices(
        cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
    )
    assert len(choices) == NUM_ANSWER_CHOICES
    assert all(choice is not None for choice in choices)


def test_correct_answer_sits_at_configured_position_default_flags() -> None:
    """Default flags honour the configured position (1-based -> 0-based)."""
    rng = JavaRandom(7)
    config = _single_layer_config(position=5)
    cells, layers = _build_cells_and_layers(config, rng)
    choices, correct_position = generate_answer_choices(
        cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
    )
    assert correct_position == config.correct_answer_position  # unchanged
    correct_answer = cells[2][2]
    assert _cell_value_equals(choices[correct_position - 1], correct_answer)


def test_no_duplicate_answer_choices_by_cell_value() -> None:
    """No two non-blank choices are value-equal (cell-level dedup)."""
    rng = JavaRandom(3)
    config = _single_layer_config(position=2)
    cells, layers = _build_cells_and_layers(config, rng)
    choices, _ = generate_answer_choices(
        cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
    )
    non_blank = [c for c in choices if c.surface_features]
    for i, a in enumerate(non_blank):
        for b in non_blank[i + 1 :]:
            assert not _cell_value_equals(a, b)


def test_correct_answer_not_duplicated_among_distractors() -> None:
    """No distractor is value-equal to the correct answer."""
    rng = JavaRandom(4)
    config = _single_layer_config(position=1)
    cells, layers = _build_cells_and_layers(config, rng)
    choices, correct_position = generate_answer_choices(
        cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
    )
    correct_answer = choices[correct_position - 1]
    others = [c for i, c in enumerate(choices) if i != correct_position - 1]
    matches = [
        c
        for c in others
        if c.surface_features and _cell_value_equals(c, correct_answer)
    ]
    assert matches == []


def test_blank_pad_produces_empty_cells_without_error() -> None:
    """An impoverished single-feature config still yields 8 choices via padding."""
    rng = JavaRandom(2)
    # A single blank-ish correct answer forces heavy blank-padding.
    correct = _cell([], Location(2, 2))
    cells = [[_cell([], Location(r, c)) for c in range(3)] for r in range(3)]
    cells[2][2] = correct
    # One trivial layer so strategy code has a layer to read (single layer).
    config = _single_layer_config(position=4)
    _, layers = _build_cells_and_layers(config, JavaRandom(0))
    choices, _ = generate_answer_choices(
        cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
    )
    assert len(choices) == NUM_ANSWER_CHOICES
    blanks = [c for c in choices if not c.surface_features]
    assert len(blanks) >= 1  # padding happened


# ---------------------------------------------------------------------------
# relocate_correct_answer flag (RNG-consumption toggle)
# ---------------------------------------------------------------------------

def _uniform_matrix() -> tuple[list[list[Cell]], list[Layer]]:
    """A matrix whose every cell holds one value-equal feature.

    Few distinct distractors can be made (a fill/scale tweak of the single
    feature), so the wrong-answer block stays short and a high configured correct
    position sits AHEAD of `position` -- the forced blank-pad / relocation case.
    Crucially the candidates are NON-empty, so duplicates increment the cap and
    the loop terminates (an all-empty matrix would spin, a degenerate the upstream
    never produces). The single shared layer makes strategies 1/2/3 read the same
    impoverished cells.
    """

    def cell(r: int, c: int) -> Cell:
        return _cell([_feature(Shape.ELLIPSE, Fill.WHITE)], Location(r, c))

    cells = [[cell(r, c) for c in range(3)] for r in range(3)]
    layer = Layer(
        cells=[[cell(r, c) for c in range(3)] for r in range(3)], structures=[]
    )
    return cells, [layer]


def test_default_flags_never_relocate_correct_position() -> None:
    """Default honours the configured position even in a forced blank-pad case."""
    cells, layers = _uniform_matrix()
    config = _single_layer_config(position=8)  # high position
    for seed in range(20):
        rng = JavaRandom(seed)
        _, correct_position = generate_answer_choices(
            cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
        )
        assert correct_position == 8


def test_relocate_flag_can_move_correct_position() -> None:
    """With relocate_correct_answer, a high position in a blank-pad case moves.

    In the impoverished matrix the wrong-answer block is short, so
    correct_position_0 > position holds and the upstream relocation
    (SGMMatrix.java:531-548) fires. The default never moves it; the flag does.
    """
    flags = CompatFlags(relocate_correct_answer=True)
    config = _single_layer_config(position=8)
    moved = False
    for seed in range(40):
        cells, layers = _uniform_matrix()
        rng = JavaRandom(seed)
        choices, correct_position = generate_answer_choices(
            cells, layers, config.correct_answer_position, _SIZE, rng, flags
        )
        assert len(choices) == NUM_ANSWER_CHOICES
        # The correct cell is wherever correct_position points.
        assert _cell_value_equals(choices[correct_position - 1], cells[2][2])
        if correct_position != 8:
            moved = True
    assert moved, "relocate flag never moved the correct position across 40 seeds"


@pytest.mark.parametrize("position", [1, 4, 8])
def test_correct_position_consistent_with_returned_index(position: int) -> None:
    """The returned correct_position always indexes the correct-answer cell."""
    rng = JavaRandom(position * 3 + 1)
    config = _single_layer_config(position=position)
    cells, layers = _build_cells_and_layers(config, rng)
    choices, correct_position = generate_answer_choices(
        cells, layers, config.correct_answer_position, _SIZE, rng, DEFAULT_FLAGS
    )
    assert _cell_value_equals(choices[correct_position - 1], cells[2][2])
