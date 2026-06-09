"""Domain model for the Raven-matrix port of SGMT.

Enums mirror the Java surface/fill/structure/locationtransform packages.
Frozen value dataclasses replace Java classes that defined equals+hashCode.
SurfaceFeature is a plain identity class (no __eq__/__hash__ override) mirroring
the upstream's absent hashCode and typed-overload equals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import NamedTuple  # noqa: UP035 — NamedTuple subclass syntax requires this

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
# Fill — 5 upstream fill patterns; each value is an Rgba NamedTuple
# ---------------------------------------------------------------------------

class Fill(Enum):
    BLACK  = Rgba(0.0,  0.0,  0.0,  0.75)
    WHITE  = Rgba(1.0,  1.0,  1.0,  0.0)
    GREY10 = Rgba(0.1,  0.1,  0.1,  0.6)
    GREY40 = Rgba(0.4,  0.4,  0.4,  0.5)
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
    HORIZONTAL          = 1
    VERTICAL            = 2
    DIAGONAL_BL_TR      = 3
    DIAGONAL_TL_BR      = 4
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

    __slots__ = ("shape", "fill", "scale", "rotation", "position")

    def __init__(
        self,
        shape: Shape,
        fill: Fill,
        scale: float,
        rotation: float,
        position: Point,
    ) -> None:
        self.shape = shape
        self.fill = fill
        self.scale = scale
        self.rotation = rotation
        self.position = position

    def value_equals(self, other: SurfaceFeature) -> bool:
        """Value comparison mirroring AbstractSGMSurfaceFeature.equals.

        Compares scale, rotation, position, shape, and fill.  No
        shape-specific custom check is implemented here (YAGNI; Phase 4
        adds geometry).
        """
        return (
            self.shape is other.shape
            and self.fill is other.fill
            and self.scale == other.scale
            and self.rotation == other.rotation
            and self.position == other.position
        )


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
    """One cell in a matrix, holding its surface features and grid location."""
    surface_features: list[SurfaceFeature]
    location: Location


@dataclass
class Layer:
    """One layer of a matrix: a grid of cells plus its structure descriptors."""
    cells: list[list[Cell]]
    structures: list  # typed fully in Phase 4


@dataclass
class Matrix:
    """A complete generated matrix with answer choices."""
    cells: list[list[Cell]]
    answer_choices: list[Cell]
    correct_answer_position: int
    layers: list[Layer]
