# Code Review Findings — phase-4

## Status: APPROVED

**Critical: 0 | Important: 2 | Minor: 2**

## Verification

```
Tests:  uv run pytest --tb=short -q  →  282 passed in 0.32s
Lint:   uv run ruff check .          →  All checks passed!
Types:  uv run ty check .            →  All checks passed!
```

## Plan Alignment

- AC1.1 (1-layer build → 3×3 + 8 choices): ✓ `test_build_returns_three_by_three_with_eight_choices`
- AC1.2 (2-layer composition): ✓ `test_build_two_layer_config_composes_both_layers`
- AC1.3 (every base relation / supplemental / direction settable): ✓ parametrised tests in `test_builder_build.py`
- AC1.4 (invalid configs raise `ValueError`): ✓ `test_validate_rejects_*` + `test_build_rejects_invalid_config`
- AC4.1 (same config+seed → identical matrix): ✓ `test_build_is_deterministic_for_a_seed`
- AC4.3 (different seeds → same structure, pinned surface differs): ✓ `test_build_different_seeds_same_structure_differ_in_pinned_feature`
- AC6.1 (`line_shape_enabled` toggle): ✓ `test_build_default_flags_never_draw_line` + `test_build_line_enabled_changes_output_for_same_seed`
- AC6.2 (registry completeness — self-enforcing): ✓ `tests/test_compat_registry.py`
- DR7 (identity in logic, value in distractor dedup): ✓ identity witnesses in `test_value_equal_but_distinct_instance_is_absent_and/xor`; cell-value dedup in `test_no_duplicate_answer_choices_by_cell_value`
- Logic-does-not-call-next/parent contract (Phase-3 interface lock): ✓ `test_build_layer_logic_never_calls_next_or_parent_on_logic_transform`
- `make_location_transform` contract (Direction enums, not raw ints, at config boundary): ✓ documented in module docstring and `test_layer_config_carries_parsed_enums`
- Hang-prevention bound (bug-catalog `gen-unbounded-generation-loop`): ✓ `test_fully_empty_matrix_blank_pads_without_hanging`
- Logic pool value-distinct precondition (termination fix): ✓ `test_logic_pool_must_be_value_distinct_or_raises`

## Issues

### Important (count: 2)

**I1 — Strategy-3 single-layer RNG draw is spurious but present**

- **Location:** `src/raven_matrix/builder.py` lines 653–656
- **Detail:** When `matrix_num_layers == 1`, the condition `if matrix_num_layers > num_layers` is false (both are 1), so the `next_int` draw at line 656 is skipped. This is correct. However when `matrix_num_layers > 1` (the 2-layer case), the code draws `next_int(matrix_num_layers) + 1` which can return `matrix_num_layers` itself, meaning every layer gets selected. The Java source (SGMMatrix.java:429) is identical: `random.nextInt(matrixNumLayers) + 1`. This is faithful. There is no bug here — but the consequence is that strategy 3 with 2 layers can produce a "combination of all layers", which is indistinguishable from a subset-of-all-layers (strategy 0 with all layers chosen). The plan notes strategy 0 is "only meaningful with ≥2 layers" but strategy 3's overlap with strategy 0 at the all-layers extreme is not called out. This is a faithful port of a Java quirk; it should be recorded in the bug catalog if not already present, so Phase 5's oracle work does not mistake it for a port error.
- **Fix:** Verify `docs/upstream-analysis/bug-catalog.md` already captures this overlap, or add a one-line entry `gen-strategy3-subsumes-strategy0-at-maxlayers`. No code change needed in Phase 4.

**I2 — `_distractor_modify_parameter` early-return drops RNG draws on empty cell**

- **Location:** `src/raven_matrix/builder.py` lines 613–614
- **Detail:** When the chosen cell has no features, the function returns `[]` immediately after the `row`/`column` draws but before the `parameter_to_change = rng.next_int(2)` draw (line 617) and (for the non-numerosity path) the `feature_index = rng.next_int(len(features))` draw. This matches the Java source (SGMMatrix.java: the `source.size() == 0` guard at approximately l.335 exits before the parameter draw). This is therefore a faithful port. However, the early return means that an empty cell silently skips draws that the Java skips too — the RNG stream stays identical — but the comment at line 614 says "Returns `[]` if the chosen cell has no features (an empty candidate the caller skips)" without noting that this is also correct for stream fidelity. The comment should say explicitly that the early return is faithful to the Java early exit and preserves the RNG stream, so a future reader does not "fix" it by moving draws before the guard.
- **Fix:** Add a one-line comment at the early return: `# faithful to Java: parameter draw not reached when cell is empty (SGMMatrix.java ~l.335).`

### Minor (count: 2)

**m1 — Blank-pad skip of `correct_position_0` undocumented against the Java line**

- **Location:** `src/raven_matrix/builder.py` lines 776–779
- **Detail:** The blank-pad loop skips `correct_position_0` when encountered. The Java loop (SGMMatrix.java:562-572) does not skip — it is safe there because the relocation block has already pushed `correct_position_0 <= position`. The Python port's skip is the correct adaptation for the honor-config path, and the comment explains the reasoning. But the comment does not cite the Java line numbers for the upstream loop, making it harder to verify during Phase 5 oracle work. The logic is sound; this is a documentation gap only.
- **Fix:** Add `# Java l.562-572 does not skip; safe there because relocation ensures correct_position_0 <= position.` to the comment block.

**m2 — `_contains_cell` type signature accepts `list[Cell | None]` but callers always pass `list[Cell | None]`; public tests import it as a private name**

- **Location:** `tests/test_builder_answers.py` line 34 (imports `_cell_value_equals`, `_contains_cell` with leading underscores)
- **Detail:** Both helpers are private (`_` prefix) but are imported directly in tests. This is the established pattern from Phase 3 (`contains_check` was similarly tested directly). It is not a problem in itself, but the plan (Task 6) explicitly says "Add a direct unit test of `_cell_value_equals`/`_contains_cell`… so the cell-list helper is covered independently of `build()`" — so the direct import is intentional. The minor concern is that if either helper is later inlined or renamed, the test breaks with an `ImportError` rather than a test failure. No action required before Phase 5, but worth noting for Phase 6 refactoring.
- **Fix:** No code change. Note for Phase 6: if either helper moves, update the import.

## Termination Fixes — Soundness Assessment

Two termination fixes are required by the plan. Both are sound.

**Logic base-pool value-distinct precondition** (`structure/base.py:157–172`):
The assertion scans the incoming pool with `_contains_by_value` and raises `ValueError` on any duplicate before the assignment loop starts. The note in the docstring is correct: the upstream `BaseSGMStructureFeatureGenerator` already guarantees a value-distinct pool via its own `containsCheck` loop, so in normal operation the `ValueError` is unreachable. The guard fires only if a caller bypasses the pool-generation path (a test-harness mistake or a future coding error). It adds no draw and does not alter the RNG stream. The termination argument is sound: with a value-distinct pool of N features and L locations, each pass assigns at least one new feature-id (because the value guard prevents duplicates and the draw is unbounded within the pass), so `assigned_feature_ids` grows toward N and `populated_locations` toward L monotonically. The loop terminates in at most N passes.

**Hang-prevention bound for empty candidates** (`builder.py:729–738`):
The upstream Java skips empty candidates without incrementing `numDuplicatesInARow` (SGMMatrix.java:483–487: bare `continue`). The port counts them. The docstring explains the reasoning correctly: in a matrix with any content, the first non-empty success resets the counter, so normal generation is unaffected. A fully-impoverished matrix (all cells empty) would otherwise spin forever; counting empty candidates toward the cap allows it to blank-pad instead of hanging. This is a documented FIX-TO-PAPER (bug-catalog `gen-unbounded-generation-loop`). The fix is sound and does not alter the stream for normal inputs.

## DR7 Identity/Value Correctness Assessment

The two helpers are kept rigorously separate throughout the diff:

- `_contains_by_identity` (base.py:242–249): used exclusively inside `LogicalAND.combine_surface_features`, `LogicalOR.combine_surface_features`, and `LogicalXOR.combine_surface_features`. Never used outside the logic-combine path.
- `_contains_by_value` (base.py:230–239): used only for pool dedup inside `_assign_base_locations`. Never used in combine.
- `contains_check` (model.py, Phase 2): used inside `_cell_value_equals` for distractor dedup. Never used for logic-combine.
- `_cell_value_equals` / `_contains_cell` (builder.py:519–544): used only for answer-choice dedup. Never used for logic-combine.

The DR7 witness tests (`test_value_equal_but_distinct_instance_is_absent_and`, `test_value_equal_but_distinct_instance_is_absent_xor`) confirm that a value-equal-but-distinct instance is correctly treated as absent by the identity-combine path. The separation is clean and each helper is tested at its own level.

## RNG Draw Order Assessment (Surface Generator)

The surface generator (`surface.py:95–143`) faithfully ports the variable pre-fill draw count. Two seeds are pinned in `tests/test_surface.py` (`test_three_prefill_draws_branch_seed0`, `test_two_prefill_draws_branch_seed2`) covering both branches (width==quarter forcing the height draw, and width!=quarter skipping it). The shape-index mapping is read from the live switch (cases 0–5 = Ellipse/Rectangle/Triangle/Tee/Diamond/Trapezoid) with the stale commented-out `case 4` for Line correctly excluded from the live order and Line placed at index 6 under the `line_shape_enabled` path.

## Consolidation Opportunities

None visible in the diff. The two `_clone` functions (`supplemental.py:_clone` and `builder.py:_clone_feature`) serve different modules and are not visible to each other within the diff context. No consolidation is warranted at this boundary without reading beyond the diff.

## Decision: APPROVED FOR MERGE
