# raven-builder Implementation Plan — Phase 3: Location transforms

**Goal:** Port the five geometric location transforms + the Logic special case, each exposing `base_locations()` / `next_location()` / `parent_location()`, anchored by the value-pinned `TopLeftCornerOut` coordinate sequences for all 8 matrix sizes from the JUnit spec.

**Architecture:** A `transforms/` package in the zero-dependency core. A `LocationTransform` ABC takes a `MatrixSize`, validates grid constraints and populates base locations at construction (faithful to the Java constructor), and declares `next_location`/`parent_location`. Five geometric transforms (Horizontal, Vertical, DiagonalBL→TR, DiagonalTL→BR, TopLeftCornerOut) implement the traversal; the Logic transform seeds the 2×2 top-left block and refuses `next`/`parent` (the upstream special case). A `make_location_transform(direction, size)` factory maps the Matzen direction digit (1,2,3,4,5) to the right class.

**Tech Stack:** Python (dev 3.14, package floor 3.12 — see Phase 1 decisions) stdlib only. Tests: pytest (value-pinned sequences) + hypothesis (traversal invariants).

**Scope:** Phase 3 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`.

**Codebase verified:** 2026-06-08 (codebase-investigator over the extracted upstream). Exact API, per-transform bodies, the odd-square diagonal constraint and the ≥3×3 Logic constraint, the direction-digit map (1=H, 2=V, 3=BL→TR, 4=TL→BR, 5=corner-out), and the literal 8-size `TopLeftCornerOut` sequences were all extracted. A genuine upstream bug was found in `Vertical.getParentLocationForStructureFeatureUse` (wraps to `numColumns-1` instead of `numRows-1`).

**Phase Type:** functionality

---

## Acceptance Criteria Coverage

### raven-builder.AC3: Location-transform spec
- **raven-builder.AC3.1 Success:** the ported TopLeftCornerOut transform produces the exact hardcoded coordinate sequences for all 8 matrix sizes from the JUnit test.
- **raven-builder.AC3.2 Success:** Horizontal, Vertical, and both diagonals produce their correct base/next/parent sequences.
- **raven-builder.AC3.3 Failure:** a diagonal/logic transform on a non-odd-square grid is rejected (matching the upstream constraint).

---

## Decisions carried into this phase (resolved during planning)

- **TopLeftCornerOut sequences are the TDD anchor** — ported as the first failing test (AC3.1).
- **Constraints raise at construction** (Python `ValueError`), matching the Java constructor `IllegalArgumentException`: diagonals require odd-AND-square (`rows % 2 == 0 or rows != cols` → reject); Logic requires `rows >= 3 and cols >= 3`.
- **`Vertical.parent_location` is fixed-to-paper** (per decision, Brian 2026-06-09, superseding the earlier "replicate verbatim" plan): the port wraps the row to `num_rows-1`, correcting the upstream `numColumns-1` bug (`VerticalSGMLocationTransform.java:108`; bug-catalog `loc-vertical-parent-wrap`: "fix-to-paper. Use `numRows`"). The bug is inert on the all-3×3 square oracle (`numColumns-1 == numRows-1`); the fix only differs on non-square grids. Record the divergence as a code comment + a non-square regression test (the Grey10/40 precedent — no separate ADR file; the bug-catalog entry is the decision record).
- Direction-digit → transform map: `1→Horizontal, 2→Vertical, 3→DiagonalBL→TR, 4→DiagonalTL→BR, 5→TopLeftCornerOut`.

---

## Source of truth for the pinned sequences

The literal sequences below were extracted from
`Test/gov/sandia/cognition/generator/matrix/locationtransform/TopLeftCornerOutSGMLocationTransformTest.java`.
The executor MUST cross-check them against that file (extract the source zip to a temp dir) before pinning — the JUnit file is canonical; the tables here are the convenience copy.

**Full traversal order** (base location first, then each `next_location` until it wraps back to `(0,0)`), per size, as `(row,col)`:

- **3×3:** (0,0)(1,0)(0,1)(2,0)(1,1)(0,2)(2,1)(1,2)(2,2)
- **1×1:** (0,0)
- **1×4:** (0,0)(0,1)(0,2)(0,3)
- **4×1:** (0,0)(1,0)(2,0)(3,0)
- **2×4:** (0,0)(1,0)(0,1)(1,1)(0,2)(1,2)(0,3)(1,3)
- **4×2:** (0,0)(1,0)(0,1)(2,0)(1,1)(3,0)(2,1)(3,1)
- **3×5:** (0,0)(1,0)(0,1)(2,0)(1,1)(0,2)(2,1)(1,2)(0,3)(2,2)(1,3)(0,4)(2,3)(1,4)(2,4)
- **10×3:** (0,0)(1,0)(0,1)(2,0)(1,1)(0,2)(3,0)(2,1)(1,2)(4,0)(3,1)(2,2)(5,0)(4,1)(3,2)(6,0)(5,1)(4,2)(7,0)(6,1)(5,2)(8,0)(7,1)(6,2)(9,0)(8,1)(7,2)(9,1)(8,2)(9,2)

**Parent-location sequence** (the `parent_location` of each non-base location, in traversal order), per size:

- **3×3:** (0,0)(0,0)(1,0)(0,1)(0,1)(1,1)(0,2)(1,2)
- **1×1:** (empty — single cell, no non-base locations)
- **1×4:** (0,0)(0,1)(0,2)
- **4×1:** (0,0)(1,0)(2,0)
- **2×4:** (0,0)(0,0)(0,1)(0,1)(0,2)(0,2)(0,3)
- **4×2:** (0,0)(0,0)(1,0)(0,1)(2,0)(1,1)(2,1)
- **3×5:** (0,0)(0,0)(1,0)(0,1)(0,1)(1,1)(0,2)(0,2)(1,2)(0,3)(0,3)(1,3)(0,4)(1,4)
- **10×3:** (0,0)(0,0)(1,0)(0,1)(0,1)(2,0)(1,1)(0,2)(3,0)(2,1)(1,2)(4,0)(3,1)(2,2)(5,0)(4,1)(3,2)(6,0)(5,1)(4,2)(7,0)(6,1)(5,2)(8,0)(7,1)(6,2)(8,1)(7,2)(8,2)

> Note: `parent_location((0,0))` for TopLeftCornerOut **raises** (no parent for the base) — the upstream throws `IllegalArgumentException`; the port raises `ValueError`.

---

<!-- START_SUBCOMPONENT_A (tasks 1-4): location transforms -->

<!-- START_TASK_1 -->
### Task 1: `LocationTransform` base + `TopLeftCornerOut` (value-pinned TDD anchor)

**Verifies:** raven-builder.AC3.1

**Files:**
- Create: `src/raven_matrix/transforms/__init__.py`
- Create: `src/raven_matrix/transforms/base.py`
- Create: `src/raven_matrix/transforms/geometric.py` (TopLeftCornerOut now; others in Tasks 2–3)
- Test: `tests/test_transforms_corner_out.py` (unit, value-pinned)

**Consumer:** Phase 4 `build()` walks each structure feature's locations via these methods; `make_location_transform` is its entry point.

**Step 1 (RED): write the pinned test**

`tests/test_transforms_corner_out.py` encodes the 8 sizes and their **full traversal order** + **parent sequence** from the tables above (cross-checked against the JUnit source). For each `MatrixSize(r, c)`:
- assert `base_locations() == [Location(0, 0)]`;
- starting from the base, repeatedly call `next_location` and assert the visited sequence equals the pinned traversal (and that it wraps back to `(0,0)` after the last cell);
- assert the `parent_location` of each non-base visited cell equals the pinned parent sequence;
- assert `parent_location(Location(0, 0))` raises `ValueError`.

Run it; it fails (no module yet).

**Step 2 (GREEN): implement `base.py` + `TopLeftCornerOut`**

`base.py` — the ABC (faithful to `AbstractSGMLocationTransform`):
```python
"""Location transforms: which cells share a feature, and in what order.

Faithful to gov.sandia.cognition.generator.matrix.locationtransform. The
constructor validates grid constraints and populates base locations, exactly
like the Java AbstractSGMLocationTransform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from raven_matrix.model import Location, MatrixSize


class LocationTransform(ABC):
    description: str

    def __init__(self, size: MatrixSize) -> None:
        self.size = size
        self._validate()           # subclass hook; default no-op
        self._base_locations = self._populate_base_locations()

    def _validate(self) -> None:   # overridden by constrained transforms
        return None

    def base_locations(self) -> list[Location]:
        return list(self._base_locations)

    @abstractmethod
    def _populate_base_locations(self) -> list[Location]: ...

    @abstractmethod
    def next_location(self, location: Location) -> Location: ...

    @abstractmethod
    def parent_location(self, location: Location) -> Location: ...
```

`geometric.py` — `TopLeftCornerOut`, a literal port of `createNextLocation` (the tall / wide-or-square branches) and `getParentLocationForStructureFeatureUse`. Keep the branch structure identical to the Java so the pinned sequences match; do not "simplify" the spiral.

**Step 3: run the test green; lint + type; commit**

```bash
uv run pytest tests/test_transforms_corner_out.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/transforms/ tests/test_transforms_corner_out.py
git commit -m "feat(transforms): LocationTransform base + value-pinned TopLeftCornerOut"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: Horizontal + Vertical (fix-to-paper Vertical parent-wrap)

**Verifies:** raven-builder.AC3.2

**Files:**
- Modify: `src/raven_matrix/transforms/geometric.py`
- Test: `tests/test_transforms_axis.py` (unit)

**Implementation (literal ports):**
- `Horizontal`: base = first column of every row (`Location(row, 0)` for each row); `next` = column+1 wrapping to 0; `parent` = column-1 wrapping to `cols-1`.
- `Vertical`: base = first row of every column (`Location(0, col)` for each col); `next` = row+1 wrapping to 0; `parent` = row-1 wrapping **to `num_rows-1`** — fixed-to-paper, correcting the upstream `numColumns-1` bug. Add a code comment:
  ```python
  # Fix-to-paper: upstream wraps to numColumns-1 here
  # (VerticalSGMLocationTransform.java:108), a bug masked on the all-3x3 square
  # oracle where numColumns == numRows. Per CLAUDE.md spec-precedence (the Matzen
  # paper is the spec) we wrap to num_rows-1. bug-catalog: loc-vertical-parent-wrap
  # (fix-to-paper). No compat flag.
  ```

**Testing (describe):**
- Horizontal/Vertical `base_locations`, full `next` traversal, and `parent` round-trips on a 3×3 (square — where the wrap value is unambiguous), pinned by hand from the upstream logic (with the Vertical parent corrected to `num_rows-1`).
- One explicit **fix-witness / regression** test: on a non-square grid (e.g. `MatrixSize(4, 2)`), `Vertical.parent_location(Location(0, c))` returns the correct row `num_rows-1 == 3` (NOT the buggy `num_columns-1 == 1`). This test fails against the upstream `numColumns-1` code, proving the fix.

**Verification + commit:**
```bash
uv run pytest tests/test_transforms_axis.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/transforms/geometric.py tests/test_transforms_axis.py
git commit -m "feat(transforms): Horizontal + Vertical (fix-to-paper parent-wrap)"
```
<!-- END_TASK_2 -->

<!-- START_TASK_3 -->
### Task 3: Diagonals + odd-square constraint

**Verifies:** raven-builder.AC3.2, raven-builder.AC3.3

**Files:**
- Modify: `src/raven_matrix/transforms/geometric.py`
- Test: `tests/test_transforms_diagonal.py` (unit)

**Implementation (literal ports):**
- `DiagonalBottomLeftTopRight`: `_validate` raises `ValueError` if `rows % 2 == 0 or rows != cols`; base = `Location(row, col)` with `row` incrementing from 0 across columns; `next` = (row-1 wrap to rows-1, col+1 wrap to 0); `parent` = (row+1 wrap to 0, col-1 wrap to cols-1).
- `DiagonalTopLeftBottomRight`: same `_validate`; base = `Location(rows-1-?, col)` with `row` decrementing from `rows-1` across columns; `next` = (row+1 wrap 0, col+1 wrap 0); `parent` = (row-1 wrap rows-1, col-1 wrap cols-1).
  > The two diagonal classes share the identical (copy-pasted) exception message upstream; reproduce the *behaviour* (rejection), but a clear Python message per class is fine — the message text is not part of any oracle.

**Testing (describe):**
- For a 3×3 (odd-square): base/next/parent pinned sequences for both diagonals.
- AC3.3: constructing either diagonal with an even or non-square size (`MatrixSize(2,2)`, `MatrixSize(3,5)`, `MatrixSize(4,4)`) raises `ValueError`; a valid odd-square (`3×3`, `5×5`) does not.

**Verification + commit:**
```bash
uv run pytest tests/test_transforms_diagonal.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/transforms/geometric.py tests/test_transforms_diagonal.py
git commit -m "feat(transforms): both diagonals + odd-square constraint (AC3.3)"
```
<!-- END_TASK_3 -->

<!-- START_TASK_4 -->
### Task 4: Logic transform + direction factory

**Verifies:** raven-builder.AC3.3 (Logic ≥3×3 constraint) + wires the public API

**Files:**
- Create: `src/raven_matrix/transforms/logic.py`
- Modify: `src/raven_matrix/transforms/__init__.py` (re-exports + `make_location_transform`)
- Test: `tests/test_transforms_logic.py`, `tests/test_transforms_factory.py` (unit)

**Implementation:**
- `LogicLocationTransform`: `_validate` raises `ValueError` if `rows < 3 or cols < 3`; base = the 2×2 top-left block `[(0,0),(0,1),(1,0),(1,1)]`; `next_location` and `parent_location` raise `NotImplementedError` (the upstream `UnsupportedOperationException` special case — Logic features don't traverse).
- `make_location_transform(direction: Direction, size: MatrixSize) -> LocationTransform` maps `1→Horizontal, 2→Vertical, 3→DiagonalBottomLeftTopRight, 4→DiagonalTopLeftBottomRight, 5→TopLeftCornerOut`. (Logic is selected by the structure layer, not this digit map; expose `LogicLocationTransform` directly.)
- `__init__.py` re-exports all six transform classes + the factory.

**Testing (describe):**
- `LogicLocationTransform(MatrixSize(3,3)).base_locations()` == the four 2×2 cells; `next_location`/`parent_location` raise `NotImplementedError`; `MatrixSize(2,3)` construction raises `ValueError`.
- `make_location_transform` returns the correct class for each of directions 1–5; an out-of-range digit raises `ValueError`.

**Verification + commit:**
```bash
uv run pytest tests/test_transforms_logic.py tests/test_transforms_factory.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/transforms/ tests/test_transforms_logic.py tests/test_transforms_factory.py
git commit -m "feat(transforms): Logic transform + direction factory"
```
<!-- END_TASK_4 -->
<!-- END_SUBCOMPONENT_A -->

---

## Phase 3 completion check

- [ ] TopLeftCornerOut reproduces the pinned base/traversal/parent sequences for all 8 sizes, cross-checked against the JUnit source (AC3.1).
- [ ] Horizontal, Vertical, both diagonals produce correct base/next/parent (AC3.2); Vertical's upstream parent-wrap bug fixed-to-paper (wraps to `num_rows-1`) with a non-square regression test and a divergence comment.
- [ ] Diagonals reject even/non-square; Logic rejects `<3×3` (AC3.3).
- [ ] `make_location_transform` maps directions 1–5 correctly.
- [ ] `uv run pytest`, `uv run ty check .`, `uv run ruff check .` all clean.
