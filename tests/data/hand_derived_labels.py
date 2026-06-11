"""Hand-derived ``(BuilderConfig, expected_code)`` table — the AC2.1 anchor.

# pattern: independent reference frame (DR6)

EVERY ``expected_code`` here is derived BY HAND from the Matzen et al. (2010)
naming convention, the published ``Structure`` codes in ``data/ravens_oracle.csv``,
and (for the ``B`` shading entries) the published norming PNGs. NONE is read from
the Java labeller (``SGMMatrixDifficultyClassifier.java``) or from ``label()``'s
output. This is the whole point of the task: it is the only externally-grounded
guard on the labeller port, so its derivations must stand on the published ground
truth alone.

How the digit is derived (the one subtle step). The published convention names
the digit by the DIRECTION OF REPETITION — the axis along which the relation's
feature stays CONSTANT (1 horizontal, 2 vertical, 3 BL->TR diag, 4 TL->BR diag,
5 outward-from-top-left). For a REPETITION relation (ShapeRepetition,
FillPatternRepetition) the feature is constant along the very axis it is laid out
on, so the published digit equals the layout direction. For a CHANGE relation
(Rotation/Scaling/Numerosity/ChangeFill) the feature CHANGES along its layout axis
and stays constant along the OTHER axis, so the published digit names that other
(constancy) axis — visible directly in the PNGs (e.g. C2_1 rotates left-to-right
yet the published code is C2, the vertical/constant axis). The ``BuilderConfig``
takes the LAYOUT direction (the axis the relation advances along); the published
digit is read off the resulting constancy axis. Both readings are grounded in the
convention and the PNGs, never in the Java digit map.

The builder ALWAYS instantiates a base relation first
(``SGMLayerGenerator.generateLayer``; documented in ``label.py``), so a
single-supplemental matrix is built as ShapeRepetition-base + supplemental. The
published norming codes for those stimuli print only the supplemental letter
(``C2``, ``D4``, ``E5``) because the base is the implicit shape carrier; the
buildable matrix here carries an explicit ShapeRepetition base on the HORIZONTAL
layout, which the convention labels ``A1`` (see entry 1). So the supplemental
entries expect ``A1`` + the published supplemental code (``A1C2`` etc.). The
``A1`` prefix is itself an externally-grounded fragment (A1_* PNGs / the A1 CSV
rows); the supplemental fragment is the entry's anchored claim.
"""

from __future__ import annotations

from dataclasses import dataclass

from raven_matrix.builder import BuilderConfig, LayerConfig
from raven_matrix.model import BaseRelation, Direction, Supplemental


@dataclass(frozen=True, slots=True)
class HandDerivedEntry:
    """One anchored row: a buildable config + its hand-derived published label.

    ``externally_grounded`` is ``True`` when a published stimulus (CSV row and/or
    PNG) backs the code. It is ``False`` only for the labeller-internal-consistency
    entry (``A6``), which has NO published stimulus and therefore does NOT count
    toward DR6's independent-reference-frame guarantee.
    """

    label_id: str
    config: BuilderConfig
    expected_code: str
    externally_grounded: bool


def _one_layer(
    *,
    base: BaseRelation = BaseRelation.SHAPE_REPETITION,
    base_direction: Direction = Direction.HORIZONTAL,
    supplementals: tuple[tuple[Supplemental, Direction], ...] = (),
) -> BuilderConfig:
    """A one-layer config (correct-answer position is irrelevant to the label)."""
    return BuilderConfig(
        layers=(
            LayerConfig(
                base=base,
                base_direction=base_direction,
                supplementals=supplementals,
            ),
        ),
        correct_answer_position=1,
    )


# ===========================================================================
# (1-4) ShapeRepetition on each PUBLISHED direction. ShapeRep is a repetition
# relation, so the published digit is the layout direction itself (no swap):
# the shape stays constant along the axis it is laid out on.
#   A1: convention "1 = horizontal repetition"; CSV rows A1 (Stimulus A1_1..A1_4,
#       "One Relation"/"Shape"); PNG A1_1 shows one shape repeated across each row.
#   A2: convention "2 = vertical"; CSV rows A2 (A2_1..A2_4); PNG A2_1 repeats down
#       each column.
#   A3: convention "3 = BL->TR diagonal"; CSV rows A3 (A3_1..A3_4).
#   A4: convention "4 = TL->BR diagonal"; CSV rows A4 (A4_1..A4_4).
# Shape repetition never uses direction 5 (the convention excludes it; CSV has no
# A5/A6), which is why the corner-out ShapeRep case (entry 5) is NOT published.
# ===========================================================================
_SHAPE_REP_ENTRIES: tuple[HandDerivedEntry, ...] = (
    HandDerivedEntry(
        label_id="A1 shape-rep horizontal",
        config=_one_layer(base_direction=Direction.HORIZONTAL),
        expected_code="A1",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A2 shape-rep vertical",
        config=_one_layer(base_direction=Direction.VERTICAL),
        expected_code="A2",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A3 shape-rep diagonal BL->TR",
        config=_one_layer(base_direction=Direction.DIAGONAL_BL_TR),
        expected_code="A3",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A4 shape-rep diagonal TL->BR",
        config=_one_layer(base_direction=Direction.DIAGONAL_TL_BR),
        expected_code="A4",
        externally_grounded=True,
    ),
)


# ===========================================================================
# (5) ShapeRepetition + corner-out -> A6. LABELLER-INTERNAL-CONSISTENCY ONLY.
# NOT externally grounded: the norming study NEVER paired shape repetition with
# the outward-from-top-left direction (the convention says shape repetition
# excludes direction 5), and ``data/ravens_oracle.csv`` has ZERO A5 and ZERO A6
# rows. The ``6`` is derived purely from the convention's structure — a repetition
# relation laid out corner-out — but no published stimulus exercises it. This
# entry pins the port's internal handling of that unpublished combination; it must
# NOT be counted toward DR6's independent-reference-frame guarantee.
# ===========================================================================
_CORNER_OUT_SHAPE_REP_ENTRY = HandDerivedEntry(
    label_id="A6 shape-rep corner-out (labeller-internal only)",
    config=_one_layer(base_direction=Direction.TOP_LEFT_CORNER_OUT),
    expected_code="A6",
    externally_grounded=False,
)


# ===========================================================================
# (6-8) Shading (B). FillPatternRepetition and ChangeFillPattern BOTH print as
# ``B`` in the published codes; the published PNGs break the tie by FILL PALETTE
# (the DR6 image reference frame):
#   - FillRep uses a 3-level palette (White, Black, Grey75) and repeats one
#     shading along a whole axis.
#   - ChangeFill uses a 5-level palette (White, Grey75, Grey40, Grey10, Black) as
#     an outward gradient.
#
# B1 = FillRep + horizontal. PNG B1_1: each ROW is one constant shading (white /
#   dark / light grey), 3-level palette; the shading is CONSTANT along the
#   horizontal axis -> published digit 1. CSV rows B1 (B1_1..B1_4, "Shading").
# B2 = FillRep + vertical. PNG B2_1: each COLUMN is one constant shading, 3-level;
#   constant along the vertical axis -> published digit 2. CSV rows B2.
# B3 = FillRep + BL->TR diagonal. PNG B3_1: 3-level palette (white/grey/black), the
#   shading CONSTANT along the BL->TR diagonal (cells of equal row+col share a
#   shading: grey, then black, then white) -> published digit 3. CSV rows B3
#   (B3_1..B3_4, "Shading").
# B4 = FillRep + TL->BR diagonal. PNG B4_1: 3-level palette, the shading CONSTANT
#   along the TL->BR diagonal (cells of equal row-col share a shading) -> published
#   digit 4. CSV rows B4 (B4_1..B4_4, "Shading").
# B5 = ChangeFill + corner-out. PNG B5_1: a 5-level shading gradient darkening
#   OUTWARD from the top-left corner -> direction 5. Digit 5 can only arise from a
#   NON-repetition feature laid out corner-out (a repetition feature + corner-out
#   would print 6, never seen in the codes), and the 5-level palette confirms
#   ChangeFill rather than FillRep. CSV rows B5 (B5_1..B5_4, "Shading").
#
# Build note: all three are a ShapeRepetition base (HORIZONTAL -> A1) carrying the
# shading supplemental, so the buildable label is A1 + the published B code. The
# supplemental layout direction is the axis the shading ADVANCES along:
#   - FillRep is a repetition relation: it stays constant along its layout axis,
#     so to be constant horizontally (B1) it is laid out HORIZONTALLY, constant
#     vertically (B2) VERTICALLY, constant along BL->TR (B3) along DIAGONAL_BL_TR,
#     and constant along TL->BR (B4) along DIAGONAL_TL_BR (a repetition relation,
#     so no swap — the digit is the layout direction itself).
#   - ChangeFill is a change relation laid out corner-out; the outward gradient is
#     the corner-out layout itself -> TOP_LEFT_CORNER_OUT.
# ===========================================================================
_SHADING_ENTRIES: tuple[HandDerivedEntry, ...] = (
    HandDerivedEntry(
        label_id="A1B1 fill-rep horizontal (3-level palette, PNG B1_1)",
        config=_one_layer(
            supplementals=((Supplemental.FILL_REPETITION, Direction.HORIZONTAL),),
        ),
        expected_code="A1B1",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A1B2 fill-rep vertical (3-level palette, PNG B2_1)",
        config=_one_layer(
            supplementals=((Supplemental.FILL_REPETITION, Direction.VERTICAL),),
        ),
        expected_code="A1B2",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A1B3 fill-rep diagonal BL->TR (3-level palette, PNG B3_1)",
        config=_one_layer(
            supplementals=((Supplemental.FILL_REPETITION, Direction.DIAGONAL_BL_TR),),
        ),
        expected_code="A1B3",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A1B4 fill-rep diagonal TL->BR (3-level palette, PNG B4_1)",
        config=_one_layer(
            supplementals=((Supplemental.FILL_REPETITION, Direction.DIAGONAL_TL_BR),),
        ),
        expected_code="A1B4",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A1B5 change-fill corner-out (5-level gradient, PNG B5_1)",
        config=_one_layer(
            supplementals=((Supplemental.CHANGE_FILL, Direction.TOP_LEFT_CORNER_OUT),),
        ),
        expected_code="A1B5",
        externally_grounded=True,
    ),
)


# ===========================================================================
# (9-11) The three unambiguous-letter change supplementals. Each LETTER maps to
# exactly one relation (no aliasing): C = orientation/Rotation, D = size/Scaling,
# E = number/Numerosity. The DIGIT is the constancy axis, read off the PNG, so the
# BuilderConfig uses the OTHER (layout/change) axis.
#
# C2 = Rotation. PNG C2_1: ellipse orientation CHANGES left-to-right and stays
#   CONSTANT down each column -> constancy axis vertical -> published digit 2. So
#   the rotation is laid out (advances) HORIZONTALLY. CSV rows C2 (C2_1..C2_4,
#   "One Relation"/"Orientation"). Buildable label A1 + C2 = A1C2.
# D4 = Scaling. PNG D4_1: circle size stays CONSTANT along the TL->BR diagonal and
#   CHANGES along the BL->TR diagonal -> constancy axis TL->BR -> published digit
#   4. So the scaling advances along the BL->TR diagonal (DIAGONAL_BL_TR). CSV
#   rows D4 (D4_1..D4_4, "Size"). Buildable label A1 + D4 = A1D4.
# E5 = Numerosity. PNG E5_1: dot count INCREASES outward from the top-left corner
#   -> direction 5. CSV rows E5 (E5_1..E5_4, "Number"). The corner-out layout is
#   the gradient itself -> TOP_LEFT_CORNER_OUT. Buildable label A1 + E5 = A1E5.
# (3x3 is an odd square, so the diagonal/corner-out transforms are valid.)
# ===========================================================================
_SUPPLEMENTAL_ENTRIES: tuple[HandDerivedEntry, ...] = (
    HandDerivedEntry(
        label_id="A1C2 rotation (PNG C2_1: changes horizontally, constant vertically)",
        config=_one_layer(
            supplementals=((Supplemental.ROTATION, Direction.HORIZONTAL),),
        ),
        expected_code="A1C2",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A1D4 scaling (PNG D4_1: constant along TL->BR, changes along BL->TR)",
        config=_one_layer(
            supplementals=((Supplemental.SCALING, Direction.DIAGONAL_BL_TR),),
        ),
        expected_code="A1D4",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="A1E5 numerosity (PNG E5_1: count grows outward from top-left)",
        config=_one_layer(
            supplementals=((Supplemental.NUMEROSITY, Direction.TOP_LEFT_CORNER_OUT),),
        ),
        expected_code="A1E5",
        externally_grounded=True,
    ),
)


# ===========================================================================
# (12-14) Logic relations. The published codes are BARE letters: X = OR, Y = AND,
# Z = XOR (convention "X OR, Y AND, Z XOR"; CSV rows X / Y / Z, "Logic"). A logic
# relation carries no direction in the published code. The labeller, however,
# always tags a Logic-transform feature with the digit 7 (the Logic transform's
# fixed digit), so the PRE-NORMALISATION label is X7 / Y7 / Z7. The round-trip
# harness (Task 4) strips that trailing 7 to recover the bare published code; here
# we anchor the pre-normalisation form the labeller is expected to emit, since the
# 7 is the published-grounded consequence of the relation BEING a logic transform
# (the bare X/Y/Z + the logic-transform fact -> X7/Y7/Z7).
# ===========================================================================
_LOGIC_ENTRIES: tuple[HandDerivedEntry, ...] = (
    HandDerivedEntry(
        label_id="X7 logical OR (bare X, +7 from the logic transform)",
        config=_one_layer(base=BaseRelation.LOGICAL_OR),
        expected_code="X7",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="Y7 logical AND (bare Y, +7 from the logic transform)",
        config=_one_layer(base=BaseRelation.LOGICAL_AND),
        expected_code="Y7",
        externally_grounded=True,
    ),
    HandDerivedEntry(
        label_id="Z7 logical XOR (bare Z, +7 from the logic transform)",
        config=_one_layer(base=BaseRelation.LOGICAL_XOR),
        expected_code="Z7",
        externally_grounded=True,
    ),
)


HAND_DERIVED_LABELS: tuple[HandDerivedEntry, ...] = (
    *_SHAPE_REP_ENTRIES,
    _CORNER_OUT_SHAPE_REP_ENTRY,
    *_SHADING_ENTRIES,
    *_SUPPLEMENTAL_ENTRIES,
    *_LOGIC_ENTRIES,
)
