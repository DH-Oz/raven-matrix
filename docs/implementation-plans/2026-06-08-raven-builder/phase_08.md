# raven-builder Implementation Plan — Phase 8: Hosted online (concluding)

**Goal:** Publish the pure-Python `raven-matrix` wheel to PyPI and produce a working WASM bundle from the marimo app via `marimo export html-wasm`, with a live GitHub Pages site as the stretch target.

**Architecture:** The pure, zero-runtime-dep core makes the wheel directly loadable in Pyodide via micropip. `app.py` declares its dependency via a PEP 723 `# /// script` block (`raven-matrix`), which marimo's exporter feeds to micropip in-browser. Because marimo #5488 (local-package import in WASM) is **open**, a *working* export requires the wheel on PyPI — so PyPI publish precedes the export. The release workflow uses Trusted Publishing (OIDC); the Pages workflow exports + deploys. The compiled `raster` extra is never used in-browser (the app renders SVG directly).

**Tech Stack:** uv (`uv build`), `pypa/gh-action-pypi-publish` (OIDC), `marimo export html-wasm` (Pyodide), `actions/upload-pages-artifact` + `actions/deploy-pages`.

**Scope:** Phase 8 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`. Concluding phase, sequenced last so deploy plumbing never blocks core correctness.

**Codebase verified:** 2026-06-08 (research). #5488 open → no local-wheel bundling; PEP 723 is the dep mechanism; Trusted Publishing is the publish path; Pages needs `.nojekyll` and likely a `<base href="/raven-matrix/">` for the project subpath. The core's import hygiene (no `ui`/`cli`/`raster` imports) is a standing invariant from Phase 1's layering — re-verified here as a WASM cold-start guard.

**Phase Type:** infrastructure (deploy)

---

## Acceptance Criteria Coverage

### raven-builder.AC7: Hosted online (concluding phase)
- **raven-builder.AC7.1 Success (DoD-met):** the marimo app runs locally and `marimo export html-wasm` produces a working static bundle that generates a matrix in-browser.
- **raven-builder.AC7.2 Success:** the `raven-matrix` wheel publishes to PyPI and installs via micropip in the WASM environment.
- **raven-builder.AC7.3 Stretch:** a live GitHub Pages URL loads the app and generates a matrix in-browser (demoted to stretch per the criterion-7 fallback if marimo #5488 or Pages plumbing blocks it).

**Verifies (operational):** wheel resolves on PyPI; export emits a served bundle that generates a matrix; (stretch) the live URL works. **Not unit-tested** — verification is operational, capped by a UAT browser check.

---

## Decisions carried into this phase (resolved during planning)

- **Sequencing (forced by open #5488):** PyPI trusted-publisher setup → **dev pre-release** (validate) → real release → `marimo export html-wasm` (working bundle) → Pages deploy (stretch).
- **First publish = dev pre-release first** (`0.1.0.dev0`) to validate the export+micropip pipeline before burning the immutable real `0.1.0`.
- **Deps via PEP 723** in `app.py` (`raven-matrix` only; raster excluded in-browser).
- **Live Pages site is stretch;** AC7.1+AC7.2 (wheel on PyPI + working local-served export) meet the DoD even if Pages is blocked.
- **Outward actions stay user-gated:** the workflow only publishes when *you* cut a GitHub Release; the one-time PyPI trusted-publisher config is a manual prerequisite.

---

<!-- START_TASK_1 -->
### Task 1: WASM-ready packaging — PEP 723 deps + core import hygiene

**Files:**
- Modify: `app.py` (add the PEP 723 script-metadata block)
- Create: `tests/test_import_hygiene.py` (guards WASM cold-start)

**Step 1: Add the PEP 723 block to `app.py`**

At the very top of `app.py`:
```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "raven-matrix",
# ]
# ///
```
(Marimo's `export html-wasm` reads this and installs `raven-matrix` via micropip. Do NOT list `resvg_py`/`typer` — neither is used in the browser path. The `>=3.12` floor matches the package; see Step 0.)

**Step 0: Confirm the live Pyodide Python version (resolves review finding I3)**

Before exporting, check the Python version the current marimo-WASM/Pyodide runtime ships (it lags CPython). If it is **≥ the package floor (3.12)**, proceed. If marimo's Pyodide is *newer* than 3.12, the floor may be raised to match (optional). If — unexpectedly — it were *below* 3.12, lower the package `requires-python` accordingly and re-confirm the core runs there. Record the observed Pyodide version in `docs/wasm-export.md`. (The `[3.12, 3.14]` CI matrix from Phase 1 already proves the package runs on 3.12.)

**Step 2: Import-hygiene guard**

`tests/test_import_hygiene.py`: import the core entry points (`raven_matrix.builder`, `.label`, `.render.svg`) in a subprocess and assert that `marimo`, `typer`, and `resvg_py` are **not** in `sys.modules` afterwards — proving the core pulls no edge dependency (fast WASM cold-start, and the pure wheel resolves in Pyodide).

**Step 3: Verify the wheel is pure + dep-free**

```bash
uv build --wheel
uv run python -c "import zipfile,glob; w=glob.glob('dist/*.whl')[0]; n=zipfile.ZipFile(w).namelist(); print(w); assert not any(x.endswith('.so') or x.endswith('.pyd') for x in n), 'compiled artifact in wheel'"
```
Confirm the wheel's `METADATA` lists no mandatory runtime deps (only the extras). 

**Step 4: Verify + commit**
```bash
uv run pytest tests/test_import_hygiene.py -v && uv run ty check . && uv run ruff check .
git add app.py tests/test_import_hygiene.py
git commit -m "build(wasm): PEP 723 deps in app.py + core import-hygiene guard"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: PyPI release workflow (Trusted Publishing) + dev pre-release

**Files:**
- Create: `.github/workflows/release.yml`
- Create/Modify: a short `docs/release.md` (the one-time manual PyPI trusted-publisher steps)

**Step 1: Document the one-time PyPI setup** (manual, user-performed)

`docs/release.md`: on PyPI, add a Trusted Publisher for the `raven-matrix` project — GitHub Actions, owner + repo, workflow `release.yml`, environment `pypi`. (This cannot be scripted; it is the human prerequisite.)

**Step 2: Release workflow** (`.github/workflows/release.yml`)
```yaml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6   # bump to current major
      - run: uv build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/ }
  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write           # OIDC — no API token
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1
```

**Step 3: Dev pre-release (validate before burning the real version)**

Set the version to `0.1.0.dev0` (in `pyproject.toml`), cut a GitHub **pre-release** tagged `v0.1.0.dev0` → the workflow publishes the dev wheel. Confirm it appears on PyPI and installs:
```bash
uv run python -c "import urllib.request,json; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/raven-matrix/json'))['info']['version'])"
```
**This publish is an outward, user-triggered act** — the human creates the release; the workflow does the rest.

**Step 4: Commit**
```bash
git add .github/workflows/release.yml docs/release.md
git commit -m "ci(release): PyPI Trusted Publishing workflow + dev pre-release docs"
```
<!-- END_TASK_2 -->

<!-- START_TASK_3 -->
### Task 3: WASM export — working bundle (AC7.1, AC7.2)

**Files:**
- Create: `docs/wasm-export.md` (the export + local-serve verification recipe)

**Step 1: Export against the dev wheel**

With `0.1.0.dev0` on PyPI and the PEP 723 block in place:
```bash
uv run --extra ui marimo export html-wasm app.py -o build --mode run
touch build/.nojekyll
```
Confirm `build/index.html` + `build/assets/` exist.

**Step 2: Serve locally + verify in-browser (UAT)**
```bash
uv run python -m http.server -d build 8000
```
Open `http://localhost:8000/`, wait for the Pyodide cold-start + micropip install of `raven-matrix`, and confirm the app **generates a matrix** (controls + code mode both render SVG). This is AC7.1 (working bundle) + AC7.2 (micropip install) met.

**Step 3: Cut the real release**

Once the dev bundle works end-to-end, bump the version to `0.1.0`, cut a real GitHub Release `v0.1.0` → the workflow publishes the real wheel. Re-export/verify against `0.1.0`.

**Step 4: Commit**
```bash
git add docs/wasm-export.md
git commit -m "docs(wasm): export + local-serve verification recipe"
```
<!-- END_TASK_3 -->

<!-- START_TASK_4 -->
### Task 4: GitHub Pages deploy (AC7.3 — stretch)

**Files:**
- Create: `.github/workflows/pages.yml`

**Step 1: Pages workflow** (`.github/workflows/pages.yml`)
```yaml
name: Deploy WASM to Pages
on:
  push: { branches: [main] }
  workflow_dispatch:
permissions:
  pages: write
  id-token: write
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv run --extra ui marimo export html-wasm app.py -o build --mode run
      - run: touch build/.nojekyll
      - uses: actions/upload-pages-artifact@v3
        with: { path: build/ }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

**Step 2: Base-path fix (project subpath gotcha)**

If assets 404 on the live `https://<user>.github.io/raven-matrix/` (they load locally but not on Pages), add `<base href="/raven-matrix/">` to the exported `index.html` (a post-export step in the workflow) — the known marimo project-subpath gotcha.

**Step 3: Verify + commit**

Enable Pages (Settings → Pages → GitHub Actions source). After the workflow runs, open the live URL and confirm it generates a matrix in-browser. **If #5488 changes, or Pages plumbing blocks this, demote per the criterion-7 fallback** — AC7.1+AC7.2 already met the DoD; record the live-site status.
```bash
git add .github/workflows/pages.yml
git commit -m "ci(pages): deploy WASM bundle to GitHub Pages (stretch)"
```
<!-- END_TASK_4 -->

---

## UAT (persisted to uat-requirements.md)

- *In-browser generation:* serve the exported bundle (locally, then the live Pages URL if reached), wait through the Pyodide cold-start, and judge whether the app generates a puzzle responsively and without errors — controls re-render, code mode loads a pasted code, SVG displays. **Wrong if:** the app hangs past a reasonable cold-start, errors on micropip install, or fails to render.

---

## Phase 8 completion check

- [ ] `app.py` declares `raven-matrix` via PEP 723; core import-hygiene guard passes (no `ui`/`cli`/`raster` in the core); wheel is pure (no compiled artifacts).
- [ ] Release workflow publishes via Trusted Publishing; dev `0.1.0.dev0` validated on PyPI before the real `0.1.0` (AC7.2).
- [ ] `marimo export html-wasm` yields `index.html`+`assets/`; served locally it generates a matrix in-browser via micropip (AC7.1).
- [ ] (Stretch) Pages workflow deploys; live URL generates a matrix, or the status is recorded and demoted per the fallback (AC7.3).
- [ ] UAT in-browser check recorded.
- [ ] Outward publishes were user-triggered (GitHub Releases), not auto-fired.
