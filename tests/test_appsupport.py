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

import re
import xml.etree.ElementTree as ET

import pytest

from raven_matrix.appsupport import (
    DIRECTION_OPTIONS,
    RELATION_OPTIONS,
    SUPPLEMENTAL_OPTIONS,
    build_outcome,
    compose_save_svg,
    layer_controls_from_column,
    option_reference,
)
from raven_matrix.builder import build_from_code
from raven_matrix.model import BaseRelation, Direction, Matrix, Supplemental
from raven_matrix.ui_config import LayerControls

_SVG_TAG = "{http://www.w3.org/2000/svg}svg"

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


# ---------------------------------------------------------------------------
# option_reference -- completeness (guards doc drift from the controls)
# ---------------------------------------------------------------------------
#
# These tests iterate the ACTUAL enums and the option maps rather than a
# hardcoded list, so adding a relation / direction / supplemental (or renaming a
# control) without documenting it fails the build. The reference must mention
# every option a researcher can pick AND every control label.


def test_option_reference_returns_markdown_string() -> None:
    text = option_reference()

    assert isinstance(text, str)
    assert text.strip()


def test_option_reference_documents_every_base_relation() -> None:
    text = option_reference()

    # Every BaseRelation member must appear by its enum name AND by the label the
    # GUI dropdown offers (the key in RELATION_OPTIONS), so neither can drift.
    for member in BaseRelation:
        assert member.name in text, f"BaseRelation.{member.name} undocumented"
    for label_text in RELATION_OPTIONS:
        assert label_text in text, f"relation label {label_text!r} undocumented"


def test_option_reference_documents_every_direction() -> None:
    text = option_reference()

    for member in Direction:
        assert member.name in text, f"Direction.{member.name} undocumented"
        # The Matzen digit code (1-5) for each direction must appear too.
        assert str(member.value) in text, f"direction digit {member.value} undocumented"
    for label_text in DIRECTION_OPTIONS:
        assert label_text in text, f"direction label {label_text!r} undocumented"


def test_option_reference_documents_every_supplemental() -> None:
    text = option_reference()

    for member in Supplemental:
        assert member.name in text, f"Supplemental.{member.name} undocumented"
    # Every enabled supplemental label (the "Disabled" sentinel maps to None).
    for label_text, mapped in SUPPLEMENTAL_OPTIONS.items():
        if mapped is not None:
            assert label_text in text, f"supplemental label {label_text!r} undocumented"


def test_option_reference_documents_every_control() -> None:
    text = option_reference()

    # Every control the researcher sees in the panel must be explained.
    for control_label in (
        "Mode",
        "Layers",
        "Base relation",
        "Base direction",
        "Supplemental",
        "Correct-answer position",
        "Seed",
        "New seed",
        "Structure code",
    ):
        assert control_label in text, f"control {control_label!r} undocumented"


# ---------------------------------------------------------------------------
# compose_save_svg (N3) -- save problem / answers / both, with optional header
# ---------------------------------------------------------------------------
#
# The problem matrix renders its document background as a WHITE
# ``class="background"`` rect; the answer sheet renders it BLACK. Answer cells
# carry their own ``class="cell-bg"`` white rects, so a bare ``fill="white"`` is
# NOT a discriminator -- the class-tagged document background is. A helper counts
# document backgrounds of each colour so "problem present" / "answers present" is
# unambiguous regardless of grid dimensions.


def _document_backgrounds(svg: str) -> list[str]:
    """The fill colour of each ``class="background"`` rect, in document order."""
    return re.findall(r'<rect class="background"[^>]*fill="(\w+)"', svg)


@pytest.fixture
def matrix() -> Matrix:
    # A real single-layer shape-repetition matrix (labels "A1"); deterministic.
    return build_from_code("A1", 0)


def test_compose_save_svg_problem_only_has_problem_not_answers(matrix: Matrix) -> None:
    svg = compose_save_svg(
        matrix, include_problem=True, include_answers=False, header_fields={}
    )

    assert _document_backgrounds(svg) == ["white"]  # problem only


def test_compose_save_svg_answers_only_has_answers_not_problem(matrix: Matrix) -> None:
    svg = compose_save_svg(
        matrix, include_problem=False, include_answers=True, header_fields={}
    )

    assert _document_backgrounds(svg) == ["black"]  # answers only


def test_compose_save_svg_both_has_problem_and_answers(matrix: Matrix) -> None:
    svg = compose_save_svg(
        matrix, include_problem=True, include_answers=True, header_fields={}
    )

    # Problem (white) then answers (black), stacked in that order.
    assert _document_backgrounds(svg) == ["white", "black"]


def test_compose_save_svg_neither_raises(matrix: Matrix) -> None:
    with pytest.raises(ValueError, match="problem|answers"):
        compose_save_svg(
            matrix, include_problem=False, include_answers=False, header_fields={}
        )


def test_compose_save_svg_no_header_when_fields_empty(matrix: Matrix) -> None:
    svg = compose_save_svg(
        matrix, include_problem=True, include_answers=False, header_fields={}
    )

    # No header band: a <text> element only appears when header_fields is given.
    assert "<text" not in svg


def test_compose_save_svg_header_lists_exactly_given_fields(matrix: Matrix) -> None:
    svg = compose_save_svg(
        matrix,
        include_problem=True,
        include_answers=False,
        header_fields={"code": "A1", "correct answer": 3, "seed": 0},
    )

    assert "<text" in svg
    # Each given key:value pair appears...
    assert "code" in svg and "A1" in svg
    assert "correct answer" in svg and "3" in svg
    assert "seed" in svg
    # ...and a field NOT passed does not leak in.
    assert "difficulty" not in svg


def test_compose_save_svg_parses_as_well_formed_svg(matrix: Matrix) -> None:
    svg = compose_save_svg(
        matrix,
        include_problem=True,
        include_answers=True,
        header_fields={"code": "A1", "seed": 0},
    )

    root = ET.fromstring(svg)
    assert root.tag == _SVG_TAG


def test_compose_save_svg_each_variant_parses(matrix: Matrix) -> None:
    for include_problem, include_answers in (
        (True, False),
        (False, True),
        (True, True),
    ):
        svg = compose_save_svg(
            matrix,
            include_problem=include_problem,
            include_answers=include_answers,
            header_fields={},
        )
        root = ET.fromstring(svg)
        assert root.tag == _SVG_TAG


# ---------------------------------------------------------------------------
# compose_save_svg -- order-independent SVG dimension extraction
# ---------------------------------------------------------------------------
#
# The renderer currently emits width before height, but the SVG spec makes
# attribute order arbitrary.  _svg_parts must extract dimensions correctly
# regardless of which attribute comes first in the opening <svg> tag.


def test_svg_parts_height_before_width_is_order_independent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """compose_save_svg must handle height="..." BEFORE width="..." in the <svg> tag.

    The renderer owns the attribute order; if it ever emits height first the
    composition must still produce a correctly-sized outer SVG and parse as
    well-formed XML.  This test replaces render_matrix_svg with a stub that
    returns a minimal height-first SVG (100 × 200) to isolate the extraction
    path from renderer internals.
    """
    height_first_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'height="200" width="100" viewBox="0 0 100 200">'
        '<rect class="background" x="0" y="0" width="100" height="200" fill="white"/>'
        "</svg>"
    )

    import raven_matrix.appsupport as _mod

    monkeypatch.setattr(_mod, "render_matrix_svg", lambda _matrix: height_first_svg)

    matrix_fixture = build_from_code("A1", 0)
    svg = compose_save_svg(
        matrix_fixture,
        include_problem=True,
        include_answers=False,
        header_fields={},
    )

    # Must parse as well-formed XML.
    root = ET.fromstring(svg)
    assert root.tag == _SVG_TAG

    # The outer SVG must carry the correct dimensions extracted from the stub.
    assert root.attrib["width"] == "100"
    assert root.attrib["height"] == "200"
