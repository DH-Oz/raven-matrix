"""The researcher-facing marimo reactive panel (Phase 7, Tasks 2 + 3/N1).

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

The final cell lays the controls and the live render side by side
(``mo.hstack([controls, output])``) so they sit adjacent in ``marimo edit``.

This is a thin EDGE layer (FCIS). It defines the UI elements (marimo needs them in
cells to track ``.value`` reactively), then defers every decision to the pure
``raven_matrix.appsupport`` seam: ``layer_controls_from_column`` and
``build_outcome`` (which themselves call ``config_from_controls`` /
``build_from_code`` / ``build`` / ``label``). The core never imports this module.
Build and parse errors (``ValueError``) are turned into a friendly message inside
``build_outcome`` and rendered as text rather than a raw traceback.
"""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    from raven_matrix.appsupport import (
        DIRECTION_OPTIONS,
        RELATION_OPTIONS,
        SUPPLEMENTAL_OPTIONS,
        build_outcome,
        compose_save_svg,
        layer_controls_from_column,
        option_reference,
    )
    from raven_matrix.render.svg import render_answers_svg, render_matrix_svg

    return (
        DIRECTION_OPTIONS,
        RELATION_OPTIONS,
        SUPPLEMENTAL_OPTIONS,
        build_outcome,
        compose_save_svg,
        layer_controls_from_column,
        mo,
        option_reference,
        render_answers_svg,
        render_matrix_svg,
    )


@app.cell
def _controls(mo):
    # The mode/seed/layer-count/position/code UI elements. These are defined here
    # so marimo tracks their `.value` reactively; the cells BELOW read those values
    # (a marimo cell may not both create an element and read its `.value`). The
    # "new seed" run button bumps the seed (read in `_effective_seed`).
    mode = mo.ui.dropdown(
        options=["Build from controls", "Build from code"],
        value="Build from controls",
        label="Mode",
    )
    seed = mo.ui.number(start=0, stop=2**31 - 1, step=1, value=0, label="Seed")
    new_seed_button = mo.ui.run_button(label="New seed")
    layer_count = mo.ui.dropdown(
        options={"1": 1, "2": 2}, value="1", label="Layers"
    )
    position = mo.ui.number(
        start=1, stop=8, step=1, value=1, label="Correct-answer position"
    )
    code_text = mo.ui.text(value="A1", label="Structure code")
    # Header toggles for the saved SVG: which fields the optional header band
    # lists. Read in `_build` to assemble header_fields for compose_save_svg.
    header_code = mo.ui.checkbox(value=True, label="Structure code")
    header_answer = mo.ui.checkbox(value=True, label="Correct answer")
    header_seed = mo.ui.checkbox(value=True, label="Seed")
    return (
        code_text,
        header_answer,
        header_code,
        header_seed,
        layer_count,
        mode,
        new_seed_button,
        position,
        seed,
    )


@app.cell
def _layer_factory(
    DIRECTION_OPTIONS,
    RELATION_OPTIONS,
    SUPPLEMENTAL_OPTIONS,
    mo,
):
    def make_layer_controls(slot: int):
        """Build one layer's control column: base + 3 supplemental slots.

        Returns an ``mo.ui.dictionary`` so the whole column reads back through a
        single ``.value``. Each supplemental slot is itself a (type, direction)
        pair, mirroring the GUI's three fixed rows. The dropdown ``options`` are
        the appsupport label->enum maps, so each slot's read-back value is already
        the enum (or ``None`` for "Disabled").
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
                    f"supp{index}": mo.ui.dictionary(
                        {
                            "type": mo.ui.dropdown(
                                options=SUPPLEMENTAL_OPTIONS,
                                value="Disabled",
                                label=f"Supplemental {index}",
                            ),
                            "direction": mo.ui.dropdown(
                                options=DIRECTION_OPTIONS,
                                value="H",
                                label=f"Direction {index}",
                            ),
                        }
                    )
                    for index in (1, 2, 3)
                },
            }
        )

    return (make_layer_controls,)


@app.cell
def _layer_controls(layer_count, make_layer_controls):
    # One control column per active layer. Layer 2 exists only when the layer
    # count is 2, so its controls render (in the panel below) only then.
    layer1 = make_layer_controls(1)
    layer2 = make_layer_controls(2) if layer_count.value == 2 else None
    return layer1, layer2


@app.cell
def _controls_panel(
    code_text,
    layer1,
    layer2,
    layer_count,
    mo,
    mode,
    new_seed_button,
    option_reference,
    position,
    seed,
):
    # Assemble the active mode's control panel. Layer-2 controls appear only when
    # the layer count is 2 (layer2 is None otherwise).
    if mode.value == "Build from controls":
        layer_columns = [mo.vstack([mo.md("**Layer 1**"), layer1])]
        if layer2 is not None:
            layer_columns.append(mo.vstack([mo.md("**Layer 2**"), layer2]))
        mode_panel = mo.vstack(
            [
                layer_count,
                mo.hstack(layer_columns, justify="start", gap=2),
                position,
            ]
        )
    else:
        mode_panel = code_text

    # The in-app reference for every control and option, sourced from appsupport
    # (the completeness test guards it against drift). It sits in a collapsed
    # accordion so it is on hand without crowding the controls.
    reference = mo.accordion({"Option reference": mo.md(option_reference())})

    controls_panel = mo.vstack(
        [
            mode,
            mode_panel,
            mo.hstack([seed, new_seed_button], justify="start"),
            reference,
        ]
    )
    return (controls_panel,)


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
def _gather_layer_controls(layer1, layer2, layer_count, layer_controls_from_column):
    # GATHER: read each active column's `.value` and map it (via the pure
    # appsupport seam) to a LayerControls, dropping any "Disabled" supplemental.
    columns = [layer1]
    if layer_count.value == 2 and layer2 is not None:
        columns.append(layer2)
    gathered_layers = [
        layer_controls_from_column(column.value) for column in columns
    ]
    return (gathered_layers,)


@app.cell
def _build(
    build_outcome,
    code_text,
    effective_seed,
    gathered_layers,
    mo,
    mode,
    position,
    render_answers_svg,
    render_matrix_svg,
):
    # PROCESS: defer to the pure core via build_outcome, which catches every
    # ValueError (a logic base with supplementals, >3 supplementals, a position
    # outside 1-8, a malformed code) and returns a friendly error instead of a
    # traceback. Render the BuildOutcome: friendly message when matrix is None,
    # else the structure code + both SVGs.
    outcome = build_outcome(
        mode=mode.value,
        gathered_layers=gathered_layers,
        position=int(position.value),
        code=code_text.value,
        seed=effective_seed,
    )

    if outcome.matrix is None:
        output = mo.md(f"**Could not build this matrix:** {outcome.error}")
    else:
        output = mo.vstack(
            [
                mo.md(
                    f"**Structure code:** `{outcome.structure_code}`  ·  "
                    f"**Correct answer:** "
                    f"{outcome.matrix.correct_answer_position}  ·  "
                    f"**Seed:** {effective_seed}"
                ),
                mo.md("**Problem**"),
                mo.Html(render_matrix_svg(outcome.matrix)),
                mo.md("**Answers**"),
                mo.Html(render_answers_svg(outcome.matrix)),
            ]
        )
    return outcome, output


@app.cell
def _save(
    compose_save_svg,
    effective_seed,
    header_answer,
    header_code,
    header_seed,
    mo,
    outcome,
):
    # SAVE: three SVG download buttons (problem · answers · both). Only offered
    # when the build succeeded -- a failed build has no matrix to save. The shell
    # computes the header fields (code, correct answer, seed) and passes only the
    # toggled ones to the pure compose_save_svg; an empty mapping -> no header band.
    if outcome.matrix is None:
        save_panel = mo.md("_Save is available once a matrix builds._")
    else:
        header_fields: dict[str, object] = {}
        if header_code.value and outcome.structure_code is not None:
            header_fields["code"] = outcome.structure_code
        if header_answer.value:
            header_fields["correct answer"] = outcome.matrix.correct_answer_position
        if header_seed.value:
            header_fields["seed"] = effective_seed

        stem = outcome.structure_code or "matrix"

        def _svg(*, include_problem: bool, include_answers: bool) -> str:
            return compose_save_svg(
                outcome.matrix,
                include_problem=include_problem,
                include_answers=include_answers,
                header_fields=header_fields,
            )

        save_panel = mo.vstack(
            [
                mo.md("**Save (SVG)**"),
                mo.hstack(
                    [header_code, header_answer, header_seed], justify="start"
                ),
                mo.hstack(
                    [
                        mo.download(
                            data=_svg(include_problem=True, include_answers=False),
                            filename=f"raven_{stem}_problem.svg",
                            mimetype="image/svg+xml",
                            label="Save problem",
                        ),
                        mo.download(
                            data=_svg(include_problem=False, include_answers=True),
                            filename=f"raven_{stem}_answers.svg",
                            mimetype="image/svg+xml",
                            label="Save answers",
                        ),
                        mo.download(
                            data=_svg(include_problem=True, include_answers=True),
                            filename=f"raven_{stem}_problem_answers.svg",
                            mimetype="image/svg+xml",
                            label="Save problem + answers",
                        ),
                    ],
                    justify="start",
                ),
            ]
        )
    return (save_panel,)


@app.cell
def _layout(controls_panel, mo, output, save_panel):
    # Controls on the left, the live render on the right, so a control change and
    # its effect sit side by side in `marimo edit`. The save panel sits under the
    # render (it depends on the built matrix).
    mo.output.replace(
        mo.hstack(
            [controls_panel, mo.vstack([output, save_panel])],
            justify="start",
            gap=2,
        )
    )
    return


if __name__ == "__main__":
    app.run()
