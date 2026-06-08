# raven-builder Implementation Plan — Phase 6: SVG rendering (+ raster)

**Goal:** Render a `Matrix` and its answer set to well-formed SVG (canonical) covering every shape and fill with correct alpha (White transparent), and rasterise SVG→PNG on demand via an optional `raster` extra.

**Architecture:** `render/svg.py` in the zero-dependency core hand-emits SVG strings: each shape → an SVG element, each fill → `fill` + `fill-opacity`, plus a 2px black stroke and an affine `transform`, ported from the Java2D geometry. `render/raster.py` lives in the `raster` extra (`resvg_py`) and converts an SVG string to PNG bytes. The bar is **data/logic equivalence, not pixel reproduction** — tests assert SVG well-formedness and correct semantics, never pixel parity with Java2D.

**Tech Stack:** Python (dev 3.14, package floor 3.12 — see Phase 1 decisions) stdlib (`xml.etree.ElementTree` for test-side parsing/validation) for the core; `resvg_py` (MIT, self-contained wheels) for the `raster` extra. Tests: pytest.

**Scope:** Phase 6 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`.

**Codebase verified:** 2026-06-08. Shape geometry extracted verbatim (Diamond pinched 4-point path; Ellipse/Rectangle centred on position; Line horizontal then rotated; Tee/Trapezoid/Triangle paths). Transform order `translate(pos)→rotate(rad)→scale→translate(-pos)`. Paint = fill (RGBA alpha) then 2px black stroke; White alpha=0 → transparent fill (outline only). Layout: 3×3, white bg, blank-white bottom-right in problem mode; answers 2×4, black bg; blank cell = white/no shapes. RasterSettings holds cell pixel size + inter-cell spacing (no hardcoded defaults upstream).

**Phase Type:** functionality

---

## Acceptance Criteria Coverage

### raven-builder.AC5: SVG rendering
- **raven-builder.AC5.1 Success:** `render_matrix_svg`/`render_answers_svg` emit well-formed SVG for a sample covering every shape and fill (alpha applied; White transparent).
- **raven-builder.AC5.2 Success:** `rasterise()` (raster group) converts the SVG to a PNG.
- **raven-builder.AC5.3 Edge:** an empty/blank answer cell renders without error.

---

## Decisions carried into this phase (resolved during planning)

- **Faithful geometry + fill semantics**, but **test semantics not pixels** — well-formedness, per-shape elements, fill/opacity attributes, PNG validity; never image diff against Java2D.
- **Raster backend = `resvg_py`** (MIT, self-contained wheels) in the `raster` extra. Exact import/function name confirmed against the installed package at implementation time (version strings from research are unverified).
- **`RasterSettings`/`DEFAULT_RASTER`** supply sizing (default 256px cell, 10px gap) since the upstream has no hardcoded defaults.

---

<!-- START_SUBCOMPONENT_A (tasks 1-2): SVG core -->

<!-- START_TASK_1 -->
### Task 1: `render/svg.py` — shapes, fills, transforms, cell rendering

**Verifies:** raven-builder.AC5.1 (shape + fill coverage), AC5.3 (blank cell)

**Files:**
- Create: `src/raven_matrix/render/__init__.py` (**keep empty or SVG-only — must NOT import or re-export `raster`/`rasterise`**; see the import-hygiene note below)
- Create: `src/raven_matrix/render/svg.py` (RasterSettings, fill mapping, per-shape SVG, per-cell SVG)
- Test: `tests/test_render_svg_cells.py` (unit; parse SVG with ElementTree)

**Consumer:** `render_matrix_svg`/`render_answers_svg` (Task 2); the CLI/app (Phase 7).

**Implementation:**
- `RasterSettings(cell_pixel_size: int = 256, pixels_between_cells: int = 10)` frozen dataclass; `DEFAULT_RASTER = RasterSettings()`.
- `_fill_attrs(fill: Fill) -> str`: `fill="rgb(R,G,B)"` (each = round(channel×255)) + `fill-opacity="A"`; for White (`a==0`) this yields `fill-opacity="0"` (transparent, outline only). Every shape also gets `stroke="black" stroke-width="2"`.
- Per-shape SVG emitters, ported from the extracted geometry (coordinates relative to `feature.position`):
  - Diamond → `<path d="M {x-hw} {y-qh} L {x} {y+hh} L {x+hw} {y-qh} L {x} {y-hh} Z">` (`hw=w/2, hh=h/2, qh=hh/2`);
  - Ellipse → `<ellipse cx cy rx=w/2 ry=h/2>`;
  - Rectangle → `<rect x=cx-w/2 y=cy-h/2 width=w height=h>`;
  - Line → `<line x1=x-len/2 y1=y x2=x+len/2 y2=y>` (rotation comes from the transform);
  - Tee/Trapezoid/Triangle → `<path>`/`<polygon>` from the pinned vertex lists.
- Transform: emit `transform="translate({px} {py}) rotate({deg}) scale({s}) translate({-px} {-py})"` where `deg = degrees(feature.rotation)` (Java rotation is radians → SVG degrees) and `s = feature.scale`. This reproduces the Java "scale+rotate about position" order.
- `render_cell_svg(cell, settings) -> str`: a `<g>` containing one element per surface feature; a cell with no features yields an **empty `<g>`** (AC5.3).
- **Import-hygiene constraint (Phase-8 dependency):** `render/__init__.py` must **not** import or re-export `render.raster` (nor `rasterise`), and `render/svg.py` must not import `resvg_py` at module scope. The `resvg_py` import stays **inside** the `rasterise` function body (Task 3). This keeps `import raven_matrix.render` / `render.svg` free of the optional `raster` dependency, which the Phase-8 WASM import-hygiene test (`tests/test_import_hygiene.py`, AC7.1) asserts. Treat this as a hard rule, not a stylistic preference.

**Testing (describe — parse the emitted SVG with `xml.etree.ElementTree`):**
- AC5.1 coverage: for each of the 7 shapes, the emitted element is the expected tag with the pinned coordinates; for each of the 5 fills, `fill`/`fill-opacity` match the RGBA (White → `fill-opacity="0"`); every shape carries `stroke-width="2"`.
- AC5.3: `render_cell_svg` on a featureless cell parses as a valid empty group, no error.

**Verification + commit:**
```bash
uv run pytest tests/test_render_svg_cells.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/render/ tests/test_render_svg_cells.py
git commit -m "feat(render): SVG shape/fill/transform emitters + cell rendering"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: `render_matrix_svg` + `render_answers_svg`

**Verifies:** raven-builder.AC5.1 (full documents), AC5.3

**Files:**
- Modify: `src/raven_matrix/render/svg.py`
- Test: `tests/test_render_svg_documents.py` (unit)

**Consumer:** the CLI/app (Phase 7); the WASM app uses these directly (Phase 8).

**Implementation (ported layout):**
- `render_matrix_svg(matrix, settings=DEFAULT_RASTER) -> str`: a full `<svg>` with a viewBox sized by `(cell+gap)*cols+gap`, white background, a 3×3 grid of `render_cell_svg` groups translated to each cell's `(x,y)`; the bottom-right cell renders **blank white** (problem mode) per the upstream.
- `render_answers_svg(matrix, settings=DEFAULT_RASTER) -> str`: a full `<svg>`, **black** background, a 2×4 grid of the 8 answer-choice cells (indices 0–3 top row, 4–7 bottom), each via `render_cell_svg`.

**Testing (describe):**
- AC5.1: both functions return SVG that parses; the matrix SVG has 9 cell groups with the bottom-right empty; the answers SVG has 8 cell groups; viewBox dimensions match the layout formula. Render a matrix built (Phase 4) to include every shape/fill across cells and confirm all render.
- AC5.3: an answer set containing a blank-pad cell renders without error.

**Verification + commit:**
```bash
uv run pytest tests/test_render_svg_documents.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/render/svg.py tests/test_render_svg_documents.py
git commit -m "feat(render): render_matrix_svg + render_answers_svg (layouts)"
```
<!-- END_TASK_2 -->
<!-- END_SUBCOMPONENT_A -->

<!-- START_SUBCOMPONENT_B (task 3): raster -->

<!-- START_TASK_3 -->
### Task 3: `render/raster.py` — `rasterise` (raster extra)

**Verifies:** raven-builder.AC5.2

**Files:**
- Create: `src/raven_matrix/render/raster.py`
- Modify: `pyproject.toml` (`[project.optional-dependencies] raster = ["resvg_py>=..."]`)
- Test: `tests/test_render_raster.py` (unit; runs under CI's `--all-extras`)

**Consumer:** the CLI `--png` option (Phase 7); end users via `raven-matrix[raster]`.

**Implementation:**
- Add `resvg_py` to the `raster` extra. **Before coding, confirm the actual import + function name** from the installed package (`uv run python -c "import resvg_py; print(dir(resvg_py))"`) — the research suggested `svg_to_bytes(svg) -> bytes` but the version/API is unverified; use whatever the installed package actually exposes.
- `rasterise(svg: str) -> bytes`: SVG string → PNG bytes via `resvg_py`. Keep the import **inside** the function (so importing the core never requires the extra), and raise a clear `ImportError`-with-hint (`pip install raven-matrix[raster]`) if `resvg_py` is missing. **Do not add `from . import raster` (or any `rasterise` re-export) to `render/__init__.py`** — the Phase-8 import-hygiene test depends on `raster` being reachable only via the explicit `raven_matrix.render.raster` path.

**Testing (describe):**
- AC5.2: `rasterise(render_matrix_svg(m))` returns bytes beginning with the PNG magic `\x89PNG\r\n\x1a\n`; decoding (stdlib: parse the IHDR width/height, or just assert the magic + non-trivial length) confirms a real PNG. No pixel comparison.
- The core import path (`import raven_matrix.render.svg`) works with the `raster` extra absent (guard with a test that the svg module imports without `resvg_py`).

**Verification + commit:**
```bash
uv sync --all-extras  # ensure resvg_py present
uv run python -c "import resvg_py; print(dir(resvg_py))"  # diagnostic: confirm the real API surface before the test
uv run pytest tests/test_render_raster.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/render/raster.py pyproject.toml uv.lock tests/test_render_raster.py
git commit -m "feat(render): rasterise SVG->PNG via resvg_py (raster extra)"
```
<!-- END_TASK_3 -->
<!-- END_SUBCOMPONENT_B -->

---

## Phase 6 completion check

- [ ] Every shape (7) and fill (5) renders to well-formed SVG; White → `fill-opacity="0"`; 2px black stroke on each shape (AC5.1).
- [ ] `render_matrix_svg` (3×3, white bg, blank bottom-right) and `render_answers_svg` (2×4, black bg) parse and have the right cell counts (AC5.1).
- [ ] `rasterise` returns valid PNG bytes via `resvg_py` (AC5.2); core SVG import works without the extra.
- [ ] `render/__init__.py` does **not** import or re-export `raster`/`rasterise`; the `resvg_py` import lives only inside `rasterise` (Phase-8 import-hygiene dependency).
- [ ] A blank/empty cell renders without error (AC5.3).
- [ ] Tests assert semantics (well-formedness, elements, attrs, PNG magic) — never pixel parity.
- [ ] `uv run pytest`, `uv run ty check .`, `uv run ruff check .` clean.
