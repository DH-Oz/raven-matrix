# Raven-Builder: Faithful Python Port of the SGMT Matrix Builder (v1) — Design

**GitHub Issue:** None

## Summary

raven-builder ports the explicit-matrix-builder path of the Sandia Generated
Matrix Tool (SGMT) into a pure-Python library. SGMT is a Java desktop
application that constructs 3×3 Raven-style progressive-matrix puzzles: the
researcher chooses a structural pattern — which visual relation (repetition,
logical combination, rotation, etc.) runs across the grid and in which direction
— and the tool fills in each cell's shapes, sizes, and fills from a random seed,
then generates eight answer choices. raven-builder reproduces that same option
surface as an importable Python API, with a thin CLI and a reactive marimo web
app layered on top.

The approach is a Pythonic re-model rather than a line-by-line transliteration:
the domain objects become dataclasses and enums, the Java GUI config becomes an
explicit frozen `BuilderConfig`, and the upstream `java.util.Random` is ported
faithfully so seeded output is deterministic. Faithfulness is defined at the
behaviour level — outputs match the upstream code, including its known bugs,
which are hidden behind named compat toggles. Correctness is verified
structurally: a hand-derived label table anchors the code-to-label rules, and
all 840 published Matzen et al. (2010) `Structure` codes are required to
round-trip through the parser and labeller. The library's zero-runtime-dependency
core makes it directly loadable in a browser via WebAssembly, which is the
concluding v1 phase: a static GitHub Pages site running the marimo app fully
in-browser via Pyodide/micropip.

## Definition of Done

**Deliverable:** a Python 3.14 pure-Python library that reproduces SGMT's
explicit matrix builder — the `ui/SGMBuilderFrame` option surface — turning a
config + seed into a 3×3 matrix with 8 answer choices, rendered to SVG, with a
structural test harness against the 840 Matzen et al. (2010) `Structure` codes.

**Done when:**

1. **Option parity** — the API exposes every `SGMBuilderFrame` generation
   option: 1–2 layers; per layer a base relation ∈ {ShapeRepetition, Logical
   OR/AND/XOR} + base direction ∈ {1–5}; up to 3 supplementals ∈ {Rotation,
   Scaling, FillPatternRepetition, ChangeFillPattern, Numerosity}, each with a
   direction; correct-answer position 1–8; RNG seed. *Falsifiable:* a checklist
   test asserting each option is settable; any missing option fails.
2. **Labeller correctness + structural consistency** — (a) PRIMARY anchor: a
   hand-derived label table (~12 configs — shape-rep × each direction incl.
   corner-out→`6`; each of the five supplementals; OR/AND/XOR) matches expected
   labels derived from the Matzen paper's naming convention and the published
   codes (an independent reference frame — NOT re-read from the Java labeller
   source); (b) consistency check: all 840
   `Structure` codes round-trip (code→config→matrix→label→code) — *necessary,
   not sufficient*, and only a weak structural constraint for the 60 logic codes
   (bare `X`/`Y`/`Z`). *Falsifiable:* the hand-derived table mismatches the
   rules, or the 840 sweep reports mismatches outside a documented exclusion
   list. Output: the table result + an N/840 report.
3. **Location-transform spec** — the value-pinned
   `TopLeftCornerOutSGMLocationTransformTest` ports to pytest with its exact
   hardcoded coordinate sequences for all 8 matrix sizes, all green. (This is
   the TDD starting point.)
4. **Determinism** — same config + same seed → identical output run-to-run.
   *Falsifiable:* generate twice, assert equal. (JVM-byte-identity not
   required.)
5. **SVG rendering** — every matrix and its answer set render to valid SVG
   across all shapes/fills; SVG rasterises to PNG on demand. *Falsifiable:*
   render produces well-formed SVG for a sample covering all shapes/fills, and a
   PNG on rasterise. (Pixel-identity to upstream is not a criterion.)
6. **Compat toggles** — known code-vs-design divergences are exposed as named
   `faithful-to-code` (default) / `faithful-to-design` flags, starting with
   `line_shape_enabled`. *Falsifiable:* the toggle exists and changes behaviour
   in a test.
7. **Hosted online (concluding phase)** — the marimo app runs the builder fully
   in-browser via WASM. *Met when:* the app runs locally and `marimo export
   html-wasm` produces a working static bundle, with the `raven-matrix` wheel
   published to PyPI. *Stretch (fallback rule):* a live GitHub Pages site loading
   the wheel via micropip — if marimo #5488 or Pages plumbing blocks it,
   criterion 7 is still met by the local app + WASM export and the live site is
   demoted to stretch. Sequenced last, after the generator is independently
   verified.

**Explicitly out of v1 scope:**

- Difficulty classifier, batch `SGMMatrixSetGenerator` (distribution-filling),
  and the normative oracle — deferred to a separate `difficulty` uv dependency
  group in a later phase.
- Exact pixel reproduction of the norming PNGs; exact distractor sets;
  correct-answer position as a *generated* property (it is an input) — all need
  the unpublished generator seeds.
- JVM-byte-identical RNG output — a verify-if-wanted differential test, not an
  acceptance gate.
- 2-SGM-layer norming reproduction — all 840 norming stimuli are single-layer;
  the 2-layer builder option is exposed for parity but is not part of the
  oracle.
- The difficulty classifier, batch generator, and normative oracle (already
  listed above) remain the only deferred-to-later-release items.

**Interface:** importable library + thin `typer` CLI + a **marimo** reactive app
exposing the full option surface (the researcher-facing surface, per the goal
steer), published as a hosted WASM web app on GitHub Pages in the concluding
phase.

## Acceptance Criteria

### raven-builder.AC1: Option parity with SGMBuilderFrame
- **raven-builder.AC1.1 Success:** `build()` accepts a 1-layer config (base relation + direction + ≤3 supplementals with directions, correct-answer position, seed) and returns a 3×3 Matrix with 8 answer choices.
- **raven-builder.AC1.2 Success:** a 2-layer config composes both layers per cell.
- **raven-builder.AC1.3 Success:** every BaseRelation (ShapeRep, OR, AND, XOR), every Supplemental (Rotation, Scaling, FillRep, ChangeFill, Numerosity), and every Direction (1–5) is settable and realised.
- **raven-builder.AC1.4 Failure:** an invalid config (>3 supplementals, correct-answer position ∉ 1–8, or a diagonal/logic transform on an even/non-square grid) raises a clear error.
- **raven-builder.AC1.5 Equality (DR7):** value-equal-but-distinct `SurfaceFeature`s are treated as distinct under identity in logic/dedup contexts; `value_equals()` returns true for them where the upstream hand-rolls a value check.

### raven-builder.AC2: Labeller correctness + structural consistency
- **raven-builder.AC2.1 Success (primary anchor):** the hand-derived label table (~12 configs incl. shape-rep × each direction with corner-out→`6`; each supplemental; OR/AND/XOR) matches expected labels derived from the Matzen paper's naming convention + the published codes (independent of the Java source).
- **raven-builder.AC2.2 Success (consistency):** all 840 `Structure` codes round-trip (code→config→matrix→label→code) outside the documented exclusion list.
- **raven-builder.AC2.3 Edge:** logic codes (`X`/`Y`/`Z`) parse and label correctly despite carrying no direction or surface detail.
- **raven-builder.AC2.4 Failure:** a malformed code raises a clear parse error.

### raven-builder.AC3: Location-transform spec
- **raven-builder.AC3.1 Success:** the ported TopLeftCornerOut transform produces the exact hardcoded coordinate sequences for all 8 matrix sizes from the JUnit test.
- **raven-builder.AC3.2 Success:** Horizontal, Vertical, and both diagonals produce their correct base/next/parent sequences.
- **raven-builder.AC3.3 Failure:** a diagonal/logic transform on a non-odd-square grid is rejected (matching the upstream constraint).

### raven-builder.AC4: Determinism
- **raven-builder.AC4.1 Success:** the same config + seed produces an identical Matrix (structure, surfaces, answers) across two runs.
- **raven-builder.AC4.2 Success:** `JavaRandom` reproduces known `java.util.Random` vectors for `nextInt(bound)` (incl. the power-of-two and rejection-loop edges) and `nextBoolean`.
- **raven-builder.AC4.3 Edge:** different seeds with the same config yield the same relations but (generally) different surfaces.

### raven-builder.AC5: SVG rendering
- **raven-builder.AC5.1 Success:** `render_matrix_svg`/`render_answers_svg` emit well-formed SVG for a sample covering every shape and fill (alpha applied; White transparent).
- **raven-builder.AC5.2 Success:** `rasterise()` (raster group) converts the SVG to a PNG.
- **raven-builder.AC5.3 Edge:** an empty/blank answer cell renders without error.

### raven-builder.AC6: Compat toggles
- **raven-builder.AC6.1 Success:** with `line_shape_enabled=False` (default) Line is never drawn; with `True` Line participates and the shape draw changes accordingly.
- **raven-builder.AC6.2 Success:** each compat flag is documented in the registry with its divergence and default.

### raven-builder.AC7: Hosted online (concluding phase)
- **raven-builder.AC7.1 Success (DoD-met):** the marimo app runs locally and `marimo export html-wasm` produces a working static bundle that generates a matrix in-browser.
- **raven-builder.AC7.2 Success:** the `raven-matrix` wheel publishes to PyPI and installs via micropip in the WASM environment.
- **raven-builder.AC7.3 Stretch:** a live GitHub Pages URL loads the app and generates a matrix in-browser (demoted to stretch per the criterion-7 fallback if marimo #5488 or Pages plumbing blocks it).

## Glossary

- **SGMT (Sandia Generated Matrix Tool)**: the upstream Java application being ported. It generates Raven-style progressive-matrix stimuli programmatically; this library ports its explicit-builder path.
- **Raven's Progressive Matrices**: a class of nonverbal reasoning test where a 3×3 grid of figures follows a visual rule and the test-taker chooses which of eight options completes the bottom-right cell.
- **Structure code**: a compact string encoding a matrix's relational structure (e.g. `A1B2C4`). Each letter names a relation type and each digit a direction; logic codes (`X`, `Y`, `Z`) encode OR/AND/XOR.
- **Base relation**: the primary structural rule applied across a matrix layer — ShapeRepetition or one of the three logical transforms (OR/AND/XOR).
- **Supplemental relation**: an additional feature-level rule layered on the base within a single layer — Rotation, Scaling, FillPatternRepetition, ChangeFillPattern, or TranslationalNumerosity.
- **Location transform**: the traversal pattern determining which grid cells share a feature. Variants: Horizontal, Vertical, DiagonalBL→TR, DiagonalTL→BR, TopLeftCornerOut. Each exposes `base_locations`, `next_location`, `parent_location`.
- **TopLeftCornerOut**: the direction-5 location transform that radiates outward from the top-left corner; its hardcoded coordinate sequences (from the JUnit spec) are the TDD starting point.
- **BuilderConfig / LayerConfig**: the frozen dataclasses that replace the upstream Swing GUI as the generation entry point — one or two `LayerConfig`s (base relation + direction + 0–3 supplemental/direction pairs), a correct-answer position, and a seed.
- **SurfaceFeature**: a drawn feature on a cell (a shape at a size with a fill). Uses object-identity equality, not value equality — matching the upstream's implicit identity semantics in `List.contains`/`HashSet`.
- **`value_equals()`**: an explicit value comparison on `SurfaceFeature`, used only where the upstream hand-rolls a value check — separating identity from value semantics deliberately.
- **compat toggle / CompatFlags**: named flags exposing known divergences between upstream code and design intent. Default `faithful-to-code`; `line_shape_enabled` is the only flag known at design time.
- **JavaRandom / `java.util.Random`**: the JVM's 48-bit LCG PRNG, used by SGMT to draw shapes/sizes/fills, re-implemented in Python (`nextInt(bound)`, `nextBoolean`) for identical seeded sequences.
- **Labeller**: `label.py`, which reads a completed `Matrix` back to its `Structure` code (ported from `SGMMatrixDifficultyClassifier.java:208–389` — the full `sb`-build: letter ladder 232–289, digit map 308–382, trailing-`_` delete 389; the narrower `308–382` omits the letter ladder). Inverse: `parse_code()`.
- **Round-trip / structural oracle**: takes each published `Structure` code, parses → builds → labels, and checks the label matches. Necessary but not sufficient — a consistency check on the parser/labeller pair.
- **Hand-derived label table**: a ~12-entry mapping from representative configs to expected `Structure` codes; the primary correctness anchor (DR6) because the round-trip alone is circular.
- **Matzen et al. (2010) norming spreadsheet**: the published QA oracle — 840 stimuli with `Structure` codes, correct-answer positions, and empirical % correct.
- **marimo**: a reactive Python notebook/app framework whose apps export to a single self-contained HTML file that runs in-browser via WASM — the chosen interface for the hosted online phase.
- **WASM / Pyodide / micropip**: WebAssembly runs compiled code in the browser; Pyodide is CPython-on-WASM; micropip installs pure-Python wheels from PyPI into it at runtime. The design publishes `raven-matrix` to PyPI to work around marimo bug #5488.
- **FCIS (Functional Core / Imperative Shell)**: keep pure logic in an import-light core; confine I/O, UI, CLI, and rasterisation to edge layers with their own dependency groups.
- **uv dependency groups**: uv's named optional dependency sets in `pyproject.toml`; here `raster`, `ui`, `cli`, and the reserved `difficulty` keep the core zero-dependency.
- **Difficulty classifier**: SGMT's `SGMMatrixDifficultyClassifier` (37-feature difficulty predictor). Deferred out of v1; relevant only as the source of the labeller code.
- **`6`/`7` labeller codes**: upstream labeller edge outputs signalling a matrix "may not correspond to a norming SGM" — distinct from the study's norming exclusions; kept separate in the oracle exclusion list.
- **`1`/`2` swap**: the upstream labeller's direction-encoding quirk (horizontal/vertical transposed for non-repetition features); must be replicated in `label.py`.
- **Java differential / golden fixtures**: best-effort golden output from running the upstream Java under a JDK, used to check RNG-driven surface/distractor behaviour; feasibility decided by the Phase-1 spike.

## Architecture

raven-builder is a pure-Python (3.14) library that reconstructs SGMT's explicit
matrix builder — the option surface of the upstream Swing `SGMBuilderFrame` —
driven by an explicit config rather than GUI widgets. The equivalence bar is
data/logic, not pixels. Faithfulness binds at the **behaviour** level ("build
what is"): outputs match the upstream code, bugs preserved behind named compat
toggles; the code structure is idiomatic Python (a re-model, not a
transliteration — see DR1).

Layering keeps the core import-light (the core never imports the UI/CLI), which
is what makes the WASM cold-start fast:

- **Core (pure-Python, zero runtime deps):** `rng.py` (a faithful
  `java.util.Random` port), `model.py` (enums + dataclasses), `transforms/`,
  `structure/`, `surface/`, `fillpattern/`, `builder.py` (config+seed → Matrix),
  `label.py` (labeller + parser), `render/svg.py`.
- **Edge layers (own dependency groups):** `render/raster.py` (SVG→PNG, `raster`
  group); `cli.py` (typer); the marimo app `app.py` (`ui` group); the reserved
  `difficulty` group (deferred).
- **Data/tools:** `data/ravens_oracle.csv` (840 rows extracted once from the
  xls); `tools/extract_oracle.py` (dev) and `tools/java_golden/` (dev,
  best-effort).

Data flow: a `BuilderConfig` (explicit relations/directions/layers + correct-
answer position) + `seed` → `build()` constructs each layer's structure features
deterministically from the config, populates the grid by walking each feature's
location transform, composes layers (cell = concatenated surface features), and
generates the correct answer (bottom-right cell) + distractors. Shapes, sizes,
and fills are drawn from the seeded `JavaRandom` — faithful to the GUI (you
choose the relation; the surfaces are random). `label()` reads a Matrix back to
its `Structure` code; `parse_code()` inverts it; `render_*_svg()` maps a Matrix
to SVG.

Contracts:

```python
def build(config: BuilderConfig, seed: int, flags: CompatFlags = DEFAULT_FLAGS) -> Matrix: ...
def build_from_code(code: str, seed: int, flags: CompatFlags = DEFAULT_FLAGS) -> Matrix: ...
def label(matrix: Matrix) -> str: ...
def parse_code(code: str) -> BuilderConfig: ...
def render_matrix_svg(matrix: Matrix, settings: RasterSettings = DEFAULT_RASTER) -> str: ...
def render_answers_svg(matrix: Matrix, settings: RasterSettings = DEFAULT_RASTER) -> str: ...

@dataclass(frozen=True)
class LayerConfig:
    base: BaseRelation
    base_direction: Direction
    supplementals: tuple[tuple[Supplemental, Direction], ...]   # 0–3

@dataclass(frozen=True)
class BuilderConfig:
    layers: tuple[LayerConfig, ...]      # 1 or 2
    correct_answer_position: int          # 1–8

@dataclass(frozen=True)
class CompatFlags:
    line_shape_enabled: bool = False      # code: Line shape disabled in the generator
```

`SurfaceFeature` uses **identity** equality (a plain object, `eq=False`), with
an explicit `value_equals()` used only where the upstream hand-rolls a value
check (DR7). The value objects `MatrixSize`/`Location`/`Point` are frozen-value
dataclasses.

## Decision Record

### DR1: Pythonic re-model over transliteration
**Status:** Accepted · **Confidence:** Medium · **Reevaluation triggers:** behaviour drift found in un-oracle-covered paths (distractors/surfaces).
**Decision:** We chose to re-model the Java domain into idiomatic Python (dataclasses/enums/functions), holding behaviour-equivalence rather than class-equivalence; "build what is" binds at the behaviour level.
**Consequences:** Enables a clean, maintainable, WASM-friendly library. Prevents line-by-line traceability to the Java, so behaviour fidelity rests on the testing strategy (DR6).
**Alternatives considered:** Faithful 1:1 transliteration — rejected (Java-isms, verbose). Hybrid (faithful logic, Pythonic shell) — rejected by the user in favour of a fuller re-model.

### DR2: Defer the difficulty classifier, batch generator, and normative oracle
**Status:** Accepted · **Confidence:** High · **Reevaluation triggers:** a funded need for normed difficulty.
**Decision:** We chose a builder-only v1; the difficulty subsystem moves to a later release in its own `difficulty` uv group.
**Consequences:** Enables a focused, fully verifiable v1 needing no ML or seeds. Prevents distribution-targeted batch generation in v1.
**Alternatives considered:** Include re-derived difficulty (rejected: the paper documents no classifier; the trained model + training data never shipped; the in-code 37-feature extractor is WIP — ~15 slots unimplemented, an index-36 clobber bug). Re-derivation stays feasible later (the oracle reconstitutes the training set).

### DR3: Port java.util.Random; demote JVM-byte-identity to verify-if-wanted
**Status:** Accepted · **Confidence:** High · **Reevaluation triggers:** a need to exactly reproduce specific seeded outputs.
**Decision:** We chose to reimplement `java.util.Random` (only `nextInt`/`nextBoolean` are used) for faithful RNG semantics and internal seed-determinism, and not to gate v1 on byte-identical generation against the JVM.
**Consequences:** Enables faithful, deterministic generation and keeps exact reproduction possible. Prevents nothing material — the structural bar does not need JVM-identity.
**Alternatives considered:** Python `random` (rejected: not faithful). A full JVM-identity gate (rejected: high cost, no v1 benefit; the consumption order was audited as List/index-driven).

### DR4: marimo for the interactive UI over Jupyter + ipywidgets
**Status:** Accepted · **Confidence:** Medium · **Reevaluation triggers:** `mo.ui` proves insufficient for the option surface, or #5488-class issues block deploy.
**Decision:** We chose a marimo reactive app for the option-parity panel.
**Consequences:** Enables a far simpler static WASM deploy (one command, one HTML, no conda channels). Prevents reuse of ipywidgets and requires the package on PyPI (marimo WASM local-import bug #5488).
**Alternatives considered:** ipywidgets + voici (rejected: more WASM drama, widget version-pinning).

### DR5: Hosted online as the concluding v1 phase
**Status:** Accepted · **Confidence:** Medium · **Reevaluation triggers:** WASM cold-start/version quirks prove larger than a final-phase effort.
**Decision:** We chose to make the marimo-WASM GitHub-Pages app a v1 deliverable, sequenced last so CI/Pages/WASM plumbing never blocks core correctness.
**Consequences:** Enables a "runs on the web" guarantee. Prevents nothing in the core.
**Alternatives considered:** Designed-in fast-follow (rejected by the user, who wanted it as a concluding phase).

### DR6: Oracle = consistency check + hand-derived label-table anchor
**Status:** Accepted · **Confidence:** High · **Reevaluation triggers:** the Java golden differential becomes available and supersedes the hand-derived table.
**Decision:** We chose to treat the 840-code round-trip as a necessary-not-sufficient consistency check (parser/labeller mutual inverse), anchored by a hand-derived (config→label) table read from the labeller code; the round-trip is only a weak structural constraint for the 60 logic stimuli.
**Consequences:** Enables a JVM-free correctness anchor. Prevents over-claiming the round-trip as validation.
**Alternatives considered:** Round-trip-as-validation (rejected on critical review: circular, weak for logic). Supersedes the earlier framing of DoD criterion 2.
**Reference frame:** the hand-derived table is grounded in the Matzen paper's naming convention + the 840 published codes (an independent reference frame), not re-read from the Java labeller source — so it does not inherit the labeller's own assumptions (per the proleptic challenge).

### DR7: SurfaceFeature identity equality
**Status:** Accepted · **Confidence:** High · **Reevaluation triggers:** none expected; revisit only if a call site needs value semantics not covered by `value_equals()`.
**Decision:** We chose to model `SurfaceFeature` with object-identity equality (not value), adding an explicit `value_equals()` only where the upstream hand-rolls a value check.
**Consequences:** Enables faithful logic (OR/AND/XOR) and distractor-dedup behaviour, matching the Java's identity-based `List.contains`/`HashSet`. Prevents naive dataclass value-equality from silently changing outcomes.
**Alternatives considered:** Frozen value-equality dataclass (rejected on critical review: `AbstractSGMSurfaceFeature` defines `equals(SGMSurfaceFeature)` as an overload, not an override, and has no `hashCode`; the upstream hand-rolls `containsCheck` precisely because `contains`/`HashSet` use identity).

## Existing Patterns

Investigation found no existing Python port — greenfield. The upstream Java
(`upstream/Matrices/`, read-only submodule; extracted to `scratch/` for
reference) is the reference implementation, mapped in depth (generation
pipeline, option surface, feature catalogue, difficulty classifier, JUnit tests)
and distilled in `scratch/findings.md`. This design introduces new patterns:

- **Functional core / imperative shell:** a pure-Python deterministic core
  (model, transforms, structure/surface/fill, builder, labeller, renderer) with
  side effects (file I/O, CLI, the marimo app, rasterisation) pushed to the edges
  in their own dependency groups.
- **Behaviour-faithful re-model:** Python idiom for structure, upstream
  behaviour for outputs (DR1), with code-vs-design divergences exposed as compat
  toggles.

No prior project convention constrains the layout; it follows the denubis coding
standards (FCIS, Python 3.14 idioms, uv, ruff, ty, pytest, Hypothesis).

## Implementation Phases

Eight phases. Functionality phases own their tests (mapped to the acceptance
criteria below).

<!-- START_PHASE_1 -->
### Phase 1: Scaffolding, CI, oracle data, Java spike
**Goal:** a working uv project skeleton, CI, the oracle fixture, and a decision on Java golden fixtures.
**Components:** `src/raven_matrix/` package; `pyproject.toml` dependency groups (dev: pytest/ruff/ty/hypothesis; `raster`; `ui`: marimo; `cli`: typer; `difficulty`: reserved); ruff/ty config; a GitHub Actions **CI** workflow (ruff + ty + pytest on push); `tools/extract_oracle.py` producing the committed `data/ravens_oracle.csv` (840 rows); a **spike** attempting to build/run the upstream Java (install a JDK, `ant` build) recording whether golden fixtures are available.
**Dependencies:** none.
**Done when:** `uv sync` succeeds; `uv run ruff check .` and `uv run ty` clean; CI green on a no-op; `data/ravens_oracle.csv` has 840 rows; the spike outcome (Java builds: yes/no) is recorded.
<!-- END_PHASE_1 -->

<!-- START_PHASE_2 -->
### Phase 2: JavaRandom + domain model
**Goal:** a faithful RNG and the value model.
**Components:** `rng.py` `JavaRandom` (`next`/`nextInt`/`nextInt(bound)`/`nextBoolean`); `model.py` enums (Shape, Fill+RGBA, BaseRelation, Supplemental, Direction), frozen-value dataclasses (MatrixSize, Location, Point), identity-equality `SurfaceFeature` (+ `value_equals`), Cell, Layer, Matrix.
**Dependencies:** Phase 1.
**Done when:** `JavaRandom` matches known `java.util.Random` vectors incl. the power-of-two and rejection-loop edges (`raven-builder.AC4.2`); `SurfaceFeature` identity-vs-value semantics covered by tests (`raven-builder.AC1.5`).
<!-- END_PHASE_2 -->

<!-- START_PHASE_3 -->
### Phase 3: Location transforms
**Goal:** the five transforms + logic, with the pinned spec.
**Components:** `transforms/` Horizontal, Vertical, DiagonalBLTR, DiagonalTLBR, TopLeftCornerOut, Logic — each exposing `base_locations()` / `next_location()` / `parent_location()`.
**Dependencies:** Phase 2.
**Done when:** the ported TopLeftCornerOut coordinate-sequence test passes for all 8 sizes (`raven-builder.AC3.1`); the other transforms' base/next/parent tests pass (`raven-builder.AC3.2`, `AC3.3`).
<!-- END_PHASE_3 -->

<!-- START_PHASE_4 -->
### Phase 4: Structure features, surfaces/fills, the builder
**Goal:** relations, surface/fill generators, and `build()`.
**Components:** `structure/` base (ShapeRepetition, Logical OR/AND/XOR) + supplemental (Rotation, Scaling, FillRep, ChangeFill, Numerosity); `surface/` shapes; `fillpattern/` fills; `builder.py` `build()` incl. layer composition + answer/distractor generation (four strategies, 500-cap dedup, blank pad); the `CompatFlags` mechanism (`line_shape_enabled` seeded).
**Dependencies:** Phase 3.
**Done when (provisional structural gate):** `build()` produces a 3×3 matrix + 8 answers across the option surface (`raven-builder.AC1.1`–`AC1.4`); the hand-derived label table (`raven-builder.AC2.1`) passes for each relation built here, giving incremental structural checks as relations land; determinism holds (`raven-builder.AC4.1`, `AC4.3`); the compat toggle flips behaviour (`raven-builder.AC6.1`). Note: Phase 4 "done" means builds + deterministic + per-relation hand-derived checks — full structural correctness (the 840 oracle) is established in Phase 5, so do not over-trust Phase 4 as proof of structural correctness.
<!-- END_PHASE_4 -->

<!-- START_PHASE_5 -->
### Phase 5: Labeller, parser, structural oracle
**Goal:** matrix↔code and the oracle harness.
**Components:** `label.py` `label()` (ported `sb`-logic with the `1`/`2` swap and `6`/`7` rules; cite `SGMMatrixDifficultyClassifier.java:208–389` — the whole `sb`-build incl. the letter ladder at 232–289, not just the `308–382` digit map) + `parse_code()`; the hand-derived label table (~12 configs); the 840-code round-trip harness reading `data/ravens_oracle.csv`.
**Dependencies:** Phase 4.
**Done when:** the hand-derived table (begun in Phase 4) is complete and matches the paper/published-code rules (`raven-builder.AC2.1`, primary anchor); all 840 round-trip outside the documented exclusion list (`raven-builder.AC2.2`); logic codes parse/label (`raven-builder.AC2.3`); property tests (`parse∘label`) pass.
<!-- END_PHASE_5 -->

<!-- START_PHASE_6 -->
### Phase 6: SVG rendering (+ optional raster)
**Goal:** matrices and answers as SVG.
**Components:** `render/svg.py` `render_matrix_svg`/`render_answers_svg` (shape geometry → SVG elements, fills with alpha, White transparent); `render/raster.py` `rasterise` (`raster` group).
**Dependencies:** Phase 4.
**Done when:** SVG renders and validates for a sample covering every shape and fill (`raven-builder.AC5.1`); `rasterise` produces a PNG (`raven-builder.AC5.2`); a blank answer cell renders (`raven-builder.AC5.3`).
<!-- END_PHASE_6 -->

<!-- START_PHASE_7 -->
### Phase 7: marimo app + typer CLI
**Goal:** the researcher-facing interfaces.
**Components:** `app.py` marimo reactive panel (`mo.ui` controls = full option parity; inline SVG via `mo.Html`); `cli.py` typer CLI (`build` from `--code` or explicit flags; `oracle`).
**Dependencies:** Phases 4–6.
**Done when:** the app exposes every `SGMBuilderFrame` option and re-renders on change (`raven-builder.AC1.*` parity, UAT); the CLI `build`/`oracle` commands work.
<!-- END_PHASE_7 -->

<!-- START_PHASE_8 -->
### Phase 8: Hosted online (concluding)
**Goal:** the WASM-exportable app and a published wheel, with a live GitHub Pages deploy as the stretch target.
**Components:** publish the pure-Python `raven-matrix` wheel to PyPI (account exists, name free — a release-workflow task); `marimo export html-wasm app.py`; a GitHub Actions Pages deploy workflow.
**Dependencies:** Phase 7; the PyPI wheel (resolves marimo #5488).
**Done when:** the app runs locally and `marimo export html-wasm` yields a working static bundle (`raven-builder.AC7.1`); the wheel publishes to PyPI and installs via micropip in WASM (`raven-builder.AC7.2`). Stretch: a live Pages URL generates a matrix in-browser (`raven-builder.AC7.3`) — demoted per the criterion-7 fallback if marimo #5488 or Pages plumbing blocks it.
<!-- END_PHASE_8 -->

## Additional Considerations

- **Re-model drift (the standing cost of DR1):** RNG-driven surface and
  distractor behaviour is pinned by neither transliteration nor the structural
  oracle. It rests on the optional Java differential (best-effort, gated on the
  Phase-1 spike); if the JDK build is infeasible, that behaviour is best-effort-
  faithful and unverified — acceptable because it sits outside the equivalence
  bar (exact distractors/surfaces need unpublished seeds).
- **Determinism is conditional:** "same config+seed → same output" depends on
  both the `JavaRandom` port and the `SurfaceFeature` equality split (DR7), since
  the dedup loop's draw count depends on value-vs-identity comparison.
  Cross-run/version determinism additionally requires that identity dedup is
  list-based (`is` / `List.contains`-style) and never routes identity objects
  through a Python `set` (whose iteration is `id()`/address-ordered) into output
  — otherwise output order would vary across runs (per the proleptic challenge).
- **Two distinct exclusion concepts:** the norming set's redundancy exclusions
  (the paper excludes 46/230 two-relation same-direction combos, and shape-rep ×
  direction-5) are a study-design choice; the labeller's `6`/`7` codes ("may not
  correspond to a norming SGM") are a code edge-case. The oracle's exclusion list
  keeps these separate.
- **External-dependency risk in Phases 1, 5, 8:** the Java-build spike (Phase 1)
  and the PyPI-wheel + WASM + Pages deploy (Phase 8) depend on external
  toolchains and a known marimo bug; these phases carry more uncertainty than the
  pure-Python phases and may need iteration.
- **The compat-toggle registry grows during the port:** every code-vs-design
  divergence found while reading a file becomes a named flag (default faithful-
  to-code), documented in a registry. Only `line_shape_enabled` is known up
  front.
- **Difficulty deferral is reversible:** the feature extractor + the oracle
  reconstitute the training set; when funded, the `difficulty` group adds
  numpy/scikit-learn/pandas and retrains without touching the core.
