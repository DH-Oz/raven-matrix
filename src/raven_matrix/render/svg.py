"""Hand-emitted SVG rendering of Raven-matrix cells (Phase 6, Tasks 1-2).

SVG is the canonical render format (rasterise down to PNG only when a bitmap is
needed — see ``render.raster``).  The bar is **data/logic equivalence, not pixel
reproduction**: this module reproduces the upstream Java2D *geometry and paint
semantics* faithfully, but correctness is judged on SVG well-formedness and
attributes, never on pixel parity.

Geometry is ported verbatim from the SGMT surface sources
(``reference/sgmt-source/Source/gov/sandia/cognition/generator/matrix/surface``):

- ``DiamondSGMSurfaceFeature.makePath`` — 4-vertex pinched diamond
  (``quarterHeight = height/4``);
- ``EllipseSGMSurfaceFeature`` — ``Ellipse2D`` centred on position;
- ``RectangleSGMSurfaceFeature`` — ``Rectangle2D`` centred on position;
- ``LineSGMSurfaceFeature.createLine`` — horizontal line centred on position
  (rotation handled by the transform);
- ``TeeSGMSurfaceFeature.makePath`` — 8-vertex tee (``quarterWidth = width/4``,
  ``quarterHeight = height/4``);
- ``TrapezoidSGMSurfaceFeature.makePath`` — 4-vertex trapezoid
  (``quarterWidth = halfWidth/2``);
- ``TriangleSGMSurfaceFeature.makePath`` — 3-vertex triangle.

The Phase-2 ``SurfaceFeature`` carries no width/height: in Java those derive
from ``sgmCellImagePixelSize`` at generation time (``SGMSurfaceFeatureGenerator``
picks 1/4..3/4 of the cell size).  The renderer pins a fixed base size of
``cell_pixel_size / 2`` (the midpoint of that range); ``feature.scale``
multiplies it through the affine transform, exactly as Java applies scale inside
the transform (``SGMCellImage.setSGMCell``) rather than baking it into the path.

Transform order matches ``SGMCellImage.setSGMCell``:
``translate(pos) -> rotate -> scale -> translate(-pos)``.  Java rotation is in
degrees; the Python model stores radians, so ``deg = degrees(feature.rotation)``.

Paint order matches ``SGMCellImage``: fill (with the fill's RGBA alpha) THEN a
2px black stroke.  White has alpha 0, so it renders as a transparent fill with a
black outline only.

Layout (Tasks 2) matches ``SGMMatrixImage`` / ``SGMAnswerChoicesImage``:
``side = (cell + gap) * count + gap``; cells at
``(gap + col*(cell+gap), gap + row*(cell+gap))``.  The matrix is a 3x3 grid on a
white background with a hard-coded blank-white bottom-right cell (problem mode,
``render-answer-cell-hardcoded-bottom-right``).  The answer sheet is a 2x4 grid
of the 8 answer choices on a black background.

Import-hygiene contract: this module must not import ``resvg_py`` (that import
lives only inside ``render.raster.rasterise``), so the zero-dependency core
import path stays free of the optional ``raster`` extra.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import degrees

from raven_matrix.model import Cell, Fill, Shape, SurfaceFeature

# ---------------------------------------------------------------------------
# Raster / layout sizing
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class RasterSettings:
    """Cell size and inter-cell spacing for rendering.

    Upstream SGMT carries no hardcoded defaults (``RasterSettings`` is always
    constructed explicitly); the port supplies sensible defaults so callers can
    render without ceremony.
    """

    cell_pixel_size: int = 256
    pixels_between_cells: int = 10


DEFAULT_RASTER = RasterSettings()


def _base_size(settings: RasterSettings) -> float:
    """Base shape side length: the midpoint of the Java 1/4..3/4 cell range."""
    return settings.cell_pixel_size / 2.0


# ---------------------------------------------------------------------------
# Fill + stroke attributes
# ---------------------------------------------------------------------------

def _fmt(value: float) -> str:
    """Format a float for an SVG attribute, trimming a trailing ``.0``-only int.

    Coordinates and opacities are emitted with their natural float repr so the
    tests can compare numerically; integers-as-floats stay readable.
    """
    return repr(value)


def _fill_attrs(fill: Fill) -> str:
    """``fill="rgb(R,G,B)" fill-opacity="A"`` for a fill enum value.

    Each RGB channel is ``round(channel * 255)``; ``fill-opacity`` is the alpha.
    White has alpha 0.0, so this yields ``fill-opacity="0"`` (transparent fill,
    outline only).
    """
    rgba = fill.value
    r = round(rgba.r * 255)
    g = round(rgba.g * 255)
    b = round(rgba.b * 255)
    opacity = rgba.a
    opacity_str = "0" if opacity == 0.0 else _fmt(opacity)
    return f'fill="rgb({r},{g},{b})" fill-opacity="{opacity_str}"'


_STROKE_ATTRS = 'stroke="black" stroke-width="2"'


# ---------------------------------------------------------------------------
# Per-shape geometry emitters (coordinates relative to feature.position)
# ---------------------------------------------------------------------------

def _path_d(points: list[tuple[float, float]]) -> str:
    """An absolute closed-path ``d`` string from a vertex list."""
    head = f"M {_fmt(points[0][0])} {_fmt(points[0][1])}"
    rest = " ".join(f"L {_fmt(x)} {_fmt(y)}" for x, y in points[1:])
    return f"{head} {rest} Z"


def _shape_body(shape: Shape, px: float, py: float, base: float) -> str:
    """The bare SVG element (tag + geometry) for one shape, centred on (px, py).

    ``base`` is the base side length; half-width and half-height are both
    ``base / 2`` (the upstream generator may pick non-square w/h, but the model
    carries no dimensions, so the port renders a square base modulated by scale).
    """
    hw = base / 2.0
    hh = base / 2.0

    match shape:
        case Shape.ELLIPSE:
            return (
                f'<ellipse cx="{_fmt(px)}" cy="{_fmt(py)}" '
                f'rx="{_fmt(hw)}" ry="{_fmt(hh)}"'
            )
        case Shape.RECTANGLE:
            return (
                f'<rect x="{_fmt(px - hw)}" y="{_fmt(py - hh)}" '
                f'width="{_fmt(2 * hw)}" height="{_fmt(2 * hh)}"'
            )
        case Shape.LINE:
            return (
                f'<line x1="{_fmt(px - hw)}" y1="{_fmt(py)}" '
                f'x2="{_fmt(px + hw)}" y2="{_fmt(py)}"'
            )
        case Shape.DIAMOND:
            qh = hh / 2.0
            d = _path_d([
                (px - hw, py - qh),
                (px, py + hh),
                (px + hw, py - qh),
                (px, py - hh),
            ])
            return f'<path d="{d}"'
        case Shape.TRIANGLE:
            d = _path_d([
                (px - hw, py + hh),
                (px + hw, py + hh),
                (px, py - hh),
            ])
            return f'<path d="{d}"'
        case Shape.TRAPEZOID:
            qw = hw / 2.0
            d = _path_d([
                (px - hw, py + hh),
                (px + hw, py + hh),
                (px + qw, py - hh),
                (px - qw, py - hh),
            ])
            return f'<path d="{d}"'
        case Shape.TEE:
            w = 2 * hw
            h = 2 * hh
            qw = w / 4.0
            qh = h / 4.0
            d = _path_d([
                (px - hw, py - hh),
                (px + hw, py - hh),
                (px + hw, py - qh),
                (px + qw, py - qh),
                (px + qw, py + hh),
                (px - qw, py + hh),
                (px - qw, py - qh),
                (px - hw, py - qh),
            ])
            return f'<path d="{d}"'


def _feature_transform(feature: SurfaceFeature) -> str:
    """Affine transform string, mirroring ``SGMCellImage.setSGMCell`` order."""
    px = feature.position.x
    py = feature.position.y
    deg = degrees(feature.rotation)
    return (
        f"translate({_fmt(px)} {_fmt(py)}) "
        f"rotate({_fmt(deg)}) "
        f"scale({_fmt(feature.scale)}) "
        f"translate({_fmt(-px)} {_fmt(-py)})"
    )


def render_feature_svg(feature: SurfaceFeature, settings: RasterSettings) -> str:
    """SVG element for one surface feature: geometry + fill + stroke + transform."""
    px = feature.position.x
    py = feature.position.y
    base = _base_size(settings)
    body = _shape_body(feature.shape, px, py, base)
    return (
        f"{body} {_fill_attrs(feature.fill)} {_STROKE_ATTRS} "
        f'transform="{_feature_transform(feature)}"/>'
    )


# ---------------------------------------------------------------------------
# Cell rendering
# ---------------------------------------------------------------------------

def render_cell_svg(cell: Cell, settings: RasterSettings = DEFAULT_RASTER) -> str:
    """A ``<g>`` holding one SVG element per surface feature.

    A featureless cell yields an empty ``<g></g>`` (AC5.3).
    """
    elements = "".join(
        render_feature_svg(feature, settings) for feature in cell.surface_features
    )
    return f"<g>{elements}</g>"
