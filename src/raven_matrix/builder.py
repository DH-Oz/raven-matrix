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

from raven_matrix.compat import DEFAULT_FLAGS, CompatFlags
from raven_matrix.fillpattern import (
    CHANGE_FILL_CYCLE,
    FILL_REP_CYCLE,
    generate_fill,
)
from raven_matrix.model import (
    BaseRelation,
    Cell,
    Direction,
    Fill,
    Layer,
    Location,
    Matrix,
    MatrixSize,
    Supplemental,
    SurfaceFeature,
    contains_check,
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
MATRIX_SIZE = MatrixSize(3, 3)        # SGMBuilderFrame.java:1028 (the only size).
# The GUI's default cell pixel size (SGMBuilderFrame.java:41). Only scales the
# absolute width/height pixel values; structure and determinism are size-agnostic
# (the bar is data/logic equivalence, not pixels), so a default suffices.
CELL_PIXEL_SIZE = 100
ROTATE_AMOUNT = 45                    # SupplementalGenerator.java:235.
SCALE_AMOUNT = 0.66                   # SupplementalGenerator.java:213.

# Distractor dedup cap (SGMMatrix.java:142): stop after this many consecutive
# duplicate candidates rather than spin forever.
MAX_DUPLICATES_IN_A_ROW = 500
# The scale a "modify scale" distractor sets (SGMMatrix.java:376,410).
DISTRACTOR_SCALE = 0.66

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
    base_constant_shape: bool = False
    """Build the ShapeRepetition base as ONE constant carrier shape (ADR 0002).

    Default ``False`` preserves the faithful 2011-source behaviour (three distinct
    carrier shapes, ``uniqueShapes=true``) on every config-driven and golden-tested
    path. ``parse_code`` sets it ``True`` ONLY for supplemental-led codes (no shape
    relation named), so the built matrix shows one carrier shape with only the
    named supplemental varying -- matching the published norming PNGs. Ignored for
    logic bases (they do not use ShapeRepetition)."""


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
    constant: bool = False,
) -> ShapeRepetition:
    """Port ``createBasicBaseSurfaceFeatures`` (l.266-304): one unique-shape
    feature per base location.

    For each base location, draw a surface feature; if its shape class is already
    used, redraw until a fresh shape appears (``uniqueShapes`` is always ``true``
    on this path, l.281-300). Each base location holds a single-feature list.

    ``constant=True`` overrides this (ADR 0002, a norming-vs-source divergence):
    draw ONE feature and place it (value-equal) at EVERY base location, so the
    ShapeRepetition base is a single constant carrier shape rather than three
    distinct shapes. Only ``parse_code``'s implicit base for supplemental-led codes
    sets this; the unconstrained generator and the golden path keep ``False`` and
    the distinct-shape loop below EXACTLY as-is. See
    ``docs/architecture/decisions/0002-supplemental-led-constant-carrier.md``.
    """
    transform = make_location_transform(direction, size)
    num_base_locations = len(transform.base_locations())
    if constant:
        # ADR 0002: one carrier shape repeated across all base locations. The
        # 2011 source forces three distinct shapes here (uniqueShapes=true); the
        # 2008 norming PNGs for supplemental-led codes show ONE shape, and per
        # CLAUDE.md spec-precedence the paper/norming wins for this path.
        feature = generate_surface_feature(rng, flags, cell_pixel_size)
        constant_features: list[list[SurfaceFeature]] = [
            [feature] for _ in range(num_base_locations)
        ]
        return ShapeRepetition(transform, constant_features)
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
        layer_config.base_direction,
        size,
        cell_pixel_size,
        rng,
        flags,
        constant=layer_config.base_constant_shape,
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


# ---------------------------------------------------------------------------
# Answer + distractor generation (SGMMatrix.java ~242-572)
# ---------------------------------------------------------------------------

def _cell_value_equals(a: Cell, b: Cell) -> bool:
    """Value equality of two cells (port of ``SGMCell.equals``, SGMBaseCell.java:202).

    Equal feature count AND mutual value-containment: every feature of ``b`` is
    value-present in ``a`` AND every feature of ``a`` is value-present in ``b``,
    each via the Phase-2 feature-list ``contains_check`` (the bidirectional check
    at l.215-228). This is the CELL-level helper -- do not confuse it with the
    feature-list ``contains_check``.
    """
    if len(a.surface_features) != len(b.surface_features):
        return False
    a_features: list[SurfaceFeature | None] = list(a.surface_features)
    b_features: list[SurfaceFeature | None] = list(b.surface_features)
    # Bidirectional value-containment (SGMBaseCell.java:215-228): every feature of
    # one cell is value-present in the other, and vice versa.
    every_b_in_a = all(
        contains_check(a_features, feature) for feature in b.surface_features
    )
    every_a_in_b = all(
        contains_check(b_features, feature) for feature in a.surface_features
    )
    return every_b_in_a and every_a_in_b


def _contains_cell(choices: list[Cell | None], candidate: Cell) -> bool:
    """Cell-list membership (port of ``SGMMatrix.containsCheck``, SGMMatrix.java:575).

    True iff some non-``None``/non-blank choice ``_cell_value_equals`` the
    candidate. ``None`` entries are skipped (l.586-589). List-based -- no ``set``.
    """
    for choice in choices:
        if choice is None:
            continue
        if _cell_value_equals(choice, candidate):
            return True
    return False


def _clone_feature(feature: SurfaceFeature) -> SurfaceFeature:
    """A fresh copy for distractor mutation (mirrors ``SGMSurfaceFeature.clone``).

    Copies width/height too (FIX-TO-PAPER ``surface-clone-drops-size-rect-ellipse``),
    matching the supplemental clone, so a mutated distractor stays value-comparable.
    """
    return SurfaceFeature(
        shape=feature.shape,
        fill=feature.fill,
        scale=feature.scale,
        rotation=feature.rotation,
        position=feature.position,
        width=feature.width,
        height=feature.height,
    )


def _layer_uses_numerosity(layer: Layer) -> bool:
    """True if any of the layer's structure features is a numerosity relation."""
    return any(
        isinstance(structure, TranslationalNumerosity)
        for structure in layer.structures
    )


def _distractor_subset_of_layers(
    layers: list[Layer], rng: JavaRandom
) -> list[SurfaceFeature]:
    """Strategy 0: a wrong answer as a subset of the correct answer's layers.

    Port of ``SGMMatrix.java:270-298`` + ``generateRandomLayerSubSet``
    (l.598-627). Only meaningful with >=2 layers (the caller excludes case 0 for
    single-layer matrices). Returns the concatenated bottom-right features of the
    chosen layer subset.
    """
    num_layers = len(layers)
    layers_not_yet_used = list(range(num_layers))
    # generateRandomLayerSubSet: numLayersToCombine = next_int(numLayers-1)+1.
    num_to_combine = num_layers
    if num_layers > 1:
        num_to_combine = rng.next_int(num_layers - 1) + 1
    subset: list[int] = []
    for _ in range(num_to_combine):
        index_to_use = rng.next_int(len(layers_not_yet_used))
        subset.append(layers_not_yet_used.pop(index_to_use))

    features: list[SurfaceFeature] = []
    for layer_index in subset:
        features.extend(layers[layer_index].cells[-1][-1].surface_features)
    return features


def _distractor_wrong_cell(
    cells: list[list[Cell]], size: MatrixSize, rng: JavaRandom
) -> list[SurfaceFeature]:
    """Strategy 1: a wrong answer = any matrix cell other than ``(2,2)``.

    Port of ``SGMMatrix.java:299-316``: redraw row/column until it is not the
    bottom-right correct-answer cell.
    """
    correct_row = size.num_rows - 1
    correct_column = size.num_columns - 1
    row, column = correct_row, correct_column
    while row == correct_row and column == correct_column:
        row = rng.next_int(size.num_rows)
        column = rng.next_int(size.num_columns)
    return list(cells[row][column].surface_features)


def _distractor_modify_parameter(
    layers: list[Layer], size: MatrixSize, rng: JavaRandom
) -> list[SurfaceFeature]:
    """Strategy 2: change one parameter of a random cell's feature(s).

    Port of ``SGMMatrix.java:317-419``. Pick a layer; pick a cell; if it has
    features, clone them and modify either the fill (a fresh ``generate_fill``
    draw) or the scale (->0.66). On a numerosity layer EVERY feature is changed
    the same way; otherwise a single random feature is changed. The order of RNG
    draws (layerID, row, column, parameter, [featureIndex], [fill]) is faithful.
    Returns ``[]`` if the chosen cell has no features (an empty candidate the
    caller skips).
    """
    layer_id = rng.next_int(len(layers))
    layer = layers[layer_id]
    numerosity_layer = _layer_uses_numerosity(layer)

    row = rng.next_int(size.num_rows)
    column = rng.next_int(size.num_columns)
    source = layer.cells[row][column].surface_features
    if len(source) == 0:
        # Faithful to the Java early exit (SGMMatrix.java:344): the parameter
        # draw below is not reached, so the RNG stream stays aligned.
        return []

    features = list(source)
    parameter_to_change = rng.next_int(2)
    if numerosity_layer:
        # Change all features the same way (l.357-386).
        if parameter_to_change == 0:
            fill = generate_fill(rng)
            for i in range(len(features)):
                clone = _clone_feature(features[i])
                clone.fill = fill
                features[i] = clone
        else:
            for i in range(len(features)):
                clone = _clone_feature(features[i])
                clone.scale = DISTRACTOR_SCALE
                features[i] = clone
    else:
        # Change one random feature (l.387-414).
        feature_index = rng.next_int(len(features))
        clone = _clone_feature(features[feature_index])
        features[feature_index] = clone
        if parameter_to_change == 0:
            clone.fill = generate_fill(rng)
        else:
            clone.scale = DISTRACTOR_SCALE
    return features


def _distractor_random_layer_combination(
    layers: list[Layer], size: MatrixSize, rng: JavaRandom
) -> list[SurfaceFeature]:
    """Strategy 3: a combination of random layers from across the matrix.

    Port of ``SGMMatrix.java:420-479``: choose ``numLayers`` (1..#layers), pick
    that many distinct layers, and from each, a random cell -- keeping each of its
    features with probability 1/2 (``next_boolean``). Returns the kept features
    (possibly empty, which the caller skips).
    """
    matrix_num_layers = len(layers)
    num_layers = 1
    if matrix_num_layers > num_layers:
        num_layers = rng.next_int(matrix_num_layers) + 1
    # When num_layers == matrix_num_layers this can reproduce strategy 0's
    # all-layers candidate; that overlap is faithful to upstream (SGMMatrix.java
    # :420-479), not a port deviation (bug-catalog
    # ``gen-strategy3-subsumes-strategy0-at-maxlayers``). Cell-level dedup drops
    # any exact duplicate, so it only reduces distractor variety.

    chosen: list[int] = []
    while len(chosen) < num_layers:
        potential = rng.next_int(matrix_num_layers)
        if potential not in chosen:
            chosen.append(potential)

    features: list[SurfaceFeature] = []
    for layer_index in chosen:
        row = rng.next_int(size.num_rows)
        column = rng.next_int(size.num_columns)
        for feature in layers[layer_index].cells[row][column].surface_features:
            if rng.next_boolean():
                features.append(feature)
    return features


def _relocate_correct_answer(
    answer_choices: list[Cell | None],
    correct_position_0: int,
    position: int,
    correct_answer: Cell,
    rng: JavaRandom,
    flags: CompatFlags,
) -> tuple[int, int]:
    """Flag-gated correct-answer relocation (SGMMatrix.java:531-552).

    ``relocate_correct_answer=False`` (default) skips the whole block -- including
    its conditional ``next_int`` draw (l.538) -- honouring the configured
    position; the honor-config path is deliberately a different RNG stream for
    relocating configs (DR §3). Returns the (possibly updated) ``(correct_position_0,
    position)`` and mutates ``answer_choices`` in place.
    """
    if not (flags.relocate_correct_answer and correct_position_0 > position):
        return correct_position_0, position
    new_position = 0
    if position > 0:
        new_position = rng.next_int(position)
    # Move whatever sits at new_position to the end of the contiguous block.
    answer_choices[position] = answer_choices[new_position]
    answer_choices[new_position] = correct_answer
    return new_position, position + 1


def _blank_pad(
    answer_choices: list[Cell | None],
    correct_position_0: int,
    position: int,
    num_answer_choices: int,
) -> None:
    """Fill remaining slots with blank cells (SGMMatrix.java:556-572).

    Upstream does not re-skip the correct position inside the loop because
    relocation (faithful-to-code path) guarantees ``correct_position_0 <=
    position`` there. In the default honor-config path relocation is skipped, so a
    high configured position may still sit AHEAD of ``position``; skip it each step
    to protect it -- the deliberate consequence of honouring the configured
    position (DR §3). Adds no RNG draw, so internal determinism is unaffected.
    """
    # Don't overwrite the correct answer if position lands on it (l.556-559).
    if position == correct_position_0:
        position += 1
    while position < num_answer_choices:
        if position == correct_position_0:
            position += 1
            continue
        answer_choices[position] = Cell(surface_features=[], location=None)
        position += 1


def generate_answer_choices(
    cells: list[list[Cell]],
    layers: list[Layer],
    correct_answer_position: int,
    size: MatrixSize,
    rng: JavaRandom,
    flags: CompatFlags,
) -> tuple[list[Cell], int]:
    """Generate the 8 answer choices and the correct answer's 1-based position.

    Port of ``SGMMatrix.java:230-572``. The correct answer is the composited
    bottom-right cell ``(2,2)``; up to seven distractors come from the four
    strategies (``next_int(4)`` for >=2 layers, ``next_int(3)+1`` for one layer);
    dedup is CELL-level by value with a ``MAX_DUPLICATES_IN_A_ROW`` cap; remaining
    slots are blank cells.

    Positions are 1-based at the boundary (the config's
    ``correct_answer_position`` is 1-8); internally the upstream's 0-based
    arithmetic is reproduced, then converted back on return.

    ``flags.relocate_correct_answer`` (default ``False``) selects the position
    behaviour. ``False`` (faithful-to-design) honours the configured position and
    SKIPS the upstream relocation block (l.531-548) ENTIRELY -- including its
    conditional ``next_int`` draw (l.538). ``True`` (faithful-to-code) replicates
    the relocation, consuming that draw. The default path is deliberately a
    different RNG stream for relocating configs (DR §3); no compensating draw.
    """
    num_answer_choices = NUM_ANSWER_CHOICES
    correct_position_0 = correct_answer_position - 1  # 1-based -> 0-based.
    correct_answer = cells[size.num_rows - 1][size.num_columns - 1]

    answer_choices: list[Cell | None] = [None] * num_answer_choices
    position = 0
    if position == correct_position_0:
        position += 1
    answer_choices[correct_position_0] = correct_answer

    num_fruitless_in_a_row = 0
    while position < num_answer_choices and (
        num_fruitless_in_a_row < MAX_DUPLICATES_IN_A_ROW
    ):
        # >=2 layers: any of the 4 strategies; 1 layer: exclude case 0 (the
        # layer-subset strategy is meaningless), so next_int(3)+1 -> 1..3.
        strategy = rng.next_int(4) if len(layers) > 1 else rng.next_int(3) + 1

        match strategy:
            case 0:
                features = _distractor_subset_of_layers(layers, rng)
            case 1:
                features = _distractor_wrong_cell(cells, size, rng)
            case 2:
                features = _distractor_modify_parameter(layers, size, rng)
            case _:
                features = _distractor_random_layer_combination(layers, size, rng)

        if len(features) == 0:
            # Empty/null candidate (l.483-487). Upstream skips WITHOUT counting,
            # so a fully-impoverished matrix spins forever. Per bug-catalog
            # ``gen-unbounded-generation-loop`` (flag-and-decide -> add a
            # hang-prevention bound), count it toward the give-up cap. A matrix
            # with any content resets the count on the next success, so realistic
            # generation is unaffected; a degenerate matrix falls through to
            # blank-pad instead of hanging.
            num_fruitless_in_a_row += 1
            continue

        candidate = Cell(surface_features=features, location=None)
        if not _cell_value_equals(candidate, correct_answer) and not _contains_cell(
            answer_choices, candidate
        ):
            answer_choices[position] = candidate
            position += 1
            if position == correct_position_0:
                position += 1
            num_fruitless_in_a_row = 0
        else:
            num_fruitless_in_a_row += 1

    correct_position_0, position = _relocate_correct_answer(
        answer_choices, correct_position_0, position, correct_answer, rng, flags
    )
    _blank_pad(answer_choices, correct_position_0, position, num_answer_choices)

    finalised = [_require_cell(choice) for choice in answer_choices]
    return finalised, correct_position_0 + 1  # 0-based -> 1-based.


# ---------------------------------------------------------------------------
# build() — the end-to-end entry point
# ---------------------------------------------------------------------------

def build(
    config: BuilderConfig,
    seed: int,
    flags: CompatFlags = DEFAULT_FLAGS,
) -> Matrix:
    """Build a complete 3x3 matrix with 8 answer choices from a config + seed.

    The single pure entry point. Validates the config, then uses ONE
    ``JavaRandom(seed)`` to drive every stochastic draw in order: each layer's
    surfaces/structure (``build_layer``), then the distractor mutation
    (``generate_answer_choices``). The upstream's config-level draws (numLayers,
    correctAnswerPosition, relation/direction choice) are replaced by ``config``
    (DR1), so the first draw is the first layer's first base surface feature --
    which is why two seeds yield the same relations but different surfaces
    (AC4.3).

    Determinism (AC4.1) follows from the deterministic ``JavaRandom`` and the
    absence of any other entropy. ``flags.relocate_correct_answer`` (default
    ``False``) honours ``config.correct_answer_position`` and skips the upstream
    relocation draw; ``line_shape_enabled`` (default ``False``) keeps Line out of
    the shape draw.

    Parameters
    ----------
    config : BuilderConfig
        The validated option surface: 1-2 layers + a 1-based correct position.
    seed : int
        The ``java.util.Random`` seed; the sole source of stochasticity.
    flags : CompatFlags, optional
        Compat toggles; defaults to faithful-to-code / faithful-to-design mix.

    Returns
    -------
    Matrix
        The 3x3 grid, the 8 answer choices, the (possibly relocated) 1-based
        correct-answer position, and the per-layer structures.
    """
    validate_config(config)
    rng = JavaRandom(seed)

    layers = [
        build_layer(layer_config, MATRIX_SIZE, CELL_PIXEL_SIZE, rng, flags)
        for layer_config in config.layers
    ]
    cells = compose_layers(layers, MATRIX_SIZE)
    answer_choices, correct_position = generate_answer_choices(
        cells,
        layers,
        config.correct_answer_position,
        MATRIX_SIZE,
        rng,
        flags,
    )
    return Matrix(
        cells=cells,
        answer_choices=answer_choices,
        correct_answer_position=correct_position,
        layers=layers,
    )


def build_from_code(
    code: str,
    seed: int,
    flags: CompatFlags = DEFAULT_FLAGS,
) -> Matrix:
    """Build a matrix from a Matzen ``Structure`` code: ``parse_code`` + ``build``.

    A thin convenience over ``parse_code(code)`` then ``build(config, seed, flags)``.
    The ``Structure`` code does not encode the correct-answer position, so
    ``parse_code`` defaults it to 1; the structural oracle (Phase 5) checks
    relations and directions, not position. A malformed code raises ``ValueError``
    from ``parse_code`` (AC2.4).

    ``parse_code`` is imported at call time to keep the module import acyclic
    (``label`` imports this module's config dataclasses; importing ``parse_code``
    at the top of ``builder`` would close the cycle).
    """
    from raven_matrix.label import parse_code

    config = parse_code(code)
    return build(config, seed, flags)
