# Project Glossary

Ubiquitous language for this project. Every term here means the same thing in
code, docs, and conversation. (Bootstrapped from the design plan
`docs/design-plans/2026-06-08-raven-builder.md`.)

## Domain Terms

- **SGMT (Sandia Generated Matrix Tool)**: the upstream Java application being ported; this project ports its explicit-builder path.
- **Raven's Progressive Matrices**: a nonverbal reasoning test where a 3×3 grid of figures follows a visual rule and the test-taker picks which of eight options completes the bottom-right cell.
- **Structure code**: a compact string encoding a matrix's relational structure (e.g. `A1B2C4`); letters name relations, digits name directions, `X`/`Y`/`Z` name OR/AND/XOR.
- **Base relation**: the primary rule across a layer — ShapeRepetition or Logical OR/AND/XOR.
- **Supplemental relation**: a feature-level rule layered on the base — Rotation, Scaling, FillPatternRepetition, ChangeFillPattern, or TranslationalNumerosity.
- **Location transform**: the cell-traversal pattern determining which cells share a feature — Horizontal, Vertical, the two diagonals, and TopLeftCornerOut, selected by direction digits 1–5 via the `make_location_transform` factory. Plus **Logic**, a *partial* transform that seeds the 2×2 top-left block and does not traverse (`next_location`/`parent_location` raise `NotImplementedError`); it is chosen by the structure layer, not a direction digit, so the factory never returns it. Each exposes `base_locations()` / `next_location()` / `parent_location()`.
- **Labeller**: the function reading a `Matrix` back to its `Structure` code (ported from the upstream difficulty classifier's scoring logic). Inverse: `parse_code`.
- **Structural oracle**: the test that parses each published `Structure` code → builds → labels → checks the label matches; a consistency check, anchored by a hand-derived label table.
- **Hand-derived label table**: ~12 config→expected-label pairs derived from the Matzen paper's naming convention + the published codes (independent of the Java source); the primary correctness anchor.
- **Compat toggle**: a named flag exposing a known code-vs-design divergence; default is faithful-to-code.
- **Difficulty classifier**: SGMT's 37-feature difficulty predictor; deferred out of v1. Its serialized form (`SerializedMatrixSGMDifficultyClassifier.xml`, loaded by the upstream `SGMMatrixSetGeneratorTest`) is **not shipped** in the source distribution, so the upstream test cannot run as-shipped — reinforcing the deferral (see `constraints.md` → Known data anomalies).
- **Stimulus Name (join key)**: the PNG basename that joins a norming-oracle row to its stimulus. Unique except for `A4_1`, which appears twice with the same `Structure` (`A4`) but different `Correct Answer` (2 vs 1) — a known 1:2 anomaly (see `constraints.md`).

## Technical Terms

- **JavaRandom / java.util.Random**: the JVM's 48-bit LCG PRNG, re-implemented in Python for identical seeded sequences (`nextInt(bound)`, `nextBoolean`).
- **marimo**: a reactive Python notebook/app framework whose apps export to a static WASM HTML bundle (`marimo export html-wasm`).
- **WASM / Pyodide / micropip**: WebAssembly runs compiled code in the browser; Pyodide is CPython-on-WASM; micropip installs pure-Python wheels from PyPI into it.
- **FCIS (Functional Core / Imperative Shell)**: pure logic in an import-light core; I/O, UI, CLI, rasterisation at the edges in their own dependency groups.
- **uv dependency groups**: uv's named optional dependency sets, keeping the core zero-dependency (`raster`, `ui`, `cli`, reserved `difficulty`).
- **SVG-canonical rendering**: SVG is the primary render artifact; PNG is produced on demand via the optional `raster` group; the browser renders SVG natively.

## Abbreviations

| Abbreviation | Full Form | Context |
|-------------|-----------|---------|
| SGMT | Sandia Generated Matrix Tool | the upstream application being ported |
| SGM | Sandia Generated Matrix | the matrix data model / Java package |
| FCIS | Functional Core / Imperative Shell | the architectural pattern |
| WASM | WebAssembly | the in-browser runtime for the marimo app |
| LCG | Linear Congruential Generator | the algorithm behind `java.util.Random` |
| DoD | Definition of Done | the design plan's acceptance bar |

## Deprecated Terms

| Old Term | Replaced By | Since | Reason |
|----------|-------------|-------|--------|
| (none yet) | | | |
