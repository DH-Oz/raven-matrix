# raven-builder — Test Requirements (AC → verification map)

Maps every acceptance criterion (AC1.1–AC7.3) from
`docs/design-plans/2026-06-08-raven-builder.md` to the automated test(s),
operational check, or UAT entry that verifies it. Each row names the test type,
the expected test file (owned by the phase that implements it), the implementing
phase, and what the verification asserts.

**Test-type legend:**

- **unit** — value-pinned or example-based assertion on one component.
- **property** — Hypothesis-generated invariant over many inputs.
- **integration** — exercises several components end-to-end (build→label→render, CLI).
- **operational** — a recorded command outcome / served-bundle / micropip check, not a pytest assertion.
- **UAT** — human-judgment verification (live parity, visual recognisability, in-browser feel); recorded in `uat-requirements.md`.

**Key framing carried from the plan (not contradicted here):**

- AC1.* parity is exercised structurally in **Phase 4** and re-exercised through the interfaces in **Phase 7**; the *live* parity judgment is **UAT**, not automated.
- AC2.1 (hand-derived table) is the hard correctness gate, verified in **Phase 5** (moved from Phase 4 per DR4).
- AC5.* assert SVG well-formedness / PNG validity, **never pixel parity**.
- AC7.1/AC7.2 are **operational**; AC7.3 is **stretch/operational**; the in-browser feel is **UAT**.

---

## AC1 — Option parity with SGMBuilderFrame

| AC | Text | Type | Test file | Phase | Asserts |
|----|------|------|-----------|-------|---------|
| AC1.1 | `build()` accepts a 1-layer config (base relation + direction + ≤3 supplementals with directions, correct-answer position, seed) and returns a 3×3 Matrix with 8 answer choices. | unit + property | `tests/test_builder_build.py` (also `tests/test_builder_layers.py`, `tests/test_builder_answers.py`) | 4 | A 1-layer config builds a 3×3 grid with exactly 8 answer choices; property test over random valid configs holds. Re-exercised through CLI in Phase 7 (`tests/test_cli.py`). |
| AC1.2 | A 2-layer config composes both layers per cell. | unit | `tests/test_builder_layers.py` | 4 | 2-layer cells contain both layers' features (concatenation; feature count = sum). |
| AC1.3 | Every BaseRelation, every Supplemental, and every Direction (1–5) is settable and realised. | unit (parametrised) | `tests/test_builder_build.py` | 4 | Parametrised over each BaseRelation × Supplemental × Direction; each builds and the layer's structure features/directions match the config (direct structural inspection per DR4). Re-exercised through CLI/`config_from_controls` in Phase 7. |
| AC1.4 | An invalid config (>3 supplementals, position ∉ 1–8, or a diagonal/logic transform on an even/non-square grid) raises a clear error. | unit | `tests/test_builder_layers.py` | 4 | >3 supplementals, position 0/9, logic-base+supplemental each raise `ValueError`; grid constraint inherited from Phase 3 transforms. |
| AC1.5 | Value-equal-but-distinct `SurfaceFeature`s are distinct under identity; `value_equals()` is true for them where upstream hand-rolls a value check (DR7). | unit | `tests/test_model_features.py` | 2 | Two equal-valued features are `!=` and `not in [a]` (identity); `a.value_equals(b)` is True; `contains_check` finds value-equal members, skips `None`. |
| AC1.* (live parity) | The marimo app exposes every `SGMBuilderFrame` option and re-renders coherently on change. | **UAT** | `uat-requirements.md` (option-parity entry; smoke: `tests/test_app_importable.py`) | 7 | Human sets each control across its range and judges every GUI option is present and a change re-renders a coherent puzzle. Wrong if a GUI option is missing, a change doesn't update, or the figure is incoherent. |

---

## AC2 — Labeller correctness + structural consistency

| AC | Text | Type | Test file | Phase | Asserts |
|----|------|------|-----------|-------|---------|
| AC2.1 | (Primary anchor) The hand-derived label table (~12 configs) matches expected labels from the Matzen naming convention + published codes (independent of the Java source). | unit | `tests/test_hand_derived_labels.py` (data: `tests/data/hand_derived_labels.py`) | **5** | For each entry, `label(build(config, seed=0)) == expected_code`, where `expected_code` is hand-derived from the paper convention + published codes/PNGs, not from the Java labeller. **The hard correctness gate.** |
| AC2.2 | (Consistency) All 840 `Structure` codes round-trip (code→config→matrix→label→code) outside the documented exclusion list. | integration (parametrised pass-map) | `tests/test_oracle_sweep.py` (data: `data/ravens_oracle.csv`; exclusions: `docs/oracle_exclusions.md`) | 5 | Over the 553 distinct codes: every failing code must appear in `docs/oracle_exclusions.md` with an inspected reason; no stale exclusions; logic codes pass via normalisation. Reports N_pass/553 + row coverage/840. |
| AC2.3 | (Edge) Logic codes (`X`/`Y`/`Z`) parse and label correctly despite carrying no direction or surface detail. | unit + property | `tests/test_parse_code.py` (cross-checked in `tests/test_oracle_sweep.py`) | 5 | `parse_code("X"/"Y"/"Z")` builds a logic config that labels to `X7`/`Y7`/`Z7` and normalises back to the bare code. |
| AC2.4 | (Failure) A malformed code raises a clear parse error. | unit | `tests/test_parse_code.py` (CLI surface: `tests/test_cli.py`) | 5 | `parse_code("Q9")`, `""`, `"A"` (missing digit) raise `ValueError`; surfaced as non-zero CLI exit in Phase 7. |

---

## AC3 — Location-transform spec

| AC | Text | Type | Test file | Phase | Asserts |
|----|------|------|-----------|-------|---------|
| AC3.1 | The ported TopLeftCornerOut transform produces the exact hardcoded coordinate sequences for all 8 matrix sizes from the JUnit test. | unit (value-pinned) | `tests/test_transforms_corner_out.py` | 3 | For each of 8 sizes: `base_locations`, full `next_location` traversal (wraps to `(0,0)`), and `parent_location` sequence equal the pinned JUnit values; `parent_location((0,0))` raises. |
| AC3.2 | Horizontal, Vertical, and both diagonals produce their correct base/next/parent sequences. | unit | `tests/test_transforms_axis.py`, `tests/test_transforms_diagonal.py` | 3 | Pinned base/next/parent on a 3×3 for each; Vertical's upstream parent-wrap bug reproduced verbatim with a bug-witness test. |
| AC3.3 | (Failure) A diagonal/logic transform on a non-odd-square grid is rejected (matching the upstream constraint). | unit | `tests/test_transforms_diagonal.py`, `tests/test_transforms_logic.py` | 3 | Diagonals reject even/non-square sizes (`ValueError`); Logic rejects `<3×3`; valid odd-square / ≥3×3 do not. |

---

## AC4 — Determinism

| AC | Text | Type | Test file | Phase | Asserts |
|----|------|------|-----------|-------|---------|
| AC4.1 | (Success) Same config + seed produces an identical Matrix across two runs. | unit | `tests/test_builder_build.py` | 4 | `build(config, seed)` twice → deep-equal matrices (structure + per-feature values + answer cells by value), for several configs. |
| AC4.2 | (Success) `JavaRandom` reproduces known `java.util.Random` vectors for `nextInt(bound)` (incl. power-of-two and rejection-loop edges) and `nextBoolean`. | unit (golden-vector) | `tests/test_rng.py` (fixture: `tests/fixtures/java_random_vectors.json`) | 2 | Every fixture block matches; explicit edges: bound=8 (power-of-two fast path) and bound=7 (rejection loop), plus `nextBoolean`. |
| AC4.3 | (Edge) Different seeds, same config → same relations but (generally) different surfaces. | unit | `tests/test_builder_build.py` | 4 | Two **pinned** seeds (chosen via the Phase-2 golden-vector fixture so the first base surface feature's `next_int(6)` shape draw differs), same config: structural inspection equal (same relations/directions) **and an exact `!=` on a specific located feature's `shape`** (the first-drawn surface of a named cell). Discriminating, not a probabilistic "some differ". |

---

## AC5 — SVG rendering (semantics only, never pixel parity)

| AC | Text | Type | Test file | Phase | Asserts |
|----|------|------|-----------|-------|---------|
| AC5.1 | `render_matrix_svg`/`render_answers_svg` emit well-formed SVG for a sample covering every shape and fill (alpha applied; White transparent). | unit (XML-parsed) | `tests/test_render_svg_cells.py`, `tests/test_render_svg_documents.py` | 6 | Each of 7 shapes → expected tag + pinned coords; each of 5 fills → matching `fill`/`fill-opacity` (White → `fill-opacity="0"`); 2px stroke; matrix SVG has 9 groups (blank bottom-right), answers SVG has 8; viewBox matches layout. Parses via ElementTree. **No pixel comparison.** |
| AC5.2 | `rasterise()` (raster group) converts the SVG to a PNG. | unit | `tests/test_render_raster.py` | 6 | `rasterise(render_matrix_svg(m))` returns bytes starting with PNG magic `\x89PNG\r\n\x1a\n` and a non-trivial length; core SVG import works without the `raster` extra. **No pixel comparison.** |
| AC5.3 | (Edge) An empty/blank answer cell renders without error. | unit | `tests/test_render_svg_cells.py`, `tests/test_render_svg_documents.py` | 6 | A featureless cell yields a valid empty `<g>`; an answer set with a blank-pad cell renders without error. |

---

## AC6 — Compat toggles

| AC | Text | Type | Test file | Phase | Asserts |
|----|------|------|-----------|-------|---------|
| AC6.1 | With `line_shape_enabled=False` (default) Line is never drawn; with `True` Line participates and the shape draw changes accordingly. | unit | `tests/test_surface.py` (build-level: `tests/test_builder_build.py`) | 4 | Default flags: shape draw uses bound 6 and never yields `Shape.LINE`; `True`: bound 7, Line can appear, output differs for the same seed. The `relocate_correct_answer` flag is also tested here (`tests/test_builder_answers.py`). |
| AC6.2 | Each compat flag is documented in the registry with its divergence and default. | unit (registry-completeness gate) | `tests/test_compat_registry.py` | 4 | Reads `docs/compat-registry.md` and asserts one documented row per `dataclasses.fields(CompatFlags)`, and no row names a non-existent flag — the registry is self-enforcing as it grows. (Defaults also pinned in `tests/test_fillpattern.py`.) |

---

## AC7 — Hosted online (concluding phase)

| AC | Text | Type | Test file / artifact | Phase | Asserts |
|----|------|------|----------------------|-------|---------|
| AC7.1 | (DoD-met) The marimo app runs locally and `marimo export html-wasm` produces a working static bundle that generates a matrix in-browser. | **operational** | `docs/wasm-export.md` (recipe); import-hygiene guard `tests/test_import_hygiene.py` | 8 | Export emits `index.html`+`assets/`; served locally the bundle generates a matrix (controls + code mode render SVG). Automated portion: the core pulls no `ui`/`cli`/`raster` import (WASM cold-start guard). The served-bundle generation itself is operational + UAT. |
| AC7.2 | (Success) The `raven-matrix` wheel publishes to PyPI and installs via micropip in the WASM environment. | **operational** | `docs/release.md`, `.github/workflows/release.yml`; wheel-purity check in Phase-8 Task 1 | 8 | Dev `0.1.0.dev0` then real `0.1.0` publish via Trusted Publishing and resolve on PyPI; micropip installs the pure wheel in-browser. Wheel-purity (no `.so`/`.pyd`, no mandatory runtime deps) is a recorded command check. |
| AC7.3 | (Stretch) A live GitHub Pages URL loads the app and generates a matrix in-browser (demoted per the criterion-7 fallback if marimo #5488 or Pages plumbing blocks it). | **operational (stretch)** | `.github/workflows/pages.yml` | 8 | Pages workflow deploys; the live URL generates a matrix in-browser, **or** the status is recorded and demoted per the fallback (AC7.1+AC7.2 already meet the DoD). |
| AC7 (in-browser feel) | The app generates a puzzle responsively in-browser without errors (cold-start, micropip install, render). | **UAT** | `uat-requirements.md` (in-browser entry) | 8 | Human serves the bundle, waits through Pyodide cold-start, and judges responsive generation. Wrong if it hangs past a reasonable cold-start, errors on micropip, or fails to render. |

---

## Coverage summary

22 numbered acceptance criteria (AC1.1–AC7.3). Each is counted once, by its **primary** verification:

- **Automated (unit / property / integration): 20** — AC1.1, AC1.2, AC1.3, AC1.4, AC1.5, AC2.1, AC2.2, AC2.3, AC2.4, AC3.1, AC3.2, AC3.3, AC4.1, AC4.2, AC4.3, AC5.1, AC5.2, AC5.3, AC6.1, AC6.2 (registry-completeness gate, `tests/test_compat_registry.py`).
- **Operational: 3** — AC7.1, AC7.2, AC7.3 (stretch).
- **UAT-only numbered AC: 0.** The two UAT items are cross-cutting human-judgment overlays, not the sole coverage of any numbered criterion:
  - AC1.* live option-parity + visual-correctness judgment (Phase 7, `uat-requirements.md`) — sits on top of AC1.1–AC1.5 automated coverage.
  - AC7 in-browser generation feel (Phase 8, `uat-requirements.md`) — sits on top of AC7.1/AC7.2 operational coverage.
- **Coverage gaps: 0.** Every numbered AC maps to at least one automated test or operational check.

**UAT-flagged (human judgment adds signal automation cannot):**

- **AC1.\*** — live option-parity + visual-correctness judgment (Phase 7, `uat-requirements.md`). Automated structurally in Phase 4 and through `config_from_controls`/CLI in Phase 7; the *live reactive parity* and *recognisable-Raven-figure* judgments are human-only.
- **AC7** — in-browser generation feel (Phase 8, `uat-requirements.md`). Automated portion is import-hygiene + wheel purity; the served/live in-browser experience is human-judged.

**Notes on framing honoured:**

- AC2.1 is owned by **Phase 5** (`tests/test_hand_derived_labels.py`), not Phase 4 — the design's "begun in Phase 4" wording is superseded by DR4; Phase 4 does direct structural inspection only.
- AC2.2 is a **pass-map with an inspected-exclusions gate** (`tests/test_oracle_sweep.py` + `docs/oracle_exclusions.md`), not a bare 840/840 assertion.
- AC5.* assert SVG well-formedness / PNG validity, **never pixel parity**.
- AC6.1 (`line_shape_enabled`) and the `relocate_correct_answer` flag are tested in Phase 4.
