# Dependency Rationale

Falsifiable justifications for every direct dependency. Each entry records why
the package was added, what evidence supports its use, and who it serves.

Maintained by design plans (when adding deps) and controlled-dependency-upgrade
(when auditing). Reviewed by restate-our-assumptions (periodic philosophical
audit).

> **Core has zero runtime dependencies by design.** The generation/render core
> (`raven_matrix` minus the CLI/UI/raster edges) imports only the Python
> standard library, keeping it WASM-loadable and import-light. Everything below
> lives in an optional uv dependency group, not in `[project.dependencies]`.

## typer
**Added:** 2026-06-08
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phase 7, `cli` group)
**Claim:** The thin CLI (`raven_matrix/cli.py`) needs argument parsing for `build` (from a `--code` or explicit relation/direction flags) and `oracle`; typer provides typed subcommands with less boilerplate than argparse.
**Evidence:** `raven_matrix/cli.py` (to be created in Phase 7).
**Serves:** developers and researchers running the generator from the shell.

## marimo
**Added:** 2026-06-08
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phases 7–8, `ui` group)
**Claim:** The interactive option-parity UI is a marimo reactive app whose `marimo export html-wasm` produces a static, server-less WASM bundle deployable to GitHub Pages — the lowest-drama path to an in-browser UI (chosen over Jupyter+ipywidgets in DR4).
**Evidence:** `app.py` (to be created in Phase 7); the WASM export + Pages deploy in Phase 8.
**Serves:** researchers using the tool interactively, locally and (stretch) online.

## pytest
**Added:** 2026-06-08
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phase 1, `dev` group)
**Claim:** The test suite (pinned transform spec, JavaRandom vectors, the 840-code oracle, determinism, rendering, toggles) runs under pytest.
**Evidence:** `tests/` (created from Phase 1 onward).
**Serves:** developers, CI.

## hypothesis
**Added:** 2026-06-08
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phase 5, `dev` group)
**Claim:** Property tests (`parse_code∘label` round-trips over generated valid codes; `build` never crashes across the option space) need generated inputs that example-based tests miss.
**Evidence:** property tests in `tests/` (Phase 5).
**Serves:** developers (correctness confidence on the labeller/parser pair).

## ruff
**Added:** 2026-06-08
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phase 1, `dev` group)
**Claim:** Linting and formatting are enforced in CI; ruff is the project's single lint+format tool.
**Evidence:** `pyproject.toml` ruff config; the CI workflow (Phase 1).
**Serves:** developers, CI.

## ty
**Added:** 2026-06-08
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phase 1, `dev` group)
**Claim:** Static type checking is enforced in CI; `ty` is the project's type checker for Python 3.14.
**Evidence:** `pyproject.toml` ty config; the CI workflow (Phase 1).
**Serves:** developers, CI.

## SVG→PNG rasteriser (selection deferred to Phase 6)
**Added:** 2026-06-08 (planned, not yet selected)
**Design plan:** docs/design-plans/2026-06-08-raven-builder.md (Phase 6, `raster` group)
**Claim:** Rasterising the canonical SVG to PNG on demand needs one rendering library (candidate: cairosvg or a resvg binding); kept in the optional `raster` group so the core stays pure-Python and the browser path needs no Python rasteriser.
**Evidence:** `raven_matrix/render/raster.py` (to be created in Phase 6); the exact package chosen and pinned then.
**Serves:** users needing bitmap output offline.

---

**Dev-tool note (not declared deps):** `tools/extract_oracle.py` reads the
upstream `.xls` using pandas + xlrd, run ephemerally via `uv run --with pandas
--with xlrd`; the output (`data/ravens_oracle.csv`) is committed so the test path
stays stdlib-only.

**Reserved (deferred, not added):** the `difficulty` group (numpy, scikit-learn,
pandas) is reserved for the deferred difficulty subsystem and is not a current
dependency.
