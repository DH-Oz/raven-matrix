# Code Review Findings — pre-merge

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 1**

## Verification

```
Tests:  uv run --all-extras pytest -q  → 327 passed in 0.37s
Lint:   uv run ruff check .            → All checks passed!
Types:  uv run ty check .              → All checks passed!
```

## Plan Alignment

- AC5.1 (SVG well-formedness, every shape + fill, correct alpha): ✓ carried over intact
- AC5.1 rotation fitness (emit degrees directly): ✓ carried over intact
- AC5.2 (rasterise → PNG): ✓ carried over intact
- AC5.3 (blank/empty cell renders without error): ✓ carried over intact
- `render/__init__.py` free of raster imports: ✓
- `resvg_py` import inside `rasterise` only: ✓
- `RasterSettings` default 256→100 to match `builder.CELL_PIXEL_SIZE`: ✓ (reconciliation closes ADR-0001 check #3)
- `_shape_body` now takes `(shape, px, py, width, height)` from `feature.width`/`feature.height`: ✓ (reconciliation closes ADR-0001 check #1)
- `_base_size` deleted: ✓
- `settings` param dropped from `render_feature_svg`: ✓
- model.py / builder.py / surface.py untouched by render commits: ✓
- Tools/harness in `tools/`, not shipped code, `previews/` gitignored: ✓

## Review by Focus Area

### 1. Reconciliation correctness (d4bcbc9)

**BASE→width/height geometry.** `_shape_body` now accepts `(shape, px, py, width, height)` and derives `hw = width / 2.0`, `hh = height / 2.0`. Every per-shape formula then uses `hw`/`hh` identically to the previous `hw = BASE`, `hh = BASE` construction — the only structural change is where the half-extents come from. Diamond's `qh = hh / 2.0`, Tee's `qw = w / 4.0` / `qh = h / 4.0`, Trapezoid's `qw = hw / 2.0` are all preserved verbatim. Line uses `hw` only (`height` is explicitly documented as unused), consistent with the Java `LineSGMSurfaceFeature.createLine` where only the length matters and rotation comes from the transform. The per-shape formulas are faithfully unchanged.

**Cell-size contract.** `builder.CELL_PIXEL_SIZE = 100` (builder.py:88). `RasterSettings.cell_pixel_size` defaults to `100` (svg.py:84). The docstring on `RasterSettings` states the matching rationale explicitly. The renderer does not import `builder` — the contract is honoured by value equality of the two constants, not by a runtime check. This is the stated design (dependency-light renderer); it is sound.

**No cross-dependency.** `grep` of `render/svg.py` and `render/raster.py` for any `builder` import returns no matches. The render subsystem remains import-clean.

### 2. Test-intent preservation

All invariant-guard tests from the renderer branch survive the reconciliation and their intent is intact:

- **`test_default_raster_has_documented_sizing`** — asserts `cell_pixel_size == 100` and `pixels_between_cells == 10`. This is now a contract test for the reconciliation: it would catch a revert of the 256→100 change.
- **`test_scale_lives_in_transform_not_geometry`** — renders the same shape at `scale=1.0` and `scale=0.66`; asserts geometry attributes are identical and only the `scale(...)` term in the transform differs. This directly guards the invariant that `feature.scale` is not baked into the path. The test uses concrete `width=height=128` features, so it exercises the new `_shape_body(shape, px, py, width, height)` signature, not a settings-derived BASE.
- **`test_off_centre_position_drives_geometry_and_transform_pivot`** — renders at `Point(64.0, 192.0)`; asserts `cx/cy` reflect that position and the transform pivots on it. Still asserts its invariant correctly under the 7-arg model: `rx/ry` come from `width/height=128` independent of position.
- **`test_rotation_degrees_emitted_directly_as_svg_rotate`** / **`test_rotation_45_degrees_emitted_directly`** — unchanged, both still fire on the old double-conversion bug.
- **`test_answers_svg_has_eight_white_cell_background_rects`** / **`test_answers_svg_white_fill_shape_has_cell_bg_rect`** — the white-answer-cell-bg tests assert the `<rect class="cell-bg">` is the first child of each answer `<g>` (before features). These pass; the implementation (`_positioned_answer_cell`) correctly emits `white_bg` before `render_cell_svg(...)`.
- **`test_matrix_svg_bottom_right_cell_is_blank`** — asserts the 9th cell group's inner `<g>` has no children. Passes; the blank-bottom-right is hardcoded.

All tests verify emitted SVG structure, not mocks. No test was reduced to a weaker assertion during the reconciliation. The geometry-pinned tests (ellipse/rectangle/line/diamond/triangle/trapezoid/tee) now use `width=height=128` (hw=hh=64) explicitly rather than deriving from a settings-based BASE; the expected coordinate values are recomputed from those dimensions, which is correct.

One minor observation about the raster test helper (not a fault): `test_rasterise_returns_nontrivial_png` asserts `len(png) > 100`. For a rendered 330×330 matrix PNG this is safe by many orders of magnitude, but the threshold communicates nothing useful about "non-trivial". This is a nit only — the PNG magic + IHDR dimension tests alongside it provide the real semantic coverage.

### 3. Merge integrity

- No conflict markers in `src/` or `tests/` (grep clean).
- `model.py` and `builder.py`: not present in the diff at all — untouched by all three commits.
- `render/__init__.py`: 12-line docstring, zero import statements. Clean.
- `render/svg.py`: imports `from __future__ import annotations`, `dataclasses.dataclass`, and `from raven_matrix.model import Cell, Fill, Matrix, Shape, SurfaceFeature`. No `resvg_py`, no `builder`, no `raster`.
- `render/raster.py`: `resvg_py` import is inside `rasterise()` only, wrapped in `try/except ImportError` with a clear hint message. Module-scope is clean.
- `uv.lock`: `resvg-py==0.3.2` added with full wheel hashes. `pyproject.toml` `raster` extra updated from placeholder to `resvg-py>=0.3.2`. Consistent.

### 4. Tool (05e39bd) — import hygiene and basic quality

`tools/render_preview.py` imports `from raven_matrix.render.raster import rasterise` explicitly — it does not import via `render.__init__`, which would have been a hygiene signal. The `resvg_py` import never reaches the core path. The tool is not on the shipped import path (`tools/` is not a package). No `sys.path` manipulation.

The tool correctly uses `DEFAULT_RASTER` (100px) for the `build` mode previews, which is right — `build()` emits positions in the 100px cell space.

## Issues

### Minor (count: 1)

- **Issue**: In `tools/render_preview.py`, the gallery mode uses `GALLERY = RasterSettings(cell_pixel_size=200)` but `_CENTRE = Point(100.0, 100.0)` is hard-coded as the default feature position. A 200px cell has its centre at `(100.0, 100.0)` — which happens to be numerically correct for a 200px cell. However, the comment on line 47 reads `"centre of the 200px gallery cell"` and `100.0` is indeed half of 200, so the value is right by coincidence of arithmetic. On closer inspection this is not wrong — `100.0 = 200 / 2` is the correct centre — but the feature size defaults (`w=120.0, h=120.0`) and cell size (200px) are independent choices that are nowhere verified to be consistent, and the comment could mislead a future editor into thinking 100.0 is the builder cell size (which it also equals). A clearer constant name such as `_GALLERY_CENTRE = Point(100.0, 100.0)` or deriving it from `GALLERY.cell_pixel_size // 2` would make the intent unambiguous.
- **Location**: `tools/render_preview.py:47`
- **Fix**: Rename `_CENTRE` to `_GALLERY_CENTRE`, or derive it: `_GALLERY_CENTRE = Point(GALLERY.cell_pixel_size / 2, GALLERY.cell_pixel_size / 2)`. This is a dev harness; it does not affect any shipped code or test behaviour.

## Open Contract Items (carry-forward, not review blockers)

These are documented in ADR-0001 and are not regressions introduced by this integration. They remain as Phase-7/8 verification tasks:

1. **Scale/BASE contract** (ADR-0001 check #1, partially closed): the reconciliation establishes that `feature.width`/`feature.height` are the authoritative size source, but `build()` must emit those fields in the same 100px cell space the renderer expects. The `render_preview.py` `build` mode is the first end-to-end exercise of this contract. Visual UAT in Phase 7 provides the human-judgment half.
2. **Multi-feature paint order** (ADR-0001 check #2): SVG document order = painter's model. Untested with real multi-layer output; deferred to Phase 7.
3. **Rotation unit cross-phase** (ADR-0001 check #4): renderer emits degrees directly; `build()` must store rotation in degrees. Unverified end-to-end; deferred to Phase 7.

## Decision: APPROVED FOR MERGE
