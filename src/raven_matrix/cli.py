"""The researcher-facing typer CLI (Phase 7, Task 1).

# pattern: Imperative Shell

Two commands:

- ``build`` -- generate a matrix from a Matzen ``Structure`` code (``--code``) OR
  explicit flags (``--relation``/``--direction``/``--supplemental``/``--layers``/
  ``--position``), at a given ``--seed``; write the problem (or ``--answers``
  sheet) as SVG to ``--out`` (or stdout), optionally rasterised to PNG via
  ``--png`` (the ``raster`` extra). The resulting Structure code is reported on
  stderr (the GUI "explanation" equivalent) so stdout stays a clean document.
- ``oracle`` -- look a code up in ``data/ravens_oracle.csv``, print its rows
  (``Stimulus Name``, ``Correct Answer``, ``% Correct``) and its round-trip
  status from the Phase-5 pass map.

This is a thin EDGE layer (FCIS): it parses flags, reads the CSV, then calls the
pure core (``config_from_controls`` / ``build_from_code`` / ``build`` / ``label``
/ ``build_pass_map``). All option->config mapping lives in ``ui_config``, shared
with the marimo app; the core never imports this module. Errors are written to
stderr and exit non-zero; primary output goes to stdout.
"""

from __future__ import annotations

import csv
import importlib.resources
import sys
from pathlib import Path
from typing import Annotated

import typer

from raven_matrix.builder import build as build_matrix
from raven_matrix.builder import build_from_code
from raven_matrix.label import label
from raven_matrix.model import BaseRelation, Direction, Supplemental
from raven_matrix.oracle import build_pass_map
from raven_matrix.render.svg import render_answers_svg, render_matrix_svg
from raven_matrix.ui_config import LayerControls, config_from_controls

app = typer.Typer(
    help="Generate Raven-style matrix puzzles (a Python port of Sandia's SGMT)."
)


def _oracle_csv_path() -> Path:
    """Return the path to the oracle CSV, working both installed and in a source tree.

    The CSV is shipped as package data in the wheel (pyproject force-include); in an
    editable/source checkout it lives at the repo-root data/ dir instead.
    """
    # Try the packaged copy first (wheel install); fall back to source tree.
    packaged = importlib.resources.files("raven_matrix") / "data" / "ravens_oracle.csv"
    if packaged.is_file():
        return Path(str(packaged))
    # Fall back to the source-tree location (repo root / data/).
    return Path(__file__).resolve().parents[2] / "data" / "ravens_oracle.csv"


def _parse_relation(name: str) -> BaseRelation:
    """Map a ``--relation`` value (a lowercase ``BaseRelation`` name) to its enum."""
    try:
        return BaseRelation[name.upper()]
    except KeyError as exc:
        valid = ", ".join(member.name.lower() for member in BaseRelation)
        raise typer.BadParameter(
            f"unknown relation {name!r}; choose one of: {valid}"
        ) from exc


def _parse_direction(name: str) -> Direction:
    """Map a ``--direction`` value (a lowercase ``Direction`` name) to its enum."""
    try:
        return Direction[name.upper()]
    except KeyError as exc:
        valid = ", ".join(member.name.lower() for member in Direction)
        raise typer.BadParameter(
            f"unknown direction {name!r}; choose one of: {valid}"
        ) from exc


def _parse_supplemental(spec: str) -> tuple[Supplemental, Direction]:
    """Parse one ``--supplemental`` spec ``TYPE:DIR`` into (Supplemental, Direction).

    ``TYPE`` is a lowercase ``Supplemental`` name, ``DIR`` a lowercase ``Direction``
    name, e.g. ``rotation:vertical``. A missing colon or unknown member raises
    ``typer.BadParameter`` (exit code 2).
    """
    if ":" not in spec:
        raise typer.BadParameter(
            f"supplemental {spec!r} must be 'TYPE:DIR' (e.g. rotation:vertical)"
        )
    type_name, _, dir_name = spec.partition(":")
    try:
        supplemental = Supplemental[type_name.upper()]
    except KeyError as exc:
        valid = ", ".join(member.name.lower() for member in Supplemental)
        raise typer.BadParameter(
            f"unknown supplemental type {type_name!r}; choose one of: {valid}"
        ) from exc
    return supplemental, _parse_direction(dir_name)


@app.command()
def build(
    code: Annotated[
        str | None,
        typer.Option(
            "--code",
            help="A Matzen Structure code (e.g. A1B2). "
            "Mutually exclusive with the explicit relation flags.",
        ),
    ] = None,
    relation: Annotated[
        str,
        typer.Option(
            "--relation",
            help="Base relation for the single explicit "
            "layer: shape_repetition, logical_or, logical_and, logical_xor.",
        ),
    ] = "shape_repetition",
    direction: Annotated[
        str,
        typer.Option(
            "--direction",
            help="Base direction: horizontal, vertical, "
            "diagonal_bl_tr, diagonal_tl_br, top_left_corner_out.",
        ),
    ] = "horizontal",
    supplemental: Annotated[
        list[str] | None,
        typer.Option(
            "--supplemental",
            help="A supplemental as TYPE:DIR "
            "(e.g. rotation:vertical). Repeatable, up to 3.",
        ),
    ] = None,
    layers: Annotated[
        int,
        typer.Option(
            "--layers",
            help="Repeat the same relation across N identical "
            "layers (1 or 2). Ignored when --code is given.",
        ),
    ] = 1,
    position: Annotated[
        int,
        typer.Option("--position", help="The 1-based correct-answer position (1-8)."),
    ] = 1,
    seed: Annotated[
        int,
        typer.Option("--seed", help="The java.util.Random seed (determinism)."),
    ] = 0,
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Write to this path instead of stdout."),
    ] = None,
    answers: Annotated[
        bool,
        typer.Option(
            "--answers/--no-answers",
            help="Render the 8-choice answer sheet instead of the problem matrix.",
        ),
    ] = False,
    png: Annotated[
        bool,
        typer.Option(
            "--png",
            help="Rasterise the SVG to PNG (needs the 'raster' "
            "extra). Implies binary --out or binary stdout.",
        ),
    ] = False,
) -> None:
    """Generate a matrix from a Structure code or explicit relation flags."""
    # GATHER + map to a validated config via the pure core.
    try:
        if code is not None:
            matrix = build_from_code(code, seed)
        else:
            base = _parse_relation(relation)
            base_direction = _parse_direction(direction)
            supplementals = [_parse_supplemental(s) for s in (supplemental or [])]
            layer_controls = LayerControls(
                base=base,
                base_direction=base_direction,
                supplementals=supplementals,
            )
            config = config_from_controls([layer_controls] * layers, position)
            matrix = build_matrix(config, seed)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    svg = render_answers_svg(matrix) if answers else render_matrix_svg(matrix)

    # PERSIST. Report the resulting Structure code on stderr (the GUI explanation),
    # keeping stdout a clean document.
    structure_code = label(matrix)
    typer.echo(f"Structure: {structure_code}", err=True)

    if png:
        payload = _rasterise_or_exit(svg)
        _write_bytes(payload, out)
    else:
        _write_text(svg, out)


def _rasterise_or_exit(svg: str) -> bytes:
    """Rasterise to PNG, exiting with a clear hint if the ``raster`` extra is absent."""
    try:
        from raven_matrix.render.raster import rasterise
    except ImportError as exc:  # the raster module itself failed to import
        typer.echo(
            "error: --png needs the 'raster' extra: uv sync --extra raster",
            err=True,
        )
        raise typer.Exit(code=1) from exc
    try:
        return rasterise(svg)
    except ImportError as exc:  # resvg_py absent (extra not installed)
        typer.echo(
            "error: --png needs the 'raster' extra: uv sync --extra raster",
            err=True,
        )
        raise typer.Exit(code=1) from exc


def _write_text(content: str, out: Path | None) -> None:
    if out is None:
        sys.stdout.write(content)
    else:
        out.write_text(content, encoding="utf-8")


def _write_bytes(content: bytes, out: Path | None) -> None:
    if out is None:
        sys.stdout.buffer.write(content)
    else:
        out.write_bytes(content)


@app.command()
def oracle(
    code: Annotated[
        str,
        typer.Option("--code", help="A Structure code to look up in the oracle CSV."),
    ],
) -> None:
    """Print the oracle rows for a Structure code and its round-trip status."""
    # GATHER the CSV rows.
    csv_path = _oracle_csv_path()
    try:
        handle = csv_path.open(encoding="utf-8", newline="")
    except FileNotFoundError as exc:
        typer.echo(
            f"error: oracle data not found at {csv_path}; "
            "regenerate it with: uv run python tools/extract_oracle.py",
            err=True,
        )
        raise typer.Exit(code=1) from exc
    with handle:
        rows = list(csv.DictReader(handle))

    matching = [row for row in rows if row["Structure"] == code]
    if not matching:
        typer.echo(f"error: code {code!r} not found in the oracle", err=True)
        raise typer.Exit(code=1)

    # PROCESS: the pure round-trip sweep over the CSV's distinct codes.
    pass_map = build_pass_map(rows)
    result = pass_map[code]
    status = (
        f"PASS ({result.mode})"
        if result.passed
        else f"FAIL ({result.mode}): {result.reason}"
    )

    # PERSIST: print the per-stimulus rows then the round-trip status.
    typer.echo(f"Structure {code}: round-trip {status}")
    typer.echo("Stimulus Name\tCorrect Answer\t% Correct in Norming Study")
    for row in matching:
        typer.echo(
            f"{row['Stimulus Name']}\t{row['Correct Answer']}\t"
            f"{row['% Correct in Norming Study']}"
        )
