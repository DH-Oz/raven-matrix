"""Tests for render/svg.py — per-shape, per-fill, per-cell SVG (Phase 6 Task 1).

The acceptance bar is SVG well-formedness + semantics, never pixel parity with
the upstream Java2D.  Every test parses the emitted SVG with
``xml.etree.ElementTree`` and asserts tags / coordinates / attributes:

- AC5.1: each of the 7 shapes emits its expected element with the pinned base
  geometry (extracted verbatim from the SGMT surface/*.java makePath/createX
  sources); each of the 5 fills maps to the right ``fill`` + ``fill-opacity``
  (White -> ``fill-opacity="0"``); every shape carries ``stroke-width="2"``.
- AC5.3: a featureless cell renders as a valid, empty ``<g>`` (no error).

Geometry note: ``SurfaceFeature`` carries explicit ``width`` / ``height``
(pre-scale absolute pixels the generator drew the feature at).  Geometry derives
from those: half-width ``hw = width / 2`` and half-height ``hh = height / 2``.
``feature.scale`` does NOT enter the geometry — it multiplies via the affine
transform, exactly as Java applies scale in the transform rather than baking it
into the path (SGMCellImage.setSGMCell).  These tests build features at
``width = height = 128.0`` (so ``hw = hh = 64.0``) to pin the per-shape geometry.
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

# Per-shape geometry is pinned to width=height=128 (hw=hh=64), independent of the
# render cell_pixel_size — geometry now comes from feature.width/height, not from
# the raster settings.  LINE overrides height to 0.0 (height is unused for lines).
_DEFAULT_WIDTH = 128.0
_DEFAULT_HEIGHT = 128.0


def _feature(shape: Shape, *, fill: Fill = Fill.BLACK,
             scale: float = 1.0, rotation: float = 0.0,
             position: Point = _DEFAULT_POS,
             width: float = _DEFAULT_WIDTH,
             height: float = _DEFAULT_HEIGHT) -> SurfaceFeature:
    return SurfaceFeature(
        shape=shape, fill=fill, scale=scale, rotation=rotation,
        position=position, width=width, height=height,
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
    # cell_pixel_size defaults to 100 to match builder.CELL_PIXEL_SIZE (the cell
    # size build() always generates at), so absolute feature pixels land right.
    assert DEFAULT_RASTER.cell_pixel_size == 100
    assert DEFAULT_RASTER.pixels_between_cells == 10


# ---------------------------------------------------------------------------
# Per-shape geometry (from feature.width/height = 128; hw = hh = 64)
# position fixed at (100, 100) -> px=100, py=100
# ---------------------------------------------------------------------------

# Features are built at width = height = 128 (see _feature), so hw = hh = 64.
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
    # LINE carries its length in width; height is unused (set 0.0). length=128 -> hw=64.
    el = _render_one(_feature(Shape.LINE, width=128.0, height=0.0))
    assert el.tag == _qn("line")
    assert isclose(float(el.get("x1")), 100.0 - _HW)
    assert isclose(float(el.get("y1")), 100.0)
    assert isclose(float(el.get("x2")), 100.0 + _HW)
    assert isclose(float(el.get("y2")), 100.0)


def test_line_has_no_fill_attrs() -> None:
    """<line> has no fill area; fill/fill-opacity must be absent (Issue 1 fix)."""
    el = _render_one(_feature(Shape.LINE, width=128.0, height=0.0))
    assert el.get("fill") is None, "LINE element must not carry a fill attribute"
    assert el.get("fill-opacity") is None, "LINE element must not carry fill-opacity"
    # Stroke must still be present.
    assert el.get("stroke") == "black"
    assert el.get("stroke-width") == "2"


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


def test_rotation_degrees_emitted_directly_as_svg_rotate() -> None:
    """Model stores rotation in degrees; SVG rotate() takes degrees; emit directly.

    A 90-degree rotation must produce rotate(90.0) in the transform, NOT
    rotate(5156.6...) (which would result from treating 90 as radians and
    converting) and NOT rotate(1.5707...) (which would embed a radians value).

    This is the tripwire for the coherence-HIGH bug: degrees(feature.rotation)
    treated a degree value as radians.
    """
    el = _render_one(_feature(Shape.RECTANGLE, scale=2.0, rotation=90.0))
    t = el.get("transform")
    assert "rotate(90.0)" in t, (
        f"Expected rotate(90.0) in transform; got: {t!r}"
    )
    assert "scale(2.0)" in t
    assert t.startswith("translate(100.0 100.0)")
    assert t.endswith("translate(-100.0 -100.0)")


def test_rotation_45_degrees_emitted_directly() -> None:
    """45-degree rotation must emit rotate(45.0), not rotate(2578.3...)."""
    el = _render_one(_feature(Shape.RECTANGLE, rotation=45.0))
    t = el.get("transform")
    assert "rotate(45.0)" in t, (
        f"Expected rotate(45.0) in transform; got: {t!r}"
    )


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


# ---------------------------------------------------------------------------
# Proleptic hardening (Phase 6) — three invariant-guard tests
# ---------------------------------------------------------------------------

def test_rotation_90_transform_exact_full_string() -> None:
    """Test #1 — exact full transform string for the 90-degree rotation case.

    The existing rotation tripwire test uses substring checks.  This test
    asserts the COMPLETE transform string so any future change to ordering,
    separators, or float formatting is caught immediately.

    Feature: shape=RECTANGLE, scale=2.0, rotation=90.0, position=Point(100.0, 100.0)
    — same values the existing test uses, plus the full-string assertion.
    """
    el = _render_one(_feature(Shape.RECTANGLE, scale=2.0, rotation=90.0))
    t = el.get("transform")
    expected = (
        "translate(100.0 100.0) rotate(90.0) scale(2.0) translate(-100.0 -100.0)"
    )
    assert t == expected, f"Full transform string did not match; got: {t!r}"


def test_scale_lives_in_transform_not_geometry() -> None:
    """Test #2 — scale is applied via the transform, not baked into path geometry.

    Render the same shape (ELLIPSE and TRIANGLE) at scale=1.0 and scale=0.66
    (the actual ApplyScaling multiplier upstream uses).  The geometry coordinates
    must be IDENTICAL between the two renders; only the scale(...) term in the
    transform may differ.

    This guards the invariant documented in svg.py: ``feature.scale multiplies it
    through the affine transform, exactly as Java applies scale inside the
    transform (SGMCellImage.setSGMCell) rather than baking it into the path.``
    """
    # --- ELLIPSE ---
    pos = _DEFAULT_POS  # Point(100.0, 100.0)
    el_10 = _render_one(_feature(Shape.ELLIPSE, scale=1.0, rotation=0.0, position=pos))
    el_066 = _render_one(
        _feature(Shape.ELLIPSE, scale=0.66, rotation=0.0, position=pos)
    )

    # Geometry: cx/cy/rx/ry must be identical
    for attr in ("cx", "cy", "rx", "ry"):
        assert el_10.get(attr) == el_066.get(attr), (
            f"ELLIPSE geometry attr {attr!r} differs between scale=1.0 and "
            f"scale=0.66: {el_10.get(attr)!r} vs {el_066.get(attr)!r}"
        )

    # Transforms differ only in the scale(...) term
    t10 = el_10.get("transform")
    t066 = el_066.get("transform")
    _t_base = "translate(100.0 100.0) rotate(0.0) scale({s}) translate(-100.0 -100.0)"
    assert t10 == _t_base.format(s="1.0"), f"ELLIPSE scale=1.0 transform: {t10!r}"
    assert t066 == _t_base.format(s="0.66"), f"ELLIPSE scale=0.66 transform: {t066!r}"

    # --- TRIANGLE (path-based shape) ---
    tr_10 = _render_one(_feature(Shape.TRIANGLE, scale=1.0, rotation=0.0, position=pos))
    tr_066 = _render_one(
        _feature(Shape.TRIANGLE, scale=0.66, rotation=0.0, position=pos)
    )

    # Path d attribute must be identical
    assert tr_10.get("d") == tr_066.get("d"), (
        f"TRIANGLE path d differs between scale=1.0 and scale=0.66: "
        f"{tr_10.get('d')!r} vs {tr_066.get('d')!r}"
    )
    # Expected path at pos=(100,100), base=128, hw=hh=64
    expected_triangle_d = "M 36.0 164.0 L 164.0 164.0 L 100.0 36.0 Z"
    assert tr_10.get("d") == expected_triangle_d, (
        f"TRIANGLE path d at scale=1.0: {tr_10.get('d')!r}"
    )

    # Transforms differ only in scale
    tt10 = tr_10.get("transform")
    tt066 = tr_066.get("transform")
    assert tt10 == _t_base.format(s="1.0"), f"TRIANGLE scale=1.0 transform: {tt10!r}"
    assert tt066 == _t_base.format(s="0.66"), (
        f"TRIANGLE scale=0.66 transform: {tt066!r}"
    )


def test_off_centre_position_drives_geometry_and_transform_pivot() -> None:
    """Test #3 — off-centre position is used coherently in geometry AND transform.

    Render an ELLIPSE at Point(64.0, 192.0) — an off-centre position, not a cell
    centre.  Geometry (rx/ry) comes from the feature's width/height (128 -> 64),
    independent of position.  Assert:
    - The geometry (cx/cy) reflects the non-centred position.
    - The transform starts with translate(64.0 192.0) and ends with
      translate(-64.0 -192.0), proving both the geometry centre and the
      rotate/scale pivot are derived from the same feature.position.
    """
    off_pos = Point(64.0, 192.0)
    el = _render_one(_feature(Shape.ELLIPSE, scale=1.0, rotation=0.0, position=off_pos))

    # Geometry must reflect the off-centre position
    assert el.get("cx") == "64.0", f"cx should be 64.0; got {el.get('cx')!r}"
    assert el.get("cy") == "192.0", f"cy should be 192.0; got {el.get('cy')!r}"
    # rx/ry come from width/height (128 -> 64), not position — still 64.0
    assert el.get("rx") == "64.0", f"rx should be 64.0; got {el.get('rx')!r}"
    assert el.get("ry") == "64.0", f"ry should be 64.0; got {el.get('ry')!r}"

    # Full transform string: pivot is position, not cell centre
    t = el.get("transform")
    expected = (
        "translate(64.0 192.0) rotate(0.0) scale(1.0) translate(-64.0 -192.0)"
    )
    assert t == expected, f"Off-centre transform string did not match; got: {t!r}"
