"""Surface-feature generation, ported from SGMSurfaceFeatureGenerator.java.

Faithful port of ``SGMSurfaceFeatureGenerator.generateSurfaceFeature``
(``reference/sgmt-source/Source/.../surface/SGMSurfaceFeatureGenerator.java``,
lines 134-202). The seeded draw order is load-bearing for oracle fidelity, so it
is preserved exactly:

1. ``width = next_int(3) * quarter + quarter``  (l.134-135) -> 1/4, 1/2, 3/4 cell.
2. ``height``: conditional (l.136-143).
   - width == 1/2 cell -> height = 3/4 cell, NO draw (l.137-138).
   - width == 3/4 cell -> height = 1/2 cell, NO draw (l.139-140).
   - else (width == 1/4 cell, the smallest) -> ``next_int(2) * quarter + half``
     (l.141-143). This draw fires ONLY for the smallest width.
3. ``swap = next_boolean()`` (l.144) -> exchange width/height when true. ALWAYS
   drawn. Net pre-fill draws are therefore 2 (no height draw) or 3 (height draw).
4. rotation = 0 (l.152), position = cell centre (half, half) (l.155-156). No draw.
5. ``fill = generate_fill(rng)`` (l.158-161) -> a single ``next_int(3)``.
6. ``shape = next_int(6)`` (l.164), widened to ``next_int(7)`` when Line is
   enabled.

Shape index -> class, read from the LIVE switch (l.165-202):
  case 0 -> Ellipse    (l.167-171)
  case 1 -> Rectangle  (l.172-176)
  case 2 -> Triangle   (l.177-181)
  case 3 -> Tee        (l.182-186)
  case 4 -> Diamond    (l.187-191)
  case 5 -> Trapezoid  (l.192-196)
The commented-out block at l.197-201 is a STALE ``case 4`` for Line that the
live switch already binds to Diamond; it does NOT define the index order. Line
is re-enabled only under ``line_shape_enabled`` as a NEW index 6 (the next free
slot), with the shape draw widened to ``next_int(7)``.

scale is birthed at 1.0 (the Java shape constructors pass ``super(1.0, ...)``,
e.g. RectangleSGMSurfaceFeature.java:103); width/height carry the absolute pixel
dimensions. For a Line, only a single length is meaningful; we store it in
``width`` (matching the model's length-in-width convention) and set height to 0.0.
"""

from __future__ import annotations

from raven_matrix.compat import CompatFlags
from raven_matrix.fillpattern import generate_fill
from raven_matrix.model import Fill, Point, Shape, SurfaceFeature
from raven_matrix.rng import JavaRandom

# Live-switch index -> Shape (SGMSurfaceFeatureGenerator.java:165-202). Index 6
# (Line) is only reachable when line_shape_enabled widens the draw to next_int(7).
_SHAPE_BY_INDEX: tuple[Shape, ...] = (
    Shape.ELLIPSE,  # case 0, l.167-171
    Shape.RECTANGLE,  # case 1, l.172-176
    Shape.TRIANGLE,  # case 2, l.177-181
    Shape.TEE,  # case 3, l.182-186
    Shape.DIAMOND,  # case 4, l.187-191 (live case 4; NOT the commented Line)
    Shape.TRAPEZOID,  # case 5, l.192-196
    Shape.LINE,  # index 6: re-enabled Line (line_shape_enabled only)
)


def generate_surface_feature(
    rng: JavaRandom,
    flags: CompatFlags,
    cell_pixel_size: int,
    allowed_fills: list[Fill] | None = None,
) -> SurfaceFeature:
    """Draw one surface feature, mirroring ``generateSurfaceFeature``.

    Ports ``SGMSurfaceFeatureGenerator.java:134-202`` exactly, including the
    variable pre-fill draw count (2 or 3). See the module docstring for the
    per-line draw map.

    Parameters
    ----------
    rng : JavaRandom
        The shared generator stream; advanced by 2-or-3 pre-fill draws, then one
        fill draw, then one shape draw.
    flags : CompatFlags
        ``line_shape_enabled`` widens the shape draw to ``next_int(7)`` and lets
        Line (index 6) appear; the default (``False``) keeps ``next_int(6)``.
    cell_pixel_size : int
        The cell's pixel size; width/height are quarter/half/three-quarter of it.
    allowed_fills : list[Fill] | None, optional
        Mirrors the upstream ``allowedFillPatterns`` overload
        (``SGMSurfaceFeatureGenerator.java:115-118`` ->
        ``SGMFillPatternGenerator.generateFillPattern(list, random)``,
        ``:88-100``). ``None`` (the default) reproduces the no-list overload: a
        single ``next_int(3)`` over the base catalogue ``[White, Grey75, Black]``
        (the geometric/ShapeRepetition path). A non-``None`` list draws
        ``next_int(len)`` over it instead -- the logic base pool passes
        ``[White]`` (``BaseSGMStructureFeatureGenerator.java:200-214``), so the
        fill draw is ``next_int(1)`` (always White), NOT ``next_int(3)``. This is
        a genuine RNG-stream divergence between the two paths, faithful to the
        upstream's two distinct fill-generator overloads.

    Returns
    -------
    SurfaceFeature
        scale 1.0, rotation 0, position the cell centre, with the drawn
        width/height/fill/shape.
    """
    half = cell_pixel_size / 2.0
    quarter = half / 2.0

    # 1. width: 1/4, 1/2, or 3/4 cell (l.134-135).
    width = (float(rng.next_int(3)) * quarter) + quarter

    # 2. height: conditional, with one dimension forced > 1/2 cell (l.136-143).
    if width == 2 * quarter:
        height = 3 * quarter  # width == 1/2 -> height 3/4, no draw (l.137-138)
    elif width == 3 * quarter:
        height = 2 * quarter  # width == 3/4 -> height 1/2, no draw (l.139-140)
    else:
        # width == 1/4 (smallest): the only branch that draws (l.141-143).
        height = (float(rng.next_int(2)) * quarter) + half

    # 3. swap width/height (always drawn) (l.144-149).
    if rng.next_boolean():
        width, height = height, width

    # 4. fixed rotation and centre position (l.152-156); no draws.
    rotation = 0
    position = Point(half, half)

    # 5. fill (l.158-161): no list -> generate_fill's next_int(3) over the base
    # catalogue; a list -> next_int(len) over the list (SGMFillPatternGenerator
    # .generateFillPattern(list, random), :98-99). The logic pool passes [White].
    if allowed_fills is None:
        fill = generate_fill(rng)
    else:
        fill = allowed_fills[rng.next_int(len(allowed_fills))]

    # 6. shape: next_int(6), widened to next_int(7) under line_shape_enabled (l.164).
    bound = 7 if flags.line_shape_enabled else 6
    shape = _SHAPE_BY_INDEX[rng.next_int(bound)]

    # Line carries a single length (stored in width); height is unused for it.
    feature_height = 0.0 if shape is Shape.LINE else height
    return SurfaceFeature(
        shape=shape,
        fill=fill,
        scale=1.0,
        rotation=rotation,
        position=position,
        width=width,
        height=feature_height,
    )
