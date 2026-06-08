# RESUME — raven-builder implementation plan: apply critical-peer-review fixes, then hand off

You are resuming after a context reset. The raven-builder **implementation plan is already
written and reviewed**; your job is a small, well-specified revision, then the execution handoff.
Do **not** re-plan or re-investigate the whole thing.

## State

- **Worktree:** `/home/brian/people/Mark/raven-matrix/.worktrees/raven-builder` (branch `raven-builder`, off `main`). Work here.
- **Plan dir:** `/home/brian/people/Mark/raven-matrix/.worktrees/raven-builder/docs/implementation-plans/2026-06-08-raven-builder/`
  contains `phase_01.md … phase_08.md`, `test-requirements.md`, `uat-requirements.md`, `code-review-findings-plan-validation.md`, `critical-peer-review-findings.md`.
- The plan **passed** code-review Finalization (APPROVED). Critical-peer-review returned **NEEDS_REVISION** with 6 fixes.
  None block the v1 acceptance bar — they are RNG-stream-fidelity provenance corrections, one missing helper, and clarifications.
- Upstream Java for verifying source-line claims: extract `…/upstream/Matrices/Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip`
  to a temp dir, or read the pre-extracted copy at `/home/brian/people/Mark/raven-matrix/scratch/SandiaGeneratedMatrixTool-1.0.0-source/Source/`.

## FIRST ACTION — read `critical-peer-review-findings.md`, then apply these targeted edits

1. **C2 — phase_04.md surface draw order.** Re-pin to: `nextInt(3)` width → **conditional `nextInt(2)` height** → **`nextBoolean()` swap** → fill → `nextInt(6)` shape (source `SGMSurfaceFeatureGenerator.java:134–164`; live switch cases are 164–202, not ~180–210). Fix the "Codebase verified" header's claimed order; rewrite the Task 2 draw-order test to advance a reference `JavaRandom` by the correct **variable** count (2 or 3 pre-fill draws), not a single one.
2. **C1 — phase_04.md relocation RNG.** Note that `relocate_correct_answer=False` (default) also **skips an upstream `nextInt`** (`SGMMatrix.java:531–548`), so it changes the RNG draw count vs the JVM for relocating configs — it is an RNG-consumption toggle, not only a position toggle. Scope the optional Java differential to `relocate_correct_answer=True`; add this to the determinism caveat.
3. **I2 — phase_04.md Task 6 cell dedup (most execution-relevant).** Define and assign a **cell-level** value-equality + `contains_check(list[Cell], Cell)` (mirroring `SGMMatrix.java:575`, used at 492). Fix the `contains_feature_check` name (it is referenced but never defined). Distinguish the Phase-2 feature-list helper from this Phase-4 cell-list helper in both phases.
4. **I1 — design glossary + phase_05.md.** Reconcile the `label()` citation: use `208–389` (was `308–382`, which omits the letter ladder 232–289). Apply in the glossary, the Phase 5 Task 1 docstring instruction, and the DR-Labeller entry.
5. **I3 — phase_04.md Task 7 + test-requirements.md AC4.3.** Make AC4.3 discriminating: pin specific seed pairs known (from the Phase-2 fixture) to differ on the first shape draw and assert a **specific** feature differs, not "some" (the current test is near-tautological/probabilistic).
6. **I4 — phase_05.md.** State that the 840-sweep validates only the **structure→label** path; the answer/distractor path runs (with default position/seed) but is **not** under test. Optionally build a structure-only matrix for the sweep.
7. **F1 — phase_05.md.** Mark the `ShapeRep+corner-out→A6` hand-table row as a **labeller-internal-consistency** entry (its `6` is derived from labeller behaviour, no published stimulus uses it) — not counted toward the "independent reference frame" guarantee.
8. **F3 — phase_06.md.** Pin explicitly that `render/__init__.py` must **not** re-export `raster` (keep the `resvg_py` import inside `rasterise`) — the Phase-8 import-hygiene test depends on it.

(F2 is an honest residual — optionally add a one-line note in phase_05.md that the inspect-every-miss gate's strength is bounded by reviewer honesty + parser/labeller co-authorship, with the hand-table as the only independent guard.)

## SECOND ACTION — verify

Re-run `denubis-plan-and-execute:critical-peer-review` **once** over the plan dir (focus: confirm C1/C2/I1/I2/I3/I4 resolved + no new Critical/Important). If it returns new Critical/Important, **HALT and present to the user** — do not auto-loop.

## THIRD ACTION — execution handoff

Follow the Execution Handoff section of `denubis-plan-and-execute:starting-an-implementation-plan`:
1. `git rev-parse --show-toplevel` → `WORKING_ROOT`.
2. `ls -d "$WORKING_ROOT/docs/implementation-plans/2026-06-08-raven-builder"` (must succeed).
3. Output the copy-paste command with **verified absolute paths**:
   `/denubis-plan-and-execute:executing-an-implementation-plan <WORKING_ROOT>/docs/implementation-plans/2026-06-08-raven-builder/ <WORKING_ROOT>/`
   plus the "copy this BEFORE /clear" warning and the `/clear` step.

## Rules
- **Do not commit** (project rule: commit only when Brian asks). The whole revision is plan-doc edits.
- Targeted edits only — do not rewrite phases wholesale.
- Honour the prior planning decisions (hybrid packaging, AC2.1 in Phase 5, honor-config position + relocate flag, Pyodide 3.12 floor, image-grounded B-disambiguation, registry-completeness test).
