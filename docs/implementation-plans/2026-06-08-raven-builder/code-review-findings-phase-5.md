# Code Review Findings — phase-5

Re-review cycle (BASE 3039247 → HEAD 77cd1b6). Prior findings: cycle 1 (BASE
8e8f330 → HEAD 3039247), same file.

---

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 0**

---

## Verification

```
Tests:  uv run pytest (full suite)  → 979 passed in 0.83s
        (phase-5 subset: 652 passed in 0.50s; up from 649 in cycle 1)

Lint:   uv run ruff check [changed files] → All checks passed!
Type:   uv run ty check .                 → All checks passed!
```

All 553 distinct codes pass (269 exact + 284 carrier-normalised); 840/840 row
coverage. No regressions.

---

## Prior Findings Verification

### Important #1 — B3/B4 missing from the hand-derived anchor table

**Status: Resolved.**

Two new `HandDerivedEntry` records added to `_SHADING_ENTRIES` in
`tests/data/hand_derived_labels.py`:

- `A1B3`: `FillRep + Direction.DIAGONAL_BL_TR`, `expected_code="A1B3"`,
  `externally_grounded=True`. Provenance comment cites PNG B3_1 (3-level palette,
  shading constant along the BL→TR diagonal) and CSV rows B3_1..B3_4 ("Shading").
- `A1B4`: `FillRep + Direction.DIAGONAL_TL_BR`, `expected_code="A1B4"`,
  `externally_grounded=True`. Provenance comment cites PNG B4_1 (3-level palette,
  constant along TL→BR) and CSV rows B4_1..B4_4.

**Provenance is sound and not circular.** FillRep is a repetition feature, so its
digit is the first element of each `_TRANSFORM_DIGITS` pair. The forward map gives
`DiagonalBLTR → ("3", "4")` → repetition digit `"3"`, and
`DiagonalTLBR → ("4", "3")` → repetition digit `"4"`. The new entries use
`DIAGONAL_BL_TR → "A1B3"` and `DIAGONAL_TL_BR → "A1B4"`, which match. The
derivation is grounded in the palette test (3-level = FillRep, confirmed against
the PNGs) and the constancy-axis reading, not read from `label()` output. Both
entries pass `test_hand_derived_label_matches_port`.

`test_table_has_expected_coverage` updated to assert
`{"A1B1", "A1B2", "A1B3", "A1B4", "A1B5"} <= expected_codes`. The table now has
16 entries (15 externally grounded).

### Minor #1 — `externally_grounded` flag never enforced

**Status: Resolved.**

New test `test_exactly_one_entry_is_not_externally_grounded` in
`tests/test_hand_derived_labels.py`:

```python
not_grounded = [e for e in HAND_DERIVED_LABELS if not e.externally_grounded]
assert [e.expected_code for e in not_grounded] == ["A6"]
```

List equality (not set or count) enforces both uniqueness and identity of the
single non-grounded entry. Correctly falsifiable: a second `False` entry fails the
test regardless of its position.

### Minor #2 — Normalisation sequence not stated in `round_trip` docstring

**Status: Resolved.**

Four-line block added to `round_trip`'s docstring in `src/raven_matrix/oracle.py`
(after the three-point outcome list):

> Normalisation sequence: the logic-7 strip is applied BEFORE storing `produced`
> (so `produced` shows the post-7 form for miss inspection); the carrier-A strip
> is applied ONLY during the comparison and is never stored, so a real miss still
> surfaces its full produced label.

This makes the two-step sequence explicit at the site where it is applied and
resolves the documentation gap. Accurate: matches the implementation.

### Important #2 — ADR-0002 status "Proposed" and untracked backfill obligation

**Status: Partially resolved — accepted as adequate for this phase.**

The fix rewrites the deferred-backfill note in ADR-0002 (`Consequences`, last
bullet) from:

> This divergence should be back-filled into the `docs/architecture/constraints.md`
> spec-precedence divergences table alongside Grey10/40, `loc-vertical-parent-wrap`,
> etc., once accepted (Status: Proposed).

to a named, reasoned obligation:

> **Deferred obligation (tracked):** this divergence must be back-filled into the
> `docs/architecture/constraints.md` spec-precedence divergences table alongside
> Grey10/40, `loc-vertical-parent-wrap`, etc. Per the plan-and-execute workflow,
> implementation-time ADRs stay **Proposed** until the post-acceptance stage (after
> final review + UAT), at which point this ADR flips to **Accepted** and the
> constraints.md backfill + citation pass happen together. The "Proposed" status is
> therefore correct in-phase, not an omission; the backfill is scheduled, not lost.

**Assessment of the workflow rationale.** The plan-and-execute model's
Proposed→Accepted gate at UAT/final-review is a coherent workflow position, not
an evasion. The original cycle-1 finding offered option (b): "change 'should be
back-filled' to 'will be back-filled in Phase N' and add a tracking note." The fix
delivers the tracking note and the workflow rationale. It does not name a specific
phase, which is the one gap relative to option (b) as stated. However: the
obligation is now explicit ("must be back-filled"), the workflow stage is named
("post-acceptance stage after final review + UAT"), and the ADR status is
explained rather than left as a silent misnomer. The constraints.md gap is a
documentation register concern, not a correctness gap in the implementation. Given
the workflow context, accepting the deferral without a hard phase number is
reasonable — the next ADR acceptance pass will surface it.

This finding is treated as resolved for merge purposes. The residual (no explicit
phase number) is recorded here for the post-acceptance documentation pass.

---

## New Issues

None. The two commits are narrow and well-scoped:

- `a1e535b` touches only `tests/data/hand_derived_labels.py` and
  `tests/test_hand_derived_labels.py`. No production code changed.
- `77cd1b6` touches only `src/raven_matrix/oracle.py` (docstring only, no logic)
  and `docs/architecture/decisions/0002-supplemental-led-constant-carrier.md`
  (prose only). No logic, no tests changed.

No new accretion, no new type-safety concerns, no new error-handling surface.

---

## Decision: APPROVED FOR MERGE

All four prior findings are resolved (three fully, one partially with an accepted
rationale). The hand-derived anchor table now covers all five FillRep directions
(B1–B4) and the one ChangeFill direction (B5), all externally grounded in
published PNGs and CSV rows. The DR6 grounding contract is a hard assertion.
The normalisation sequence is documented at the point of use. The ADR-0002
backfill obligation is tracked with workflow rationale.

Phase 5 is complete and the branch is ready to proceed to Phase 6.
