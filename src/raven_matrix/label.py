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

from raven_matrix.model import Matrix
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
