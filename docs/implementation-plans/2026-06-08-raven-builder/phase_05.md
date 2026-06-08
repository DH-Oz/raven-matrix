# raven-builder Implementation Plan — Phase 5: Labeller, parser, structural oracle

**Goal:** Port `label()` (matrix → Structure code) faithfully from the Java labeller; build `parse_code()` (code → config) from the Matzen naming convention; anchor correctness with an independently hand-derived label table; and run the 840-code round-trip as a fully-accounted **pass map** where every non-pass is inspected.

**Architecture:** `label.py` in the zero-dependency core. `label()` is a literal port of `SGMMatrixDifficultyClassifier.evaluate`'s sb-logic: it walks `matrix.layers[].structures`, emits a letter per relation type and a digit per transform (with the `1/2` swap and the `6/7` edge codes), `_`-joins layers. `parse_code()` is a **new** artifact (no upstream inverse exists) driven by the naming scheme. The **hand-derived table** (~12 configs → expected codes, derived from the paper's convention + the published codes, NOT from the Java labeller — DR6) is the hard correctness gate. The 840-sweep is a consistency check that emits a per-code pass map; logic codes are normalised; every failure is inspected and recorded with a reason, and the test fails on any *uninspected* miss.

**Tech Stack:** Python (dev 3.14, package floor 3.12 — see Phase 1 decisions) stdlib only (`csv`). Tests: pytest + hypothesis.

**Scope:** Phase 5 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`.

**Codebase verified:** 2026-06-08. Labeller pinned verbatim (`SGMMatrixDifficultyClassifier.java:208–389` — the `sb`-build inside `evaluate()`, whose signature is at l.191): letter map `A`=ShapeRep, `X/Y/Z`=OR/AND/XOR, `B`=FillRep **and** ChangeFill, `C`=Rotation, `D`=Scaling, `E`=Numerosity, fallbacks `U`/`V`; digit map with the `1/2` swap (repetition features {ShapeRep, FillRep} keep the same-direction digit, others swap); `6`=TopLeftCornerOut+repetition, `7`=Logic transform, `0`=unknown. Reads bound structure features (not inferred from cells). No upstream parser. Oracle CSV (840 rows, 553 distinct codes) committed in Phase 1.

**Phase Type:** functionality

---

## Acceptance Criteria Coverage

### raven-builder.AC2: Labeller correctness + structural consistency
- **raven-builder.AC2.1 Success (primary anchor):** the hand-derived label table (~12 configs incl. shape-rep × each direction with corner-out→`6`; each supplemental; OR/AND/XOR) matches expected labels derived from the Matzen paper's naming convention + the published codes (independent of the Java source).
- **raven-builder.AC2.2 Success (consistency):** all 840 `Structure` codes round-trip (code→config→matrix→label→code) outside the documented exclusion list.
- **raven-builder.AC2.3 Edge:** logic codes (`X`/`Y`/`Z`) parse and label correctly despite carrying no direction or surface detail.
- **raven-builder.AC2.4 Failure:** a malformed code raises a clear parse error.

---

## Decisions carried into this phase (resolved during planning)

- **`label()`** = faithful port of the verbatim sb-logic (letters, digits, `1/2` swap, `6/7`), reading `matrix.layers[].structures`.
- **Hand-derived table (AC2.1) is the HARD gate**, built independently from the Matzen naming convention + the published codes **+ the published PNGs for genuinely ambiguous cases** (DR6's independent reference frame) — never read from the Java labeller. It is created **wholly in Phase 5** (the design's "begun in Phase 4" wording is superseded by DR4 — Phase 4 does direct structural inspection, no label-based table).
- **`B`-aliasing resolved by the norming images** (FillRep for `B1`–`B4`, ChangeFill for `B5`; distinguished by fill palette — see Task 2). No compat flag — it is a derivation pinned by ground truth, documented in the hand-table's provenance comments.
- **840-sweep = transparent pass map; inspect every miss.** Logic codes normalised (strip the LogicTransform `7`). The sweep emits a per-distinct-code map (pass / fail+reason). A curated `oracle_exclusions.md` holds every *inspected* failure with its reason. **The test fails if any code misses and is NOT in the curated, reasoned list** — forcing inspection of anything new. Suspected real bugs (not modeling gaps) escalate to the user.
- **Supplemental-only codes (`C3`, `D4`, …):** first establish (by reading the source) whether `ApplyRotation`/`ApplyScaling` provide their own base surface features. If yes, they label as a single feature (`C3`) and round-trip. If no, `parse_code` supplies a documented implicit base and the resulting mismatch is an inspected, recorded modeling gap.

---

<!-- START_SUBCOMPONENT_A (tasks 1-2): labeller + parser -->

<!-- START_TASK_1 -->
### Task 1: `label.py` — `label()` (faithful port)

**Verifies:** raven-builder.AC2.1 (the labeller half), foundation for AC2.2/AC2.3

**Files:**
- Create: `src/raven_matrix/label.py`
- Test: `tests/test_label.py` (unit, structural fixtures)

**Consumer:** the hand-derived table test (Task 3), the round-trip harness (Task 4), the CLI `oracle` command (Phase 7).

**Step 1 (RED): structural fixtures**

`tests/test_label.py` builds matrices with **known** structure features (via Phase 4 `build()` with explicit configs) and asserts `label()` emits the expected code. Cover: ShapeRep on each direction (`A1`,`A2`,`A3`,`A4`, corner-out→`A6`); FillRep (`B1`/`B2` — repetition digit) vs ChangeFill (`B2`/`B1` — swapped digit); Rotation `C`, Scaling `D`, Numerosity `E` with the `1/2` swap; logic OR/AND/XOR → `X7`/`Y7`/`Z7`; a 2-layer config → `_`-joined code. (These assert the *port's* behaviour, including the `6`/`7` the Java emits.)

**Step 2 (GREEN): port `label()`**

Literal port of `SGMMatrixDifficultyClassifier.evaluate` lines 208–389 (the full `sb`-build: `sb` init l.208, the layer loop from l.210, the **letter ladder** 232–289, the digit map 308–382, trailing-`_` delete l.389):
- iterate `matrix.layers`; for each, iterate `layer.structures`;
- per feature, append the letter (`isinstance` ladder: ShapeRep→`A`, OR→`X`, AND→`Y`, XOR→`Z`, else base→`U`; FillRep→`B`, Rotation→`C`, Scaling→`D`, Numerosity→`E`, ChangeFill→`B`, else supplemental→`V`);
- append the digit from `(location_transform_type, is_repetition_feature)` where `is_repetition_feature = isinstance(feature, (ShapeRepetition, FillPatternRepetition))` — Horizontal→`1`/`2`, Vertical→`2`/`1`, DiagBLTR→`3`/`4`, DiagTLBR→`4`/`3`, CornerOut→`6`/`5`, Logic→`7` (both), unknown→`0`;
- append `_` after each layer; delete the trailing `_`.
Keep the structure identical to the Java; cite `SGMMatrixDifficultyClassifier.java:208–389` in a docstring (the complete `sb`-build — the letter ladder lives at 232–289, so the narrower `308–382` would omit how letters are assigned).

**Step 3: green, type, lint, commit**
```bash
uv run pytest tests/test_label.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/label.py tests/test_label.py
git commit -m "feat(label): faithful label() port (letters, 1/2 swap, 6/7 codes)"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: `parse_code()` + `build_from_code()`

**Verifies:** raven-builder.AC2.3, raven-builder.AC2.4

**Files:**
- Modify: `src/raven_matrix/label.py` (add `parse_code`)
- Modify: `src/raven_matrix/builder.py` (add `build_from_code` = `parse_code` + `build`)
- Test: `tests/test_parse_code.py` (unit + property)

**Consumer:** the round-trip harness (Task 4), the CLI/app `--code` path (Phase 7).

**Implementation:** `parse_code(code: str) -> BuilderConfig` driven by the naming scheme (not the Java — there is no upstream parser):
- Split on `_` into per-layer segments; each segment is a sequence of (letter, digit) pairs.
- Letter → relation: `A`→ShapeRepetition (base); `X/Y/Z`→OR/AND/XOR (base, logic — these carry no meaningful digit, the published code is bare); `C`→Rotation; `D`→Scaling; `E`→Numerosity (these three are non-repetition supplementals with no repetition counterpart, so they are unambiguous).
- **`B` is the one aliasing case (resolved during planning by the norming images, not invented).** Both FillRep and ChangeFill label to `B`, and the `1/2` swap makes `parse_code("B1")` ambiguous in the abstract (`FillRep+Horizontal` *or* `ChangeFill+Vertical`). The tie is broken by **fill palette in the published PNGs** (ground truth, part of DR6's independent reference frame): **FillRep uses a 3-level palette `[White, Black, Grey75]`; ChangeFill uses a 5-level palette `[White, Grey75, Grey40, Grey10, Black]`.** Confirmed by inspection of `1 Layer Stim/B*_1.png`:
  - `B1` = **FillRep + Horizontal** (rows constant, 3-level), `B2` = **FillRep + Vertical** (columns constant), `B3`/`B4` = **FillRep** + the matching diagonal (Phase 5 confirms each by palette);
  - `B5` = **ChangeFill + TopLeftCornerOut** — digit `5` can *only* come from a non-repetition feature + corner-out (FillRep + corner-out labels as `6`), and the PNG shows the 5-level corner-out gradient.
  So `parse_code` maps `B1`–`B4` → `FillRep` (repetition reading, digit = transform direction) and `B5` → `ChangeFill + corner-out`. The executor re-inspects the `B*` PNGs to pin `B3`/`B4` before committing the table.
- Digit → direction, inverting the `1/2` swap per repetition/non-repetition feature.
- **First decide the supplemental-only question by reading the source:** does `ApplyRotation`/`ApplyScaling` provide base surface features? If yes, a lone `C3`/`D4` is a valid single-feature layer. If no, `parse_code` injects a documented implicit ShapeRepetition base (flagged so the harness can record the resulting mismatch as a modeling gap).
- `correct_answer_position` is not encoded in the Structure code; default it (e.g. 1) for `build_from_code`, documenting that the oracle checks structure, not position, here.
- Malformed input (unknown letter, bad digit, empty) raises `ValueError` (AC2.4).

**Testing (describe):**
- AC2.3: `parse_code("X")`/`"Y"`/`"Z"` produce logic configs that build and label (to `X7` etc., normalised in Task 4).
- AC2.4: `parse_code("Q9")`, `""`, `"A"` (missing digit) raise `ValueError`.
- Property (hypothesis): for codes generated from valid (letter,digit) grammar, `parse_code` round-trips structurally with `label` on non-excluded forms.

**Verification + commit:**
```bash
uv run pytest tests/test_parse_code.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/label.py src/raven_matrix/builder.py tests/test_parse_code.py
git commit -m "feat(label): parse_code + build_from_code (naming-scheme inverse)"
```
<!-- END_TASK_2 -->
<!-- END_SUBCOMPONENT_A -->

<!-- START_SUBCOMPONENT_B (task 3): the primary anchor -->

<!-- START_TASK_3 -->
### Task 3: Hand-derived label table (PRIMARY anchor, AC2.1)

**Verifies:** raven-builder.AC2.1

**Files:**
- Create: `tests/data/hand_derived_labels.py` (the ~12-entry table, with provenance comments)
- Test: `tests/test_hand_derived_labels.py` (unit)

**Consumer:** this is the hard correctness gate; no downstream consumer.

**Implementation:** A table of ~12 `(BuilderConfig, expected_code)` entries where each `expected_code` is worked out **by hand from the Matzen paper's naming convention + the published `data/ravens_oracle.csv` codes + the published PNGs** (for the `B` cases) — explicitly NOT read from the Java labeller (DR6). Each entry carries a comment citing the convention rule and a matching published `Stimulus Name`/`Structure` row (or PNG) that justifies it. Cover:
- ShapeRep × {H→`A1`, V→`A2`, BLTR→`A3`, TLBR→`A4`} (each grounded in published codes/PNGs — DR6's independent reference frame); plus the corner-out entry ShapeRep+corner-out→`A6`, marked as a **labeller-internal-consistency** entry only: its `6` is *derived from the labeller's own rule* (repetition+corner-out yields `6`) and **no published stimulus uses it** (the norming study never paired shape-repetition with corner-out — direction 5 excludes shape repetition). **It does NOT count toward DR6's independent-reference-frame guarantee**; flag it as such in its provenance comment so it is never mistaken for an externally-grounded anchor;
- the image-grounded shading entries: FillRep+H→`B1`, FillRep+V→`B2`, ChangeFill+corner-out→`B5` (see Task 2);
- Rotation→`C`, Scaling→`D`, Numerosity→`E` (each unambiguous);
- OR/AND/XOR (logic, bare letter; labels to `X7`/`Y7`/`Z7` pre-normalisation).

**Testing (describe):** for each entry, `label(build(config, seed=0))` equals `expected_code`. This test passing is the phase's correctness proof. If an entry mismatches, either the port is wrong or the hand-derivation is wrong — investigate both, do not "fix" the test to match the code.

**Verification + commit:**
```bash
uv run pytest tests/test_hand_derived_labels.py -v && uv run ty check . && uv run ruff check .
git add tests/data/hand_derived_labels.py tests/test_hand_derived_labels.py
git commit -m "test(oracle): hand-derived label table (primary anchor, independent of Java)"
```
<!-- END_TASK_3 -->
<!-- END_SUBCOMPONENT_B -->

<!-- START_SUBCOMPONENT_C (task 4): the 840 sweep + pass map -->

<!-- START_TASK_4 -->
### Task 4: 840-code round-trip — transparent pass map, inspect every miss

**Verifies:** raven-builder.AC2.2

**Files:**
- Create: `src/raven_matrix/oracle.py` (`round_trip(code) -> RoundTripResult`, `build_pass_map(rows)`)
- Create: `docs/oracle_exclusions.md` (curated, reasoned list of inspected non-passes)
- Test: `tests/test_oracle_sweep.py` (parametrised over distinct codes)

**Consumer:** the CLI `oracle` command (Phase 7) reuses `build_pass_map`.

**Implementation:**
- `round_trip(code)`: `parse_code(code)` → `build(config, seed=0)` → `label(matrix)` → **normalise** (strip a trailing LogicTransform `7` from bare logic codes so `X7`→`X`) → compare to `code`. Return pass/fail + the produced label + a reason tag on fail.
- **Scope of what the sweep tests (do not overclaim):** `label()` reads only `matrix.layers[].structures`, so the sweep validates **only the structure→label path**. `build()` still runs the *full* answer/distractor pipeline (with a fabricated default `correct_answer_position` and `seed=0`), but **that path is not under test here** — its output is neither asserted nor inspected by the sweep; only the layer structures feed the label. The fabricated position/seed are inputs of convenience, not a checked claim. *(Optional, to make the scope literal: build a **structure-only** matrix for the sweep — run layer generation/composition and skip answer generation — so the sweep exercises exactly what it asserts. If kept as full `build()`, this scope note stands.)*
- `build_pass_map(rows)`: over the 553 distinct codes (covering all 840 rows), produce a structured map: `{code: (pass: bool, produced: str, reason: str | None, row_count: int)}`.
- `docs/oracle_exclusions.md`: a curated table of every code expected to fail, each with an **inspected reason** (e.g. "supplemental-only `C3`: ApplyRotation provides no base feature → implicit base adds `A` — modeling gap, needs unpublished seed"). Logic codes should **pass** via normalisation (so they are NOT exclusions) — confirm.

**Testing (the pass-map discipline):**
- Build the pass map over all distinct codes.
- **Assert: every failing code is present in `docs/oracle_exclusions.md` with a reason.** A failure not in the curated list fails the test — this is the "inspect every miss" gate; the executor must read the source, explain it, and either fix the port or record the modeling gap (escalating to the user if it looks like a real bug, not a gap).
- **Assert: every code listed in `oracle_exclusions.md` actually fails** (no stale exclusions masking a regression).
- Report N_pass / 553 distinct codes and the equivalent row coverage / 840, emitted to test output.
- AC2.3 cross-check: the three logic codes pass via normalisation.

> Discipline note: do NOT grow the exclusion list to make the bar green. An exclusion is only valid once its cause is read in the source and written down. Unexplained mismatches are bugs until proven otherwise.
>
> Honest bound (the residual this gate cannot close): the sweep is a **consistency check on a parser/labeller pair written by the same executor**, so a real bug can hide as a mutually-compensating parse+label error, and a "modeling gap" label can absorb a defect the executor didn't recognise. The inspect-every-miss gate's strength is therefore bounded by executor honesty. The **hand-derived table (AC2.1)** — grounded in the published codes/PNGs, excluding the labeller-internal-consistency rows (see Task 3) — is the **only independent guard** here; the 840-sweep is necessary-not-sufficient (DR6). Suspected real bugs escalate to the user rather than being recorded as gaps.

**Verification + commit:**
```bash
uv run pytest tests/test_oracle_sweep.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/oracle.py docs/oracle_exclusions.md tests/test_oracle_sweep.py
git commit -m "feat(oracle): 840-code round-trip pass map with inspected-exclusions gate"
```
<!-- END_TASK_4 -->
<!-- END_SUBCOMPONENT_C -->

---

## Phase 5 completion check

- [ ] `label()` reproduces the structural fixtures incl. the `1/2` swap and `6`/`7` codes (port of `SGMMatrixDifficultyClassifier:208–389`).
- [ ] `parse_code` inverts the naming scheme; logic + malformed codes handled (AC2.3, AC2.4).
- [ ] **Hand-derived table passes** — the hard correctness gate (AC2.1), derived independently of the Java labeller.
- [ ] 840-sweep produces a pass map; **every miss is in `docs/oracle_exclusions.md` with an inspected reason**; no stale exclusions; logic codes pass via normalisation (AC2.2).
- [ ] N_pass/553 distinct (and row coverage/840) reported; any suspected real bug escalated, not excluded.
- [ ] `uv run pytest`, `uv run ty check .`, `uv run ruff check .` clean.
