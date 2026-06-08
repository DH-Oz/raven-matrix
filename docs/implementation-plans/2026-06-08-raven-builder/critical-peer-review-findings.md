# Critical Peer Review — raven-builder implementation plan

**Verdict:** NEEDS_REVISION · 2 Critical, 4 Important, 4 Flagged (mostly clean)
**Date:** 2026-06-08 · falsification-first pass that opened the upstream Java source
**Why it caught what the code-review didn't:** the prior code-review (APPROVED) checked
coverage/cross-references but did not read the Java; C1/C2/I1/I2 are visible only against source.

**Calibration note (the planner's read, not the reviewer's):** C1 and C2 affect **RNG-stream
fidelity vs the JVM** and the *optional* Java differential — they do **NOT** threaten the v1
acceptance bar (the structural oracle, AC2.*) nor internal determinism (AC4.1, run-twice),
both of which hold regardless of the exact draw order. The design already scoped stream/distractor
fidelity as best-effort (DR1/DR3). So these are real **provenance/test defects to fix**, but they
are not v1-blocking in the way "Critical" implies. I2 (missing cell-dedup artifact) is the most
execution-relevant.

---

## Critical

### C1 — `relocate_correct_answer=False` (default) skips a conditional `nextInt`, diverging the RNG stream
- **Where:** phase_04.md Task 6 + Decisions §3.
- **Source:** `SGMMatrix.java:531–548` — relocation is conditional and, when it fires with
  `positionInAnswerChoices>0`, draws `random.nextInt(positionInAnswerChoices)`. The default path
  skips that draw → every later draw shifts vs the JVM for relocating configs.
- **Real but scoped:** the default is correctly labelled *faithful-to-design* (honor config); the gap
  is that the plan presents the flag as a *position* toggle only, omitting that it is also an
  *RNG-consumption* toggle. Affects the Java differential, not AC4.1/AC2.*.
- **Fix:** state the default changes the RNG draw count vs upstream for relocating configs; scope the
  Java differential to `relocate_correct_answer=True`; add to the determinism caveat.

### C2 — pinned per-surface draw order is wrong against source (single `nextInt(3)` vs 2–3 draws)
- **Where:** phase_04.md "Codebase verified" header + Task 2 ("size → fill → shape"; test asserts one-draw advance).
- **Source:** `SGMSurfaceFeatureGenerator.java:134–164` — `nextInt(3)` width → **conditional `nextInt(2)`
  height** (else-branch) → **`nextBoolean()` swap** → fill → `nextInt(6)` shape. Pre-fill draws = 2 or 3, not 1.
- **Note:** the plan already told the executor to "read the source directly" and flagged investigator
  disagreement — so the body is half-honest, but the header pins a wrong order as "source-verified" and
  the draw-order test encodes the wrong count.
- **Fix:** re-pin the sequence (cite 134–164); rewrite the draw-order test to advance the reference
  `JavaRandom` by the correct variable count; correct the contaminated provenance header; the "read lines
  ~180–210" pointer should be 164–202 (the live switch cases).

---

## Important

### I1 — `label()` cited as `308–382`, which omits the letter ladder (232–289)
- **Where:** design glossary + phase_05.md Task 1 docstring instruction (says 308–382); Step 2 separately says 210–389.
- **Fix:** use `208–389` (or 210–389) consistently. Trivial citation reconciliation.

### I2 — cell-level dedup helper referenced but never defined (most execution-relevant)
- **Where:** phase_04.md Decisions §2 + Task 6 use `value_equals` + `contains_feature_check` / "cell value equality";
  Phase 2 Task 4 defines only `contains_check(features: list[SurfaceFeature], item)`.
- **Source:** upstream has TWO checks — feature-list (`containsFeatureCheck`, SGMBaseCell.java:188) AND
  **cell-list** (`containsCheck(List<SGMCell>, SGMCell)`, SGMMatrix.java:575, used at 492). Distractor dedup is
  over **cells**, not feature lists.
- **Fix:** Phase 4 Task 6 must define cell-level value-equality + a `contains_check(list[Cell], Cell)`
  (mirroring SGMMatrix.java:575); fix the `contains_feature_check` name; distinguish the two helpers in Phase 2 and 4.

### I3 — AC4.3 test is near-tautological / probabilistic
- **Where:** phase_04.md Task 7 + test-requirements AC4.3 ("structure equal but some surfaces differ").
- **Why:** "structure equal" is guaranteed by construction (tests nothing about RNG); "some differ" is hedged
  and could collide → flaky, not falsifying.
- **Fix:** pin specific seed pairs known to differ on the first shape draw; assert a *specific* feature differs.

### I4 — the 840-sweep runs full `build()` (with a fabricated position + seed=0) but only validates structure→label
- **Where:** phase_05.md Task 2 (default position 1) + Task 4 (`build(config, seed=0)`).
- **Why:** `label()` reads only `matrix.layers[].structures`, so the answer/distractor path runs but is **not**
  under test — mild overclaim of what the sweep covers.
- **Fix:** state the sweep covers only structure→label; optionally build a structure-only matrix for the sweep.

---

## Flagged (mostly honest residuals)

- **F1:** the `ShapeRep+corner-out→A6` hand-table row IS labeller-derived (no published stimulus uses it) — mark it a
  labeller-internal-consistency entry, NOT counted toward the "independent reference frame" guarantee.
- **F2:** the inspect-every-miss gate's strength is bounded by reviewer honesty (a modeling-gap label can absorb a real
  bug; parser+labeller authored by the same executor can compensate). The hand-table (F1 aside) is the only guard — state
  this bound plainly.
- **F3 (WASM clean):** pin that Phase 6 `render/__init__.py` must NOT re-export `raster` (the import-hygiene test relies
  on `rasterise`'s import staying inside the function — phase_06 already does this; make the constraint explicit).
- **F4:** other "Verifies" mappings spot-checked clean (AC3.1, AC4.2, AC5.1/5.2, AC6.2, AC1.5).

---

## Required before execution (reviewer's list)
Fix C2 draw order + provenance; disclose C1 + scope Java differential to `True`; reconcile I1 citation; define+assign the
cell-level dedup helper and fix its name (I2); make AC4.3 discriminating (I3). I4/F1/F2/F3 are short clarifications.
