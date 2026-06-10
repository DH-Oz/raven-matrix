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

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from raven_matrix.builder import build, build_from_code
from raven_matrix.label import label
from raven_matrix.model import BaseRelation, Direction, Matrix, Supplemental
from raven_matrix.ui_config import LayerControls, config_from_controls

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
