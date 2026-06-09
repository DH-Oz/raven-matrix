"""Tests for render/svg.py — per-shape, per-fill, per-cell SVG (Phase 6 Task 1).

The acceptance bar is SVG well-formedness + semantics, never pixel parity with
the upstream Java2D.  Every test parses the emitted SVG with
``xml.etree.ElementTree`` and asserts tags / coordinates / attributes:

- AC5.1: each of the 7 shapes emits its expected element with the pinned base
  geometry (extracted verbatim from the SGMT surface/*.java makePath/createX
  sources); each of the 5 fills maps to the right ``fill`` + ``fill-opacity``
  (White -> ``fill-opacity="0"``); every shape carries ``stroke-width="2"``.
- AC5.3: a featureless cell renders as a valid, empty ``<g>`` (no error).

Geometry note: the Phase-2 ``SurfaceFeature`` carries no width/height (the Java
model derives them from ``sgmCellImagePixelSize`` at render time).  The renderer
pins a fixed base size of ``settings.cell_pixel_size / 2`` (the midpoint of the
Java 1/4..3/4 range); ``feature.scale`` multiplies it via the affine transform,
exactly as Java applies scale in the transform rather than baking it into the
path (SGMCellImage.setSGMCell).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from math import isclose

from raven_matrix.model import Fill, Point, Shape, SurfaceFeature

SVG_NS = "http://www.w3.org/2000/svg"


def _qn(tag: str) -> str:
    """Qualify a bare tag name with the SVG namespace as ElementTree reports it."""
    return f"{{{SVG_NS}}}{tag}"


_DEFAULT_POS = Point(100.0, 100.0)


def _feature(shape: Shape, *, fill: Fill = Fill.BLACK,
             scale: float = 1.0, rotation: float = 0.0,
             position: Point = _DEFAULT_POS) -> SurfaceFeature:
    return SurfaceFeature(
        shape=shape, fill=fill, scale=scale, rotation=rotation, position=position
    )


def _render_one(feature: SurfaceFeature):
    """Render a single-feature cell and return the parsed shape element.

    Wrap the cell SVG (a ``<g>``) in a root ``<svg>`` so ElementTree has a single
    document element to parse, then return the first child of the group.
    """
    from raven_matrix.model import Cell, Location
    from raven_matrix.render.svg import DEFAULT_RASTER, render_cell_svg

    cell = Cell(surface_features=[feature], location=Location(0, 0))
    group_svg = render_cell_svg(cell, DEFAULT_RASTER)
    doc = f'<svg xmlns="{SVG_NS}">{group_svg}</svg>'
    root = ET.fromstring(doc)
    group = root.find(_qn("g"))
    assert group is not None
    children = list(group)
    assert len(children) == 1
    return children[0]


# ---------------------------------------------------------------------------
# RasterSettings
# ---------------------------------------------------------------------------

def test_default_raster_has_documented_sizing() -> None:
    from raven_matrix.render.svg import DEFAULT_RASTER, RasterSettings

    assert isinstance(DEFAULT_RASTER, RasterSettings)
    assert DEFAULT_RASTER.cell_pixel_size == 256
    assert DEFAULT_RASTER.pixels_between_cells == 10


# ---------------------------------------------------------------------------
# Per-shape geometry (base size = cell_pixel_size / 2 = 128; hw = hh = 64)
# position fixed at (100, 100) -> px=100, py=100
# ---------------------------------------------------------------------------

# With DEFAULT_RASTER cell_pixel_size=256: base = 128, hw = hh = 64.
_HW = 64.0
_HH = 64.0


def test_ellipse_emits_ellipse_with_pinned_geometry() -> None:
    el = _render_one(_feature(Shape.ELLIPSE))
    assert el.tag == _qn("ellipse")
    assert isclose(float(el.get("cx")), 100.0)
    assert isclose(float(el.get("cy")), 100.0)
    assert isclose(float(el.get("rx")), _HW)
    assert isclose(float(el.get("ry")), _HH)


def test_rectangle_emits_rect_with_pinned_geometry() -> None:
    el = _render_one(_feature(Shape.RECTANGLE))
    assert el.tag == _qn("rect")
    assert isclose(float(el.get("x")), 100.0 - _HW)
    assert isclose(float(el.get("y")), 100.0 - _HH)
    assert isclose(float(el.get("width")), 2 * _HW)
    assert isclose(float(el.get("height")), 2 * _HH)


def test_line_emits_horizontal_line_centred_on_position() -> None:
    el = _render_one(_feature(Shape.LINE))
    assert el.tag == _qn("line")
    assert isclose(float(el.get("x1")), 100.0 - _HW)
    assert isclose(float(el.get("y1")), 100.0)
    assert isclose(float(el.get("x2")), 100.0 + _HW)
    assert isclose(float(el.get("y2")), 100.0)


def _path_points(d: str) -> list[tuple[float, float]]:
    """Parse an absolute M/L/Z path of float pairs into a point list."""
    points: list[tuple[float, float]] = []
    tokens = d.replace(",", " ").split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("M", "L"):
            x = float(tokens[i + 1])
            y = float(tokens[i + 2])
            points.append((x, y))
            i += 3
        elif tok == "Z":
            i += 1
        else:  # bare coordinate pair continuing a command
            i += 1
    return points


def test_diamond_emits_path_with_pinned_vertices() -> None:
    el = _render_one(_feature(Shape.DIAMOND))
    assert el.tag == _qn("path")
    pts = _path_points(el.get("d"))
    qh = _HH / 2.0
    assert pts == [
        (100.0 - _HW, 100.0 - qh),
        (100.0, 100.0 + _HH),
        (100.0 + _HW, 100.0 - qh),
        (100.0, 100.0 - _HH),
    ]


def test_triangle_emits_path_with_pinned_vertices() -> None:
    el = _render_one(_feature(Shape.TRIANGLE))
    assert el.tag == _qn("path")
    pts = _path_points(el.get("d"))
    assert pts == [
        (100.0 - _HW, 100.0 + _HH),
        (100.0 + _HW, 100.0 + _HH),
        (100.0, 100.0 - _HH),
    ]


def test_trapezoid_emits_path_with_pinned_vertices() -> None:
    el = _render_one(_feature(Shape.TRAPEZOID))
    assert el.tag == _qn("path")
    pts = _path_points(el.get("d"))
    qw = _HW / 2.0
    assert pts == [
        (100.0 - _HW, 100.0 + _HH),
        (100.0 + _HW, 100.0 + _HH),
        (100.0 + qw, 100.0 - _HH),
        (100.0 - qw, 100.0 - _HH),
    ]


def test_tee_emits_path_with_pinned_vertices() -> None:
    el = _render_one(_feature(Shape.TEE))
    assert el.tag == _qn("path")
    pts = _path_points(el.get("d"))
    # Java TeeSGMSurfaceFeature.makePath: quarterWidth=width/4, quarterHeight=height/4
    w = 2 * _HW
    h = 2 * _HH
    qw = w / 4.0
    qh = h / 4.0
    assert pts == [
        (100.0 - _HW, 100.0 - _HH),
        (100.0 + _HW, 100.0 - _HH),
        (100.0 + _HW, 100.0 - qh),
        (100.0 + qw, 100.0 - qh),
        (100.0 + qw, 100.0 + _HH),
        (100.0 - qw, 100.0 + _HH),
        (100.0 - qw, 100.0 - qh),
        (100.0 - _HW, 100.0 - qh),
    ]


def test_all_seven_shapes_render_without_error() -> None:
    for shape in Shape:
        el = _render_one(_feature(shape))
        assert el.tag in {_qn("ellipse"), _qn("rect"), _qn("line"), _qn("path")}


# ---------------------------------------------------------------------------
# Fill mapping (fill + fill-opacity) and stroke
# ---------------------------------------------------------------------------

def test_black_fill_maps_to_rgb_and_alpha() -> None:
    el = _render_one(_feature(Shape.RECTANGLE, fill=Fill.BLACK))
    assert el.get("fill") == "rgb(0,0,0)"
    assert isclose(float(el.get("fill-opacity")), 0.75)


def test_white_fill_is_transparent_outline_only() -> None:
    el = _render_one(_feature(Shape.RECTANGLE, fill=Fill.WHITE))
    assert el.get("fill") == "rgb(255,255,255)"
    assert el.get("fill-opacity") == "0"


def test_grey10_fill_maps_to_rgb_and_alpha() -> None:
    el = _render_one(_feature(Shape.RECTANGLE, fill=Fill.GREY10))
    # 0.1 * 255 = 25.5 -> round() -> 26 (banker's rounding: round(25.5)=26)
    assert el.get("fill") == "rgb(26,26,26)"
    assert isclose(float(el.get("fill-opacity")), 0.6)


def test_grey40_fill_maps_to_rgb_and_alpha() -> None:
    el = _render_one(_feature(Shape.RECTANGLE, fill=Fill.GREY40))
    assert el.get("fill") == "rgb(102,102,102)"
    assert isclose(float(el.get("fill-opacity")), 0.5)


def test_grey75_fill_maps_to_rgb_and_alpha() -> None:
    el = _render_one(_feature(Shape.RECTANGLE, fill=Fill.GREY75))
    assert el.get("fill") == "rgb(191,191,191)"
    assert isclose(float(el.get("fill-opacity")), 0.4)


def test_every_fill_yields_two_pixel_black_stroke() -> None:
    for fill in Fill:
        el = _render_one(_feature(Shape.ELLIPSE, fill=fill))
        assert el.get("stroke") == "black"
        assert el.get("stroke-width") == "2"


# ---------------------------------------------------------------------------
# Transform (translate(pos) rotate(deg) scale(s) translate(-pos))
# ---------------------------------------------------------------------------

def test_zero_rotation_unit_scale_transform_is_identity_form() -> None:
    el = _render_one(_feature(Shape.RECTANGLE, scale=1.0, rotation=0.0))
    t = el.get("transform")
    assert t == "translate(100.0 100.0) rotate(0.0) scale(1.0) translate(-100.0 -100.0)"


def test_rotation_radians_become_svg_degrees() -> None:
    from math import pi

    el = _render_one(_feature(Shape.RECTANGLE, scale=2.0, rotation=pi / 2))
    t = el.get("transform")
    # pi/2 rad -> 90 degrees; scale carried verbatim
    assert "rotate(90.0)" in t
    assert "scale(2.0)" in t
    assert t.startswith("translate(100.0 100.0)")
    assert t.endswith("translate(-100.0 -100.0)")


# ---------------------------------------------------------------------------
# Cell rendering: empty cell -> empty <g> (AC5.3)
# ---------------------------------------------------------------------------

def test_featureless_cell_renders_empty_group() -> None:
    from raven_matrix.model import Cell, Location
    from raven_matrix.render.svg import DEFAULT_RASTER, render_cell_svg

    cell = Cell(surface_features=[], location=Location(2, 2))
    group_svg = render_cell_svg(cell, DEFAULT_RASTER)
    root = ET.fromstring(f'<svg xmlns="{SVG_NS}">{group_svg}</svg>')
    group = root.find(_qn("g"))
    assert group is not None
    assert list(group) == []


def test_multi_feature_cell_renders_all_features() -> None:
    from raven_matrix.model import Cell, Location
    from raven_matrix.render.svg import DEFAULT_RASTER, render_cell_svg

    cell = Cell(
        surface_features=[_feature(Shape.ELLIPSE), _feature(Shape.RECTANGLE)],
        location=Location(0, 0),
    )
    group_svg = render_cell_svg(cell, DEFAULT_RASTER)
    root = ET.fromstring(f'<svg xmlns="{SVG_NS}">{group_svg}</svg>')
    group = root.find(_qn("g"))
    assert group is not None
    assert len(list(group)) == 2
