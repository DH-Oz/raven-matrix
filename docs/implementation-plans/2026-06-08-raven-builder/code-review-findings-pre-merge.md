# Code Review Findings — pre-merge
# Pre-Merge Cross-Phase Integration Review (raven-builder → main)
# Supersedes earlier per-phase pre-merge file written during Phase 6.

## Status: APPROVED

**Critical: 0 | Important: 1 | Minor: 2**

## Verification

```
Tests (no extras):        uv run pytest                     → 1029 passed in 1.12s
Tests (ui extra):         uv run --extra ui pytest           → 1029 passed in 1.11s
Type check:               uv run ty check .                  → All checks passed!
Type check (ui extra):    uv run --extra ui ty check .       → All checks passed!
Lint:                     uv run ruff check .                → All checks passed!
```

All five gates green. Zero failures, zero skips, zero type errors, zero lint warnings.
No TODO/FIXME/type-suppression annotations anywhere in `src/raven_matrix/` or `app.py`.

## Plan Alignment

- SVG-canonical render (CLAUDE.md invariant): confirmed — render/svg.py is the canonical path; raster is optional-extra only, never at module scope in core.
- Core import hygiene / Pyodide-readiness invariant: confirmed — see FCIS section.
- Data/logic equivalence bar (not pixel reproduction): honoured — oracle.round_trip tests structure + correct-answer position for all 840 oracle rows.
- Option parity with upstream SGMBuilderFrame: confirmed — ui_config.config_from_controls covers all upstream controls; app.py delegates to appsupport.
- ADR-0002 constant-carrier: confirmed — see dedicated section.
- 1029 tests passing across all phases.

## FCIS / Import Hygiene

The core is clean. Layering is strictly one-directional:

    model → structure/transforms/surface/fillpattern/rng/compat
          → builder → label → oracle
          → ui_config → appsupport → {cli.py, app.py}
    render/svg (core leaf, imports model only)
    render/raster (edge leaf, optional extra)

Verified by grep:

- Zero back-imports of cli into any core module.
- Zero marimo imports outside app.py.
- Zero typer imports outside cli.py.
- raster import in cli.py is a deferred `try/import` inside `_rasterise_or_exit()` (cli.py:194), never at module level. Correct guard pattern.
- appsupport.py imports `render/svg` directly — correct, svg is a core leaf.
- render/svg.py imports only `raven_matrix.model`. No builder, no raster, no cli.

## ADR-0002 Constant-Carrier Path

`base_constant_shape` has exactly one write site: `label.py:_parse_segment()`, set only when a supplemental-led code triggers the implicit ShapeRepetition injection (label.py:374 default False, label.py:402 set True). It flows into `LayerConfig.base_constant_shape` (builder.py:132), consumed at builder.py:294 as the `constant=` argument to `_build_shape_repetition`. No other module reads or writes this field. The path is consistent and uncontradicted across the full package.

## API Consistency Across Module Seams

All seams are coherent with no signature drift:

- `build()` / `build_from_code()` / `BuilderConfig` (Phase 4): consumed identically by oracle.py, appsupport.py, and cli.py with the same `(config, seed)` / `(code, seed)` signatures.
- `label()` / `parse_code()` (Phase 5): oracle.py uses both; appsupport.py uses `label` for display; cli.py uses `label` for stderr reporting. All consistent.
- `render_matrix_svg` / `render_answers_svg` (Phase 6): called by appsupport.py and cli.py with identical `(matrix, settings=DEFAULT_RASTER)` signatures.
- `oracle.round_trip` / `build_pass_map` (Phase 5/7): cli.py oracle command calls `build_pass_map(rows)` correctly — CLI owns CSV I/O, oracle module stays pure.
- `config_from_controls` / `LayerControls` (Phase 7): shared between cli.py and appsupport.py via ui_config with no duplication of the mapping logic.

## Packaging Coherence

- `[project.optional-dependencies]`: raster / ui / cli / difficulty extras declared. Clean.
- `[project.scripts]`: `raven-matrix = "raven_matrix.cli:app"` — correct target. Typer is in the `cli` extra, not base deps; a bare install produces a broken entry point (see Minor issue below).
- `[tool.hatch.build.targets.wheel.force-include]`: `"data/ravens_oracle.csv" = "raven_matrix/data/ravens_oracle.csv"` — matches `_oracle_csv_path()` (cli.py:55, importlib.resources path). Source-tree fallback at cli.py:60 is consistent. Both paths verified.
- `requires-python = ">=3.12"`, `ruff target-version = "py312"`, `ty python-version = "3.12"`: consistent Pyodide floor, documented in comments.
- `exclude-newer = "2026-06-02T00:00:00Z"`: absolute date — correct, overrides any user-level relative span for reproducible CI locks.

## Issues

### Critical (count: 0)

None.

### Important (count: 1)

- **Issue**: cli.py re-implements the build-and-render orchestration that appsupport.build_outcome already encapsulates. The cli `build` command (cli.py:159-181) performs: parse code or assemble config → call build → call render_*_svg → call label. This is the same four-step sequence as appsupport.build_outcome (appsupport.py:295-320) plus compose_save_svg. The duplication is currently shallow — both delegate immediately to the same core calls with no diverged branching logic — but it creates two maintenance targets for the same operation.
- **Location**: `src/raven_matrix/cli.py:159-181` vs `src/raven_matrix/appsupport.py:295-320`
- **Fix**: Have cli.py's build command call `build_outcome()` from appsupport, then extract SVG from `BuildOutcome.matrix`. This collapses the duplication and ensures CLI and app stay in lockstep when orchestration logic evolves. Not a correctness risk at current scope; raise priority if Phase 8 adds complexity to the build path.

### Minor (count: 2)

- **Issue**: `[project.scripts]` declares `raven-matrix` pointing at `raven_matrix.cli:app`, but `typer` is only in the optional `cli` extra. A bare `pip install raven-matrix` (without `[cli]`) installs the entry point but it fails at runtime with ImportError. This is a distribution-time footgun for anyone installing from PyPI without reading the extras documentation.
- **Location**: `pyproject.toml` — `[project.scripts]` block
- **Fix**: Add a prominent note to the README (or pyproject description) that the entry point requires `pip install raven-matrix[cli]`. Alternatively, move the script declaration so it is only advertised when the extra is present. Not a blocker — the project is not yet on PyPI — but address before any public release.

- **Issue**: `src/raven_matrix/__init__.py` exports nothing beyond `__version__`. All consumers must import from submodules directly. This is valid at v0.1.0, but Phase 8 (Pyodide/WASM) will need a stable browser entry point. Without a declared public API in `__init__.py`, there is no pinned surface for the WASM wrapper to depend on.
- **Location**: `src/raven_matrix/__init__.py`
- **Fix**: Before Phase 8, decide which symbols constitute the public API (at minimum: `build`, `build_from_code`, `BuilderConfig`, `render_matrix_svg`, `render_answers_svg`) and re-export them from `__init__.py`. Not blocking for this merge.

## Decision: APPROVED FOR MERGE

No critical issues. The integration layer is coherent across all seven phases: FCIS boundaries are clean, ADR-0002 constant-carrier is consistently honoured, all five verification gates pass at 1029 tests, and there is no dead code, TODO/FIXME, or type suppression anywhere in the code surface. The one Important finding (cli/appsupport orchestration duplication) is shallow and carries no correctness risk at current scope; it is a Phase 8 prep item.
