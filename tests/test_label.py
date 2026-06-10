"""Tests for ``label()`` — the faithful port of the Java labeller (Task 1).

``label(matrix) -> str`` reproduces the ``sb``-build inside
``SGMMatrixDifficultyClassifier.evaluate`` (lines 208-389): it walks
``matrix.layers[].structures``, emits a LETTER per relation type and a DIGIT per
transform (with the upstream ``1/2`` swap and the ``6``/``7`` edge codes), and
``_``-joins the layers.

These fixtures build matrices via the Phase-4 ``build()`` with EXPLICIT configs
so the structure features are known, then assert the produced code. They pin the
PORT's behaviour — including the ``6``/``7`` codes the Java emits — not the
published norming labels (those are anchored independently in Task 3).
"""

from __future__ import annotations

import pytest

from raven_matrix.builder import BuilderConfig, LayerConfig, build
from raven_matrix.label import label
from raven_matrix.model import BaseRelation, Direction, Supplemental


def _single(
    base: BaseRelation = BaseRelation.SHAPE_REPETITION,
    direction: Direction = Direction.HORIZONTAL,
    supplementals: tuple[tuple[Supplemental, Direction], ...] = (),
    position: int = 1,
) -> BuilderConfig:
    """A one-layer config with the given base + supplementals."""
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


# ---------------------------------------------------------------------------
# ShapeRepetition (A) × each direction — repetition digit, no swap
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("direction", "expected"),
    [
        (Direction.HORIZONTAL, "A1"),
        (Direction.VERTICAL, "A2"),
        (Direction.DIAGONAL_BL_TR, "A3"),
        (Direction.DIAGONAL_TL_BR, "A4"),
        (Direction.TOP_LEFT_CORNER_OUT, "A6"),  # repetition + corner-out -> 6.
    ],
)
def test_shape_repetition_each_direction(
    direction: Direction, expected: str
) -> None:
    matrix = build(_single(direction=direction), seed=0)
    assert label(matrix) == expected


# ---------------------------------------------------------------------------
# FillRepetition vs ChangeFill — the 1/2 swap distinguishes them at B
# ---------------------------------------------------------------------------

def test_fill_repetition_horizontal_is_b1() -> None:
    # FillRep IS a repetition feature: Horizontal -> '1' (no swap).
    matrix = build(
        _single(supplementals=((Supplemental.FILL_REPETITION, Direction.HORIZONTAL),)),
        seed=0,
    )
    assert label(matrix) == "A1B1"


def test_fill_repetition_vertical_is_b2() -> None:
    # FillRep + Vertical -> '2' (no swap).
    matrix = build(
        _single(supplementals=((Supplemental.FILL_REPETITION, Direction.VERTICAL),)),
        seed=0,
    )
    assert label(matrix) == "A1B2"


def test_change_fill_horizontal_is_b2() -> None:
    # ChangeFill is NOT a repetition feature: Horizontal -> '2' (swapped).
    matrix = build(
        _single(supplementals=((Supplemental.CHANGE_FILL, Direction.HORIZONTAL),)),
        seed=0,
    )
    assert label(matrix) == "A1B2"


def test_change_fill_vertical_is_b1() -> None:
    # ChangeFill + Vertical -> '1' (swapped).
    matrix = build(
        _single(supplementals=((Supplemental.CHANGE_FILL, Direction.VERTICAL),)),
        seed=0,
    )
    assert label(matrix) == "A1B1"


def test_change_fill_corner_out_is_b5() -> None:
    # Non-repetition + corner-out -> '5'.
    matrix = build(
        _single(
            supplementals=((Supplemental.CHANGE_FILL, Direction.TOP_LEFT_CORNER_OUT),)
        ),
        seed=0,
    )
    assert label(matrix) == "A1B5"


# ---------------------------------------------------------------------------
# Rotation (C), Scaling (D), Numerosity (E) — non-repetition, digit swapped
# ---------------------------------------------------------------------------

def test_rotation_horizontal_is_c2() -> None:
    # Rotation is non-repetition: Horizontal -> '2' (swapped).
    matrix = build(
        _single(supplementals=((Supplemental.ROTATION, Direction.HORIZONTAL),)),
        seed=0,
    )
    assert label(matrix) == "A1C2"


def test_scaling_vertical_is_d1() -> None:
    # Scaling non-repetition: Vertical -> '1' (swapped).
    matrix = build(
        _single(supplementals=((Supplemental.SCALING, Direction.VERTICAL),)),
        seed=0,
    )
    assert label(matrix) == "A1D1"


def test_numerosity_horizontal_is_e2() -> None:
    # Numerosity non-repetition: Horizontal -> '2' (swapped).
    matrix = build(
        _single(supplementals=((Supplemental.NUMEROSITY, Direction.HORIZONTAL),)),
        seed=0,
    )
    assert label(matrix) == "A1E2"


# ---------------------------------------------------------------------------
# Logic relations (X/Y/Z) — the Logic transform always emits '7'
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (BaseRelation.LOGICAL_OR, "X7"),
        (BaseRelation.LOGICAL_AND, "Y7"),
        (BaseRelation.LOGICAL_XOR, "Z7"),
    ],
)
def test_logic_relations(base: BaseRelation, expected: str) -> None:
    matrix = build(_single(base=base), seed=0)
    assert label(matrix) == expected


# ---------------------------------------------------------------------------
# Multi-layer — '_'-joined, trailing '_' deleted
# ---------------------------------------------------------------------------

def test_two_layer_code_is_underscore_joined() -> None:
    config = BuilderConfig(
        layers=(
            LayerConfig(
                base=BaseRelation.SHAPE_REPETITION,
                base_direction=Direction.HORIZONTAL,
            ),
            LayerConfig(
                base=BaseRelation.SHAPE_REPETITION,
                base_direction=Direction.VERTICAL,
            ),
        ),
        correct_answer_position=1,
    )
    matrix = build(config, seed=0)
    assert label(matrix) == "A1_A2"


def test_base_plus_supplemental_in_one_layer_concatenates() -> None:
    # One layer with a base + a supplemental: letters+digits concatenate, no '_'.
    matrix = build(
        _single(
            direction=Direction.HORIZONTAL,
            supplementals=((Supplemental.ROTATION, Direction.HORIZONTAL),),
        ),
        seed=0,
    )
    # ShapeRep+H -> A1, Rotation(non-rep)+H -> C2.
    assert label(matrix) == "A1C2"
