# raven-builder Implementation Plan — Phase 7: marimo app + typer CLI

**Goal:** The researcher-facing interfaces: a `typer` CLI (`build` from a code or explicit flags; `oracle`) and a `marimo` reactive app mirroring the full `SGMBuilderFrame` option surface, with live SVG, a "build from code" mode, and the resulting Structure code shown.

**Architecture:** A pure, testable `config_from_controls(...)` helper (in the core) maps option choices → `BuilderConfig`; both the CLI and the marimo app call it, keeping side-effectful UI thin (FCIS). `cli.py` (the `cli` extra, typer) and `app.py` (the `ui` extra, marimo) are edge layers; neither is imported by the core. The app re-renders reactively on control change (marimo's reason-for-being, DR4) and displays `render_matrix_svg`/`render_answers_svg` inline via `mo.Html`.

**Tech Stack:** Python (dev 3.14, package floor 3.12 — see Phase 1 decisions); `typer` (`cli` extra), `marimo` (`ui` extra). Tests: pytest + typer's `CliRunner` for the CLI; the app's logic is tested through `config_from_controls`, the reactive wiring is UAT.

**Scope:** Phase 7 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`.

**Codebase verified:** 2026-06-08. `SGMBuilderFrame` control surface extracted: layer count 1/2; per layer base relation {ShapeRep, OR, AND, XOR} + base direction {H,V,DiagTL,DiagBL,CornerOut}; 3 fixed supplemental slots {Disabled, Scaling, Rotation, FillRep, ChangeFill, Numerosity} each with a direction; correct-answer position 1–8 (default 1); seed (default current time). Hard-coded 3×3, 8 answers, sizing. marimo (`mo.App`/`@app.cell`, `mo.ui.*`, `mo.Html` for inline SVG) + typer (`@app.command`, `Annotated` options, `[project.scripts]`) APIs confirmed — exact current API re-checked at implementation (version strings unverified).

**Phase Type:** functionality

---

## Acceptance Criteria Coverage

### raven-builder.AC1: Option parity with SGMBuilderFrame
- **raven-builder.AC1.1 / AC1.2 / AC1.3** — exercised end-to-end through the CLI/app surface (each `SGMBuilderFrame` option settable and realised). Automated where possible via `config_from_controls`; the live-parity judgment is UAT.

> Phase 7 mostly re-verifies AC1.* through the interfaces; the underlying behaviour was tested in Phase 4. Its distinctive deliverable is the **human-judged** parity + visual correctness (uat-requirements.md).

---

## Decisions carried into this phase (resolved during planning)

- **App = faithful control panel** (live-reactive) **+ a separate "build from code" mode** (toggle; no bidirectional sync), showing the resulting Structure code via `label()` (the GUI "explanation" equivalent) and a "new seed" button.
- **CLI** `build` (from `--code` or explicit flags; `--png` via raster extra) + `oracle`; entry point in `[project.scripts]`.
- **FCIS:** a pure `config_from_controls` helper is the single source of truth for option→config mapping, shared by CLI and app; UI stays thin.
- **UAT entries persisted** (collated in uat-requirements.md): option-parity judgment, and the visual-correctness judgment deferred from Phase 6.

---

<!-- START_SUBCOMPONENT_A (task 1): CLI -->

<!-- START_TASK_1 -->
### Task 1: `cli.py` — typer CLI (`build`, `oracle`) + config helper

**Verifies:** raven-builder.AC1.1, AC1.3 (through the CLI)

**Files:**
- Create: `src/raven_matrix/ui_config.py` (`config_from_controls(...)` pure helper)
- Create: `src/raven_matrix/cli.py` (typer app)
- Modify: `pyproject.toml` (`cli = ["typer"]` already; add `[project.scripts] raven-matrix = "raven_matrix.cli:app"`)
- Test: `tests/test_cli.py` (unit via `typer.testing.CliRunner`), `tests/test_ui_config.py` (unit)

**Consumers:** `cli.py` and `app.py` (Task 2) both call `config_from_controls`; the script entry point is the installed CLI.

**Implementation:**
- `config_from_controls(layers: list[LayerControls], correct_answer_position: int) -> BuilderConfig` — pure mapping from option choices (per-layer base relation + direction, list of (supplemental, direction) with Disabled filtered out) to a validated `BuilderConfig`. Reuses Phase 4 validation. This is the tested seam.
- `cli.py` typer app:
  - `build`: `--code TEXT` (→ `build_from_code`) **or** explicit flags (`--relation`, `--direction`, `--supplemental` repeatable as `TYPE:DIR`, `--layers`, `--position`, `--seed`); `--out PATH` (default stdout); `--answers/--no-answers`; `--png` (uses the raster extra → `rasterise`, error with a clear hint if the extra is absent). Writes SVG (or PNG) and prints the Structure code via `label()`.
  - `oracle`: `--code TEXT` looks the code up in `data/ravens_oracle.csv` (+ the Phase-5 pass map) and prints its rows (`Stimulus Name`, `Correct Answer`, `% Correct`, round-trip status).
  - `[project.scripts] raven-matrix = "raven_matrix.cli:app"`.

**Testing (describe — `CliRunner`):**
- `build --code A1 --seed 0` exits 0 and emits well-formed SVG containing the expected cells; `build` with explicit flags produces an equivalent matrix; `--png` (under `--all-extras`) emits PNG magic bytes; a malformed `--code` exits non-zero with a clear message (AC2.4 surfaced).
- `oracle --code A1` prints matching oracle rows; an unknown code reports "not found".
- `config_from_controls` builds the right `BuilderConfig` for representative option sets and rejects invalid ones (>3 supplementals, position ∉1–8).

**Verification + commit:**
```bash
uv run pytest tests/test_cli.py tests/test_ui_config.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/ui_config.py src/raven_matrix/cli.py pyproject.toml tests/test_cli.py tests/test_ui_config.py
git commit -m "feat(cli): typer build/oracle commands + pure config helper"
```
<!-- END_TASK_1 -->
<!-- END_SUBCOMPONENT_A -->

<!-- START_SUBCOMPONENT_B (task 2): marimo app -->

<!-- START_TASK_2 -->
### Task 2: `app.py` — marimo reactive panel (full parity + code mode)

**Verifies:** raven-builder.AC1.* (UAT — the live-parity judgment)

**Files:**
- Create: `app.py` (marimo app at repo root, so `marimo edit app.py` / `marimo export html-wasm app.py` are clean)
- Test: `tests/test_app_importable.py` (smoke: the module imports; reactive behaviour is UAT)

**Consumer:** researchers (interactive); Phase 8 exports this to WASM.

**Implementation:** a marimo `app.py` (confirm the current `mo.App`/`@app.cell` idiom at implementation):
- **Mode toggle:** `mo.ui.dropdown`/radio — "Build from controls" vs "Build from code".
- **Controls mode (faithful GUI mirror):** layer-count (1/2); for each active layer: base relation dropdown {ShapeRep, OR, AND, XOR}, base direction dropdown {H, V, DiagTL, DiagBL, CornerOut}, and **3 fixed supplemental slots** (each a {Disabled, Scaling, Rotation, FillRep, ChangeFill, Numerosity} dropdown + a direction dropdown) — mirroring the GUI's 3-slot layout. Correct-answer-position number (1–8). Seed number + a "new seed" button. Layer-2 controls show only when layer-count = 2.
- **Code mode:** a `mo.ui.text` for a Structure code (e.g. `A1B2C4`) + seed; uses `build_from_code`.
- **Reactivity:** a cell reads the controls, calls `config_from_controls` (or `build_from_code`), `build()`, and renders. Build/parse errors are caught and shown as a friendly message (not a traceback).
- **Output:** `mo.Html(render_matrix_svg(matrix))` (problem) + `mo.Html(render_answers_svg(matrix))` (answers), plus the resulting Structure code via `label(matrix)` and the configured correct-answer position.

**Testing:** a smoke test imports `app.py`'s module (or asserts the file parses and exposes `app`) so CI catches syntax/import breakage. The interactive parity + rendering is verified by UAT, not automated tests.

**UAT entries** (recorded here; the planning flow's final UAT-collation step writes them, with the Phase-8 in-browser entry, into `docs/implementation-plans/.../uat-requirements.md` — no phase task creates that file):
- *Option parity:* run `marimo edit app.py`, set each control across its range (every base relation, every direction, each supplemental, 1 and 2 layers, each answer position), and judge that every `SGMBuilderFrame` option is present and that changing any control re-renders a coherent puzzle. **Wrong if:** a GUI option is missing, or a change doesn't update the puzzle, or produces an incoherent figure.
- *Visual correctness (deferred from Phase 6):* render puzzles spanning all 7 shapes and all 5 fills and judge whether they read as recognisable Raven-style figures (shapes distinct, White transparent/outline-only, greys layered). **Wrong if:** shapes are unrecognisable or fills look wrong.

**Verification + commit:**
```bash
uv run pytest tests/test_app_importable.py -v && uv run ty check . && uv run ruff check .
# Manual: uv run --extra ui marimo edit app.py   (UAT)
git add app.py tests/test_app_importable.py
git commit -m "feat(app): marimo reactive panel — full option parity + code mode"
```
<!-- END_TASK_2 -->
<!-- END_SUBCOMPONENT_B -->

<!-- START_SUBCOMPONENT_C (task 3): app UX polish — raised in the Phase 7 UAT -->

<!-- START_TASK_3 -->
### Task 3: app UX polish (N1–N5, from the Phase 7 UAT)

**Verifies:** raven-builder.AC1.* (usability of the parity surface; re-UAT). Additive to Task 2 — **no behaviour change to the generator**. FCIS holds: pure logic moves to a tested module; `app.py` stays a thin reactive shell.

**Why:** the Phase 7 UAT confirmed parity / visual / constant-carrier but surfaced five researcher-usability gaps (Brian, 2026-06-10).

**Files:**
- Create: `src/raven_matrix/appsupport.py` (pure helpers — the new tested seam)
- Modify: `app.py` (slim to a reactive shell; controls beside output; reference docs; save controls)
- Create: `tests/test_appsupport.py`
- Modify: `README.md` (replace the stale "no code yet" status with real install/run docs)
- Investigate only (no change this task): `src/raven_matrix/render/svg.py` / `surface.py` (N4)

**N1 — FCIS extract + controls-beside-output.**
- Move the option-label→enum maps, the column→`LayerControls` mapping (current `to_layer_controls`), and a pure `build_outcome(...)` (calls `config_from_controls`+`build` or `build_from_code`; catches `ValueError`; returns a small result carrying `matrix | None`, `error | None`, and the `label()` code) into `appsupport.py`. `app.py` imports them.
- Consolidate the control-definition cells; **delete the dead `mo.sql` cell** (current `app.py` ~lines 314–321). The final cell lays out `mo.hstack([controls_panel, output])` — controls left, live render right — so they sit adjacent in `marimo edit`.
- Reactivity rule: UI elements stay defined in cells (so `.value` is reactive); only the pure mapping/build moves out.

**N2 — reference for every control and option.**
- `appsupport.option_reference() -> str`: markdown documenting every control and every option (the A/B/C/D/E relation letters, the 1–5 directions incl. corner-out, each supplemental, position, seed, mode), sourced from the Matzen naming scheme in `CLAUDE.md`.
- `app.py` renders it in a collapsible `mo.accordion` by the controls.

**N3 — save with variants (researcher spec).**
- `appsupport.compose_save_svg(matrix, *, include_problem: bool, include_answers: bool, header_fields: Sequence[...]) -> str`: composes problem / answers / problem+answers (vertical stack) from `render_matrix_svg` / `render_answers_svg`, with an optional header band showing the toggled fields (Structure code, correct-answer position, seed). SVG is the saved format (canonical; raster-free, so it works regardless of the `raster` extra).
- `app.py`: three `mo.download` buttons (problem · answers · both) + three header toggles (`mo.ui.checkbox`: code, correct answer, seed) feeding `compose_save_svg`.

**N4 — small-triangle legibility (INVESTIGATE; do not speculatively change).**
- The squat triangles in the UAT contact sheet were the **2008 norming PNGs**, not the port. First confirm whether the port's own Triangle has any issue: render it at small sizes (a size-relation code yielding a triangle) and assess apex/orientation legibility.
- The 2px outline is an intentional spec and the Triangle geometry is faithful to upstream; a change would diverge from upstream and churn the Phase-6 goldens (`tests/golden/sgmt_matrices.json`, `test_surface.py`, `test_render_svg_cells.py`). **No renderer change in this task** — produce sample renders + a written assessment, surfaced at the re-UAT for Brian's decision. If he wants a fix, it becomes its own scoped change with a deliberate golden update.

**N5 — README.**
- Replace the stale `## Status` ("No generator code yet") with accurate content: what works now (generator, CLI, marimo app, SVG/PNG); install (`uv sync --extra ui --extra cli --extra raster`; uv fetches Python); run the app (`uv run --extra ui marimo edit app.py`); run the CLI (`raven-matrix build … / oracle …`); the no-submodule-needed-to-run note; regenerating the oracle CSV; and that online hosting (Phase 8) is optional. Keep BSD-3 / attribution.

**Testing (`tests/test_appsupport.py`):**
- option maps; `layer_controls_from_column` drops Disabled slots; `build_outcome` success + each `ValueError` path (logic-base+supplemental, >3 supplementals, position ∉ 1–8, malformed code) → friendly error.
- `option_reference()` is **complete** — every `BaseRelation` / `Direction` / `Supplemental` member and every control label appears (guards doc drift).
- `compose_save_svg` includes exactly the requested pieces (problem/answers/both) and only the toggled header fields, and emits well-formed SVG.
- `tests/test_app_importable.py` still passes (smoke). N4 is investigation (no automated test); N5 is docs (no test).

**Verification + commit:**
```bash
uv run pytest && uv run --extra ui pytest && uv run ty check . && uv run ruff check .
# logical commits: (1) appsupport extract + app.py slim + layout (N1); (2) reference docs (N2);
# (3) save controls (N3); (4) README (N5). N4 = investigation notes only.
```
<!-- END_TASK_3 -->
<!-- END_SUBCOMPONENT_C -->

---

## Phase 7 completion check

- [ ] CLI `build` works from `--code` and explicit flags; `--png` uses the raster extra; `oracle` queries the CSV + pass map (AC1.* via CLI).
- [ ] `config_from_controls` is a pure, tested seam shared by CLI and app.
- [ ] `[project.scripts] raven-matrix` entry point installed and runnable.
- [ ] `app.py` exposes every `SGMBuilderFrame` option + a code mode, re-renders reactively, shows the Structure code; imports cleanly in CI.
- [ ] UAT entries (option parity, visual correctness) recorded in uat-requirements.md.
- [ ] `uv run pytest`, `uv run ty check .`, `uv run ruff check .` clean.

### Task 3 (app UX, post-UAT)
- [ ] Pure logic lives in `appsupport.py` (tested); `app.py` is a thin shell with controls beside the live render; the dead `mo.sql` cell is gone (N1).
- [ ] In-app reference documents every control and option; a completeness test guards drift (N2).
- [ ] Save controls: problem / answers / both, with header toggles for code · correct answer · seed (N3).
- [ ] Port small-triangle legibility investigated; samples + assessment surfaced at re-UAT (no speculative renderer change) (N4).
- [ ] `README.md` reflects what works now + how to install and run (N5).
