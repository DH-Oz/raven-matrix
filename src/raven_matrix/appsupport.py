"""Pure helpers behind the marimo app (Phase 7, Task 3 / N1).

# pattern: Functional Core

The marimo app (``app.py``) is a thin reactive shell: it defines the UI elements
(so marimo can track their ``.value`` reactively) and lays out the live render.
Everything decidable WITHOUT marimo lives here -- the option-label -> enum maps,
the column-read-back -> ``LayerControls`` mapping, and the build orchestration --
so it can be tested with plain assertions and no marimo runtime (FCIS).

This module is PURE: no marimo, no typer, no I/O. It defers every generation
decision to the core (``config_from_controls`` / ``build`` / ``build_from_code`` /
``label``) and catches the ``ValueError`` those raise for option sets the upstream
surface could not produce, returning a small ``BuildOutcome`` the shell renders.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from xml.sax.saxutils import escape

from raven_matrix.builder import build, build_from_code
from raven_matrix.label import label
from raven_matrix.model import BaseRelation, Direction, Matrix, Supplemental
from raven_matrix.render.svg import render_answers_svg, render_matrix_svg
from raven_matrix.ui_config import LayerControls, config_from_controls

_SVG_NS = "http://www.w3.org/2000/svg"

# ---------------------------------------------------------------------------
# Option-label -> enum maps (the GUI's fixed pick lists)
# ---------------------------------------------------------------------------
#
# These mirror the dropdown choices in ``SGMBuilderFrame``. The app passes each
# dict straight to ``mo.ui.dropdown(options=...)``, so the read-back ``.value`` is
# already the mapped enum (or ``None`` for the "Disabled" supplemental slot),
# which is why ``layer_controls_from_column`` below sees enums, not labels.

RELATION_OPTIONS: dict[str, BaseRelation] = {
    "ShapeRep": BaseRelation.SHAPE_REPETITION,
    "OR": BaseRelation.LOGICAL_OR,
    "AND": BaseRelation.LOGICAL_AND,
    "XOR": BaseRelation.LOGICAL_XOR,
}

DIRECTION_OPTIONS: dict[str, Direction] = {
    "H": Direction.HORIZONTAL,
    "V": Direction.VERTICAL,
    "DiagTL": Direction.DIAGONAL_TL_BR,
    "DiagBL": Direction.DIAGONAL_BL_TR,
    "CornerOut": Direction.TOP_LEFT_CORNER_OUT,
}

# "Disabled" maps to None so the edge layer can drop the slot before constructing
# LayerControls (the GUI's three fixed supplemental rows each include a disabled
# choice).
SUPPLEMENTAL_OPTIONS: dict[str, Supplemental | None] = {
    "Disabled": None,
    "Scaling": Supplemental.SCALING,
    "Rotation": Supplemental.ROTATION,
    "FillRep": Supplemental.FILL_REPETITION,
    "ChangeFill": Supplemental.CHANGE_FILL,
    "Numerosity": Supplemental.NUMEROSITY,
}


# ---------------------------------------------------------------------------
# Column read-back -> LayerControls
# ---------------------------------------------------------------------------


def layer_controls_from_column(column_value: Mapping[str, Any]) -> LayerControls:
    """Map one GUI column's read-back dict onto a ``LayerControls``.

    ``column_value`` is what a layer's ``mo.ui.dictionary`` reads back: ``"base"``
    and ``"base_direction"`` are already mapped enums, and each of ``"supp1"`` /
    ``"supp2"`` / ``"supp3"`` is a ``{"type": Supplemental | None, "direction":
    Direction}`` slot. Every "Disabled" slot (its ``type`` is ``None``) is dropped
    before constructing the dataclass, matching the ``ui_config`` contract that
    ``supplementals`` holds only ENABLED slots.
    """
    supplementals = [
        (slot["type"], slot["direction"])
        for key in ("supp1", "supp2", "supp3")
        if (slot := column_value[key])["type"] is not None
    ]
    return LayerControls(
        base=column_value["base"],
        base_direction=column_value["base_direction"],
        supplementals=supplementals,
    )


# ---------------------------------------------------------------------------
# Build orchestration
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BuildOutcome:
    """The result of one build attempt, ready for the shell to render.

    Exactly one of ``matrix`` / ``error`` is set: on success ``matrix`` holds the
    built ``Matrix`` and ``structure_code`` its ``label``; on a forbidden option
    set or a malformed code, ``error`` carries the friendly ``ValueError`` text and
    both ``matrix`` and ``structure_code`` are ``None``.
    """

    matrix: Matrix | None
    error: str | None
    structure_code: str | None


# ---------------------------------------------------------------------------
# In-app reference (N2): document every control and every option
# ---------------------------------------------------------------------------
#
# The reference is sourced from the Matzen naming scheme (CLAUDE.md, "## QA
# target") and rendered into a collapsing accordion beside the controls. It is
# pure markdown -- no marimo -- so it is built and tested here. Where it can, the
# text is GENERATED by iterating the same option maps / enums the controls use
# (RELATION_OPTIONS, DIRECTION_OPTIONS, SUPPLEMENTAL_OPTIONS, BaseRelation,
# Direction, Supplemental), so a new option appears in the docs automatically and
# the completeness test in tests/test_appsupport.py guards against drift.

# Matzen relation letter (A-E) for each base/supplemental relation, and the prose
# meaning. The letter is the leading character of a Structure code segment; the
# generator realises it through the structure/ package (see CLAUDE.md). Logic
# bases (OR/AND/XOR) compose a whole layer and take no supplementals.
_RELATION_MEANING: dict[BaseRelation, tuple[str, str]] = {
    BaseRelation.SHAPE_REPETITION: (
        "A",
        "Shape repetition -- the same shape recurs across the row/column.",
    ),
    BaseRelation.LOGICAL_OR: (
        "X",
        "Logical OR -- the third cell is the union of the first two.",
    ),
    BaseRelation.LOGICAL_AND: (
        "Y",
        "Logical AND -- the third cell is the intersection of the first two.",
    ),
    BaseRelation.LOGICAL_XOR: (
        "Z",
        "Logical XOR -- the third cell is the symmetric difference of the first two.",
    ),
}

_SUPPLEMENTAL_MEANING: dict[Supplemental, tuple[str, str]] = {
    Supplemental.CHANGE_FILL: (
        "B",
        "Shading -- the fill pattern changes across the repetition direction.",
    ),
    Supplemental.FILL_REPETITION: (
        "B",
        "Shading repetition -- a fill pattern recurs across the direction.",
    ),
    Supplemental.ROTATION: (
        "C",
        "Orientation -- the shape rotates across the repetition direction.",
    ),
    Supplemental.SCALING: (
        "D",
        "Size -- the shape scales across the repetition direction.",
    ),
    Supplemental.NUMEROSITY: (
        "E",
        "Number repetition -- the count of shapes changes across the direction.",
    ),
}

# Matzen direction digit (1-5) meaning. Sourced from CLAUDE.md; the digit is the
# Direction enum's own IntEnum value, so it is read straight off the member.
_DIRECTION_MEANING: dict[Direction, str] = {
    Direction.HORIZONTAL: "left to right across each row",
    Direction.VERTICAL: "top to bottom down each column",
    Direction.DIAGONAL_BL_TR: "bottom-left to top-right diagonal",
    Direction.DIAGONAL_TL_BR: "top-left to bottom-right diagonal",
    Direction.TOP_LEFT_CORNER_OUT: "outward from the top-left corner",
}

# Label (the GUI dropdown key) for each relation / direction / supplemental enum,
# inverted from the option maps so the prose can cite the exact control choice.
_RELATION_LABEL: dict[BaseRelation, str] = {
    relation: label_text for label_text, relation in RELATION_OPTIONS.items()
}
_DIRECTION_LABEL: dict[Direction, str] = {
    direction: label_text for label_text, direction in DIRECTION_OPTIONS.items()
}
_SUPPLEMENTAL_LABEL: dict[Supplemental, str] = {
    supplemental: label_text
    for label_text, supplemental in SUPPLEMENTAL_OPTIONS.items()
    if supplemental is not None
}


def option_reference() -> str:
    """Return markdown documenting every control and every option a researcher sees.

    Pure: builds a single markdown string from the same option maps / enums the
    controls are wired to (so the docs cannot silently drift -- the completeness
    test iterates the enums and asserts each member, label, and direction digit
    appears here). The meanings come from the Matzen naming scheme in CLAUDE.md
    (relation letters A Shape / B Shading / C Orientation / D Size / E Number
    repetition; direction digits 1-5; the logic bases OR/AND/XOR).
    """
    lines: list[str] = [
        "## Option reference",
        "",
        "Every control mirrors the upstream SGMT `SGMBuilderFrame`. Option",
        "meanings follow the Matzen et al. (2010) naming scheme (relation letter +",
        "direction digit; e.g. `A1B2C4`).",
        "",
        "### Mode",
        "",
        "The **Mode** toggle chooses how the puzzle is built:",
        "",
        "- *Build from controls* -- pick each relation, direction, and supplemental",
        "  by hand (the faithful control panel).",
        "- *Build from code* -- type a Structure code (e.g. `A1B2C4`) into the",
        "  **Structure code** field and the generator composes one layer per segment.",
        "",
        "### Layers",
        "",
        "**Layers** sets the layer count (1 or 2). Each layer carries its own base",
        "relation, base direction, and three supplemental slots; with 2 layers the",
        "second layer's controls appear too. The layer count is the `... Layer Stim`",
        "grouping in the norming set.",
        "",
        "### Base relation",
        "",
        "The **Base relation** dropdown picks the layer's core logic. ShapeRep is the",
        "non-logic base; OR/AND/XOR are the logic bases (which compose a whole layer",
        "and take no supplementals):",
        "",
    ]
    for relation in BaseRelation:
        letter, meaning = _RELATION_MEANING[relation]
        label_text = _RELATION_LABEL[relation]
        lines.append(
            f"- **{label_text}** (`{relation.name}`, letter `{letter}`) -- {meaning}"
        )

    lines += [
        "",
        "### Base direction",
        "",
        "The **Base direction** dropdown sets which way the relation repeats. The",
        "digit (1-5) is the second character of a Structure-code segment. Shape",
        "repetition excludes the corner-out direction (digit 5):",
        "",
    ]
    for direction in Direction:
        label_text = _DIRECTION_LABEL[direction]
        meaning = _DIRECTION_MEANING[direction]
        lines.append(
            f"- **{label_text}** (`{direction.name}`, digit `{direction.value}`)"
            f" -- {meaning}."
        )

    lines += [
        "",
        "### Supplemental relations",
        "",
        "Each layer has three **Supplemental** slots (`Supplemental 1`/`2`/`3`), each",
        "with its own direction dropdown. A slot set to *Disabled* is dropped. The",
        "enabled choices add a transform on top of the base relation:",
        "",
    ]
    for supplemental in Supplemental:
        letter, meaning = _SUPPLEMENTAL_MEANING[supplemental]
        label_text = _SUPPLEMENTAL_LABEL[supplemental]
        lines.append(
            f"- **{label_text}** (`{supplemental.name}`, letter `{letter}`)"
            f" -- {meaning}"
        )

    lines += [
        "",
        "### Correct-answer position",
        "",
        "**Correct-answer position** places the correct tile among the eight answer",
        "choices (1-8, reading left to right, top to bottom).",
        "",
        "### Seed",
        "",
        "**Seed** fixes the random draw, so the same seed reproduces the same puzzle.",
        "**New seed** draws a fresh random seed for a new realisation of the same",
        "relations.",
    ]
    return "\n".join(lines)


def build_outcome(
    *,
    mode: str,
    gathered_layers: list[LayerControls],
    position: int,
    code: str,
    seed: int,
) -> BuildOutcome:
    """Build a matrix from the gathered controls (or a code) into a ``BuildOutcome``.

    For ``mode == "Build from controls"`` this maps the controls via
    ``config_from_controls`` then ``build``; otherwise it parses+builds the
    Structure ``code`` via ``build_from_code``. Any option set the upstream surface
    could not produce (a logic base with supplementals, >3 supplementals, a
    position outside 1-8) or a malformed code raises ``ValueError`` in the core;
    it is caught here and returned as ``error`` rather than surfaced as a traceback.

    Pure: ``seed`` is supplied by the caller (the shell), so this is deterministic
    and side-effect free.
    """
    try:
        if mode == "Build from controls":
            config = config_from_controls(gathered_layers, position)
            matrix = build(config, seed)
        else:
            matrix = build_from_code(code, seed)
    except ValueError as exc:
        return BuildOutcome(matrix=None, error=str(exc), structure_code=None)
    return BuildOutcome(matrix=matrix, error=None, structure_code=label(matrix))


# ---------------------------------------------------------------------------
# Save composition (N3): problem / answers / both, with an optional header band
# ---------------------------------------------------------------------------
#
# SVG is the canonical save format (raster-free, so a save works whether or not
# the optional ``raster`` extra is installed). ``compose_save_svg`` reuses the
# existing ``render_matrix_svg`` / ``render_answers_svg`` output verbatim and
# stacks the requested pieces vertically inside one outer ``<svg>``, with an
# optional header text band. It is PURE -- no ``label()``, no seed draw, no I/O:
# the shell decides which header fields to include (it computes the code, the
# position, the seed) and passes only the toggled ones.

# A rendered sheet opens with ``<svg ...>`` and closes with ``</svg>``; the
# opening tag is matched first, then width/height are extracted independently
# so attribute order does not matter (the SVG spec makes order arbitrary).
_SVG_TAG_RE = re.compile(r"^<svg\b[^>]*>")
_SVG_WIDTH_RE = re.compile(r'\bwidth="(\d+)"')
_SVG_HEIGHT_RE = re.compile(r'\bheight="(\d+)"')

# Header band geometry (only emitted when header_fields is non-empty).
_HEADER_HEIGHT = 28
_HEADER_PAD_X = 8
_HEADER_TEXT_Y = 19
_HEADER_FONT_SIZE = 14


def _svg_parts(rendered: str) -> tuple[int, int, str]:
    """Split a rendered ``<svg>`` into ``(width, height, inner_body)``.

    ``inner_body`` is everything between the opening ``<svg ...>`` tag and the
    closing ``</svg>`` -- the background rect and the cell groups -- ready to drop
    inside a translated ``<g>``.

    Width and height are extracted independently (order-agnostic): the SVG spec
    does not mandate attribute order, so two separate searches are used rather
    than a single ordered pattern.
    """
    tag_match = _SVG_TAG_RE.match(rendered)
    if tag_match is None:  # pragma: no cover - guards a render contract change
        raise ValueError("rendered SVG did not start with a parseable <svg> tag")
    open_tag = tag_match.group(0)
    w_match = _SVG_WIDTH_RE.search(open_tag)
    h_match = _SVG_HEIGHT_RE.search(open_tag)
    if w_match is None or h_match is None:  # pragma: no cover - render contract
        raise ValueError("rendered SVG did not start with a parseable <svg> tag")
    width = int(w_match.group(1))
    height = int(h_match.group(1))
    # exactly one </svg> per rendered document (no nested <svg>); rindex is unambiguous
    inner = rendered[tag_match.end() : rendered.rindex("</svg>")]
    return width, height, inner


def _header_band(header_fields: Mapping[str, object], width: int) -> str:
    """A header ``<g>`` (background + one ``<text>``) listing the given fields.

    Renders exactly the supplied ``key: value`` pairs, in iteration order, joined
    on one line. Keys and values are XML-escaped, so arbitrary text is safe inside
    the ``<text>`` element. The band is ``_HEADER_HEIGHT`` tall and as wide as the
    composition; callers only invoke it when ``header_fields`` is non-empty.
    """
    summary = "   ".join(f"{key}: {value}" for key, value in header_fields.items())
    text = escape(summary)
    return (
        f'<g class="header">'
        f'<rect x="0" y="0" width="{width}" height="{_HEADER_HEIGHT}" '
        f'fill="white"/>'
        f'<text x="{_HEADER_PAD_X}" y="{_HEADER_TEXT_Y}" '
        f'font-family="sans-serif" font-size="{_HEADER_FONT_SIZE}" '
        f'fill="black">{text}</text>'
        f"</g>"
    )


def compose_save_svg(
    matrix: Matrix,
    *,
    include_problem: bool,
    include_answers: bool,
    header_fields: Mapping[str, object],
) -> str:
    """Compose a single saveable ``<svg>`` from the chosen pieces of ``matrix``.

    Stacks the requested sheets vertically: the problem (``render_matrix_svg``)
    and/or the answer sheet (``render_answers_svg``). At least one of
    ``include_problem`` / ``include_answers`` must be true (``ValueError`` if
    neither). When ``header_fields`` is non-empty a header band listing exactly
    those ``key: value`` pairs is prepended; when empty there is NO header.

    The outer ``<svg>`` width is the widest piece and its height the sum of the
    stacked pieces (plus the header). Each piece is reused verbatim inside a
    ``<g transform="translate(0 y)">``, so the geometry is unchanged. PURE: no I/O,
    no ``label()`` -- the caller passes the header fields it wants shown.
    """
    if not include_problem and not include_answers:
        raise ValueError("compose_save_svg needs at least one of problem or answers")

    pieces: list[tuple[int, int, str]] = []
    if include_problem:
        pieces.append(_svg_parts(render_matrix_svg(matrix)))
    if include_answers:
        pieces.append(_svg_parts(render_answers_svg(matrix)))

    total_width = max(width for width, _height, _inner in pieces)

    body: list[str] = []
    y_offset = 0
    if header_fields:
        body.append(_header_band(header_fields, total_width))
        y_offset = _HEADER_HEIGHT

    for _width, height, inner in pieces:
        body.append(f'<g transform="translate(0 {y_offset})">{inner}</g>')
        y_offset += height

    total_height = y_offset
    return (
        f'<svg xmlns="{_SVG_NS}" width="{total_width}" height="{total_height}" '
        f'viewBox="0 0 {total_width} {total_height}">'
        f"{''.join(body)}"
        f"</svg>"
    )
