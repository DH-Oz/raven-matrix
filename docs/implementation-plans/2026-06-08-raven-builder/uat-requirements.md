# UAT Requirements — raven-builder

Human-judgment falsification entries. Each requires a human to **use** the built thing
and exercise judgment that automated tests cannot capture.

Quality gate: every entry has (1) what the human **does** (an action pursuing the goal,
not an inspection), (2) what they're **judging** (a subjective quality), (3) what
**failure** looks like (a concrete experience).

**Phases 1–6 produce no UAT entries** — they are foundational (RNG, model, transforms,
builder, labeller/oracle, SVG core) and verified entirely by automated tests + operational
checks. The first human-facing surface is the Phase 7 app, where the figures and the option
panel become visible; the in-browser experience is judged in Phase 8. The Phase-6 visual
question is deferred here because the renderer's output is only *seen* (and judged) once the
app surfaces it.

---

## Phase 7: marimo app + typer CLI

### Option parity (the AC1.* human gate)

**This decision assumes:** the marimo control panel faithfully mirrors the upstream
`SGMBuilderFrame` option surface, and every option, when changed, drives a corresponding,
correct change in the generated puzzle.

**To shatter it:** run `uv run --extra ui marimo edit app.py`. Work through the panel as a
researcher would — switch layer count between 1 and 2; for each layer pick every base
relation (ShapeRep, OR, AND, XOR) and every base direction (H, V, both diagonals,
corner-out); enable each supplemental (Scaling, Rotation, FillRep, ChangeFill, Numerosity)
with directions; move the correct-answer position across 1–8; change the seed. Also paste a
published code (e.g. `A1B2C4`) into the code mode.

**It's wrong if:** any `SGMBuilderFrame` option is missing from the panel; changing a
control does not re-render the puzzle; the displayed Structure code disagrees with the
controls you set; or a valid selection yields an incoherent matrix (e.g. a relation visibly
not applied in the chosen direction).

### Visual correctness (deferred from Phase 6)

**This decision assumes:** the SVG renderer turns the model into figures that a person
reads as recognisable Raven-style shapes, with fills behaving correctly (White transparent /
outline-only; greys layered; a 2px outline on every shape).

**To shatter it:** drive the app to render matrices that, across a handful of seeds and
configs, exercise **all seven shapes** (Diamond, Ellipse, Line[only with the compat flag],
Rectangle, Tee, Trapezoid, Triangle) and **all five fills** (Black, White, Grey10/40/75).
Look at the rendered problem and answer choices.

**It's wrong if:** a shape is unrecognisable or indistinguishable from another; White renders
as a filled (not outline-only) shape, or a non-White fill renders transparent; the greys are
not visually ordered; or the answer grid / blank cell looks broken.

---

## Phase 8: Hosted online (concluding)

### In-browser generation feel

**This decision assumes:** the WASM bundle (served locally, then the live Pages URL if
reached) loads and lets a person generate puzzles responsively, the Pyodide cold-start +
micropip install of `raven-matrix` completing within a tolerable wait.

**To shatter it:** serve the exported bundle (`python -m http.server -d build`), open it in a
browser, wait through the "initialising Python" cold-start, then generate a puzzle from the
controls and from a pasted code. If the live Pages site is reached, repeat there.

**It's wrong if:** the page hangs past a reasonable cold-start (no progress, no puzzle); the
micropip install errors (e.g. a `requires-python` mismatch refusing the wheel — the I3 risk);
the SVG fails to display; or interaction is so sluggish it's unusable.

---

## Notes

- These entries route their phases to the `exec-uat-gate` during execution; the foundational
  phases (1–6) route to `exec-coherence-review` instead (no human-judgment surface).
- The visual-correctness entry is the single human check that the data/logic-equivalence
  test bar (well-formed SVG, correct attributes) cannot capture — a figure can be valid SVG
  and still read wrongly.
