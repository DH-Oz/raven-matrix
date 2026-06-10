"""Structural labeller: matrix -> Matzen ``Structure`` code.

# pattern: Functional Core

``label()`` is a LITERAL port of the ``sb``-build inside
``SGMMatrixDifficultyClassifier.evaluate`` (``reference/sgmt-source/Source/gov/
sandia/cognition/generator/matrix/SGMMatrixDifficultyClassifier.java:208-389`` —
the ``evaluate(SGMMatrix)`` overload whose signature is at l.191). The Java method
also accumulates feature-count maps for the difficulty score; we port ONLY the
``sb`` (``StringBuilder``) thread, which is the structural label.

The faithful shape (line cites are into the Java above):

- ``sb`` starts empty (l.208); we walk ``matrix.layers`` (``getSGMLayers()``,
  l.210) and within each ``layer.structures`` (``getStructureFeatures()``, l.213).
- LETTER ladder (l.218-291): a ``BaseSGMStructureFeature`` emits one of
  ``A``/``X``/``Y``/``Z`` (ShapeRep / OR / AND / XOR) else ``U`` (l.232-251); a
  supplemental emits ``B``/``C``/``D``/``E``/``B`` (FillRep / Rotation / Scaling /
  Numerosity / ChangeFill) else ``V`` (l.267-290). NOTE both FillRep AND ChangeFill
  emit ``B`` — the source of the ``B``-aliasing resolved in ``parse_code``.
- DIGIT map (l.308-382): keyed on the feature's ``location_transform`` type AND
  whether the feature is a "repetition" feature (``ShapeRepetition`` OR
  ``FillPatternRepetition``, l.310-311 etc.). Repetition features keep the
  same-direction digit; every other feature SWAPS the ``1``/``2`` pair (and the
  ``3``/``4`` and ``5``/``6`` pairs): the label encodes the direction in which the
  feature stays the SAME, which for a non-repetition (changing) feature is the
  opposite axis. Horizontal->``1``/``2``, Vertical->``2``/``1``,
  DiagBLTR->``3``/``4``, DiagTLBR->``4``/``3``, CornerOut->``6``/``5`` (rep gets
  ``6``, the "may-not-correspond-to-norming" flag; non-rep gets ``5``, the
  documented outward gradient), Logic->``7`` (both), unknown->``0``.
- ``_`` after each layer (l.385); the trailing ``_`` is deleted at the end
  (l.389).

Reads BOUND structure features (``matrix.layers[].structures``), exactly as the
Java reads ``layer.getStructureFeatures()`` — never inferred from rendered cells.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from raven_matrix.model import BaseRelation, Direction, Matrix, Supplemental
from raven_matrix.structure.base import (
    BaseStructureFeature,
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
from raven_matrix.transforms.geometric import (
    DiagonalBottomLeftTopRight,
    DiagonalTopLeftBottomRight,
    Horizontal,
    TopLeftCornerOut,
    Vertical,
)
from raven_matrix.transforms.logic import LogicLocationTransform

if TYPE_CHECKING:
    from raven_matrix.builder import BuilderConfig, LayerConfig

# Digit pairs keyed by transform type: (repetition_digit, other_digit).
# Mirrors the per-transform if/else ladder (Java l.308-382): the FIRST digit is
# emitted when the feature is a repetition feature (ShapeRep or FillRep), the
# SECOND otherwise. Note the deliberate 1<->2, 3<->4 and 5<->6 swap encoded in
# each pair. Logic emits '7' regardless, so it is handled out of band.
_TRANSFORM_DIGITS: dict[type, tuple[str, str]] = {
    Horizontal: ("1", "2"),
    Vertical: ("2", "1"),
    DiagonalBottomLeftTopRight: ("3", "4"),
    DiagonalTopLeftBottomRight: ("4", "3"),
    TopLeftCornerOut: ("6", "5"),
}

# The 1:1 correspondence between a transform class and the Direction enum the
# builder realises it from. Lets parse_code invert _TRANSFORM_DIGITS (above)
# instead of maintaining a second, drift-prone digit->direction table.
_TRANSFORM_TO_DIRECTION: dict[type, Direction] = {
    Horizontal: Direction.HORIZONTAL,
    Vertical: Direction.VERTICAL,
    DiagonalBottomLeftTopRight: Direction.DIAGONAL_BL_TR,
    DiagonalTopLeftBottomRight: Direction.DIAGONAL_TL_BR,
    TopLeftCornerOut: Direction.TOP_LEFT_CORNER_OUT,
}


def _build_digit_inverses() -> tuple[dict[str, Direction], dict[str, Direction]]:
    """Invert ``_TRANSFORM_DIGITS`` into two digit -> Direction maps.

    A REPETITION feature (ShapeRep, FillRep) keeps the same-direction digit, so
    its inverse reads the FIRST element of each pair; a NON-repetition feature
    (Rotation, Scaling, Numerosity, ChangeFill) carries the labeller's ``1<->2``
    / ``3<->4`` (and ``5/6``) swap, so its inverse reads the SECOND. Deriving both
    from the single forward table guarantees the parser is the exact inverse of
    the labeller — they can never drift.
    """
    repetition: dict[str, Direction] = {}
    non_repetition: dict[str, Direction] = {}
    for transform, (repetition_digit, other_digit) in _TRANSFORM_DIGITS.items():
        direction = _TRANSFORM_TO_DIRECTION[transform]
        repetition[repetition_digit] = direction
        non_repetition[other_digit] = direction
    return repetition, non_repetition


_REP_DIGIT_TO_DIRECTION, _NONREP_DIGIT_TO_DIRECTION = _build_digit_inverses()


def _letter(feature: object) -> str:
    """Port the letter ladder (Java l.218-291).

    A base feature (``BaseStructureFeature``) emits A/X/Y/Z else U; a supplemental
    emits B/C/D/E/B else V. ChangeFill and FillRep both emit ``B`` (the aliasing).
    The base/supplemental split mirrors the Java
    ``instanceof BaseSGMStructureFeature`` branch (l.218): ShapeRep and the logic
    operations subclass ``AbstractBaseSGMStructureFeature``; the five supplementals
    subclass ``AbstractSupplementalSGMStructureFeature``.
    """
    if isinstance(feature, BaseStructureFeature):
        # Base structure features (l.232-251).
        if isinstance(feature, ShapeRepetition):
            return "A"
        if isinstance(feature, LogicalOR):
            return "X"
        if isinstance(feature, LogicalAND):
            return "Y"
        if isinstance(feature, LogicalXOR):
            return "Z"
        return "U"  # unknown base (l.250).
    # Supplemental structure features (l.267-290).
    if isinstance(feature, FillPatternRepetition):
        return "B"
    if isinstance(feature, ApplyRotation):
        return "C"
    if isinstance(feature, ApplyScaling):
        return "D"
    if isinstance(feature, TranslationalNumerosity):
        return "E"
    if isinstance(feature, ChangeFillPattern):
        return "B"
    return "V"  # unknown supplemental (l.289).


def _is_repetition_feature(feature: object) -> bool:
    """Repetition features keep the same-direction digit (Java l.310-311 etc.).

    The Java guard is ``instanceof ShapeRepetition || instanceof
    FillPatternRepetition`` at every transform branch; we hoist it once.
    """
    return isinstance(feature, ShapeRepetition | FillPatternRepetition)


def _digit(feature: object) -> str:
    """Port the digit map (Java l.308-382).

    Keyed on the feature's bound ``location_transform`` type and whether the
    feature is a repetition feature; Logic always emits ``7``; an unrecognised
    transform emits ``0`` (the Java final ``else``, l.379-382).
    """
    transform = getattr(feature, "location_transform", None)
    if isinstance(transform, LogicLocationTransform):
        return "7"
    pair = _TRANSFORM_DIGITS.get(type(transform))
    if pair is None:
        return "0"  # unknown transform (l.379-382).
    repetition_digit, other_digit = pair
    return repetition_digit if _is_repetition_feature(feature) else other_digit


def label(matrix: Matrix) -> str:
    """Return the Matzen ``Structure`` code for ``matrix``.

    Faithful port of the ``sb``-build in
    ``SGMMatrixDifficultyClassifier.java:208-389``. Walks each layer's bound
    structure features, appends a (letter, digit) pair per feature, and joins the
    layers with ``_`` (trailing separator deleted).

    Example: a single ShapeRepetition layer on the Horizontal transform yields
    ``"A1"``; a two-layer ShapeRep-Horizontal / ShapeRep-Vertical matrix yields
    ``"A1_A2"``.
    """
    parts: list[str] = []
    for layer in matrix.layers:
        for feature in layer.structures:
            parts.append(_letter(feature))
            parts.append(_digit(feature))
        parts.append("_")  # separate layers (l.385).
    if parts and parts[-1] == "_":
        parts.pop()  # remove final '_' (l.389).
    return "".join(parts)


# ===========================================================================
# parse_code — the naming-scheme INVERSE (a NEW artifact; no upstream parser)
# ===========================================================================
#
# parse_code reads a Matzen ``Structure`` code and produces a ``BuilderConfig``.
# It is NOT a port — there is no Java parser. It inverts the published naming
# convention (decoded in CLAUDE.md and the paper's sheet legend):
#
# - LETTER -> relation. ``A`` = ShapeRepetition (base). ``X``/``Y``/``Z`` =
#   logical OR/AND/XOR (base, logic) and are BARE — they carry no digit in the
#   published codes. ``B`` = shading, ``C`` = orientation (Rotation), ``D`` =
#   size (Scaling), ``E`` = number repetition (Numerosity) — all supplementals.
# - DIGIT -> transform direction, but the labeller's digit is the axis along
#   which the feature stays the SAME (the published 1-Layer PNGs confirm this:
#   A1 repeats the shape along rows, C2_1 CHANGES orientation along rows). For a
#   REPETITION feature (ShapeRep, FillRep) the constancy axis IS the transform
#   direction, so the digit maps directly (1 Horizontal, 2 Vertical, 3 BL->TR,
#   4 TL->BR). For a NON-repetition feature (Rotation/Scaling/Numerosity/
#   ChangeFill) the labeller swaps 1<->2 and 3<->4, so parse_code inverts that
#   swap (_NONREP_DIGIT_TO_DIRECTION) to rebuild the SAME stimulus, not its
#   transpose. Reading the digit literally was a bug (fixed): it built C1 as C2.
#
# B aliasing (resolved by the published PNG palettes — DR6 independent frame):
# both FillRep and ChangeFill label to ``B``. The 1-Layer norming PNGs distinguish
# them by fill palette (FillRep is a 3-level palette [White, Black, Grey75];
# ChangeFill is 5-level [White, Grey75, Grey40, Grey10, Black]). Inspection of
# ``B[1-5]_1.png`` (confirmed in Phase 5) shows ``B1``-``B4`` are FillRep on the
# matching transform (digit = direction, 3-level palette, constant along that
# axis) and ``B5`` is ChangeFill + corner-out (5-level outward gradient). So
# ``B1``-``B4`` -> ``FILL_REPETITION`` and ``B5`` -> ``CHANGE_FILL`` + corner-out.
# Digit 5 can only come from a non-repetition feature + corner-out, since FillRep
# (a repetition feature) + corner-out would label ``6`` (never seen in the codes).
#
# Supplemental-only codes (``C3``, ``D4E2``, ``E5``, …) — established BY READING
# THE SOURCE: ``AbstractRepetitionSGMStructureFeature.provideBaseSurfaceFeatures``
# (l.82-87) returns ``existingSurfaceFeaturesAtLocation`` UNCHANGED, and
# ``ChangeFill``/``FillRep``/``Numerosity`` likewise only rewrite features a base
# already placed. ``SGMLayerGenerator.generateLayer`` (l.92-98) ALWAYS creates a
# base structure feature first ("which defines the base surface features"), then
# adds supplementals. So a supplemental NEVER stands alone: a code with no base
# letter (``A``/``X``/``Y``/``Z``) gets an injected implicit ``ShapeRepetition``
# base. The label then re-emits that base's ``A`` letter, so a supplemental-only
# code does NOT round-trip to itself — a documented modeling gap (Task 4), not a
# bug.

# Letter -> base relation (the first pair in a non-supplemental-led segment).
_LETTER_TO_BASE: dict[str, BaseRelation] = {
    "A": BaseRelation.SHAPE_REPETITION,
    "X": BaseRelation.LOGICAL_OR,
    "Y": BaseRelation.LOGICAL_AND,
    "Z": BaseRelation.LOGICAL_XOR,
}
_LOGIC_LETTERS = frozenset({"X", "Y", "Z"})

# Letter -> non-aliased supplemental (C/D/E; B is resolved separately by digit).
_LETTER_TO_SUPPLEMENTAL: dict[str, Supplemental] = {
    "C": Supplemental.ROTATION,
    "D": Supplemental.SCALING,
    "E": Supplemental.NUMEROSITY,
}

# The implicit base direction for a supplemental-led code (no published base
# digit constrains it; HORIZONTAL is the documented default — the resulting 'A1'
# prefix is part of the documented round-trip modeling gap).
_IMPLICIT_BASE_DIRECTION = Direction.HORIZONTAL


def _parse_pairs(segment: str) -> list[tuple[str, str | None]]:
    """Split one layer segment into (letter, digit) pairs.

    Logic letters (``X``/``Y``/``Z``) are BARE: ``digit`` is ``None``. Every other
    letter MUST be followed by a single digit. Raises ``ValueError`` on a leading
    digit, a missing digit, a doubled letter, or any non-``[A-EXYZ0-9]`` char.
    """
    pairs: list[tuple[str, str | None]] = []
    index = 0
    length = len(segment)
    while index < length:
        letter = segment[index]
        if not letter.isalpha():
            raise ValueError(
                f"expected a relation letter at position {index} of {segment!r}, "
                f"got {letter!r}"
            )
        letter = letter.upper()
        index += 1
        if letter in _LOGIC_LETTERS:
            # Bare logic letter: must NOT be followed by a digit (the published
            # logic codes are bare).
            if index < length and segment[index].isdigit():
                raise ValueError(
                    f"logic letter {letter!r} must be bare (no digit) in {segment!r}"
                )
            pairs.append((letter, None))
            continue
        # Every non-logic letter needs exactly one digit.
        if index >= length or not segment[index].isdigit():
            raise ValueError(
                f"relation letter {letter!r} must be followed by a direction "
                f"digit in {segment!r}"
            )
        pairs.append((letter, segment[index]))
        index += 1
    return pairs


def _direction_from_digit(digit: str) -> Direction:
    """Map a direction digit (1-5) to a ``Direction``; bad digits raise.

    ``Direction(int(digit))`` raises ``ValueError`` for 0 or 6-9 (out of range).
    """
    return Direction(int(digit))


def _supplemental_from_pair(letter: str, digit: str) -> tuple[Supplemental, Direction]:
    """Resolve one supplemental (letter, digit) pair, inverting the labeller swap.

    ``B`` aliases two relations, disambiguated by digit (per the published PNG
    palettes): ``B5`` -> ChangeFill + corner-out (a non-repetition feature, the
    5-level outward gradient); ``B1``-``B4`` -> FillRep on the matching transform
    (a REPETITION feature, so the digit IS the direction directly, 3-level
    palette). ``C``/``D``/``E`` are NON-repetition supplementals: the labeller
    emits the swapped (constancy-axis) digit, so we invert it via
    ``_NONREP_DIGIT_TO_DIRECTION`` to recover the transform direction.

    Ground truth for the swap: ``C2_1.png`` shows orientation CHANGING
    horizontally (digit 2 -> Rotation on the Horizontal transform); ``C1_1.png``
    shows it changing vertically (digit 1 -> Vertical). Reading the digit
    literally would build the transpose of the published stimulus.
    """
    if letter == "B":
        if digit == "5":
            # B5: ChangeFill (non-repetition) + corner-out.
            return Supplemental.CHANGE_FILL, _NONREP_DIGIT_TO_DIRECTION["5"]
        direction = _REP_DIGIT_TO_DIRECTION.get(digit)
        if direction is None or direction is Direction.TOP_LEFT_CORNER_OUT:
            # FillRep is a repetition feature on directions 1-4 only (corner-out
            # with fill repetition never appears in the norming codes).
            raise ValueError(
                f"digit {digit!r} is not a valid FillRepetition direction in "
                f"B{digit}"
            )
        return Supplemental.FILL_REPETITION, direction
    supplemental = _LETTER_TO_SUPPLEMENTAL.get(letter)
    if supplemental is None:
        raise ValueError(f"unknown supplemental relation letter {letter!r}")
    direction = _NONREP_DIGIT_TO_DIRECTION.get(digit)
    if direction is None:
        raise ValueError(
            f"digit {digit!r} is not a valid direction for non-repetition "
            f"supplemental {letter!r}"
        )
    return supplemental, direction


def _parse_segment(segment: str) -> LayerConfig:
    """Parse one layer segment into a ``LayerConfig``.

    Classifies the FIRST pair as the base (``A``/``X``/``Y``/``Z``) or, if it is a
    supplemental letter, injects an implicit ``ShapeRepetition`` base. Remaining
    pairs are supplementals.
    """
    from raven_matrix.builder import LayerConfig

    if not segment:
        raise ValueError("empty layer segment")
    pairs = _parse_pairs(segment)
    if not pairs:
        raise ValueError(f"layer segment {segment!r} has no relations")

    # Default: an EXPLICIT base (A / X / Y / Z) is an active shape relation and
    # keeps the faithful three-distinct-shape ShapeRepetition. Only the implicit
    # base injected for supplemental-led codes becomes a constant carrier (ADR
    # 0002), so it flips this to True below.
    base_constant_shape = False
    first_letter, first_digit = pairs[0]
    if first_letter in _LETTER_TO_BASE:
        base = _LETTER_TO_BASE[first_letter]
        if first_letter in _LOGIC_LETTERS:
            # Bare logic base: it carries no direction and forbids supplementals.
            if len(pairs) > 1:
                raise ValueError(
                    f"logic base {first_letter!r} forbids supplementals in "
                    f"{segment!r}"
                )
            return LayerConfig(
                base=base, base_direction=_IMPLICIT_BASE_DIRECTION, supplementals=()
            )
        assert first_digit is not None  # non-logic base always has a digit.
        base_direction = _direction_from_digit(first_digit)
        supplemental_pairs = pairs[1:]
    else:
        # Supplemental-led code: inject an implicit ShapeRepetition base. The
        # supplemental relations provide no base surface features of their own
        # (see module note above), so a base must exist for them to act on.
        # That implicit base is a CONSTANT carrier shape (ADR 0002): the published
        # norming PNGs for these codes show ONE shape with only the named
        # supplemental varying, so the base must not introduce three distinct
        # shapes of its own (which would make a hidden ShapeRepetition relation).
        base = BaseRelation.SHAPE_REPETITION
        base_direction = _IMPLICIT_BASE_DIRECTION
        supplemental_pairs = pairs
        base_constant_shape = True

    supplementals: list[tuple[Supplemental, Direction]] = []
    for letter, digit in supplemental_pairs:
        if digit is None:
            # A logic letter only appears as the first pair of a segment.
            raise ValueError(
                f"logic letter {letter!r} cannot be a supplemental in {segment!r}"
            )
        supplementals.append(_supplemental_from_pair(letter, digit))

    return LayerConfig(
        base=base,
        base_direction=base_direction,
        supplementals=tuple(supplementals),
        base_constant_shape=base_constant_shape,
    )


def parse_code(code: str, *, correct_answer_position: int = 1) -> BuilderConfig:
    """Invert a Matzen ``Structure`` code into a ``BuilderConfig``.

    Splits on ``_`` into per-layer segments, parses each into a ``LayerConfig``,
    and wraps them with ``correct_answer_position`` (NOT encoded in the code, so it
    is defaulted — the structural oracle checks relations/directions, not position).

    Raises ``ValueError`` for any malformed code: empty, an unknown letter, a
    missing or out-of-range digit, a logic letter carrying a digit, an empty layer
    segment (e.g. a trailing ``_``), or a base/supplemental shape the upstream
    option surface could not produce.

    This is the naming-scheme inverse, NOT a port (no upstream parser exists). See
    the module note above for the B-aliasing and implicit-base derivations.
    """
    from raven_matrix.builder import BuilderConfig

    if not code:
        raise ValueError("cannot parse an empty Structure code")
    segments = code.split("_")
    if any(segment == "" for segment in segments):
        raise ValueError(
            f"Structure code {code!r} has an empty layer segment (a stray '_')"
        )
    layers = tuple(_parse_segment(segment) for segment in segments)
    return BuilderConfig(
        layers=layers, correct_answer_position=correct_answer_position
    )
