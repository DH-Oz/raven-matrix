"""Render preview PNGs for visual QA of the SVG renderer.

A developer/QA harness — NOT a pytest. It exercises the full
``build() -> render_*_svg -> rasterise`` pipeline and writes PNGs (plus their
SVG sources) to ``previews/`` (gitignored) so a human can eyeball the renderer.
The deferred Phase-6 "Visual correctness" UAT lives here until the Phase-7 app
provides the user-facing path.

Two modes:

* ``gallery`` — hand-built matrices covering all 7 shapes x 5 fills, a 0deg/90deg
  rotation pair, and a scale pair. Deterministic, exhaustive, rendered at a
  clarity-friendly 200px cell.
* ``build`` — ``build()`` real matrices from a few representative configs/seeds,
  rendered at the generator's native 100px cell (``DEFAULT_RASTER``).

Requires the ``raster`` extra (``uv run --all-extras python tools/render_preview.py``).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from raven_matrix.builder import BuilderConfig, LayerConfig, build
from raven_matrix.model import (
    BaseRelation,
    Cell,
    Direction,
    Fill,
    Location,
    Matrix,
    Point,
    Shape,
    Supplemental,
    SurfaceFeature,
)
from raven_matrix.render.raster import rasterise
from raven_matrix.render.svg import (
    RasterSettings,
    render_answers_svg,
    render_matrix_svg,
)

PREVIEWS = Path(__file__).resolve().parent.parent / "previews"
GALLERY = RasterSettings(cell_pixel_size=200, pixels_between_cells=12)
# Centre of a GALLERY cell — derived from GALLERY so it tracks cell_pixel_size
# (NOT the builder's CELL_PIXEL_SIZE, which it happens to equal at 200/2 = 100).
_GALLERY_CENTRE = Point(GALLERY.cell_pixel_size / 2, GALLERY.cell_pixel_size / 2)


def _feat(
    shape: Shape,
    fill: Fill,
    *,
    w: float = 120.0,
    h: float = 120.0,
    scale: float = 1.0,
    rot: float = 0.0,
    pos: Point = _GALLERY_CENTRE,
) -> SurfaceFeature:
    return SurfaceFeature(shape, fill, scale, rot, pos, w, h)


def _cell(row: int, col: int, *features: SurfaceFeature) -> Cell:
    return Cell(list(features), Location(row, col))


def _matrix(rows: list[list[Cell]], answers: list[Cell]) -> Matrix:
    return Matrix(
        cells=rows, answer_choices=answers, correct_answer_position=1, layers=[],
    )


def _save(name: str, svg: str) -> None:
    PREVIEWS.mkdir(exist_ok=True)
    (PREVIEWS / f"{name}.svg").write_text(svg)
    (PREVIEWS / f"{name}.png").write_bytes(rasterise(svg))
    print(f"  {name}.png")


def gallery() -> None:
    """Hand-built coverage: every shape, every fill, a rotation pair, a scale pair."""
    print("gallery:")
    shapes_grid = [
        [_cell(0, 0, _feat(Shape.DIAMOND, Fill.GREY40)),
         _cell(0, 1, _feat(Shape.ELLIPSE, Fill.GREY40)),
         _cell(0, 2, _feat(Shape.LINE, Fill.GREY40, h=0.0))],
        [_cell(1, 0, _feat(Shape.RECTANGLE, Fill.GREY40)),
         _cell(1, 1, _feat(Shape.TEE, Fill.GREY40)),
         _cell(1, 2, _feat(Shape.TRAPEZOID, Fill.GREY40))],
        [_cell(2, 0, _feat(Shape.TRIANGLE, Fill.GREY40)),
         _cell(2, 1, _feat(Shape.TRIANGLE, Fill.GREY40, rot=90.0)),  # rotation check
         _cell(2, 2)],  # forced-blank bottom-right (problem mode)
    ]
    filler = [_cell(0, i, _feat(Shape.ELLIPSE, Fill.GREY40)) for i in range(8)]
    _save("gallery_shapes", render_matrix_svg(_matrix(shapes_grid, filler), GALLERY))

    fills_grid = [
        [_cell(0, 0, _feat(Shape.RECTANGLE, Fill.BLACK)),
         _cell(0, 1, _feat(Shape.RECTANGLE, Fill.GREY10)),
         _cell(0, 2, _feat(Shape.RECTANGLE, Fill.GREY40))],
        [_cell(1, 0, _feat(Shape.RECTANGLE, Fill.GREY75)),
         _cell(1, 1, _feat(Shape.RECTANGLE, Fill.WHITE)),  # outline-only
         _cell(1, 2, _feat(Shape.LINE, Fill.BLACK, h=0.0, rot=45.0))],
        [_cell(2, 0, _feat(Shape.ELLIPSE, Fill.BLACK, scale=0.5)),  # scale check
         _cell(2, 1, _feat(Shape.ELLIPSE, Fill.BLACK)),
         _cell(2, 2)],
    ]
    _save("gallery_fills", render_matrix_svg(_matrix(fills_grid, filler), GALLERY))

    answer_cells = [
        _cell(0, i, _feat(list(Shape)[i % 7], list(Fill)[i % 5])) for i in range(8)
    ]
    answers_matrix = Matrix(
        cells=shapes_grid, answer_choices=answer_cells,
        correct_answer_position=3, layers=[],
    )
    _save("gallery_answers", render_answers_svg(answers_matrix, GALLERY))


_CONFIGS = {
    "shape_rep_h": BuilderConfig(
        layers=(LayerConfig(BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL),),
        correct_answer_position=1,
    ),
    "scaling": BuilderConfig(
        layers=(LayerConfig(
            BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL,
            supplementals=((Supplemental.SCALING, Direction.HORIZONTAL),),
        ),),
        correct_answer_position=3,
    ),
    "two_layer": BuilderConfig(
        layers=(
            LayerConfig(BaseRelation.SHAPE_REPETITION, Direction.HORIZONTAL),
            LayerConfig(BaseRelation.LOGICAL_OR, Direction.VERTICAL),
        ),
        correct_answer_position=5,
    ),
}


def build_previews(seed: int) -> None:
    """Render real ``build()`` output at the generator's native 100px cell."""
    print(f"build previews (seed {seed}):")
    for name, cfg in _CONFIGS.items():
        matrix = build(cfg, seed=seed)
        _save(f"build_{name}_problem", render_matrix_svg(matrix))
        _save(f"build_{name}_answers", render_answers_svg(matrix))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "mode", nargs="?", default="all", choices=["all", "gallery", "build"],
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.mode in ("all", "gallery"):
        gallery()
    if args.mode in ("all", "build"):
        build_previews(args.seed)
    print(f"\nPNGs (and SVG sources) in {PREVIEWS}/")


if __name__ == "__main__":
    main()
