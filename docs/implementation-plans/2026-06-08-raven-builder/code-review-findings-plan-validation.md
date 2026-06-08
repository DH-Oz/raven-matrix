# Code Review Findings — plan-validation

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 1**

## Verification

No code exists yet — this is a pre-implementation plan review. Verification commands cannot be run.

## Prior Findings Verification

### I1 — "begun in Phase 4" dangle — RESOLVED

phase_05.md Decisions section now states explicitly: "the design's 'begun in Phase 4' wording is superseded by DR4 — Phase 4 does direct structural inspection, no label-based table." The hand-derived table is described as "created wholly in Phase 5." No Phase 4 task references a partial table. The cross-phase confusion is gone.

### I2 — B disambiguation unpinned — RESOLVED

phase_05.md Task 2 now states the tie-breaking rule concretely and cites the physical evidence: FillRep uses a 3-level palette [White, Black, Grey75]; ChangeFill uses a 5-level palette [White, Grey75, Grey40, Grey10, Black]. The mapping is pinned: B1=FillRep+H, B2=FillRep+V, B3/B4=FillRep+respective diagonal (executor confirms by palette), B5=ChangeFill+corner-out (the only way digit 5 can arise for a non-repetition feature). The derivation is attributed to the norming PNGs (ground truth, DR6 independent frame), not invented. This is a falsifiable specification.

### I3 — Pyodide floor / requires-python mismatch — RESOLVED

phase_01.md Task 1 now sets `requires-python = ">=3.12"`, `ruff target-version = "py312"`, `tool.ty.environment python-version = "3.12"`, and the CI matrix is `["3.12", "3.14"]`. The decisions block explains the rationale (micropip honours requires-python; a >=3.14 wheel would refuse to load in Pyodide). phase_08.md Task 1 adds Step 0 (confirm the live Pyodide Python version; raise or lower the floor if the observed version differs from 3.12; record in docs/wasm-export.md). The PEP 723 block in the same task is `>=3.12`. The risk is now explicitly gated, not silently assumed.

### m1 — uat-requirements.md creation never tasked — RESOLVED

phase_07.md Task 2 UAT entries section now reads: "recorded here; the planning flow's final UAT-collation step writes them, with the Phase-8 in-browser entry, into `docs/implementation-plans/.../uat-requirements.md` — no phase task creates that file." The intent is clear: entries are authored in the phase task; the collation step produces the file. No ambiguity about which task creates it.

### m2 — raster API unverified, no pre-test diagnostic — RESOLVED

phase_06.md Task 3 Verification block now includes `uv run python -c "import resvg_py; print(dir(resvg_py))"` as a named diagnostic step before the pytest invocation. This surfaces API name mismatches before the test runs.

### m3 — docs/spikes/ directory never explicitly created — RESOLVED

phase_01.md Task 5 Step 3 now reads: "Create the directory first: `mkdir -p docs/spikes`." Explicit and consistent with the plan's other directory-creation steps.

### m4 — B disambiguation not recorded in compat registry — RESOLVED (via I2)

phase_05.md Decisions section states: "No compat flag — it is a derivation pinned by ground truth, documented in the hand-table's provenance comments." The decision not to add a registry entry is now explicit and justified. This is the correct disposition once I2 is resolved (the rule is unambiguous from the source + images, so it is a pure implementation detail).

---

## Ripple Check: "Python 3.14" references after the floor change

The Tech Stack header lines in phases 2–7 still read "Python 3.14" (dev version). This is cosmetically inconsistent with the new dual-version framing, but it is **not a correctness problem**: the plan's Phase 1 decisions block, the CI matrix, and the pyproject.toml commentary all explain that 3.14 is the dev version and 3.12 is the package floor. An executor reading any phase header and then the Phase 1 decisions block will understand the relationship. Flagging as Minor below.

Phase 8 Tech Stack header reads "Python 3.14" but Phase 8 Task 1 correctly uses `>=3.12` in the PEP 723 block and adds Step 0 to confirm the live Pyodide version. The header is cosmetic; the load-bearing instructions are correct.

---

## Issues

### Minor (count: 1)

**m5 — Phase 2–7 Tech Stack headers still say "Python 3.14" without the floor qualification**
- **Location:** phase_02.md through phase_07.md Tech Stack lines; phase_08.md Tech Stack line.
- **Issue:** After the I3 fix, the authoritative framing is "dev on 3.14, wheel floor 3.12." Phases 2–7 Tech Stack lines were not updated and still read "Python 3.14" with no qualification. The Phase 1 decisions block carries the full explanation, so this does not mislead anyone who reads Phase 1 first. It would mislead an executor who jumps directly to a later phase without reading Phase 1's decisions — a plausible scenario for a phase-resumption after a break. The Phase 8 Tech Stack line has the same issue but is less risky because Phase 8 Task 1 Step 0 recites the floor check.
- **Fix:** Add a one-line qualifier to each phase's Tech Stack entry, e.g. "Python — dev on 3.14, package floor 3.12 (see Phase 1 decisions)." Alternatively, add a single boxed note at the top of the implementation plan index referencing the dual-version framing once. This is low-urgency: the load-bearing instructions are correct in every phase; it is a readability hazard, not a correctness hazard.

---

## Plan Alignment

All AC/DoD/DR coverage from the prior cycle is unchanged and verified. No new deviations introduced.

---

## Decision: APPROVED FOR MERGE (of the plan)

All Important and Critical findings from the prior cycle are resolved. The one remaining Minor finding (m5) is a readability hazard in the phase headers, not a correctness gap: every phase's executable instructions are correct, the CI matrix enforces the 3.12 floor, and Phase 8 explicitly gates the Pyodide version check. No issue blocks execution.
