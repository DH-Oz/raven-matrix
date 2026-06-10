"""The pure option->config seam shared by the CLI and the marimo app (Phase 7).

# pattern: Functional Core

``config_from_controls`` maps the ``SGMBuilderFrame``-style option choices onto a
validated ``BuilderConfig``. It is the single source of truth for the
option->config mapping, so the CLI (``cli.py``) and the marimo app (``app.py``)
stay thin edge layers (FCIS): each gathers control values, calls this helper, and
renders the result. The helper is PURE -- no I/O, no typer/marimo imports -- and
reuses the Phase-4 ``validate_config``, so invalid option sets (a logic base with
supplementals, >3 supplementals, a position outside 1-8, 0 layers) raise
``ValueError`` here rather than deep inside ``build``.

``LayerControls`` mirrors one column of the GUI: a base relation + its direction
and a list of (supplemental, direction) pairs. The GUI's three fixed supplemental
slots include a "Disabled" choice; the edge layer filters those out before
constructing ``LayerControls``, so the list here holds only the ENABLED
supplementals (each already a real ``Supplemental`` + ``Direction``).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from raven_matrix.builder import BuilderConfig, LayerConfig, validate_config
from raven_matrix.model import BaseRelation, Direction, Supplemental


@dataclass(frozen=True, slots=True)
class LayerControls:
    """The option choices for one layer (the GUI's per-layer control column).

    ``supplementals`` holds only the ENABLED supplemental slots as
    (supplemental, direction) pairs; the edge layer drops any "Disabled" slot
    before building this. All fields are parsed ENUMS, never raw digits, matching
    the ``LayerConfig`` boundary contract.
    """

    base: BaseRelation
    base_direction: Direction
    supplementals: list[tuple[Supplemental, Direction]] = field(default_factory=list)


def config_from_controls(
    layers: list[LayerControls], correct_answer_position: int
) -> BuilderConfig:
    """Map GUI-style option choices onto a validated ``BuilderConfig``.

    Pure mapping: each ``LayerControls`` becomes a ``LayerConfig`` (supplementals
    converted from a list to the immutable tuple ``LayerConfig`` expects), then the
    whole config is run through the Phase-4 ``validate_config``. Any option set the
    upstream surface could not produce (0 or >2 layers, >3 supplementals in a
    layer, a logic base carrying supplementals, or a position outside 1-8) raises
    ``ValueError``.

    Parameters
    ----------
    layers:
        One ``LayerControls`` per active layer (1 or 2).
    correct_answer_position:
        The 1-based correct-answer position (1-8).

    Returns
    -------
    BuilderConfig
        The validated config, ready for ``build``.
    """
    layer_configs = tuple(
        LayerConfig(
            base=controls.base,
            base_direction=controls.base_direction,
            supplementals=tuple(controls.supplementals),
        )
        for controls in layers
    )
    config = BuilderConfig(
        layers=layer_configs,
        correct_answer_position=correct_answer_position,
    )
    validate_config(config)
    return config
