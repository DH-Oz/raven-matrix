# raven-builder Implementation Plan — Phase 4: Structure features, surfaces/fills, the builder

**Goal:** Port the relation catalogue (base + supplemental), the surface and fill generators, and `build(config, seed, flags)` — config-driven layer generation, layer composition, and answer/distractor generation — plus the `CompatFlags` mechanism seeded with `line_shape_enabled` and `relocate_correct_answer`.

**Architecture:** Zero-dependency functional core. `build()` is the imperative-but-pure entry point: it takes an explicit `BuilderConfig` (relations/directions/layers/correct-answer position) + `seed` + `flags`, and uses a single `JavaRandom(seed)` **only** for the stochastic parts (surface shapes/sizes/fills and distractor mutation) — the upstream's config-level draws (numLayers, position, relation choice) are replaced by config (the SGMBuilderFrame option surface, DR1). Logic relations use identity feature membership; distractor dedup uses value equality (DR7). Known code-vs-design divergences are exposed via a `CompatFlags` frozen dataclass and a `docs/compat-registry.md`.

**Tech Stack:** Python (dev 3.14, package floor 3.12 — see Phase 1 decisions) stdlib only. Tests: pytest + hypothesis.

**Scope:** Phase 4 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`. This is a **provisional structural gate** — builds + deterministic + per-relation structural inspection; full structural correctness (the 840 oracle) lands in Phase 5. Do not over-trust Phase 4 as proof of correctness.

**Codebase verified:** 2026-06-08 (two parallel codebase-investigators), re-pinned against `SGMSurfaceFeatureGenerator.java:134–164` (the prior `size → fill → shape` summary was wrong — it dropped the conditional height draw and the swap). Pinned surface RNG order: `nextInt(3)` width (l.134) → **conditional `nextInt(2)` height** (the `else` branch at l.142, taken only when width is the smallest size; skipped for the two larger widths) → **`nextBoolean()` width/height swap** (l.144) → fixed rotation/position (no draw) → fill (call at l.159; the actual `nextInt(3)` over the 3-fill catalogue is in `SGMFillPatternGenerator.java:71`/`:99`) → shape `nextInt(6)` (l.164). **Pre-fill draws = 2 or 3** (3 when the smallest width forces the height draw, else 2). Live switch cases are 164–202; Line is the **commented-out** case at lines 197–201 (a stale `case 4`, which the live switch reuses for Diamond). Base-fill catalogue `[White,Grey75,Black]`; supplemental params (rotate +45 additive, scale ×0.66, ChangeFill cycle over `[White,Grey75,Grey40,Grey10,Black]`, FillRep base-cycle `[White,Black,Grey75]`, Numerosity 1–2 copies); base relations (ShapeRep cycle; AND/OR/XOR over two prior cells via identity `.contains`); composite cell = concatenation; answer generation (correct=`(2,2)`, 8 choices, four strategies, 500-cap value dedup, blank-pad, correct-position relocation).

**Phase Type:** functionality

---

## Acceptance Criteria Coverage

### raven-builder.AC1: Option parity with SGMBuilderFrame
- **raven-builder.AC1.1 Success:** `build()` accepts a 1-layer config (base relation + direction + ≤3 supplementals with directions, correct-answer position, seed) and returns a 3×3 Matrix with 8 answer choices.
- **raven-builder.AC1.2 Success:** a 2-layer config composes both layers per cell.
- **raven-builder.AC1.3 Success:** every BaseRelation (ShapeRep, OR, AND, XOR), every Supplemental (Rotation, Scaling, FillRep, ChangeFill, Numerosity), and every Direction (1–5) is settable and realised.
- **raven-builder.AC1.4 Failure:** an invalid config (>3 supplementals, correct-answer position ∉ 1–8, or a diagonal/logic transform on an even/non-square grid) raises a clear error.

### raven-builder.AC4: Determinism
- **raven-builder.AC4.1 Success:** the same config + seed produces an identical Matrix (structure, surfaces, answers) across two runs.
- **raven-builder.AC4.3 Edge:** different seeds with the same config yield the same relations but a **pinned first-drawn surface feature differs** (seeds chosen, via the Phase-2 fixture, so its shape draw differs — a specific inequality, not a probabilistic "some differ").

### raven-builder.AC6: Compat toggles
- **raven-builder.AC6.1 Success:** with `line_shape_enabled=False` (default) Line is never drawn; with `True` Line participates and the shape draw changes accordingly.
- **raven-builder.AC6.2 Success:** each compat flag is documented in the registry with its divergence and default. *(Tested in Task 1: a registry-completeness test asserts one documented row per `CompatFlags` field.)*

> **AC2.1 is NOT verified here** (decision DR4): the label-based hand-derived table needs `label()`, which doesn't exist until Phase 5. Phase 4 verifies structure by direct inspection of `build()` output instead.

---

## Decisions carried into this phase (resolved during planning)

1. **Re-model boundary:** config replaces the upstream config-level RNG draws; RNG is used only for surface/fill/distractor generation, with the per-surface draw order (`width → conditional height → swap → fill → shape`, 2–3 pre-fill draws; see the Codebase-verified header) ported faithfully. The binding requirement is **internal determinism** (same config+seed → same output), not byte-identity vs the Java batch generator (DR3). **Caveat (RNG-stream fidelity):** even setting aside config-level draws, the default `relocate_correct_answer=False` skips a conditional upstream `nextInt` for relocating configs (see §3), so byte-stream identity with the JVM is only attainable under `relocate_correct_answer=True`; the optional Java differential is scoped to that flag.
2. **Identity in logic, value in dedup (DR7):** AND/OR/XOR use Python identity membership over **shared** `SurfaceFeature` instances; distractor dedup uses **cell-level** value equality. Upstream has **two distinct** value helpers — keep them separate: (a) the **feature-list** helper from Phase 2, `contains_check(list[SurfaceFeature], SurfaceFeature)`, mirroring `SGMBaseCell.containsFeatureCheck` (SGMBaseCell.java:188); and (b) a **Phase-4 cell-list** helper `_contains_cell(list[Cell], Cell)`, mirroring `SGMMatrix.containsCheck` (SGMMatrix.java:575, the distractor-dedup call at l.492), which rests on a cell value-equality `_cell_value_equals(Cell, Cell)` mirroring `SGMCell.equals` (SGMBaseCell.java:202). Distractor dedup is over **cells**, not feature lists. Dedup is list-based — no `set` in any output path.
3. **CompatFlags** frozen dataclass threaded through `build()`, documented in `docs/compat-registry.md`:
   - `line_shape_enabled: bool = False` — code disables Line (False = faithful-to-code). True → `nextInt(7)` + Line case.
   - `relocate_correct_answer: bool = False` — code relocates the correct position on blank-pad; **False = faithful-to-design (honor the configured position)**, the default; True = replicate upstream relocation. *(Note the inverted default polarity vs `line_shape_enabled`: the design makes position an explicit input, so honor-config wins by default.)* **It is also an RNG-consumption toggle, not only a position toggle:** the upstream relocation block (`SGMMatrix.java:531–548`) fires conditionally and, when `positionInAnswerChoices > 0`, draws `random.nextInt(positionInAnswerChoices)` (l.538). The default (`False`) skips that whole block, so **for relocating configs it consumes one fewer draw than the JVM and every later draw shifts** vs upstream. This does not affect internal determinism (AC4.1) or the structural oracle (AC2.*) — both hold regardless — but it does mean the *optional* Java byte-stream differential is only meaningful under `relocate_correct_answer=True` (see Decisions §1 caveat).
4. **AC2.1 deferred to Phase 5;** Phase 4 verifies structure by direct inspection.

---

<!-- START_SUBCOMPONENT_A (tasks 1-2): CompatFlags + surface/fill generators -->

<!-- START_TASK_1 -->
### Task 1: `CompatFlags` + fill-pattern generator + registry

**Verifies:** raven-builder.AC6.2 (registry completeness); foundation for AC6.1

**Files:**
- Create: `src/raven_matrix/compat.py` (`CompatFlags`, `DEFAULT_FLAGS`)
- Create: `src/raven_matrix/fillpattern.py` (fill generator + the catalogue lists)
- Create: `docs/compat-registry.md`
- Test: `tests/test_fillpattern.py` (unit)
- Test: `tests/test_compat_registry.py` (unit — registry-completeness gate)

**Consumers:** `CompatFlags` → every `build()` call (Task 7) + the surface generator (Task 2); the fill generator → the surface generator (Task 2) and the ChangeFill/FillRep supplementals (Task 4).

**Implementation:**
- `compat.py`:
  ```python
  from dataclasses import dataclass

  @dataclass(frozen=True, slots=True)
  class CompatFlags:
      line_shape_enabled: bool = False       # code: Line disabled in generator
      relocate_correct_answer: bool = False  # code relocates correct pos on blank-pad

  DEFAULT_FLAGS = CompatFlags()
  ```
- `fillpattern.py`: the **base** fill catalogue in upstream draw order `[Fill.WHITE, Fill.GREY75, Fill.BLACK]` and `generate_fill(rng) -> Fill` doing `catalogue[rng.next_int(3)]`. Also expose the named lists the supplementals need (port verbatim from source): `CHANGE_FILL_CYCLE = [WHITE, GREY75, GREY40, GREY10, BLACK]`, `FILL_REP_CYCLE = [WHITE, BLACK, GREY75]`. The executor must re-read `SGMFillPatternGenerator.java` + the supplemental generators to confirm each list order before pinning.
- `docs/compat-registry.md`: a table with columns *flag · divergence · default · source*. Seed both flags above. Add a one-line note: most flags default faithful-to-code; `relocate_correct_answer` defaults faithful-to-design because the design makes correct-answer position an explicit input. Use a stable, parseable row format (one row per flag, the flag name in the first column verbatim, e.g. a Markdown table or `| line_shape_enabled | … |`) so the completeness test can match field names against rows.

**Testing (describe):**
- `generate_fill` returns the catalogue element at the drawn index for pinned seeds; the catalogue order is exactly `[White, Grey75, Black]`; `CompatFlags()` has both defaults `False`.
- **AC6.2 registry completeness** (`tests/test_compat_registry.py`): read `docs/compat-registry.md` (stdlib only — `pathlib`), and assert that **every field of `CompatFlags`** (via `dataclasses.fields(CompatFlags)`) appears as a documented row in the registry, and that no registry row names a non-existent flag. This makes the registry self-enforcing: a flag added to `CompatFlags` without a registry entry (or vice versa) fails the build — keeping the *growing* registry honest as later phases discover divergences.

**Verification + commit:**
```bash
uv run pytest tests/test_fillpattern.py tests/test_compat_registry.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/compat.py src/raven_matrix/fillpattern.py docs/compat-registry.md tests/test_fillpattern.py tests/test_compat_registry.py
git commit -m "feat(compat,fill): CompatFlags + self-enforcing registry + fill-pattern generator"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: Surface-feature generator (+ `line_shape_enabled`)

**Verifies:** raven-builder.AC6.1

**Files:**
- Create: `src/raven_matrix/surface.py`
- Test: `tests/test_surface.py` (unit)

**Consumer:** the base/supplemental structure features (Tasks 3–4) and `build()` (Task 7) draw surfaces via this.

**Implementation:** `generate_surface_feature(rng, flags, cell_pixel_size) -> SurfaceFeature` ported from `SGMSurfaceFeatureGenerator.java:134–164`, preserving the **exact draw order** (read the source — do not trust this summary blind):
1. width: `rng.next_int(3)` → `quarter*(n+1)` of the cell (l.134), i.e. ¼/½/¾ cell;
2. height: **conditional** — if width is ½ cell → height ¾ cell (no draw); elif width is ¾ cell → height ½ cell (no draw); **else** (width ¼ cell) `rng.next_int(2)` → height (the `else` branch at l.142). So this draw fires only for the smallest width;
3. **swap:** `rng.next_boolean()` (l.144) → swap width/height when true. **This draw always fires.** Net pre-fill draws = **2 or 3** (3 only when step 2 drew);
4. rotation = 0, position = centre (no draw);
5. fill via `generate_fill(rng)` (the call is at `SGMSurfaceFeatureGenerator` l.159; the actual draw is a single `next_int(3)` over the allowed fills, inside `SGMFillPatternGenerator.java:71`/`:99`);
6. shape index: `rng.next_int(6)` faithful-to-code (l.164); **if `flags.line_shape_enabled`** then `rng.next_int(7)` and Line participates.
- **The shape index→class mapping must be read directly from the source switch** (the two investigators gave slightly inconsistent orderings). The executor reads `SGMSurfaceFeatureGenerator.java` **lines 164–202** (the live `switch`), ports the live `case` order verbatim for the `False` branch (0=Ellipse, 1=Rectangle, 2=Triangle, 3=Tee, 4=Diamond, 5=Trapezoid — confirm against source), and adds the Line case only under the `True` branch. Note the **commented-out** Line block at lines 197–201 carries a stale `case 4` label that the live switch already uses for Diamond — do not let it mislead the index order. Pin the mapping in a comment with the source line numbers.

**Testing (describe):**
- AC6.1: with default flags, drawing many surfaces over fixed seeds never yields `Shape.LINE`, and the shape draw uses bound 6; with `line_shape_enabled=True`, the bound is 7 and Line can appear (and the produced sequence differs from the False case for the same seed — the draw bound changed).
- **Draw-order / draw-count test (against a reference `JavaRandom`):** for the seed, replay the pinned sequence on a *separate* reference `JavaRandom(seed)` — `next_int(3)` (width), then **only if** the width is the smallest size `next_int(2)` (height), then `next_boolean()` (swap), then `next_int(3)` (fill), then `next_int(6)` (shape) — and assert (a) the produced `SurfaceFeature`'s width/height/swap/fill/shape correspond to those drawn values, and (b) the generator's `rng` is left in the **same internal state** as the reference advanced by the matching **variable** count (**2 or 3 pre-fill draws** + fill + shape), proving the generator consumed exactly that many draws in that order. Pin **two** seeds: one whose width forces the height draw (3 pre-fill draws) and one whose width skips it (2 pre-fill draws), so both branches are covered. Do **not** assume a single fixed pre-fill draw count.

**Verification + commit:**
```bash
uv run pytest tests/test_surface.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/surface.py tests/test_surface.py
git commit -m "feat(surface): surface-feature generator with line_shape_enabled toggle"
```
<!-- END_TASK_2 -->
<!-- END_SUBCOMPONENT_A -->

<!-- START_SUBCOMPONENT_B (tasks 3-4): structure features -->

<!-- START_TASK_3 -->
### Task 3: Base relations (ShapeRepetition + Logical AND/OR/XOR)

**Verifies:** (structural foundation for AC1.1–AC1.3; full check in Task 7)

**Files:**
- Create: `src/raven_matrix/structure/__init__.py`
- Create: `src/raven_matrix/structure/base.py`
- Test: `tests/test_structure_base.py` (unit)

**Consumer:** `build()` layer generation (Task 5) instantiates these per the config's base relation.

**Implementation (port from `structure/base/`):**
- A `BaseStructureFeature` protocol exposing `provide_base_surface_features(base_index)` and a transform hook, plus its `LocationTransform`.
- `ShapeRepetition`: `provide_base_surface_features` cycles a pre-built feature list by `base_index % len`; derived locations inherit the parent's features unchanged.
- `LogicalAND/OR/XOR`: operate over feature lists from **two** prior cells (the 2×2 LogicLocationTransform block). Use **identity** membership (Python `in` over `SurfaceFeature`, which is identity) so the upstream `List.contains` semantics are preserved, and **share** feature instances (do not copy) so identity is meaningful:
  - AND = features in cell-one that are also (by identity) in cell-two;
  - OR = cell-one features, then cell-two features not already present (by identity);
  - XOR = features in exactly one of the two (by identity).
  The logic base-feature assignment draws (`next_int(n+1)` count, `next_int(n)` pick, 3–5 base features) port from `AbstractLogicOperationSGMStructureFeature`.

**Testing (describe):**
- ShapeRepetition over a horizontal transform on a 3×3: each row repeats the base feature; assert the produced grid's features.
- AND/OR/XOR over hand-built 2×2 source cells of **shared** instances reproduce intersection/union/symmetric-difference **by identity** — and a value-equal-but-distinct instance is treated as absent (the DR7 witness at the relation level).

**Verification + commit:**
```bash
uv run pytest tests/test_structure_base.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/structure/ tests/test_structure_base.py
git commit -m "feat(structure): base relations — ShapeRepetition + logical AND/OR/XOR (identity)"
```
<!-- END_TASK_3 -->

<!-- START_TASK_4 -->
### Task 4: Supplemental relations

**Verifies:** (structural foundation for AC1.3; full check in Task 7)

**Files:**
- Create: `src/raven_matrix/structure/supplemental.py`
- Modify: `src/raven_matrix/structure/__init__.py` (re-exports)
- Test: `tests/test_structure_supplemental.py` (unit)

**Consumer:** `build()` layer generation (Task 5) applies these (≤3) atop a non-logic base.

**Implementation (port from `structure/supplemental/`, exact params):**
- `ApplyRotation`: derived rotation = `45 + parent.rotation` (additive).
- `ApplyScaling`: derived scale = `0.66 * parent.scale` (multiplicative).
- `ChangeFillPattern`: base locations all take `CHANGE_FILL_CYCLE[0]`; derived fill = `CHANGE_FILL_CYCLE[(index_of(parent.fill)+1) % len]`.
- `FillPatternRepetition`: base locations cycle `FILL_REP_CYCLE[base_index % len]`; derived inherit parent fill.
- `TranslationalNumerosity`: produce `initial_numerosity` (1–2) copies at base, `n+1` copies at derived, laid out on the computed grid (port `numPositions`/`positionStepSize`/`scaling`). Operates on copies — confirm whether copies are fresh instances (they are mutated for layout), so use fresh `SurfaceFeature` instances here (numerosity is not part of the identity-logic path).

**Testing (describe):** each supplemental, applied over a 3-cell horizontal chain, produces the pinned rotation/scale/fill/count progression. Edge: ChangeFill wraps at the end of its cycle.

**Verification + commit:**
```bash
uv run pytest tests/test_structure_supplemental.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/structure/ tests/test_structure_supplemental.py
git commit -m "feat(structure): supplemental relations (rotation/scaling/fill/numerosity)"
```
<!-- END_TASK_4 -->
<!-- END_SUBCOMPONENT_B -->

<!-- START_SUBCOMPONENT_C (tasks 5-7): the builder -->

<!-- START_TASK_5 -->
### Task 5: `BuilderConfig`/`LayerConfig` + layer generation + composition

**Verifies:** raven-builder.AC1.1, AC1.2, AC1.4 (validation)

**Files:**
- Create: `src/raven_matrix/builder.py` (config dataclasses + layer build + composition; `build()` finished in Task 7)
- Test: `tests/test_builder_layers.py` (unit)

**Consumer:** `build()` (Task 7) and the CLI/app/parser (Phases 5, 7).

**Implementation:**
- `LayerConfig(base: BaseRelation, base_direction: Direction, supplementals: tuple[tuple[Supplemental, Direction], ...])` and `BuilderConfig(layers: tuple[LayerConfig, ...], correct_answer_position: int)` — frozen, exactly the design contract.
- **Validation** (raises `ValueError`, AC1.4): 1–2 layers; ≤3 supplementals per layer; `1 <= correct_answer_position <= 8`; a logic base relation forbids supplementals (upstream constraint); diagonal/logic directions inherit the Phase-3 grid constraint (3×3 is odd-square so it passes; the error path is exercised via a non-odd-square size if exposed).
- `_build_layer(layer_config, size, rng, flags) -> Layer`: instantiate the base relation with its `LocationTransform`, generate its base surface features (via Task 2, drawing in order), walk the transform to populate the grid (ShapeRep/derived for geometric; the two-prior-cell fill for logic), then apply each supplemental in config order. Mirror `SGMLayerGenerator`'s per-feature draw order **minus** the config-level draws.
- `_compose(layers, size) -> list[list[Cell]]`: each cell = **concatenation** of every layer's feature list at that location (`combineWith` semantics), in layer order.

**Testing (describe):**
- AC1.1/AC1.2: a 1-layer and a 2-layer config build a 3×3 grid; the 2-layer cells contain both layers' features (concatenation, count = sum).
- AC1.4: >3 supplementals, position 0 or 9, and a logic base + supplemental each raise `ValueError`.

**Verification + commit:**
```bash
uv run pytest tests/test_builder_layers.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/builder.py tests/test_builder_layers.py
git commit -m "feat(builder): config dataclasses + validation + layer build + composition"
```
<!-- END_TASK_5 -->

<!-- START_TASK_6 -->
### Task 6: Answer + distractor generation

**Verifies:** (part of AC1.1 — 8 answer choices; determinism in Task 7)

**Files:**
- Modify: `src/raven_matrix/builder.py` (answer generation)
- Test: `tests/test_builder_answers.py` (unit)

**Consumer:** `build()` (Task 7).

**Implementation (port from `SGMMatrix.java` ~242–572):**
- Correct answer = the composited bottom-right cell `(2,2)`.
- Generate up to 7 distractors via the **four strategies** (`rng.next_int(4)` selects; port each case verbatim): (0) subset-of-layers (only meaningful when ≥2 layers); (1) a wrong cell (any matrix cell except `(2,2)`); (2) modify one parameter (fill or scale→0.66) of a random feature in a random layer/cell; (3) random layer combination.
- **Dedup (cell-level — define both helpers here):** `_cell_value_equals(a: Cell, b: Cell) -> bool` mirrors `SGMCell.equals` (SGMBaseCell.java:202): equal feature count **and** every feature of one is value-present in the other via the **Phase-2 feature-list** `contains_check(list[SurfaceFeature], …)`. `_contains_cell(choices: list[Cell], candidate: Cell) -> bool` mirrors `SGMMatrix.containsCheck` (SGMMatrix.java:575, used at l.492): True iff some non-`None`/non-blank choice `_cell_value_equals` the candidate. A candidate that `_cell_value_equals` the correct answer or any existing choice increments a duplicate counter; reset on a unique insert; stop at `MAX_DUPLICATES_IN_A_ROW = 500`. **Do not reuse the feature-list `contains_check` for this** — dedup compares whole cells, not feature lists.
- **Blank-pad:** remaining slots become blank cells (no features, location `None`).
- **Position:** place the correct answer at the configured `correct_answer_position` (1-based → 0-based). **Default (honor config):** never relocate; blanks fill the other slots around the fixed correct position. **If `flags.relocate_correct_answer`:** replicate the upstream relocation block (`SGMMatrix.java:531–548`) — it fires only when the configured position sits past the contiguous wrong-answer block, and then draws `rng.next_int(positions_filled)` (l.538, skipped when `positions_filled == 0`) — registered as the faithful-to-code path. **RNG note:** because that draw is *inside* the skipped block, the default path consumes one fewer draw than upstream for relocating configs (the RNG-consumption divergence recorded in Decisions §3); do not "compensate" with a throwaway draw — the honor-config path is deliberately a different stream.

**Testing (describe):**
- 8 answer choices are produced; the correct answer sits at the configured position (default flags); duplicates are excluded by **cell value equality** (`_cell_value_equals`): two distinct cells with value-equal feature lists don't both appear, and a candidate cell value-equal to the correct answer is rejected. Add a direct unit test of `_cell_value_equals`/`_contains_cell` on hand-built cells (value-equal-but-distinct → equal; differing feature count → not equal; `None`/blank skipped) so the cell-list helper is covered independently of `build()`.
- A deliberately impoverished config (e.g. a blank-ish single feature) triggers blank-pad without error (AC5.3 precursor).
- With `relocate_correct_answer=True` in a forced blank-pad case, the correct position can move; with default flags it cannot.

**Verification + commit:**
```bash
uv run pytest tests/test_builder_answers.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/builder.py tests/test_builder_answers.py
git commit -m "feat(builder): answer/distractor generation (4 strategies, 500-cap dedup, blank-pad)"
```
<!-- END_TASK_6 -->

<!-- START_TASK_7 -->
### Task 7: `build()` end-to-end — determinism, option-surface, flag

**Verifies:** raven-builder.AC1.1, AC1.3, AC4.1, AC4.3, AC6.1

**Files:**
- Modify: `src/raven_matrix/builder.py` (`build()` + `build_from_code` stub deferred to Phase 5)
- Test: `tests/test_builder_build.py` (unit + property)

**Implementation:** `build(config, seed, flags=DEFAULT_FLAGS) -> Matrix` ties Tasks 5–6 together: one `JavaRandom(seed)`, build each layer, compose, generate answers, return `Matrix(cells, answer_choices, correct_answer_position, layers)`.

**Testing (describe):**
- **AC1.3 (option surface):** parametrize over every `BaseRelation`, every `Supplemental`, every `Direction` (1–5) — each builds and the produced layer's structure features/directions match the config (direct structural inspection, per DR4).
- **AC4.1 (determinism):** `build(config, seed)` twice → deep-equal matrices (compare structure + per-feature values + answer cells by value). Run for several configs.
- **AC4.3 (seed independence — discriminating, not probabilistic):** choose **two specific seeds** whose `JavaRandom` streams are known (replay them against the **Phase-2 golden-vector fixture** / a reference `JavaRandom`) to produce a **different shape index** (`next_int(6)`) for the **first base surface feature drawn** under a fixed single-layer config (identify that feature's grid location from the chosen config). Assert: (a) the two matrices are **structurally equal** (same relations/directions/layers, by inspection); (b) that **named, located feature**'s `shape` is **exactly `!=`** between the two runs (a specific inequality on a specific attribute — not "some feature somewhere differs"). This is falsifying: if `build()` failed to thread the surface RNG, the asserted feature would be identical and the test would fail.
- **AC6.1:** a config whose surfaces could include Line never does with default flags; with `line_shape_enabled=True` the output differs for the same seed.
- Property (hypothesis): for random valid configs + seeds, `build` returns a 3×3 with exactly 8 answer choices and a correct answer at the configured position (default flags).

**Verification + commit:**
```bash
uv run pytest tests/test_builder_build.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/builder.py tests/test_builder_build.py
git commit -m "feat(builder): build() end-to-end — determinism, option surface, compat flag"
```
<!-- END_TASK_7 -->
<!-- END_SUBCOMPONENT_C -->

---

## Phase 4 completion check

- [ ] `build()` produces a 3×3 + 8 answers for 1- and 2-layer configs (AC1.1, AC1.2).
- [ ] Every base relation, supplemental, and direction 1–5 builds and is structurally realised (AC1.3, by direct inspection).
- [ ] Invalid configs raise `ValueError` (AC1.4): >3 supplementals, position ∉1–8, logic+supplemental.
- [ ] Same config+seed → identical matrix; different seed → same relations, different surfaces (AC4.1, AC4.3).
- [ ] `line_shape_enabled` flips behaviour (AC6.1); `relocate_correct_answer` honors config by default.
- [ ] Logic relations use identity membership over shared instances; dedup is value-based and list-based (no `set` in output).
- [ ] `docs/compat-registry.md` documents both flags + the default-polarity note.
- [ ] `uv run pytest`, `uv run ty check .`, `uv run ruff check .` clean.
- [ ] (Noted) AC2.1 deferred to Phase 5; Phase 4 is a provisional gate.
