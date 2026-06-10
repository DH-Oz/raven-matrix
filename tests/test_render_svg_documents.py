"""Tests for render/svg.py document layouts (Phase 6 Task 2).

``render_matrix_svg`` and ``render_answers_svg`` wrap per-cell groups into full
``<svg>`` documents with the upstream layout (``SGMMatrixImage`` /
``SGMAnswerChoicesImage``):

- matrix: 3x3 grid, white background, blank-white bottom-right cell (problem
  mode, ``render-answer-cell-hardcoded-bottom-right``);
- answers: 2x4 grid of the 8 answer choices, black background.

The acceptance bar is SVG well-formedness + semantics: tests parse with
``xml.etree.ElementTree`` and assert cell-group counts, the blank bottom-right,
viewBox dimensions per the layout formula, and that every shape/fill across a
hand-built sample renders.  Never pixel parity with Java2D.

Phase-4 independence: there is no builder/``build()`` on this branch.  The
sample ``Matrix`` is hand-constructed by directly instantiating the model
classes, with its 3x3 cells collectively covering all 7 shapes and all 5 fills.
"""

from __future__ import annotations

import dataclasses
import xml.etree.ElementTree as ET

from raven_matrix.model import (
    Cell,
    Fill,
    Layer,
    Location,
    Matrix,
    Point,
    Shape,
    SurfaceFeature,
)
from raven_matrix.render.svg import (
    DEFAULT_RASTER,
    render_answers_svg,
    render_matrix_svg,
)

SVG_NS = "http://www.w3.org/2000/svg"


def _qn(tag: str) -> str:
    return f"{{{SVG_NS}}}{tag}"


def _feat(shape: Shape, fill: Fill) -> SurfaceFeature:
    # Absolute pre-scale pixels; width/height are explicit per the 7-arg model.
    # Position (50, 50) is the centre of a 100px cell (the render cell size); a
    # 50px feature (¼..¾ of the 100px cell) sits well inside it.  Layout/viewBox
    # assertions below derive from cell_pixel_size symbolically, so the exact
    # geometry here only needs to be valid, not pinned.
    return SurfaceFeature(
        shape=shape, fill=fill, scale=1.0, rotation=0.0,
        position=Point(50.0, 50.0), width=50.0, height=50.0,
    )


def _sample_matrix() -> Matrix:
    """A 3x3 matrix whose cells collectively span all 7 shapes and all 5 fills.

    Hand-built (no Phase-4 builder on this branch).  The bottom-right cell is
    deliberately featured to prove the renderer still blanks it (problem mode).
    Answer choices: 8 cells, each carrying one (shape, fill) so the answer sheet
    also exercises coverage.
    """
    shapes = list(Shape)   # 7
    fills = list(Fill)     # 5

    # Lay one (shape, fill) pair into each of the 9 grid cells, cycling so that
    # all 7 shapes and all 5 fills appear at least once across the grid.
    grid: list[list[Cell]] = []
    k = 0
    for row in range(3):
        grid_row: list[Cell] = []
        for col in range(3):
            shape = shapes[k % len(shapes)]
            fill = fills[k % len(fills)]
            grid_row.append(
                Cell(surface_features=[_feat(shape, fill)], location=Location(row, col))
            )
            k += 1
        grid.append(grid_row)

    # 8 answer-choice cells, one (shape, fill) each (also full coverage).
    answers: list[Cell] = []
    for i in range(8):
        feature = _feat(shapes[i % len(shapes)], fills[i % len(fills)])
        answers.append(
            Cell(surface_features=[feature], location=Location(0, 0))
        )

    layer = Layer(cells=grid, structures=[])
    return Matrix(
        cells=grid,
        answer_choices=answers,
        correct_answer_position=3,
        layers=[layer],
    )


# ---------------------------------------------------------------------------
# Matrix document
# ---------------------------------------------------------------------------

def test_matrix_svg_parses_as_wellformed_svg() -> None:
    root = ET.fromstring(render_matrix_svg(_sample_matrix()))
    assert root.tag == _qn("svg")


def test_matrix_svg_viewbox_matches_layout_formula() -> None:
    root = ET.fromstring(render_matrix_svg(_sample_matrix()))
    cell = DEFAULT_RASTER.cell_pixel_size
    gap = DEFAULT_RASTER.pixels_between_cells
    side = (cell + gap) * 3 + gap
    assert root.get("viewBox") == f"0 0 {side} {side}"
    assert root.get("width") == str(side)
    assert root.get("height") == str(side)


def test_matrix_svg_has_nine_cell_groups() -> None:
    root = ET.fromstring(render_matrix_svg(_sample_matrix()))
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    assert len(cell_groups) == 9


def test_matrix_svg_bottom_right_cell_is_blank() -> None:
    root = ET.fromstring(render_matrix_svg(_sample_matrix()))
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    # The 9th cell (row 2, col 2) is the hard-coded problem-mode blank.
    bottom_right = cell_groups[-1]
    # No shape elements inside the blanked cell's nested <g>.
    inner = bottom_right.find(_qn("g"))
    assert inner is not None
    assert list(inner) == []


def test_matrix_svg_non_blank_cells_carry_their_features() -> None:
    root = ET.fromstring(render_matrix_svg(_sample_matrix()))
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    # The first 8 cells each hold one feature.
    for group in cell_groups[:8]:
        inner = group.find(_qn("g"))
        assert inner is not None
        assert len(list(inner)) == 1


def test_matrix_svg_has_white_background_rect() -> None:
    root = ET.fromstring(render_matrix_svg(_sample_matrix()))
    bg = root.find(f"./{_qn('rect')}[@class='background']")
    assert bg is not None
    assert bg.get("fill") == "white"


def test_matrix_svg_covers_every_shape_and_fill() -> None:
    """Across the rendered grid, all 7 shape tags and all 5 fills appear."""
    svg = render_matrix_svg(_sample_matrix())
    # Every shape kind appears as an element somewhere in the document.
    assert "<ellipse" in svg
    assert "<rect" in svg  # both the bg rect and any rectangle features
    assert "<line" in svg
    assert "<path" in svg
    # Every distinct fill RGB appears.
    for fill in Fill:
        rgba = fill.value
        rgb = f"rgb({round(rgba.r * 255)},{round(rgba.g * 255)},{round(rgba.b * 255)})"
        assert rgb in svg, f"missing fill {fill.name} ({rgb})"


# ---------------------------------------------------------------------------
# Answers document
# ---------------------------------------------------------------------------

def test_answers_svg_parses_as_wellformed_svg() -> None:
    root = ET.fromstring(render_answers_svg(_sample_matrix()))
    assert root.tag == _qn("svg")


def test_answers_svg_viewbox_matches_two_by_four_layout() -> None:
    root = ET.fromstring(render_answers_svg(_sample_matrix()))
    cell = DEFAULT_RASTER.cell_pixel_size
    gap = DEFAULT_RASTER.pixels_between_cells
    width = (cell + gap) * 4 + gap
    height = (cell + gap) * 2 + gap
    assert root.get("viewBox") == f"0 0 {width} {height}"
    assert root.get("width") == str(width)
    assert root.get("height") == str(height)


def test_answers_svg_has_eight_cell_groups() -> None:
    root = ET.fromstring(render_answers_svg(_sample_matrix()))
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    assert len(cell_groups) == 8


def test_answers_svg_has_black_background_rect() -> None:
    root = ET.fromstring(render_answers_svg(_sample_matrix()))
    bg = root.find(f"./{_qn('rect')}[@class='background']")
    assert bg is not None
    assert bg.get("fill") == "black"


def test_answers_svg_cells_translate_to_two_by_four_positions() -> None:
    root = ET.fromstring(render_answers_svg(_sample_matrix()))
    cell = DEFAULT_RASTER.cell_pixel_size
    gap = DEFAULT_RASTER.pixels_between_cells
    step = cell + gap
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    # Index 0 -> (row 0, col 0); index 4 -> (row 1, col 0); index 7 -> (row 1, col 3).
    expected = {
        0: (gap, gap),
        4: (gap, gap + step),
        7: (gap + 3 * step, gap + step),
    }
    for idx, (ex, ey) in expected.items():
        t = cell_groups[idx].get("transform")
        assert t == f"translate({ex} {ey})", f"answer {idx}: {t}"


# ---------------------------------------------------------------------------
# AC5.3: blank / empty answer cell renders without error
# ---------------------------------------------------------------------------

def test_answers_svg_with_blank_pad_cell_renders() -> None:
    matrix = _sample_matrix()
    # Replace one answer with a featureless (blank-pad) cell without mutating
    # the original list — guards against answer_choices becoming an immutable
    # sequence in future.
    choices = list(matrix.answer_choices)
    choices[5] = Cell(surface_features=[], location=Location(0, 0))
    matrix = dataclasses.replace(matrix, answer_choices=choices)
    root = ET.fromstring(render_answers_svg(matrix))
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    assert len(cell_groups) == 8
    blank_inner = cell_groups[5].find(_qn("g"))
    assert blank_inner is not None
    assert list(blank_inner) == []


# ---------------------------------------------------------------------------
# White cell backgrounds for answer choices (visibility on black backdrop)
# Mirrors SGMAnswerChoicesImage compositing white SGMCellImage cells onto the
# black backdrop — each SGMCellImage fills itself white before drawing features.
# ---------------------------------------------------------------------------

def test_answers_svg_has_eight_white_cell_background_rects() -> None:
    """Each answer cell must have a white cell-bg rect behind its features.

    The black backdrop is the single <rect class="background"> element.
    The eight white cell backgrounds are <rect class="cell-bg"> elements,
    one per cell, at (0,0) in cell-local coords, sized cell_pixel_size square.
    This test MUST fail before the fix: the current code emits no cell-bg rects.
    """
    root = ET.fromstring(render_answers_svg(_sample_matrix()))
    cell_size = DEFAULT_RASTER.cell_pixel_size

    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    assert len(cell_groups) == 8, "expected 8 cell groups"

    for i, group in enumerate(cell_groups):
        bg_rects = group.findall(f".//{_qn('rect')}[@class='cell-bg']")
        assert len(bg_rects) == 1, (
            f"answer cell {i} must have exactly one cell-bg rect, got {len(bg_rects)}"
        )
        rect = bg_rects[0]
        assert rect.get("fill") == "white", (
            f"cell-bg rect in answer cell {i} must be fill='white'"
        )
        assert rect.get("x") == "0", (
            f"cell-bg rect in answer cell {i} must be at x=0"
        )
        assert rect.get("y") == "0", (
            f"cell-bg rect in answer cell {i} must be at y=0"
        )
        assert rect.get("width") == str(cell_size), (
            f"cell-bg rect width must equal cell_pixel_size={cell_size}"
        )
        assert rect.get("height") == str(cell_size), (
            f"cell-bg rect height must equal cell_pixel_size={cell_size}"
        )


def test_answers_svg_white_fill_shape_has_cell_bg_rect() -> None:
    """A WHITE-fill shape in an answer cell must have a cell-bg rect behind it.

    Without the white cell background, a WHITE-fill shape (fill-opacity=0,
    black 2px stroke) is invisible against the black backdrop.  This test
    hand-builds a Matrix with a WHITE-fill shape in the first answer cell and
    asserts the cell-bg rect precedes the feature element inside the cell group.
    Mirrors SGMCellImage.setSGMCell: white fill drawn first, shape on top.
    """
    white_feature = SurfaceFeature(
        shape=Shape.ELLIPSE,
        fill=Fill.WHITE,
        scale=1.0,
        rotation=0.0,
        position=Point(50.0, 50.0),
        width=50.0,
        height=50.0,
    )
    white_cell = Cell(surface_features=[white_feature], location=Location(0, 0))
    # Build minimal 3x3 matrix — all grid cells blank, one answer is the white cell.
    blank = Cell(surface_features=[], location=Location(0, 0))
    grid = [[blank, blank, blank], [blank, blank, blank], [blank, blank, blank]]
    answers = [white_cell] + [blank] * 7
    layer = Layer(cells=grid, structures=[])
    matrix = Matrix(
        cells=grid,
        answer_choices=answers,
        correct_answer_position=0,
        layers=[layer],
    )

    root = ET.fromstring(render_answers_svg(matrix))
    cell_groups = root.findall(f"./{_qn('g')}[@class='cell']")
    first_cell = cell_groups[0]

    # Must have a cell-bg rect.
    bg_rects = first_cell.findall(f".//{_qn('rect')}[@class='cell-bg']")
    assert len(bg_rects) == 1, "white-fill answer cell must have a cell-bg rect"
    assert bg_rects[0].get("fill") == "white"

    # The cell-bg rect must appear before the feature elements in document order
    # (so features paint on top of the white background, not hidden behind it).
    inner_g = first_cell.find(_qn("g"))
    assert inner_g is not None
    children = list(inner_g)
    assert len(children) >= 1, "inner group must have at least the feature element"
    # The cell-bg rect lives directly in the cell group (sibling of inner <g>),
    # so it is the first direct child of the cell <g>.
    direct_children = list(first_cell)
    assert direct_children[0].get("class") == "cell-bg", (
        "cell-bg rect must be the first child of the cell group so it renders "
        "behind the features"
    )
