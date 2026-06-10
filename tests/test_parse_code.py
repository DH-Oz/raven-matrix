"""Tests for ``parse_code()`` + ``build_from_code()`` (Task 2).

``parse_code(code) -> BuilderConfig`` inverts the Matzen naming scheme (there is
NO upstream parser — this is a new artifact driven by the published convention).
``build_from_code(code, seed) -> Matrix`` is ``parse_code`` + the Phase-4
``build``.

Key derivations pinned by ground truth (NOT invented):

- ``B`` aliasing — both FillRep and ChangeFill label to ``B``. Resolved by the
  fill palette in the published 1-Layer PNGs (FillRep is a 3-level palette;
  ChangeFill is 5-level): ``B1``-``B4`` -> FillRep + the matching transform,
  ``B5`` -> ChangeFill + corner-out. Confirmed by inspecting ``B[1-5]_1.png``.
- Supplemental-only codes (``C3``, ``D4E2``, ``E5``, …) — ApplyRotation /
  ApplyScaling provide NO base surface features of their own
  (``AbstractRepetitionSGMStructureFeature.provideBaseSurfaceFeatures`` returns
  ``existing`` unchanged; ``SGMLayerGenerator`` always creates a base first). So a
  supplemental-led code gets an injected implicit ``ShapeRepetition`` base.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from raven_matrix.builder import build_from_code
from raven_matrix.label import label, parse_code
from raven_matrix.model import BaseRelation, Direction, Supplemental
from raven_matrix.structure.base import (
    LogicalAND,
    LogicalOR,
    LogicalXOR,
    ShapeRepetition,
)
from raven_matrix.structure.supplemental import (
    ApplyRotation,
    ApplyScaling,
    ChangeFillPattern,
    FillPatternRepetition,
    TranslationalNumerosity,
)

# ---------------------------------------------------------------------------
# Single-relation base codes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("code", "direction"),
    [
        ("A1", Direction.HORIZONTAL),
        ("A2", Direction.VERTICAL),
        ("A3", Direction.DIAGONAL_BL_TR),
        ("A4", Direction.DIAGONAL_TL_BR),
    ],
)
def test_shape_repetition_codes(code: str, direction: Direction) -> None:
    config = parse_code(code)
    assert len(config.layers) == 1
    layer = config.layers[0]
    assert layer.base is BaseRelation.SHAPE_REPETITION
    assert layer.base_direction is direction
    assert layer.supplementals == ()


def test_shape_repetition_round_trips() -> None:
    # A1-A4 are repetition features: the label re-emits the same code exactly.
    for code in ("A1", "A2", "A3", "A4"):
        assert label(build_from_code(code, seed=0)) == code


# ---------------------------------------------------------------------------
# B aliasing — FillRep (B1-B4) vs ChangeFill (B5)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("code", "direction"),
    [
        ("B1", Direction.HORIZONTAL),
        ("B2", Direction.VERTICAL),
        ("B3", Direction.DIAGONAL_BL_TR),
        ("B4", Direction.DIAGONAL_TL_BR),
    ],
)
def test_b1_to_b4_are_fill_repetition(code: str, direction: Direction) -> None:
    config = parse_code(code)
    layer = config.layers[0]
    # Implicit ShapeRepetition base injected; the supplemental is FillRep.
    assert layer.base is BaseRelation.SHAPE_REPETITION
    assert layer.supplementals == ((Supplemental.FILL_REPETITION, direction),)


def test_b5_is_change_fill_corner_out() -> None:
    config = parse_code("B5")
    layer = config.layers[0]
    assert layer.base is BaseRelation.SHAPE_REPETITION
    assert layer.supplementals == (
        (Supplemental.CHANGE_FILL, Direction.TOP_LEFT_CORNER_OUT),
    )


def test_b1_realises_fill_repetition_structure() -> None:
    # The built matrix's supplemental is a FillPatternRepetition, not ChangeFill.
    matrix = build_from_code("B1", seed=0)
    structures = matrix.layers[0].structures
    assert any(isinstance(s, FillPatternRepetition) for s in structures)
    assert not any(isinstance(s, ChangeFillPattern) for s in structures)


def test_b5_realises_change_fill_structure() -> None:
    matrix = build_from_code("B5", seed=0)
    structures = matrix.layers[0].structures
    assert any(isinstance(s, ChangeFillPattern) for s in structures)
    assert not any(isinstance(s, FillPatternRepetition) for s in structures)


# ---------------------------------------------------------------------------
# Supplemental-only codes (C/D/E) — implicit ShapeRepetition base injected
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("code", "kind"),
    [
        ("C3", Supplemental.ROTATION),
        ("D4", Supplemental.SCALING),
        ("E5", Supplemental.NUMEROSITY),
    ],
)
def test_supplemental_only_injects_shape_repetition_base(
    code: str, kind: Supplemental
) -> None:
    config = parse_code(code)
    layer = config.layers[0]
    # No base letter in the code -> implicit ShapeRepetition base.
    assert layer.base is BaseRelation.SHAPE_REPETITION
    assert len(layer.supplementals) == 1
    assert layer.supplementals[0][0] is kind


def test_supplemental_only_builds_a_base_and_the_supplemental() -> None:
    # C3 realises a ShapeRepetition base + an ApplyRotation supplemental.
    matrix = build_from_code("C3", seed=0)
    structures = matrix.layers[0].structures
    assert isinstance(structures[0], ShapeRepetition)
    assert any(isinstance(s, ApplyRotation) for s in structures)


def test_scaling_and_numerosity_build() -> None:
    d_matrix = build_from_code("D4", seed=0)
    assert any(isinstance(s, ApplyScaling) for s in d_matrix.layers[0].structures)
    e_matrix = build_from_code("E2", seed=0)
    assert any(
        isinstance(s, TranslationalNumerosity)
        for s in e_matrix.layers[0].structures
    )


# ---------------------------------------------------------------------------
# Multi-supplemental and multi-layer codes
# ---------------------------------------------------------------------------

def test_explicit_base_plus_supplementals() -> None:
    # A1B2C4: ShapeRep+H base, FillRep+V (repetition: digit = direction directly),
    # and Rotation+C4. C4 is a NON-repetition supplemental, so the published digit
    # is the labeller's swapped (constancy-axis) form: digit 4 inverts to the
    # BL->TR transform (non-rep digit 4 = DiagonalBottomLeftTopRight in the forward
    # map). The pre-fix parser read this LITERALLY as TL_BR — the transpose bug.
    config = parse_code("A1B2C4")
    layer = config.layers[0]
    assert layer.base is BaseRelation.SHAPE_REPETITION
    assert layer.base_direction is Direction.HORIZONTAL
    assert layer.supplementals == (
        (Supplemental.FILL_REPETITION, Direction.VERTICAL),
        (Supplemental.ROTATION, Direction.DIAGONAL_BL_TR),
    )


# ---------------------------------------------------------------------------
# Non-repetition supplemental digit inversion (the labeller 1<->2, 3<->4 swap).
#
# Ground truth: the published 1-Layer PNGs. C2_1.png shows orientation CHANGING
# horizontally (constant down each column) -> the published digit is 2, which is
# Rotation on the HORIZONTAL transform. C1_1.png shows it changing vertically ->
# digit 1 -> Rotation on the VERTICAL transform. A repetition feature keeps the
# direction digit directly, but a non-repetition feature (C/D/E) carries the
# labeller's swapped digit, so parse_code MUST invert the swap to rebuild the
# SAME stimulus rather than its transpose.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("code", "expected_direction"),
    [
        ("C1", Direction.VERTICAL),       # C1_1.png: orientation changes vertically.
        ("C2", Direction.HORIZONTAL),      # C2_1.png: changes horizontally.
        ("C3", Direction.DIAGONAL_TL_BR),  # non-rep digit 3 -> TL->BR transform.
        ("C4", Direction.DIAGONAL_BL_TR),  # non-rep digit 4 -> BL->TR transform.
        ("C5", Direction.TOP_LEFT_CORNER_OUT),  # digit 5 -> corner-out (no swap).
    ],
)
def test_non_repetition_supplemental_inverts_the_swap(
    code: str, expected_direction: Direction
) -> None:
    config = parse_code(code)
    ((kind, direction),) = config.layers[0].supplementals
    assert kind is Supplemental.ROTATION
    assert direction is expected_direction


@pytest.mark.parametrize(
    "code",
    # Base-named non-repetition codes drawn from data/ravens_oracle.csv: the
    # explicit A-base removes the base-omission convention gap, so these must
    # round-trip EXACTLY once the non-repetition swap is inverted. (Before the
    # fix they relabel to the swapped digit, e.g. A1C2 -> A1C1, A1B2C4 -> A1B2C3.)
    ["A1C2", "A1C3", "A1C4", "A1C5", "A1B2C4", "A1B2D4", "A1B2E3", "A1B4C2", "A1C2D4"],
)
def test_base_named_non_repetition_codes_round_trip(code: str) -> None:
    assert label(build_from_code(code, seed=0)) == code


@pytest.mark.parametrize("digit", ["1", "2", "3", "4", "5"])
def test_rotation_round_trips_for_every_direction(digit: str) -> None:
    # With an explicit A1 base (no base-omission gap), Rotation on every direction
    # must round-trip: the parser inverse is the exact inverse of the labeller's
    # forward digit map across all five directions.
    code = f"A1C{digit}"
    assert label(build_from_code(code, seed=0)) == code


def test_two_layer_code_splits_on_underscore() -> None:
    config = parse_code("A1_A2")
    assert len(config.layers) == 2
    assert config.layers[0].base_direction is Direction.HORIZONTAL
    assert config.layers[1].base_direction is Direction.VERTICAL


# ---------------------------------------------------------------------------
# AC2.3 — logic codes (bare X/Y/Z) parse, build, and label
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("code", "base", "op_class", "expected_label"),
    [
        ("X", BaseRelation.LOGICAL_OR, LogicalOR, "X7"),
        ("Y", BaseRelation.LOGICAL_AND, LogicalAND, "Y7"),
        ("Z", BaseRelation.LOGICAL_XOR, LogicalXOR, "Z7"),
    ],
)
def test_logic_codes_parse_build_label(
    code: str, base: BaseRelation, op_class: type, expected_label: str
) -> None:
    config = parse_code(code)
    layer = config.layers[0]
    assert layer.base is base
    assert layer.supplementals == ()
    matrix = build_from_code(code, seed=0)
    assert any(isinstance(s, op_class) for s in matrix.layers[0].structures)
    # The Logic transform always emits '7' (normalised to bare in Task 4).
    assert label(matrix) == expected_label


# ---------------------------------------------------------------------------
# AC2.4 — malformed codes raise ValueError
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "code",
    [
        "",          # empty.
        "A",         # missing digit on a non-logic letter.
        "Q9",        # unknown letter.
        "A9",        # digit out of the 1-5 range.
        "A0",        # zero is not a valid direction digit.
        "1A",        # leading digit (no letter).
        "AB",        # letter where a digit is expected.
        "A1_",       # trailing empty layer segment.
        "X1",        # logic letter must be bare (no digit).
    ],
)
def test_malformed_codes_raise_value_error(code: str) -> None:
    with pytest.raises(ValueError):
        parse_code(code)


# ---------------------------------------------------------------------------
# Property: codes from the valid grammar round-trip structurally for
# repetition-only forms (ShapeRep + FillRep), where the label adds no swap.
# ---------------------------------------------------------------------------

# Repetition features keep the same-direction digit, so a code built only from
# A (ShapeRep base) labels back to itself; the property checks parse->build->label
# is stable for that exact family across all four repetition directions.
_REPETITION_DIRECTION_DIGITS = st.sampled_from(["1", "2", "3", "4"])


@given(digit=_REPETITION_DIRECTION_DIGITS)
def test_shape_repetition_codes_round_trip_property(digit: str) -> None:
    code = f"A{digit}"
    assert label(build_from_code(code, seed=0)) == code


@given(digit=_REPETITION_DIRECTION_DIGITS)
def test_fill_repetition_round_trips_to_a_plus_b(digit: str) -> None:
    # B1-B4 are FillRep (repetition): the B part round-trips, the implicit
    # ShapeRepetition base prefixes an 'A' with the base's (default) direction.
    code = f"B{digit}"
    produced = label(build_from_code(code, seed=0))
    assert produced.endswith(f"B{digit}")
    assert produced.startswith("A")
