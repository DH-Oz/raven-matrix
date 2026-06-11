# raven-builder Implementation Plan — Phase 8: Hosted online (concluding)

> **Revised 2026-06-11** after a WASM spike (this session) that changed the plan's
> spine. The original assumed **PyPI-first** (because marimo #5488 blocks
> local-wheel bundling) and **SVG-only** in-browser. Both proved unnecessary:
>
> - **No PyPI needed.** micropip installs the pure wheel **bundled in the export's
>   `assets/`**. micropip resolves the bare wheel name relative to the Pyodide
>   *worker* (which lives under `assets/`), so it also resolves under the Pages
>   project subpath — verified, no `<base href>` required. #5488 is only about
>   *automatic* local-package bundling; manual micropip sidesteps it.
> - **PNG works in-browser** via an HTML `<canvas>` inside `mo.iframe` (marimo's
>   iframe carries no `sandbox`, so the blob download fires). `resvg-py` is a
>   compiled Rust wheel that cannot load under Pyodide; it stays the CLI/headless
>   rasteriser and is never shipped to WASM.
> - **PyPI is deferred** to an optional future (was AC7.2). The web app no longer
>   needs it; revisit only if `pip install raven-matrix` becomes a goal in itself.
>   Doing it later costs no more than doing it now, and would only tempt rewiring
>   the proven `assets/` bootstrap into a PEP-723-from-PyPI load.
> - The repo **`DH-Oz/raven-matrix` already exists and is public**; GitHub Pages
>   is the deploy target.

**Goal:** Publish the marimo app as a static, in-browser WASM bundle on GitHub
Pages — generating matrices and exporting **SVG + PNG entirely client-side**, with
no server and no PyPI dependency.

**Architecture:** The pure, zero-runtime-dep core wheel loads in Pyodide via
micropip. `app.py` carries a guarded `_wasm_bootstrap` cell that, only under
Pyodide, micropip-installs the wheel bundled in `assets/`; it is a no-op locally.
PNG export is pure client-side JS (canvas) inside `mo.iframe`. The Pages workflow
builds the wheel, exports the bundle, drops the wheel into `assets/`, strips the
stray `CLAUDE.md` the exporter sweeps in, and deploys.

**Tech stack:** uv (`uv build`), `marimo export html-wasm` (Pyodide, run mode),
`actions/upload-pages-artifact` + `actions/deploy-pages`.

**Verification:** operational, not unit-tested. Proven this session with headless
Chrome / Playwright against the served bundle: matrix builds in-browser; SVG and
PNG both download; the chain survives a `/raven-matrix/` project subpath with zero
404s. A wheel-name guard test ties `app.py`'s bootstrap to the package version.

---

## Acceptance Criteria Coverage

### raven-builder.AC7: Hosted online (concluding phase)
- **AC7.1 (DoD-met):** `marimo export html-wasm` produces a static bundle that
  generates a matrix in-browser, served locally and on Pages. **Met + verified.**
- **AC7.2 → DEFERRED:** publish the wheel to PyPI. No longer on the critical path;
  reopened only if package distribution is wanted.
- **AC7.3:** a live GitHub Pages URL loads the app and generates a matrix
  in-browser. Now the primary deliverable (not stretch), since no PyPI gate
  precedes it.
- **AC7.4 (new):** the app exports PNG client-side (Qualtrics-ingestible), not
  only SVG. **Met + verified.**

---

## Tasks

<!-- START_TASK_1 -->
### Task 1: WASM bootstrap + wheel bundling — DONE

- `app.py` `_wasm_bootstrap` (hidden cell): under `"pyodide" in sys.modules`,
  `import micropip` (a `# ty: ignore[unresolved-import]` — Pyodide-provided, no
  local stub) then `micropip.install("raven_matrix-<ver>-py3-none-any.whl")`.
  No-op locally. Returns `bootstrapped`, which `_imports` consumes to force this
  cell to run first (marimo orders by data dependency).
- The wheel is pure: no compiled artifacts; every `Requires-Dist` is extras-only
  (`marimo`/`typer`/`resvg-py` all behind extras). The marimo-as-mandatory-dep
  edit was reverted — a hard dep would make micropip chase marimo from PyPI.
- **Guard test:** assert `app.py` references `raven_matrix-{__version__}-…whl`, so
  a version bump that forgets the bootstrap fails CI. *(to add)*
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: In-browser PNG export — DONE

- `app.py` `_save` cell: alongside the three SVG `mo.download` buttons, an
  `mo.iframe` (not `mo.Html`, which strips `<script>`) holding three PNG buttons.
  Each SVG is handed in as a base64 `data:` URL; a `<canvas>` draws it at 2× on a
  white ground and triggers a blob download. Works identically locally and in
  WASM (marimo's frontend is a browser in both).
- `resvg-py` remains the CLI/headless rasteriser; it is never imported in-browser.
<!-- END_TASK_2 -->

<!-- START_TASK_3 -->
### Task 3: GitHub Pages deploy workflow — DONE (needs one manual setting)

- `.github/workflows/pages.yml`: on push to `main` / dispatch — `uv build --wheel`
  → `marimo export html-wasm app.py -o build --mode run` → `cp dist/*.whl
  build/assets/` → `rm build/CLAUDE.md` → `.nojekyll` → upload + deploy.
- **Manual prerequisite (human):** Settings → Pages → Source = "GitHub Actions".
- No `<base href>` step: the exporter uses relative asset paths and the wheel is
  worker-relative, both verified clean under the project subpath.
<!-- END_TASK_3 -->

<!-- START_TASK_4 -->
### Task 4: PyPI publish — DEFERRED (optional future)

Only if `pip install raven-matrix` becomes a goal. Then: PyPI Trusted Publisher
(manual, one-time) + a `release.yml` on GitHub Release (OIDC). The web app does
not depend on this; it can ship and stay live without it.
<!-- END_TASK_4 -->

---

## CI hygiene folded in this session

- Adopted `ruff format` across the repo (the `ruff format --check` gate was red on
  35 hand-formatted files); CI now green on format.
- `ty` clean: the one Pyodide-only import (`micropip`) carries a targeted
  `# ty: ignore[unresolved-import]` (a real platform module the checker's
  environment cannot have — not a logic suppression).

---

## Phase 8 completion check

- [x] `app.py` bootstrap installs the bundled wheel under Pyodide; no-op locally.
- [x] Wheel is pure (no compiled artifacts; deps are extras-only).
- [x] In-browser SVG **and** PNG export, verified by headless browser download.
- [x] Bundle survives the Pages project subpath (no 404s, no base-href).
- [x] `pages.yml` builds + bundles the wheel + strips stray files + deploys.
- [ ] Pages enabled (Source = GitHub Actions) and the live URL generates a matrix.
- [ ] Wheel-name guard test added.
- [ ] UAT: open the live Pages URL, build a matrix, download a PNG.
- [~] PyPI publish — deferred (AC7.2), not required for the live site.

---

## Deferred from pre-merge review (2026-06-10)

Three items from the raven-builder → main pre-merge review remain open (Phase-8/
release-prep, not defects):

- **[Important] Fold the CLI build path through `appsupport.build_outcome`.**
  `cli.py` `build` repeats the parse → build → render → label sequence that
  `build_outcome` already encapsulates. Shallow today; tidy before the build path
  grows.
- **[Minor] `[project.scripts]` entry point needs the `cli` extra** — a bare
  `pip install raven-matrix` installs the script but `typer` is optional. Only
  bites if/when PyPI publish (Task 4) happens.
- **[Minor] Declare a public API in `__init__.py`** — it exports only
  `__version__`; a pinned surface would help any future packaging.
