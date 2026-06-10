"""Tests for render/raster.py — SVG→PNG rasterisation (Phase 6 Task 3).

``rasterise(svg) -> bytes`` converts a canonical SVG string to PNG bytes via the
optional ``raster`` extra (``resvg_py``).  The acceptance bar is data/logic
equivalence, not pixel reproduction: tests assert the returned bytes are a real
PNG (magic header + a parseable IHDR), never pixel parity with Java2D.

This file runs under CI's ``--all-extras``, so ``resvg_py`` is installed.  It
also guards the import-hygiene contract that Phase 8 depends on: importing the
core SVG renderer (``raven_matrix.render.svg``) must not drag in the optional
``resvg_py`` backend.

Phase-4 independence: there is no builder/``build()`` on this branch.  The sample
``Matrix`` is hand-constructed by directly instantiating the model classes (same
pattern as ``tests/test_render_svg_documents.py``).
"""

from __future__ import annotations

import struct
import subprocess
import sys

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
from raven_matrix.render.raster import rasterise
from raven_matrix.render.svg import render_matrix_svg

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _feat(shape: Shape, fill: Fill) -> SurfaceFeature:
    # Absolute pre-scale pixels (7-arg model); centre/size valid for a 100px cell.
    return SurfaceFeature(
        shape=shape, fill=fill, scale=1.0, rotation=0.0,
        position=Point(50.0, 50.0), width=50.0, height=50.0,
    )


def _sample_matrix() -> Matrix:
    """A 3x3 matrix spanning all 7 shapes and all 5 fills (hand-built)."""
    shapes = list(Shape)
    fills = list(Fill)
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
    answers = [
        Cell(surface_features=[_feat(shapes[i % len(shapes)], fills[i % len(fills)])],
             location=Location(0, 0))
        for i in range(8)
    ]
    layer = Layer(cells=grid, structures=[])
    return Matrix(
        cells=grid,
        answer_choices=answers,
        correct_answer_position=3,
        layers=[layer],
    )


def _png_dimensions(png: bytes) -> tuple[int, int]:
    """Parse (width, height) from a PNG's IHDR chunk (stdlib only)."""
    # Bytes 8..16 are the IHDR length + type; 16..24 are width then height (big-endian).
    width, height = struct.unpack(">II", png[16:24])
    return width, height


# ---------------------------------------------------------------------------
# AC5.2: rasterise produces a real PNG
# ---------------------------------------------------------------------------

def test_rasterise_returns_png_magic() -> None:
    png = rasterise(render_matrix_svg(_sample_matrix()))
    assert isinstance(png, bytes)
    assert png[:8] == PNG_MAGIC


def test_rasterise_returns_nontrivial_png() -> None:
    png = rasterise(render_matrix_svg(_sample_matrix()))
    # A real rendered matrix PNG is far larger than the 8-byte magic.
    assert len(png) > 100


def test_rasterise_png_ihdr_has_positive_dimensions() -> None:
    png = rasterise(render_matrix_svg(_sample_matrix()))
    width, height = _png_dimensions(png)
    assert width > 0
    assert height > 0


# ---------------------------------------------------------------------------
# Import hygiene: the core SVG path must not require the raster extra
# ---------------------------------------------------------------------------

def test_importing_core_svg_does_not_load_resvg_py() -> None:
    """``raven_matrix.render.svg`` must import without pulling in ``resvg_py``.

    Run in a fresh interpreter so a prior ``import resvg_py`` in this process (or
    test session) cannot mask a stray module-scope import in the core renderer.
    """
    code = (
        "import sys\n"
        "import raven_matrix.render.svg\n"
        "assert 'resvg_py' not in sys.modules, "
        "'core svg import must not load resvg_py'\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
