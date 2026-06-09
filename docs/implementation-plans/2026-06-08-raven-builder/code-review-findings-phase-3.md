# Code Review Findings — phase-3

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 0**

## Verification

```
Tests:  uv run pytest --tb=short -q  →  153 passed in 0.11s  (was 151; +2 new)
Lint:   uv run ruff check .          →  All checks passed!
Type:   uv run ty check .            →  All checks passed!
```

## Prior Findings Verification

### Important — factory `Direction | int` union

**Status: Resolved (per Brian's decision — union KEPT, note added)**

Evidence: `src/raven_matrix/transforms/__init__.py` diff, lines 53–57. A five-line
block was added to the existing docstring:

> The `Direction | int` union is intentional: oracle `Structure`-code direction
> digits arrive as raw `int`s, so this factory owns the int→`Direction`
> conversion and the out-of-range error. The contract will be revisited at the
> Phase 4 interface once the actual consumer exists.

The signature (`direction: Direction | int`) is unchanged — the union was
deliberately kept. The out-of-range test in `test_transforms_factory.py` is
present and still passes (confirmed by the 153-pass run). This matches the
documented decision: note added, union retained, revisit deferred to Phase 4.

### Minor — `_require_odd_square` missing type annotation

**Status: Resolved**

Evidence: `src/raven_matrix/transforms/geometric.py` diff, line 75. The
function signature changed from `def _require_odd_square(size, description: str)`
to `def _require_odd_square(size: MatrixSize, description: str) -> None:`.
`MatrixSize` was added to the import on line 12. `ty check` passes clean.

### Minor — diagonal tests missing full next-cycle coverage

**Status: Resolved**

Evidence: `tests/test_transforms_diagonal.py` diff, lines 106–131. A new
parametrised test `test_diagonal_full_next_cycle_from_every_base_on_3x3` was
added. It iterates over both diagonal classes, constructs a 3×3, calls
`_full_next_cycle` from every base location, asserts the cycle length equals
`num_rows`, and asserts `next_location(cycle[-1]) == base`. Test count went from
151 to 153, confirming both parametrised cases run. Matches the fix the prior
review requested.

---

## Plan Alignment

- AC3.1 TopLeftCornerOut value-pinned sequences for all 8 matrix sizes: present and passing (unchanged from prior cycle).
- AC3.2 Horizontal, Vertical, both diagonals — base/next/parent sequences: present and passing (unchanged from prior cycle).
- AC3.3 Diagonal odd-square rejection + Logic ≥3×3 rejection: present and passing (unchanged from prior cycle).
- `make_location_transform` factory: present and passing (unchanged from prior cycle).
- LogicLocationTransform: present and passing (unchanged from prior cycle).
- All six transforms + factory re-exported from `__init__.py`: present (unchanged from prior cycle).

## Issues

None.

## Decision: APPROVED FOR MERGE
