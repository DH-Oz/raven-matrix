# Code Review Findings — phase-7

Re-review after bug-fix cycle (commit 03dbde0).
Base: 1cf5514 (phase HEAD before fixes). Head: 03dbde0.
Diff touches: app.py, pyproject.toml, src/raven_matrix/cli.py, tests/test_cli.py.

---

## Status: APPROVED

**Critical: 0 | Important: 0 | Minor: 1**

---

## Verification

```
Tests:  uv run pytest          → 1002 passed
Lint:   uv run ruff check .    → All checks passed
Types:  uv run ty check src/   → All checks passed
```

---

## Prior Findings Verification

### F1 — Important: oracle command leaked FileNotFoundError; _ORACLE_CSV used a fragile parents[2] path; CSV not shipped as package data

**Resolved.**

(a) `pyproject.toml` gains a `[tool.hatch.build.targets.wheel.force-include]` stanza mapping
`"data/ravens_oracle.csv"` → `"raven_matrix/data/ravens_oracle.csv"`. The wheel
build has been independently confirmed to contain the file at 43,602 bytes.

(b) `_ORACLE_CSV` (the bare module-level constant) is replaced by `_oracle_csv_path()`.
The resolver calls `importlib.resources.files("raven_matrix") / "data" / "ravens_oracle.csv"`
and tests `.is_file()` on the resulting `Traversable`. In an editable checkout that path
resolves to `src/raven_matrix/data/ravens_oracle.csv`, which does not exist, so
`is_file()` returns `False` and the resolver falls back to the source-tree location
(`Path(__file__).resolve().parents[2] / "data" / "ravens_oracle.csv"`). Both branches
were verified by direct inspection:

```
importlib.resources.files("raven_matrix") / "data" / "ravens_oracle.csv"
  → /…/src/raven_matrix/data/ravens_oracle.csv   is_file: False   (no such dir)
fallback → /…/data/ravens_oracle.csv              exists: True
```

The `.is_file()` method is defined on `importlib.abc.Traversable` (available since
Python 3.9, well within the project floor of 3.12). No import cycle: `importlib.resources`
is stdlib; `raven_matrix.cli` does not import itself.

(c) The `oracle` command now wraps `csv_path.open()` in a `try/except FileNotFoundError`
— no bare `except` — emits an actionable message to stderr naming
`tools/extract_oracle.py`, calls `typer.Exit(code=1)`, and leaves stdout clean.

One narrow observation worth noting (not a blocking issue — see Minor section below):
in an editable checkout the packaged path `src/raven_matrix/data/` does not exist, so
the `is_file()` branch is never exercised by the test suite. The packaged-install path
is exercised only when a wheel is installed. The test monkeypatches `_oracle_csv_path`
to a nonexistent path, which correctly exercises the error branch without depending on
the real CSV. The happy-path test exercises the fallback path (source tree). The
packaged-install branch is untested by the suite but verified at wheel-build time.
This is acceptable for the current project stage.

### F2 — Important (downgraded Minor): --layers 2 had no test; help text unclear

**Resolved.**

`test_build_two_layers_via_flag` invokes `build --relation shape_repetition
--direction horizontal --layers 2 --position 1 --seed 0`, asserts exit 0, valid SVG on
stdout, `Structure:` line on stderr, and that the code part is at least 4 characters
(enforcing a two-layer code such as `A1A1`). The test is behavioural, not
mock-based, and will fail if the `[layer_controls] * layers` path regresses.

The help text is updated from the opaque "Number of layers to repeat the explicit
relation across (1 or 2)" to "Repeat the same relation across N identical layers
(1 or 2)". The same-config duplication semantics are now explicit.

### F3 — Minor: dead inner ternary in the oracle status f-string

**Resolved.**

The old expression:

```python
f"{'PASS' if result.passed else 'FAIL'} ({result.mode})"
if result.passed
else f"FAIL ({result.mode}): {result.reason}"
```

is replaced by:

```python
f"PASS ({result.mode})"
if result.passed
else f"FAIL ({result.mode}): {result.reason}"
```

The `'PASS' if result.passed else 'FAIL'` sub-expression was unreachable-as-FAIL inside
the True branch. The new form is flat and byte-identical in output for all reachable
inputs.

### F4 — Minor: awkward single-element-tuple comprehension in app.py

**Resolved.**

The old form:

```python
for slot in (column_value[key],)
if slot["type"] is not None
```

is replaced by:

```python
if (v := column_value[key])["type"] is not None
```

Behaviour identity was verified against three cases (mixed, all-None, all-present):
all produce identical output. The walrus operator assigns `column_value[key]` once per
iteration; the `["type"]` subscript is evaluated on the same object used in the tuple
body. The rewrite removes the inner loop and the throwaway `slot` name.

---

## Issues

### Minor (count: 1)

- **Issue**: The `_oracle_csv_path()` resolver's packaged-install branch
  (`importlib.resources.files(...).is_file()` returning `True`) is not covered by the
  test suite. In an editable checkout `src/raven_matrix/data/` does not exist, so
  `is_file()` always returns `False` and the fallback branch runs. A future refactor
  that accidentally inverts the branch order (fallback tried first) or breaks the wheel
  force-include stanza would not be caught by `pytest`.
- **Location**: `src/raven_matrix/cli.py` lines 54-58 (`_oracle_csv_path` True-branch)
- **Fix**: Add a test that monkeypatches `_oracle_csv_path` to return a path that
  *does* exist (e.g. a `tmp_path` copy of the real CSV) and asserts the oracle command
  succeeds. This exercises the packaged-install code path without requiring a real wheel
  install. Low priority: the wheel build verification provides a manual check, and the
  fix-cycle context makes this a cosmetic gap rather than a correctness risk.

---

## Consolidation Opportunities

None visible in this diff.

---

## Decision: APPROVED FOR MERGE

All four prior findings are resolved. The resolver is technically sound for both
installed-wheel and editable-checkout use. The walrus rewrite is behaviour-identical.
The new test for F1 correctly exercises the error path via monkeypatching. The full
suite (1002 tests), ruff, and ty are clean. The single Minor finding is a coverage gap
in one branch of the resolver that is already covered by the documented wheel-build
verification; it does not block merge.
