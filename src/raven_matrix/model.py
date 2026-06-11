"""Domain model for the Raven-matrix port of SGMT.

Enums mirror the Java surface/fill/structure/locationtransform packages.
Frozen value dataclasses replace Java classes that defined equals+hashCode.
SurfaceFeature is a plain identity class (no __eq__/__hash__ override) mirroring
the upstream's absent hashCode and typed-overload equals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Any, NamedTuple

# ---------------------------------------------------------------------------
# RGBA palette entry — named access so .a reads cleanly
# ---------------------------------------------------------------------------


class Rgba(NamedTuple):
    r: float
    g: float
    b: float
    a: float


# ---------------------------------------------------------------------------
# Shape — 7 upstream surface shapes
# ---------------------------------------------------------------------------


class Shape(Enum):
    DIAMOND = auto()
    ELLIPSE = auto()
    LINE = auto()
    RECTANGLE = auto()
    TEE = auto()
    TRAPEZOID = auto()
    TRIANGLE = auto()


# ---------------------------------------------------------------------------
# Fill — the five shading levels (Matzen et al. 2010, "five possible fill
# patterns").  Each value is an Rgba NamedTuple; RGBA drives rendering only and
# is not a fidelity target (the bar is data/logic equivalence, not pixels).
#
# Deliberate divergence from upstream: SGMT compares fills by getDescription()
# inside AbstractSGMSurfaceFeature.customEqualsCheck, and both
# Grey10SGMFillPattern and Grey40SGMFillPattern return DESCRIPTION = "Red" (a
# copy-paste bug — the Grey10 source file is even mis-headed
# "Grey25SGMFillPattern.java").  That makes upstream treat Grey10 and Grey40 as
# the SAME fill in feature/cell equality.  The paper specifies five DISTINCT
# fill patterns, and per project policy the paper is the fundamental spec, so we
# fix the bug: the five fills are distinct and compared by enum identity (see
# SurfaceFeature.value_equals).  We carry no description string — it encoded only
# the Swing label and the bug.
# ---------------------------------------------------------------------------


class Fill(Enum):
    BLACK = Rgba(0.0, 0.0, 0.0, 0.75)
    WHITE = Rgba(1.0, 1.0, 1.0, 0.0)
    GREY10 = Rgba(0.1, 0.1, 0.1, 0.6)
    GREY40 = Rgba(0.4, 0.4, 0.4, 0.5)
    GREY75 = Rgba(0.75, 0.75, 0.75, 0.4)


# ---------------------------------------------------------------------------
# BaseRelation — four base relation types
# ---------------------------------------------------------------------------


class BaseRelation(Enum):
    SHAPE_REPETITION = auto()
    LOGICAL_OR = auto()
    LOGICAL_AND = auto()
    LOGICAL_XOR = auto()


# ---------------------------------------------------------------------------
# Supplemental — five supplemental relation types
# ---------------------------------------------------------------------------


class Supplemental(Enum):
    ROTATION = auto()
    SCALING = auto()
    CHANGE_FILL = auto()
    FILL_REPETITION = auto()
    NUMEROSITY = auto()


# ---------------------------------------------------------------------------
# Direction — IntEnum so it can be compared against the Matzen digit codes
# ---------------------------------------------------------------------------


class Direction(IntEnum):
    HORIZONTAL = 1
    VERTICAL = 2
    DIAGONAL_BL_TR = 3
    DIAGONAL_TL_BR = 4
    TOP_LEFT_CORNER_OUT = 5


# ---------------------------------------------------------------------------
# Frozen value dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MatrixSize:
    num_rows: int
    num_columns: int


@dataclass(frozen=True, slots=True)
class Location:
    row: int
    column: int


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float


# ---------------------------------------------------------------------------
# SurfaceFeature — plain identity class (no __eq__/__hash__ override)
# Mirrors upstream's missing hashCode + typed-overload equals pattern.
# ---------------------------------------------------------------------------


class SurfaceFeature:
    """A surface feature drawn in one cell.

    Identity equality is deliberate: two SurfaceFeature instances are only
    ``==`` if they are the same object, mirroring the upstream Java class
    that defines no hashCode and uses a typed equals overload.  Use
    value_equals() for value comparison; use contains_check() for
    membership tests over lists.
    """

    __slots__ = ("shape", "fill", "scale", "rotation", "position", "width", "height")

    def __init__(
        self,
        shape: Shape,
        fill: Fill,
        scale: float,
        rotation: float,
        position: Point,
        width: float,
        height: float,
    ) -> None:
        self.shape = shape
        self.fill = fill
        self.scale = scale
        self.rotation = rotation
        self.position = position
        # Absolute pixel dimensions from the generator's 1/4, 1/2, 3/4-cell
        # draw. scale is a SEPARATE multiplier (birthed at 1.0 in the Java
        # constructors, e.g. RectangleSGMSurfaceFeature.java:103) that the
        # supplementals multiply later; do not conflate it with width/height.
        # For Line, width carries the single length value (height is unused).
        self.width = width
        self.height = height

    def value_equals(self, other: SurfaceFeature) -> bool:
        """Value comparison mirroring AbstractSGMSurfaceFeature.equals.

        Combines the common checks (scale, rotation, position, shape, fill;
        AbstractSGMSurfaceFeature.java:175-180) AND-ed with the per-shape
        customEqualsCheck geometry term:

        - Most shapes (Rectangle, Ellipse, the path-based Triangle/Tee/
          Diamond/Trapezoid) compare ``width*scale`` and ``height*scale``
          (RectangleSGMSurfaceFeature.java:192-195;
          AbstractPathBasedSGMSurfaceFeature.java:188-191).
        - Line compares ``length*scale`` only and ignores height
          (LineSGMSurfaceFeature.java:191-194). Line stores its length in
          ``width``, so we compare ``width*scale`` and skip the height term.

        Fill is compared by enum identity, so the five shadings stay distinct.
        Upstream instead compares fills by getDescription(), under which the
        Grey10/Grey40 "Red" label bug collapses those two shadings; we follow
        the Matzen 2010 paper (five distinct fill patterns) and do not
        reproduce that collapse.  See the Fill enum comment for detail.
        """
        common = (
            self.shape is other.shape
            and self.fill is other.fill
            and self.scale == other.scale
            and self.rotation == other.rotation
            and self.position == other.position
        )
        if not common:
            return False
        # width*scale is the compared quantity, not raw width (customEqualsCheck).
        if self.width * self.scale != other.width * other.scale:
            return False
        # Line ignores height (length-only check); every other shape compares it.
        if self.shape is Shape.LINE:
            return True
        return self.height * self.scale == other.height * other.scale


# ---------------------------------------------------------------------------
# contains_check — feature-list helper (mirrors SGMBaseCell.containsFeatureCheck)
# ---------------------------------------------------------------------------


def contains_check(
    features: list[SurfaceFeature | None],
    item: SurfaceFeature,
) -> bool:
    """Return True iff some non-None element value_equals item."""
    for feature in features:
        if feature is not None and feature.value_equals(item):
            return True
    return False


# ---------------------------------------------------------------------------
# Containers — minimal data holders; Phase 4 populates them
# ---------------------------------------------------------------------------


@dataclass
class Cell:
    """One cell in a matrix, holding its surface features and grid location.

    ``location`` is ``None`` for answer-choice cells (distractors and blank
    pads), mirroring the upstream ``SGMLocation``-null answer cells
    (``SGMMatrix.java:475,564``); grid cells always carry a real location.
    """

    surface_features: list[SurfaceFeature]
    location: Location | None


@dataclass
class Layer:
    """One layer of a matrix: a grid of cells plus its structure descriptors."""

    cells: list[list[Cell]]
    structures: list[Any]  # placeholder; structure-feature type lands in Phase 4


@dataclass
class Matrix:
    """A complete generated matrix with answer choices."""

    cells: list[list[Cell]]
    answer_choices: list[Cell]
    correct_answer_position: int
    layers: list[Layer]
