# Code Review Findings — phase-6

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 0**

## Verification

```
Tests:  uv run pytest -q  → 117 passed in 0.14s
Lint:   uv run ruff check . → All checks passed!
Types:  uv run ty check .   → All checks passed!
```

## Prior Findings Verification

All three findings from the prior cycle (cycle at 9e79c3d) were resolved and
remain resolved in this cycle. No regression from the rotation fix.

**Minor 1 — LINE element emits semantically redundant `fill`/`fill-opacity` attributes**
Status: **Resolved** (unchanged from prior cycle)

**Minor 2 — `_fmt` docstring inaccurate**
Status: **Resolved** (unchanged from prior cycle)

**Minor 3 — Test mutates `Matrix.answer_choices` directly**
Status: **Resolved** (unchanged from prior cycle)

---

## Rotation Fix (55e8ea0) — Targeted Checks

### Check 1: Rotation emitted directly; tripwire test asserts exact value

`_feature_transform` now contains `f"rotate({_fmt(feature.rotation)})"` with no
intermediate variable and no `degrees()` call. The old code assigned
`deg = degrees(feature.rotation)` and emitted `rotate({_fmt(deg)})`.

The replacement test `test_rotation_degrees_emitted_directly_as_svg_rotate` passes
`rotation=90.0` (a degree value) and asserts `"rotate(90.0)" in t` with a
descriptive failure message. Against the old code, `degrees(90.0)` would have
yielded `≈5156.6`, so `rotate(90.0)` would not appear and the test would fail.
The tripwire fires correctly.

The secondary test `test_rotation_45_degrees_emitted_directly` passes `rotation=45.0`
and asserts `"rotate(45.0)" in t`. Same analysis: the old code would produce
`degrees(45.0) ≈ 2578.3`, which would not match, so the tripwire also fires.

Both tests verify behaviour (the emitted SVG string) rather than mocks. Pass.

### Check 2: `degrees` import removed and not referenced

`grep -n "degrees" src/raven_matrix/render/svg.py` returns only docstring prose,
no import statement and no function call. `ruff check` passes (no unused-import
warning). Clean.

### Check 3: Transform order, scale, geometry, paint order unchanged

The diff to `_feature_transform` is strictly:
- Remove `deg = degrees(feature.rotation)`
- Replace `_fmt(deg)` with `_fmt(feature.rotation)`

The four-clause transform string (`translate → rotate → scale → translate`) is
structurally identical. No geometry, fill, stroke, or paint-order code was
touched. The existing `test_zero_rotation_unit_scale_transform_is_identity_form`
continues to pass, confirming the identity-rotation case is undisturbed.

### Check 4: Import hygiene unchanged

`render/__init__.py` contains only docstring references to `raster`/`rasterise`/
`resvg_py` — no import statements. The module-level import guard is intact and
the subprocess isolation test (`test_importing_core_svg_does_not_load_resvg_py`)
still passes (confirmed by the 117-test green run).

### Check 5: No new issues in the test replacement

`test_rotation_radians_become_svg_degrees` is removed entirely; its replacement
is `test_rotation_degrees_emitted_directly_as_svg_rotate` plus
`test_rotation_45_degrees_emitted_directly`. The old test encoded the bug (it
relied on `degrees(pi/2) == 90` to produce the expected 90.0, meaning it could
not distinguish a correct direct-emit from a double-conversion). The new tests
pass a plain degree value and assert the same value appears, which is the correct
invariant. No mock complexity. No mutation. No import of `pi` or `math`. Net
test count: 117 (was 116 before this fix — one test became two, replacing the
removed one).

---

## Plan Alignment

All Phase 6 acceptance criteria satisfied (unchanged):

- AC5.1 (SVG well-formedness, every shape + fill, correct alpha) ✓
- AC5.1 rotation fitness: a feature's rotation in degrees is emitted directly ✓ (new)
- AC5.2 (rasterise → PNG) ✓
- AC5.3 (blank/empty cell renders without error) ✓
- `render/__init__.py` free of raster imports ✓
- `resvg_py` import inside function only ✓
- `RasterSettings` frozen dataclass + `DEFAULT_RASTER` ✓
- Transform order matches `SGMCellImage.setSGMCell` ✓
- Fill RGBA values verified against Java source ✓
- Paint order (fill then stroke) matches Java ✓
- Blank-white bottom-right in problem mode ✓
- Diamond / Tee / Trapezoid / Triangle geometry ✓

## Issues

None.

## Decision: APPROVED FOR MERGE
