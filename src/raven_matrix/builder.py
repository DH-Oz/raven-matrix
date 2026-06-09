"""The headless builder: config-driven layer generation and composition.

# pattern: Functional Core

This reconstructs the GUI-driven generation path (``SGMBuilderFrame.generateMatrix``
+ ``SGMLayer`` + ``SGMMatrix``) as a single pure function of an explicit
``BuilderConfig`` + ``seed`` + ``CompatFlags``. The design re-models the boundary
(DR1): the upstream's config-level RNG draws -- ``numLayers`` and
``correctAnswerPosition`` (``SGMMatrixSetGenerator.java:144,150``), and the per-
structure-feature *type* / *direction* draws (the ``UNSPECIFIED`` branches of the
generators) -- are replaced by config. The shared ``JavaRandom(seed)`` is used
ONLY for the genuinely stochastic parts the GUI still leaves to chance:

- the surface-feature shapes/sizes/fills (``SGMSurfaceFeatureGenerator``),
- the logic base-pool size + content + base-location assignment,
- the numerosity ``initialNumerosity`` draw,
- and (Task 6) the distractor mutation.

DECISION (make_location_transform contract): ``BuilderConfig``/``LayerConfig``
carry parsed ``Direction`` ENUMS, never raw digits. ``build_layer`` passes a
``Direction`` to ``make_location_transform``. The factory's ``int`` acceptance is
reserved for Phase-5 ``parse_code`` (oracle ``Structure``-code digits); the config
boundary is ALWAYS a ``Direction``.

Sources (reference/sgmt-source/Source/.../):
- ``ui/SGMBuilderFrame.java:1086-1368`` (the option surface this config mirrors).
- ``SGMLayerGenerator.java:80-117`` (base-then-supplementals; logic forbids
  supplementals at l.102-113).
- ``SGMLayer.java:132-356`` (the per-cell traversal ported by ``build_layer``).
- ``BaseSGMStructureFeatureGenerator.java:120-324`` (base pool generation).
- ``SupplementalSGMStructureFeatureGenerator.java:142-270`` (supplemental params).
- ``SGMMatrix.java:198-228`` (the ``combineWith`` composition ported by
  ``compose_layers``).
"""

from __future__ import annotations

from dataclasses import dataclass

from raven_matrix.compat import CompatFlags
from raven_matrix.fillpattern import CHANGE_FILL_CYCLE, FILL_REP_CYCLE
from raven_matrix.model import (
    BaseRelation,
    Cell,
    Direction,
    Fill,
    Layer,
    Location,
    MatrixSize,
    Supplemental,
    SurfaceFeature,
)
from raven_matrix.rng import JavaRandom
from raven_matrix.structure.base import (
    BaseStructureFeature,
    LogicalAND,
    LogicalOR,
    LogicalXOR,
    LogicOperation,
    ShapeRepetition,
)
from raven_matrix.structure.supplemental import (
    MAX_INITIAL_NUMEROSITY,
    ApplyRotation,
    ApplyScaling,
    ChangeFillPattern,
    FillPatternRepetition,
    SupplementalStructureFeature,
    TranslationalNumerosity,
)
from raven_matrix.surface import generate_surface_feature
from raven_matrix.transforms import make_location_transform
from raven_matrix.transforms.logic import LogicLocationTransform

# Pinned upstream constants (option-surface parity with SGMBuilderFrame).
MAX_SUPPLEMENTALS_PER_LAYER = 3       # SGMBuilderFrame.java:1030 (max - 1 base).
NUM_ANSWER_CHOICES = 8                # SGMBuilderFrame.java:1031.
ROTATE_AMOUNT = 45                    # SupplementalGenerator.java:235.
SCALE_AMOUNT = 0.66                   # SupplementalGenerator.java:213.

# Logic base pool size bounds (BaseSGMStructureFeatureGenerator.java:106-107).
_MIN_LOGIC_FEATURES = 3
_MAX_LOGIC_FEATURES = 5

# The logic base pool draws surfaces with White fill only
# (BaseSGMStructureFeatureGenerator.java:200-202): allowedFillPatterns=[White].
_LOGIC_ALLOWED_FILLS: list[Fill] = [Fill.WHITE]

_LOGIC_BASES = frozenset(
    {BaseRelation.LOGICAL_OR, BaseRelation.LOGICAL_AND, BaseRelation.LOGICAL_XOR}
)
_LOGIC_OP_CLASS: dict[BaseRelation, type[LogicOperation]] = {
    BaseRelation.LOGICAL_OR: LogicalOR,
    BaseRelation.LOGICAL_AND: LogicalAND,
    BaseRelation.LOGICAL_XOR: LogicalXOR,
}


# ---------------------------------------------------------------------------
# Config dataclasses (the SGMBuilderFrame option surface, DR1)
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class LayerConfig:
    """One layer: a base relation + direction, plus <=3 supplementals.

    Mirrors one column of ``SGMBuilderFrame`` (base relation + its direction, then
    up to three supplementals each with their own direction). All fields are
    parsed ENUMS, never raw digits.
    """

    base: BaseRelation
    base_direction: Direction
    supplementals: tuple[tuple[Supplemental, Direction], ...] = ()


@dataclass(frozen=True, slots=True)
class BuilderConfig:
    """A full matrix config: 1-2 layers + a 1-based correct-answer position."""

    layers: tuple[LayerConfig, ...]
    correct_answer_position: int


# ---------------------------------------------------------------------------
# Validation (AC1.4)
# ---------------------------------------------------------------------------

def validate_config(config: BuilderConfig) -> None:
    """Reject configs the upstream option surface could not produce (AC1.4).

    Raises ``ValueError`` for: not 1-2 layers; >3 supplementals in any layer; a
    ``correct_answer_position`` outside 1-8; or supplementals atop a logic base
    (``gen-supplemental-disabled-when-logic-base``,
    ``SGMLayerGenerator.java:102-113``).
    """
    if not 1 <= len(config.layers) <= 2:
        raise ValueError(
            f"a matrix must have 1 or 2 layers; got {len(config.layers)}"
        )
    if not 1 <= config.correct_answer_position <= NUM_ANSWER_CHOICES:
        raise ValueError(
            "correct_answer_position must be within 1 to "
            f"{NUM_ANSWER_CHOICES}; got {config.correct_answer_position}"
        )
    for index, layer in enumerate(config.layers):
        if len(layer.supplementals) > MAX_SUPPLEMENTALS_PER_LAYER:
            raise ValueError(
                f"layer {index} has {len(layer.supplementals)} supplementals; at "
                f"most {MAX_SUPPLEMENTALS_PER_LAYER} are allowed"
            )
        if layer.base in _LOGIC_BASES and layer.supplementals:
            raise ValueError(
                f"layer {index} uses a logic base relation ({layer.base.name}), "
                "which forbids supplemental relations"
            )


# ---------------------------------------------------------------------------
# Base relation construction (BaseSGMStructureFeatureGenerator)
# ---------------------------------------------------------------------------

def _build_shape_repetition(
    direction: Direction,
    size: MatrixSize,
    cell_pixel_size: int,
    rng: JavaRandom,
    flags: CompatFlags,
) -> ShapeRepetition:
    """Port ``createBasicBaseSurfaceFeatures`` (l.266-304): one unique-shape
    feature per base location.

    For each base location, draw a surface feature; if its shape class is already
    used, redraw until a fresh shape appears (``uniqueShapes`` is always ``true``
    on this path, l.281-300). Each base location holds a single-feature list.
    """
    transform = make_location_transform(direction, size)
    num_base_locations = len(transform.base_locations())
    base_surface_features: list[list[SurfaceFeature]] = []
    shapes_used: set = set()
    for _ in range(num_base_locations):
        feature = generate_surface_feature(rng, flags, cell_pixel_size)
        while feature.shape in shapes_used:
            feature = generate_surface_feature(rng, flags, cell_pixel_size)
        shapes_used.add(feature.shape)
        base_surface_features.append([feature])
    return ShapeRepetition(transform, base_surface_features)


def _build_logic_operation(
    base: BaseRelation,
    size: MatrixSize,
    cell_pixel_size: int,
    rng: JavaRandom,
    flags: CompatFlags,
) -> LogicOperation:
    """Port the logic branch (``BaseSGMStructureFeatureGenerator.java:198-249``).

    Draw ``numSurfaceFeatures = next_int(3) + 3`` (3-5), then fill a VALUE-DISTINCT
    pool (the ``containsCheck`` loop, l.210-221): repeatedly draw a White-only
    surface feature and append it only if no pooled feature value-equals it. The
    value dedup both honours the upstream distinctness intent (l.306-323) and
    guarantees the assignment loop in ``LogicOperation`` terminates (the loop can
    only complete when every feature is placeable, which requires distinctness).
    The chosen ``LogicOperation`` constructor then runs the base-location
    assignment draws.
    """
    # next_int(MAX - MIN + 1) + MIN  (l.204-207); MAX=5, MIN=3 -> next_int(3)+3.
    num_surface_features = (
        rng.next_int(_MAX_LOGIC_FEATURES - _MIN_LOGIC_FEATURES + 1)
        + _MIN_LOGIC_FEATURES
    )
    pool: list[SurfaceFeature] = []
    while len(pool) < num_surface_features:
        feature = generate_surface_feature(
            rng, flags, cell_pixel_size, _LOGIC_ALLOWED_FILLS
        )
        if not _pool_contains_value(pool, feature):
            pool.append(feature)
    transform = LogicLocationTransform(size)
    return _LOGIC_OP_CLASS[base](transform, pool, rng)


def _pool_contains_value(
    pool: list[SurfaceFeature], candidate: SurfaceFeature
) -> bool:
    """Value membership for the pool dedup (``containsCheck`` l.306-323)."""
    return any(f.value_equals(candidate) for f in pool)


def _build_base_relation(
    layer_config: LayerConfig,
    size: MatrixSize,
    cell_pixel_size: int,
    rng: JavaRandom,
    flags: CompatFlags,
) -> BaseStructureFeature:
    """Dispatch to ShapeRepetition or a logic op, per the configured base."""
    if layer_config.base in _LOGIC_BASES:
        return _build_logic_operation(
            layer_config.base, size, cell_pixel_size, rng, flags
        )
    return _build_shape_repetition(
        layer_config.base_direction, size, cell_pixel_size, rng, flags
    )


# ---------------------------------------------------------------------------
# Supplemental construction (SupplementalSGMStructureFeatureGenerator)
# ---------------------------------------------------------------------------

def _build_supplemental(
    kind: Supplemental,
    direction: Direction,
    size: MatrixSize,
    cell_pixel_size: int,
    rng: JavaRandom,
) -> SupplementalStructureFeature:
    """Build one supplemental with its pinned params (l.209-267).

    Only ``NUMEROSITY`` draws RNG on the config path (``initialNumerosity =
    next_int(2) + 1``, l.243-244); the others take fixed params. The location
    transform is created first (l.167-169) and never draws on the specified path.
    """
    transform = make_location_transform(direction, size)
    match kind:
        case Supplemental.ROTATION:
            return ApplyRotation(transform, ROTATE_AMOUNT)
        case Supplemental.SCALING:
            return ApplyScaling(transform, SCALE_AMOUNT)
        case Supplemental.FILL_REPETITION:
            return FillPatternRepetition(transform, list(FILL_REP_CYCLE))
        case Supplemental.CHANGE_FILL:
            return ChangeFillPattern(transform, list(CHANGE_FILL_CYCLE))
        case Supplemental.NUMEROSITY:
            initial_numerosity = rng.next_int(MAX_INITIAL_NUMEROSITY) + 1
            return TranslationalNumerosity(
                transform, cell_pixel_size, size, initial_numerosity
            )


# ---------------------------------------------------------------------------
# Layer build (SGMLayer traversal) and composition
# ---------------------------------------------------------------------------

def build_layer(
    layer_config: LayerConfig,
    size: MatrixSize,
    cell_pixel_size: int,
    rng: JavaRandom,
    flags: CompatFlags,
) -> Layer:
    """Build one layer's grid of cells (port of ``SGMLayer``, l.132-356).

    Instantiates the base relation, then (for a non-logic base) each supplemental
    in config order, and applies each structure feature in turn to populate the
    grid -- mirroring the upstream's structure-feature loop. Logic ops take the
    special 2x2-seed-then-combine path; geometric features walk their transform.
    """
    base_relation = _build_base_relation(
        layer_config, size, cell_pixel_size, rng, flags
    )
    structure_features: list[object] = [base_relation]
    if layer_config.base not in _LOGIC_BASES:
        for kind, direction in layer_config.supplementals:
            structure_features.append(
                _build_supplemental(kind, direction, size, cell_pixel_size, rng)
            )

    grid: list[list[Cell | None]] = [
        [None] * size.num_columns for _ in range(size.num_rows)
    ]
    for structure_feature in structure_features:
        if isinstance(structure_feature, LogicOperation):
            _apply_logic_structure(structure_feature, grid, size)
        elif isinstance(structure_feature, ShapeRepetition):
            _apply_base_structure(structure_feature, grid)
        else:
            assert isinstance(structure_feature, SupplementalStructureFeature)
            _apply_supplemental_structure(structure_feature, grid)

    cells: list[list[Cell]] = [
        [_require_cell(grid[r][c]) for c in range(size.num_columns)]
        for r in range(size.num_rows)
    ]
    return Layer(cells=cells, structures=list(structure_features))


def _require_cell(cell: Cell | None) -> Cell:
    if cell is None:  # defense-in-depth: every cell must be populated by now.
        raise ValueError("layer build left a cell unpopulated")
    return cell


def _apply_logic_structure(
    relation: LogicOperation,
    grid: list[list[Cell | None]],
    size: MatrixSize,
) -> None:
    """Port the logic branch (``SGMLayer.java:175-242``).

    Seed the four 2x2 base cells from ``provide_base_surface_features``, then scan
    the grid row-major filling each null cell from TWO prior cells: for ``row >
    1`` the two cells directly above (``[row-2][col]``, ``[row-1][col]``); else
    the two cells to the left (``[row][col-2]``, ``[row][col-1]``). NEVER calls
    ``next_location`` / ``parent_location`` on the (partial) Logic transform.
    """
    transform = relation.location_transform
    for base_index, location in enumerate(transform.base_locations()):
        grid[location.row][location.column] = Cell(
            surface_features=relation.provide_base_surface_features(base_index),
            location=Location(location.row, location.column),
        )
    for row in range(size.num_rows):
        for column in range(size.num_columns):
            if grid[row][column] is not None:
                continue
            if row > 1:
                cell_one = grid[row - 2][column]
                cell_two = grid[row - 1][column]
            else:
                cell_one = grid[row][column - 2]
                cell_two = grid[row][column - 1]
            assert cell_one is not None and cell_two is not None
            grid[row][column] = Cell(
                surface_features=relation.combine_surface_features(
                    cell_one.surface_features, cell_two.surface_features
                ),
                location=Location(row, column),
            )


def _apply_base_structure(
    relation: ShapeRepetition, grid: list[list[Cell | None]]
) -> None:
    """Port the geometric base branch (``SGMLayer.java:243-353``, base case).

    For each base location, seed its cell, then walk ``next_location`` until it
    returns to the base location, deriving each cell from its
    ``parent_location``'s features via ``transform_surface_features``.
    """
    transform = relation.location_transform
    for base_index, base_location in enumerate(transform.base_locations()):
        grid[base_location.row][base_location.column] = Cell(
            surface_features=relation.provide_base_surface_features(base_index),
            location=Location(base_location.row, base_location.column),
        )
        current = transform.next_location(base_location)
        while current != base_location:
            parent_location = transform.parent_location(current)
            parent_cell = grid[parent_location.row][parent_location.column]
            assert parent_cell is not None
            grid[current.row][current.column] = Cell(
                surface_features=relation.transform_surface_features(
                    parent_cell.surface_features
                ),
                location=Location(current.row, current.column),
            )
            current = transform.next_location(current)


def _apply_supplemental_structure(
    relation: SupplementalStructureFeature, grid: list[list[Cell | None]]
) -> None:
    """Port the geometric supplemental branch (``SGMLayer.java:243-353``).

    Like the base branch, but each hook also receives the EXISTING features the
    prior structure feature(s) placed at that cell, and the supplemental rewrites
    them. Base cells use ``provide_base_surface_features(base_index, existing)``;
    derived cells use ``transform_surface_features(parent_features, existing)``.
    """
    transform = relation.location_transform
    for base_index, base_location in enumerate(transform.base_locations()):
        existing_cell = grid[base_location.row][base_location.column]
        existing = (
            existing_cell.surface_features if existing_cell is not None else []
        )
        grid[base_location.row][base_location.column] = Cell(
            surface_features=relation.provide_base_surface_features(
                base_index, existing
            ),
            location=Location(base_location.row, base_location.column),
        )
        current = transform.next_location(base_location)
        while current != base_location:
            existing_cell = grid[current.row][current.column]
            existing = (
                existing_cell.surface_features
                if existing_cell is not None
                else []
            )
            parent_location = transform.parent_location(current)
            parent_cell = grid[parent_location.row][parent_location.column]
            assert parent_cell is not None
            grid[current.row][current.column] = Cell(
                surface_features=relation.transform_surface_features(
                    parent_cell.surface_features, existing
                ),
                location=Location(current.row, current.column),
            )
            current = transform.next_location(current)


def compose_layers(layers: list[Layer], size: MatrixSize) -> list[list[Cell]]:
    """Composite layers per cell by concatenation (``SGMMatrix.java:198-228``).

    Each output cell holds every layer's surface-feature list at that location, in
    layer order (``combineWith`` semantics). Feature instances are shared, not
    copied, mirroring the upstream ``addAll``.
    """
    composed: list[list[Cell]] = []
    for row in range(size.num_rows):
        composed_row: list[Cell] = []
        for column in range(size.num_columns):
            features: list[SurfaceFeature] = []
            for layer in layers:
                features.extend(layer.cells[row][column].surface_features)
            composed_row.append(
                Cell(surface_features=features, location=Location(row, column))
            )
        composed.append(composed_row)
    return composed
