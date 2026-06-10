# Code Review Findings — phase-7-task-3

## Status: APPROVED

**Critical: 0 | Important: 1 | Minor: 2**

## Verification

```
Tests (no extras): uv run pytest → 1028 passed
Tests (ui extra):  uv run --extra ui pytest → 1028 passed
Type check:        uv run ty check . → All checks passed
Lint:              uv run ruff check . → All checks passed
```

## Plan Alignment

- N1 (FCIS extract + controls-beside-output): ✓ implemented. Pure logic moved to `appsupport.py`; `app.py` is a thin reactive shell; `mo.hstack([controls_panel, output])` in `_layout`; dead `mo.sql` cell gone.
- N2 (option reference): ✓ implemented. `option_reference()` is pure markdown; rendered in `mo.accordion`; completeness test iterates real enums.
- N3 (save controls): ✓ implemented. `compose_save_svg` + three `mo.download` buttons + three header checkboxes.
- N4 (triangle investigation only): ✓ correctly absent — no speculative renderer change.
- N5 (README): ✓ implemented. Stale "no code yet" replaced with accurate install/run/oracle/hosting docs.

## Strengths

- FCIS boundary is clean. `appsupport.py` imports nothing from marimo, typer, or any I/O layer. The core import graph is unidirectional: `appsupport` → core; `app.py` → `appsupport` + core renderers; nothing imports `app.py`. Confirmed by AST scan and manual inspection.
- `build_outcome` preserves the prior app behaviour exactly. Every `ValueError` path (logic base + supplementals, >3 supplementals, position outside 1–8, malformed code) returns `BuildOutcome(matrix=None, error=..., structure_code=None)` and the shell renders it as a friendly message. The success path sets all three fields. Tests cover each branch.
- SVG composition is robust for the current renderer. Verified: `render_matrix_svg` and `render_answers_svg` emit `width` before `height` in the opening `<svg>` tag; `RasterSettings` fields are `int` so the dimensions are always integers matching `\d+`; each rendered document contains exactly one `</svg>` so `rindex` is unambiguous. All three `compose_save_svg` variants parse as well-formed XML (ET.fromstring verified in tests).
- Completeness test genuinely guards drift. It iterates `BaseRelation`, `Direction`, and `Supplemental` by calling `list(Enum)` at test time — not a hardcoded list — so adding an enum member without documenting it breaks CI. It also checks every control label string present in the GUI.
- Option maps moved cleanly. The three dicts (`RELATION_OPTIONS`, `DIRECTION_OPTIONS`, `SUPPLEMENTAL_OPTIONS`) are module-level constants in `appsupport.py`; `app.py` imports them and passes them to `mo.ui.dropdown(options=...)` so marimo's read-back value is already the mapped enum. No conversion in the shell.
- Variable-name swap in `make_layer_controls` fixed (the outer loop parameter was renamed from `slot` → `index` and the inner comprehension variable from the conflicting outer name). The result is clearer and the keys (`supp1/2/3`) are stable.

## Issues

### Important (count: 1)

- **Issue**: `_SVG_OPEN_RE` requires `width` to appear before `height` in the opening `<svg>` tag. The regex `^<svg\b[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"[^>]*>` silently falls through to the `pragma: no cover` guard if the renderer ever emits `height` before `width`. Today this matches because both renderers write `width="{width}" height="{height}"` in that order (verified). But the coupling is undocumented and fragile: any refactor of `render_matrix_svg` / `render_answers_svg` that swaps attribute order would cause `compose_save_svg` to raise at runtime with a message pointing at a renderer-contract violation, rather than a clear mismatch.
- **Location**: `src/raven_matrix/appsupport.py` line 926–927 (`_SVG_OPEN_RE`), plus the `_svg_parts` docstring (line 937–950) which describes the contract but does not name the ordering assumption.
- **Fix**: Either (a) add a comment on `_SVG_OPEN_RE` explicitly stating it assumes `width` precedes `height` and noting which renderer lines guarantee that, so a future maintainer knows what to update if the renderer changes; or (b) use two separate single-attribute captures with `re.search` rather than a single anchored match, which tolerates either order. Option (a) is the minimal change; option (b) removes the fragility entirely. A one-line note on the constant suffices for now given the renderer is in the same repo and tested.

### Minor (count: 2)

- **Issue**: `_svg_parts` uses `rendered.rindex("</svg>")` to locate the end of the inner body. This is correct today (one `</svg>` per rendered document, verified). The comment at line 945 (`# pragma: no cover - guards a render contract change`) explains the `match is None` guard but there is no parallel note explaining why `rindex` is safe (i.e. that the renderer never emits nested `<svg>` elements). The reasoning is implicit.
- **Location**: `src/raven_matrix/appsupport.py` line 949 (`rendered[match.end() : rendered.rindex("</svg>")]`)
- **Fix**: Add a brief inline comment — e.g. `# rendered SVG contains exactly one </svg> (no nested <svg>); rindex is unambiguous` — so the assumption is visible next to the code.

- **Issue**: In `_save` in `app.py`, `_svg` is a closure over `outcome.matrix` and `header_fields` defined inside the `else` branch, then called three times immediately to produce the three download payloads. This is correct and not a bug. However, because `mo.download` receives a `str` (already materialised), the three SVGs are rendered at cell-evaluation time even when the researcher does not click save. For a typical 340×340 + 450×230 composition this is negligible, but the pattern diverges slightly from the lazy-data idiom (`mo.download` also accepts a callable). Not worth changing now; worth noting if the app is extended with raster output.
- **Location**: `app.py` lines 523–560 (`_save` cell, the `_svg` closure and the three `mo.download` calls)
- **Fix**: No action required now. If PNG output is added (raster extra), consider passing a callable to `mo.download` so the rasterisation happens only on click.

## Consolidation Opportunities

None visible in the diff context.

## Decision: APPROVED FOR MERGE
