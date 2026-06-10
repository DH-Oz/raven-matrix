"""The researcher-facing marimo reactive panel (Phase 7, Task 2).

# pattern: Imperative Shell

A faithful, live-reactive mirror of the upstream Swing ``SGMBuilderFrame``:

- a mode toggle ("Build from controls" vs "Build from code");
- controls mode -- layer count (1/2); per active layer a base relation dropdown
  {ShapeRep, OR, AND, XOR} + a base direction dropdown {H, V, DiagTL, DiagBL,
  CornerOut} + three fixed supplemental slots (each {Disabled, Scaling, Rotation,
  FillRep, ChangeFill, Numerosity} + a direction dropdown); a correct-answer
  position (1-8); a seed number + a "new seed" button (layer-2 controls show only
  when the layer count is 2);
- code mode -- a Structure-code text field (e.g. ``A1B2C4``) + a seed;
- output -- the problem and answer-sheet SVGs inline (``mo.Html``), plus the
  resulting Structure code (``label``) and the configured correct-answer position.

This is a thin EDGE layer (FCIS). It gathers the control values, then defers every
decision to the pure core: ``config_from_controls`` / ``build_from_code`` /
``build`` / ``label`` / ``render_*_svg``. The core never imports this module. Build
and parse errors (``ValueError``) are caught in the build cell and shown as a
friendly message rather than a raw traceback.
"""

import marimo

app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    from raven_matrix.builder import build, build_from_code
    from raven_matrix.label import label
    from raven_matrix.model import BaseRelation, Direction, Supplemental
    from raven_matrix.render.svg import render_answers_svg, render_matrix_svg
    from raven_matrix.ui_config import LayerControls, config_from_controls

    return (
        BaseRelation,
        Direction,
        LayerControls,
        Supplemental,
        build,
        build_from_code,
        config_from_controls,
        label,
        mo,
        render_answers_svg,
        render_matrix_svg,
    )


@app.cell
def _option_maps(BaseRelation, Direction, Supplemental):
    # Option label -> enum maps, mirroring the GUI's fixed pick lists. The
    # "Disabled" supplemental slot maps to None so the edge layer can drop it
    # before constructing LayerControls.
    RELATION_OPTIONS = {
        "ShapeRep": BaseRelation.SHAPE_REPETITION,
        "OR": BaseRelation.LOGICAL_OR,
        "AND": BaseRelation.LOGICAL_AND,
        "XOR": BaseRelation.LOGICAL_XOR,
    }
    DIRECTION_OPTIONS = {
        "H": Direction.HORIZONTAL,
        "V": Direction.VERTICAL,
        "DiagTL": Direction.DIAGONAL_TL_BR,
        "DiagBL": Direction.DIAGONAL_BL_TR,
        "CornerOut": Direction.TOP_LEFT_CORNER_OUT,
    }
    SUPPLEMENTAL_OPTIONS = {
        "Disabled": None,
        "Scaling": Supplemental.SCALING,
        "Rotation": Supplemental.ROTATION,
        "FillRep": Supplemental.FILL_REPETITION,
        "ChangeFill": Supplemental.CHANGE_FILL,
        "Numerosity": Supplemental.NUMEROSITY,
    }
    return DIRECTION_OPTIONS, RELATION_OPTIONS, SUPPLEMENTAL_OPTIONS


@app.cell
def _mode_and_seed(mo):
    # The mode toggle and the seed controls are shared by both modes. The "new
    # seed" run button bumps the seed (read reactively in the build cell).
    mode = mo.ui.dropdown(
        options=["Build from controls", "Build from code"],
        value="Build from controls",
        label="Mode",
    )
    seed = mo.ui.number(start=0, stop=2**31 - 1, step=1, value=0, label="Seed")
    new_seed_button = mo.ui.run_button(label="New seed")
    return mode, new_seed_button, seed


@app.cell
def _layer_count(mo):
    layer_count = mo.ui.dropdown(
        options={"1": 1, "2": 2}, value="1", label="Layers"
    )
    return (layer_count,)


@app.cell
def _layer_factory(DIRECTION_OPTIONS, RELATION_OPTIONS, SUPPLEMENTAL_OPTIONS, mo):
    def make_layer_controls(index: int):
        """Build one layer's control column: base + 3 supplemental slots.

        Returns an ``mo.ui.dictionary`` so the whole column reads back through a
        single ``.value``. Each supplemental slot is itself a (type, direction)
        pair, mirroring the GUI's three fixed rows.
        """
        return mo.ui.dictionary(
            {
                "base": mo.ui.dropdown(
                    options=RELATION_OPTIONS,
                    value="ShapeRep",
                    label="Base relation",
                ),
                "base_direction": mo.ui.dropdown(
                    options=DIRECTION_OPTIONS,
                    value="H",
                    label="Base direction",
                ),
                **{
                    f"supp{slot}": mo.ui.dictionary(
                        {
                            "type": mo.ui.dropdown(
                                options=SUPPLEMENTAL_OPTIONS,
                                value="Disabled",
                                label=f"Supplemental {slot}",
                            ),
                            "direction": mo.ui.dropdown(
                                options=DIRECTION_OPTIONS,
                                value="H",
                                label=f"Direction {slot}",
                            ),
                        }
                    )
                    for slot in (1, 2, 3)
                },
            }
        )

    return (make_layer_controls,)


@app.cell
def _layer_controls(layer_count, make_layer_controls):
    # One control column per active layer. Layer 2 exists only when the layer
    # count is 2, so its controls render (below) only then.
    layer1 = make_layer_controls(1)
    layer2 = make_layer_controls(2) if layer_count.value == 2 else None
    return layer1, layer2


@app.cell
def _position(mo):
    position = mo.ui.number(
        start=1, stop=8, step=1, value=1, label="Correct-answer position"
    )
    return (position,)


@app.cell
def _code_controls(mo):
    code_text = mo.ui.text(value="A1", label="Structure code")
    return (code_text,)


@app.cell
def _render_controls(
    code_text,
    layer1,
    layer2,
    layer_count,
    mo,
    mode,
    new_seed_button,
    position,
    seed,
):
    # Show the panel for the active mode. Layer-2 controls appear only when the
    # layer count is 2 (layer2 is None otherwise).
    if mode.value == "Build from controls":
        layer_columns = [mo.vstack([mo.md("**Layer 1**"), layer1])]
        if layer2 is not None:
            layer_columns.append(mo.vstack([mo.md("**Layer 2**"), layer2]))
        controls_panel = mo.vstack(
            [
                layer_count,
                mo.hstack(layer_columns, justify="start", gap=2),
                position,
            ]
        )
    else:
        controls_panel = code_text

    panel = mo.vstack(
        [
            mode,
            controls_panel,
            mo.hstack([seed, new_seed_button], justify="start"),
        ]
    )
    # Explicit display (marimo renders the cell's output); a statement, not a bare
    # trailing expression, so it reads as intentional.
    mo.output.replace(panel)
    return


@app.cell
def _effective_seed(new_seed_button, seed):
    import secrets

    # The "new seed" button draws a fresh seed; otherwise the seed control wins.
    # Reading new_seed_button.value makes this cell re-run on each click.
    if new_seed_button.value:
        effective_seed = secrets.randbelow(2**31)
    else:
        effective_seed = int(seed.value)
    return (effective_seed,)


@app.cell
def _gather_layer_controls(LayerControls, layer1, layer2, layer_count):
    def to_layer_controls(column_value: dict) -> LayerControls:
        """Map one GUI column's read-back dict onto a ``LayerControls``.

        Drops every "Disabled" supplemental slot (its type maps to ``None``)
        before constructing the dataclass, matching the ``ui_config`` contract.
        """
        supplementals = [
            (slot["type"], slot["direction"])
            for key in ("supp1", "supp2", "supp3")
            for slot in (column_value[key],)
            if slot["type"] is not None
        ]
        return LayerControls(
            base=column_value["base"],
            base_direction=column_value["base_direction"],
            supplementals=supplementals,
        )

    columns = [layer1]
    if layer_count.value == 2 and layer2 is not None:
        columns.append(layer2)
    gathered_layers = [to_layer_controls(column.value) for column in columns]
    return (gathered_layers,)


@app.cell
def _build(
    build,
    build_from_code,
    code_text,
    config_from_controls,
    effective_seed,
    gathered_layers,
    label,
    mo,
    mode,
    position,
    render_answers_svg,
    render_matrix_svg,
):
    # PROCESS: defer to the pure core. Any option set the upstream surface could
    # not produce (a logic base with supplementals, >3 supplementals, a position
    # outside 1-8) or a malformed code raises ValueError; catch it and show a
    # friendly message instead of a traceback.
    matrix = None
    error: str | None = None
    try:
        if mode.value == "Build from controls":
            config = config_from_controls(gathered_layers, int(position.value))
            matrix = build(config, effective_seed)
        else:
            matrix = build_from_code(code_text.value, effective_seed)
    except ValueError as exc:
        error = str(exc)

    # Branch on `matrix` directly (not `error`) so the type narrows from
    # `Matrix | None` to `Matrix` in the success path -- `label`/`render_*` then
    # see a non-None matrix without a cast.
    if matrix is None:
        output = mo.md(f"**Could not build this matrix:** {error}")
    else:
        structure_code = label(matrix)
        output = mo.vstack(
            [
                mo.md(
                    f"**Structure code:** `{structure_code}`  ·  "
                    f"**Correct answer:** {matrix.correct_answer_position}  ·  "
                    f"**Seed:** {effective_seed}"
                ),
                mo.md("**Problem**"),
                mo.Html(render_matrix_svg(matrix)),
                mo.md("**Answers**"),
                mo.Html(render_answers_svg(matrix)),
            ]
        )
    # Explicit display (see the controls cell); a statement, not a bare expression.
    mo.output.replace(output)
    return


if __name__ == "__main__":
    app.run()
