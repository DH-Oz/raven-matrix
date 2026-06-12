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

A visible "How to use this notebook" cell sits first (a short usage preamble plus
the full ``option_reference()``), then the controls, then a final cell laying the
controls and the live render side by side (``mo.hstack([controls, output])``) so
they sit adjacent in ``marimo edit``. Every cell is ``hide_code=True`` so
``marimo edit`` shows the rendered outputs rather than the source -- the reactive
graph is unchanged (``hide_code`` is purely presentational).

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


@app.cell(hide_code=True)
async def _wasm_bootstrap():
    # WASM bootstrap (Phase 8). In the Pyodide/marimo-WASM runtime the
    # `raven_matrix` wheel is NOT preinstalled, so micropip fetches the pure wheel
    # bundled next to index.html. This is a no-op locally (raven_matrix is already
    # importable and we are not under Pyodide). `bootstrapped` (no leading
    # underscore, so it is shared across cells) is consumed by `_imports` to force
    # this cell to run FIRST -- marimo orders by data dependency, not file order.
    import sys

    if "pyodide" in sys.modules:
        # micropip is Pyodide-provided (no local stub); the targeted ignore is for a
        # real platform module the type-checker's environment can't have.
        import micropip  # ty: ignore[unresolved-import]

        await micropip.install("raven_matrix-0.1.0-py3-none-any.whl")
    bootstrapped = True
    return (bootstrapped,)


@app.cell(hide_code=True)
def _imports(bootstrapped):
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


@app.cell(hide_code=True)
def _intro(mo, option_reference):
    # FIRST visible cell: how to use this notebook. A short usage preamble (the two
    # modes, the live render, the seed + "New seed" button, the save buttons + the
    # three header toggles) followed by the full in-app option reference. The
    # reference text is NOT duplicated here -- it is `option_reference()` from the
    # pure appsupport seam (guarded against drift by the completeness test), called
    # so every control/option meaning lands on the page. This cell's CODE is hidden
    # (`hide_code=True`); its rendered markdown shows, so the guide is always
    # visible above the controls (no accordion to expand).
    usage_preamble = "\n".join(
        [
            "# How to use this notebook",
            "",
            "This panel builds Raven-style progressive-matrix puzzles. The render",
            "below updates **live** as you change any control -- there is no run",
            "button.",
            "",
            "## Two ways to build",
            "",
            "- **Build from controls** -- pick the relations, directions, and",
            "  supplementals by hand (the faithful control panel).",
            "- **Build from code** -- switch the **Mode** dropdown to *Build from",
            "  code* and type a Structure code (e.g. `A1B2C4`) into the",
            "  **Structure code** field.",
            "",
            "## Seed",
            "",
            "The **Seed** number fixes the random draw, so the same seed reproduces",
            "the same puzzle. Click **New seed** to draw a fresh one for a new",
            "realisation of the same relations.",
            "",
            "## Saving",
            "",
            "Once a matrix builds, **Save** buttons download the problem, the",
            "answers, or both, as SVG or PNG. A quiet row of toggles below them",
            "chooses which fields appear in BOTH a subtle readout under the live",
            "render and an optional header band on the saved file (**Structure",
            "code**, **Correct answer**, **Seed**). **Correct answer** is off by",
            "default, so neither the screen nor a printed problem reveals it.",
            "",
            "The full option reference follows.",
        ]
    )
    mo.md(usage_preamble + "\n\n" + option_reference())
    return


@app.cell(hide_code=True)
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
    layer_count = mo.ui.dropdown(options={"1": 1, "2": 2}, value="1", label="Layers")
    position = mo.ui.number(
        start=1, stop=8, step=1, value=1, label="Correct-answer position"
    )
    code_text = mo.ui.text(value="A1", label="Structure code")
    # Header toggles: which fields appear in BOTH the on-screen readout (under the
    # live render, `_build`) and the optional header band on saved files (`_save`).
    header_code = mo.ui.checkbox(value=True, label="Structure code")
    # Default OFF: a printed problem must not reveal its own answer (the
    # test-taking ergonomic). Code/Seed stay on -- they aid filing, not cheating.
    header_answer = mo.ui.checkbox(value=False, label="Correct answer")
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


@app.cell(hide_code=True)
def _layer_controls(
    DIRECTION_OPTIONS,
    RELATION_OPTIONS,
    SUPPLEMENTAL_OPTIONS,
    layer_count,
    mo,
):
    # The layer-column factory lives here with its single caller (it is used
    # nowhere else, and CREATES the UI elements -- it reads no `.value`, so this is
    # safe in the same cell as the calls below).
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

    # One control column per active layer. Layer 2 exists only when the layer
    # count is 2, so its controls render (in the panel below) only then.
    layer1 = make_layer_controls(1)
    layer2 = make_layer_controls(2) if layer_count.value == 2 else None
    return layer1, layer2


@app.cell(hide_code=True)
def _controls_panel(
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
    # Assemble the active mode's control panel. Layer-2 controls appear only when
    # the layer count is 2 (layer2 is None otherwise). The option reference now
    # lives in the visible intro cell at the top, so it is no longer attached here.
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

    controls_panel = mo.vstack(
        [
            mode,
            mode_panel,
            mo.hstack([seed, new_seed_button], justify="start"),
        ]
    )
    return (controls_panel,)


@app.cell(hide_code=True)
def _read_back(
    layer1,
    layer2,
    layer_count,
    layer_controls_from_column,
    new_seed_button,
    seed,
):
    import secrets

    # GATHER (read-back only -- this cell creates no UI elements, so reading every
    # `.value` here is safe). Two reads feed the build:
    #
    # 1. The effective seed: the "new seed" button draws a fresh one; otherwise the
    #    seed control wins. Reading new_seed_button.value re-runs this on each click.
    if new_seed_button.value:
        effective_seed = secrets.randbelow(2**31)
    else:
        effective_seed = int(seed.value)

    # 2. The active layer columns: read each `.value` and map it (via the pure
    #    appsupport seam) to a LayerControls, dropping any "Disabled" supplemental.
    columns = [layer1]
    if layer_count.value == 2 and layer2 is not None:
        columns.append(layer2)
    gathered_layers = [layer_controls_from_column(column.value) for column in columns]
    return effective_seed, gathered_layers


@app.cell(hide_code=True)
def _build(
    build_outcome,
    code_text,
    effective_seed,
    gathered_layers,
    header_answer,
    header_code,
    header_seed,
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
    # else both SVGs, then a subtle, toggle-gated grey readout at the bottom.
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
        # On-screen readout, FAITHFUL TO THE SAME header toggles as export
        # (header_code / header_answer / header_seed -- identical guards to
        # `_save`). Correct answer defaults OFF, so a screenshot of the live view
        # cannot leak it. Rendered LAST and grey-on-white: deliberately subtle,
        # because this is reproduction/debug info, not part of the puzzle.
        readout_parts: list[str] = []
        if header_code.value and outcome.structure_code is not None:
            readout_parts.append(f"Structure code: {outcome.structure_code}")
        if header_answer.value:
            readout_parts.append(
                f"Correct answer: {outcome.matrix.correct_answer_position}"
            )
        if header_seed.value:
            readout_parts.append(f"Seed: {effective_seed}")
        readout = (
            mo.Html(
                "<div style='color:#999;font-size:0.8rem;margin-top:0.75rem'>"
                + "  ·  ".join(readout_parts)
                + "</div>"
            )
            if readout_parts
            else mo.md("")
        )
        output = mo.vstack(
            [
                mo.md("**Problem**"),
                mo.Html(render_matrix_svg(outcome.matrix)),
                mo.md("**Answers**"),
                mo.Html(render_answers_svg(outcome.matrix)),
                readout,
            ]
        )
    return outcome, output


@app.cell(hide_code=True)
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

        svg_problem = _svg(include_problem=True, include_answers=False)
        svg_answers = _svg(include_problem=False, include_answers=True)
        svg_both = _svg(include_problem=True, include_answers=True)

        # PNG export must run in the BROWSER. resvg-py (the `raster` extra) is a
        # compiled Rust wheel and cannot load under Pyodide/WASM, so the marimo
        # frontend rasterises the SVG itself via an HTML <canvas>. This needs
        # mo.iframe -- mo.Html strips <script>. Each SVG is passed in as a base64
        # data URL (robust against srcdoc escaping and Unicode), drawn to a 2x
        # canvas on a white ground (SVGs have no opaque background), then handed to
        # the user as a PNG blob download. Works identically locally and in WASM,
        # since marimo's frontend is a browser in both.
        import base64
        import json

        def _data_url(svg_text: str) -> str:
            encoded = base64.b64encode(svg_text.encode()).decode()
            return "data:image/svg+xml;base64," + encoded

        _png_sources = json.dumps(
            {
                "problem": _data_url(svg_problem),
                "answers": _data_url(svg_answers),
                "both": _data_url(svg_both),
            }
        )
        _png_names = json.dumps(
            {
                "problem": f"raven_{stem}_problem.png",
                "answers": f"raven_{stem}_answers.png",
                "both": f"raven_{stem}_problem_answers.png",
            }
        )
        _png_html = (
            "<!doctype html><meta charset=utf-8>"
            "<style>body{margin:0;font-family:sans-serif}"
            "button{margin:0 6px 0 0;padding:6px 10px;cursor:pointer}</style>"
            "<button onclick=\"dl('problem')\">Save problem</button>"
            "<button onclick=\"dl('answers')\">Save answers</button>"
            "<button onclick=\"dl('both')\">Save problem + answers</button>"
            "<a id=lnk hidden></a>"
            "<script>const SRC=" + _png_sources + ",NAMES=" + _png_names + ";"
            "async function dl(k){const i=new Image();"
            "await new Promise((y,n)=>{i.onload=y;i.onerror=n;i.src=SRC[k];});"
            "const s=2,w=(i.naturalWidth||800)*s,h=(i.naturalHeight||600)*s;"
            "const c=document.createElement('canvas');c.width=w;c.height=h;"
            "const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,w,h);"
            "g.drawImage(i,0,0,w,h);"
            "c.toBlob(b=>{const a=document.getElementById('lnk');"
            "a.href=URL.createObjectURL(b);a.download=NAMES[k];a.click();},"
            "'image/png');}</script>"
        )

        save_panel = mo.vstack(
            [
                mo.md("**Save (SVG)**"),
                mo.hstack(
                    [
                        mo.download(
                            data=svg_problem,
                            filename=f"raven_{stem}_problem.svg",
                            mimetype="image/svg+xml",
                            label="Save problem",
                        ),
                        mo.download(
                            data=svg_answers,
                            filename=f"raven_{stem}_answers.svg",
                            mimetype="image/svg+xml",
                            label="Save answers",
                        ),
                        mo.download(
                            data=svg_both,
                            filename=f"raven_{stem}_problem_answers.svg",
                            mimetype="image/svg+xml",
                            label="Save problem + answers",
                        ),
                    ],
                    justify="start",
                ),
                mo.md("**Save (PNG)**"),
                mo.iframe(_png_html, height="48px"),
                # Subtle, self-explaining header-band toggles. They sit LAST,
                # below the primary save actions, under a quiet italic caption --
                # they govern an optional header on every saved file (SVG and
                # PNG alike), so they belong here, not nested under "Save (SVG)".
                mo.md(
                    "_Optional header band on saved files. Tick a field to print it:_"
                ),
                mo.hstack([header_code, header_answer, header_seed], justify="start"),
            ]
        )
    return (save_panel,)


@app.cell(hide_code=True)
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
