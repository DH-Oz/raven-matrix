# Code Review Findings — phase-1

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 0**

## Verification

```
ruff check .              → All checks passed (PASS)
ruff format --check .     → 5 files already formatted (PASS)
ty check .                → All checks passed (PASS)
pytest -v                 → 6 passed in 0.06s (PASS)
```

## Prior Findings Verification

### Important 1 — SgmtDump.generate() cold-start seeding undocumented

**Status: Resolved.**

`docs/spikes/golden-fixtures.md` now contains a "Seeding note" paragraph
(diff hunk `+156`–`+165`) that explicitly states:

- Each config entry is an independent cold-start from seed 42.
- `generate()` calls `new Random(SEED)` per invocation, so the five matrices
  are five independent draws, not five consecutive draws from one stream.
- Upstream `SGMMatrixSetGenerator.generateMatrices` uses one `Random` across
  the whole run.
- The cold-start fixture is the correct oracle for Phase 4's `build(config,
  seed, flags)` API, which seeds its own `JavaRandom` per call.
- Single-stream / accept-reject behaviour is out of scope for these fixtures.

The note directly addresses the impact concern raised in the prior review
(Phase 4 misinterpreting fixtures as consecutive stream draws) and correctly
characterises the relationship between fixture design and the intended Phase 4
API. No further action needed.

### Important 2 — regenerate.sh double-trap fragility

**Status: Resolved.**

`tools/golden/regenerate.sh` now uses a single `cleanup()` function registered
once via `trap cleanup EXIT` (diff hunk `+53`–`+62`). Both `RNG_BUILD` and
`SGMT_BUILD` are pre-initialised to empty strings at the top, and the function
guards each `rm -rf` with `[ -n "$VAR" ]`. The two inline `trap` calls at lines
56 and 71 (prior) are removed. The fragility pattern (second trap silently
replacing first) is eliminated. The guard-on-non-empty pattern is the correct
approach for this structure.

### Minor 3 — CI uv sync missing --group dev

**Status: Resolved.**

`.github/workflows/ci.yml` sync step is now
`uv sync --locked --all-extras --group dev` (diff hunk `+26`). Intent is now
explicit in the YAML.

## Plan Alignment

No plan-alignment change from the prior review. All Phase 1 tasks remain
implemented as assessed previously.

## Issues

None.

## Decision: APPROVED FOR MERGE
