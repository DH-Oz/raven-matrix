"""Unit tests for ``appsupport`` -- the pure seam behind the marimo app.

``app.py`` is a thin marimo edge layer; everything testable lives here. These are
pure functions over plain data, so they are tested with plain assertions and no
mocks (the app's reactive wiring is UAT, not automated). The module must NOT
import marimo or typer -- it is part of the functional core (FCIS).

Coverage:
- the option-label -> enum maps (including the supplemental "Disabled" -> None);
- ``layer_controls_from_column`` builds the right ``LayerControls`` and drops every
  "Disabled" supplemental slot;
- ``build_outcome`` returns a built matrix + structure code for a valid control
  set and for a valid code, and the friendly error (matrix ``None``) for each
  ``ValueError`` path the upstream surface forbids.
"""

from __future__ import annotations

from raven_matrix.appsupport import (
    DIRECTION_OPTIONS,
    RELATION_OPTIONS,
    SUPPLEMENTAL_OPTIONS,
    build_outcome,
    layer_controls_from_column,
)
from raven_matrix.model import BaseRelation, Direction, Matrix, Supplemental
from raven_matrix.ui_config import LayerControls

# ---------------------------------------------------------------------------
# Option maps
# ---------------------------------------------------------------------------

def test_relation_options_map_labels_to_base_relations() -> None:
    assert RELATION_OPTIONS == {
        "ShapeRep": BaseRelation.SHAPE_REPETITION,
        "OR": BaseRelation.LOGICAL_OR,
        "AND": BaseRelation.LOGICAL_AND,
        "XOR": BaseRelation.LOGICAL_XOR,
    }


def test_direction_options_map_labels_to_directions() -> None:
    assert DIRECTION_OPTIONS == {
        "H": Direction.HORIZONTAL,
        "V": Direction.VERTICAL,
        "DiagTL": Direction.DIAGONAL_TL_BR,
        "DiagBL": Direction.DIAGONAL_BL_TR,
        "CornerOut": Direction.TOP_LEFT_CORNER_OUT,
    }


def test_supplemental_options_map_labels_with_disabled_to_none() -> None:
    assert SUPPLEMENTAL_OPTIONS == {
        "Disabled": None,
        "Scaling": Supplemental.SCALING,
        "Rotation": Supplemental.ROTATION,
        "FillRep": Supplemental.FILL_REPETITION,
        "ChangeFill": Supplemental.CHANGE_FILL,
        "Numerosity": Supplemental.NUMEROSITY,
    }


# ---------------------------------------------------------------------------
# layer_controls_from_column
# ---------------------------------------------------------------------------

def _disabled_slot() -> dict[str, object]:
    return {"type": None, "direction": Direction.HORIZONTAL}


def test_layer_controls_from_column_all_disabled_has_no_supplementals() -> None:
    column = {
        "base": BaseRelation.SHAPE_REPETITION,
        "base_direction": Direction.HORIZONTAL,
        "supp1": _disabled_slot(),
        "supp2": _disabled_slot(),
        "supp3": _disabled_slot(),
    }

    controls = layer_controls_from_column(column)

    assert controls == LayerControls(
        base=BaseRelation.SHAPE_REPETITION,
        base_direction=Direction.HORIZONTAL,
        supplementals=[],
    )


def test_layer_controls_from_column_keeps_enabled_drops_disabled() -> None:
    column = {
        "base": BaseRelation.SHAPE_REPETITION,
        "base_direction": Direction.VERTICAL,
        "supp1": {"type": Supplemental.ROTATION, "direction": Direction.HORIZONTAL},
        "supp2": _disabled_slot(),
        "supp3": {"type": Supplemental.SCALING, "direction": Direction.VERTICAL},
    }

    controls = layer_controls_from_column(column)

    # Only the two ENABLED slots survive, in slot order, paired with their
    # directions; the middle "Disabled" slot is dropped.
    assert controls == LayerControls(
        base=BaseRelation.SHAPE_REPETITION,
        base_direction=Direction.VERTICAL,
        supplementals=[
            (Supplemental.ROTATION, Direction.HORIZONTAL),
            (Supplemental.SCALING, Direction.VERTICAL),
        ],
    )


# ---------------------------------------------------------------------------
# build_outcome -- success paths
# ---------------------------------------------------------------------------

def test_build_outcome_from_controls_returns_matrix_and_code() -> None:
    layers = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[],
        )
    ]

    outcome = build_outcome(
        mode="Build from controls",
        gathered_layers=layers,
        position=1,
        code="ignored-in-controls-mode",
        seed=0,
    )

    assert outcome.error is None
    assert isinstance(outcome.matrix, Matrix)
    # A single ShapeRepetition layer on the Horizontal transform labels "A1".
    assert outcome.structure_code == "A1"
    assert outcome.matrix.correct_answer_position == 1


def test_build_outcome_from_code_returns_matrix_and_code() -> None:
    outcome = build_outcome(
        mode="Build from code",
        gathered_layers=[],
        position=1,
        code="A1",
        seed=0,
    )

    assert outcome.error is None
    assert isinstance(outcome.matrix, Matrix)
    assert outcome.structure_code == "A1"


def test_build_outcome_is_deterministic_for_a_seed() -> None:
    outcome_a = build_outcome(
        mode="Build from code", gathered_layers=[], position=1, code="A1", seed=7
    )
    outcome_b = build_outcome(
        mode="Build from code", gathered_layers=[], position=1, code="A1", seed=7
    )

    assert outcome_a.matrix is not None and outcome_b.matrix is not None
    assert outcome_a.structure_code == outcome_b.structure_code
    assert (
        outcome_a.matrix.correct_answer_position
        == outcome_b.matrix.correct_answer_position
    )


# ---------------------------------------------------------------------------
# build_outcome -- friendly error paths (matrix None)
# ---------------------------------------------------------------------------

def test_build_outcome_logic_base_with_supplemental_is_friendly_error() -> None:
    layers = [
        LayerControls(
            base=BaseRelation.LOGICAL_OR,
            base_direction=Direction.HORIZONTAL,
            supplementals=[(Supplemental.ROTATION, Direction.HORIZONTAL)],
        )
    ]

    outcome = build_outcome(
        mode="Build from controls",
        gathered_layers=layers,
        position=1,
        code="",
        seed=0,
    )

    assert outcome.matrix is None
    assert outcome.structure_code is None
    assert outcome.error is not None
    assert "logic base" in outcome.error


def test_build_outcome_too_many_supplementals_is_friendly_error() -> None:
    layers = [
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

    outcome = build_outcome(
        mode="Build from controls",
        gathered_layers=layers,
        position=1,
        code="",
        seed=0,
    )

    assert outcome.matrix is None
    assert outcome.structure_code is None
    assert outcome.error is not None
    assert "supplemental" in outcome.error


def test_build_outcome_position_out_of_range_is_friendly_error() -> None:
    layers = [
        LayerControls(
            base=BaseRelation.SHAPE_REPETITION,
            base_direction=Direction.HORIZONTAL,
            supplementals=[],
        )
    ]

    outcome = build_outcome(
        mode="Build from controls",
        gathered_layers=layers,
        position=9,
        code="",
        seed=0,
    )

    assert outcome.matrix is None
    assert outcome.structure_code is None
    assert outcome.error is not None
    assert "correct_answer_position" in outcome.error


def test_build_outcome_malformed_code_is_friendly_error() -> None:
    outcome = build_outcome(
        mode="Build from code",
        gathered_layers=[],
        position=1,
        code="!!bogus!!",
        seed=0,
    )

    assert outcome.matrix is None
    assert outcome.structure_code is None
    assert outcome.error is not None
