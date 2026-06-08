# Personae

User types, their goals, access patterns, and constraints. (Bootstrapped from the
design plan `docs/design-plans/2026-06-08-raven-builder.md`.)

## Researcher

**Role:** A cognitive/psychology researcher who uses SGMT-style matrices to build or reproduce study stimuli ("use the software as it was to produce studies as they were"). The primary user.

**Goals:**
- Construct specific matrix structures (by `Structure` code or by choosing relations/directions/layers) faithfully matching the original SGMT behaviour.
- Reproduce or extend the Matzen et al. (2010) norming-set structures.
- Get SVG (and on-demand PNG) of the matrix + its eight answer choices.

**Access patterns:**
- The Python library API (`build`, `build_from_code`, `label`, `parse_code`, `render_*`).
- The thin typer CLI (batch / scripted use).
- The marimo app (interactive option-parity panel), locally or — stretch — hosted in-browser via WASM.

**Constraints:**
- Reproduces *structure* faithfully; exact shapes/distractors/pixels are not reproducible (unpublished seeds) and are out of the equivalence bar.
- Difficulty norming is out of v1 scope.

**Key scenarios:**
1. "Build `A1B2C4` with seed 42, give me the SVG and the answer key."
2. "Set up a 2-layer matrix with shape-repetition horizontal + a vertical fill-pattern relation, vary the seed, eyeball the result in the app."
3. "Check that the port reproduces all 840 norming `Structure` codes."

## Developer

**Role:** A maintainer porting/extending the library.

**Goals:**
- Keep behaviour faithful to the upstream code (verified by the test suite).
- Add compat toggles as code-vs-design divergences surface.
- Eventually add the deferred difficulty subsystem without touching the core.

**Access patterns:**
- The test suite (pytest, Hypothesis), CI (ruff, ty), the oracle harness, and the best-effort Java golden differential.

**Constraints:**
- Must not edit `upstream/Matrices/` (immutable reference).
- Core stays pure-Python / import-light (WASM-loadable).

**Key scenarios:**
1. "A new file reveals a divergence between code and intent — add a named compat flag (default faithful-to-code) and document it."
2. "Run the 840-code oracle and the hand-derived label table after changing the labeller."

## Persona Relationships

The Developer builds and verifies the tool the Researcher uses. They share the
same library; the Researcher consumes its public API/CLI/app while the Developer
owns the tests, toggles, and the deferred-subsystem roadmap.
