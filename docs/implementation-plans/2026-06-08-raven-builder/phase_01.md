# raven-builder Implementation Plan — Phase 1: Scaffolding, CI, oracle data, Java spike

**Goal:** Stand up a working uv project skeleton (src-layout package, lint/type/test tooling, CI), produce the committed 840-row oracle CSV from the Matzen norming spreadsheet, and run a timeboxed spike that records whether the upstream Java builds (for later golden fixtures).

**Architecture:** Functional-core / imperative-shell from the start. The core package `src/raven_matrix/` carries zero runtime dependencies (`dependencies = []`). Optional, user-facing features live in `[project.optional-dependencies]` extras (`raster`, `ui`, `cli`, reserved `difficulty`); developer tooling lives in a PEP 735 `[dependency-groups] dev`. The oracle CSV is generated once by a dev-only tool (`tools/extract_oracle.py`, xlrd) reading the spreadsheet straight from the read-only `upstream/` submodule, then committed so the runtime/test path never needs xlrd or the `.xls`.

**Tech Stack:** Python — dev on 3.14 (`.python-version`), wheel floor `>=3.12` for Pyodide; uv, hatchling (build backend), ruff (lint/format, `py312` target), ty (type check against the 3.12 floor, exact-pinned because it is pre-1.0), pytest + hypothesis (tests), xlrd 2.x (dev-only `.xls` reader), GitHub Actions CI (`[3.12, 3.14]` matrix). Spike toolchain: Temurin JDK 8 + Apache Ant (selected by repo-root `.envrc`).

**Scope:** Phase 1 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`.

**Codebase verified:** 2026-06-08 (two codebase-investigator passes + one internet-researcher pass). Greenfield confirmed: no `src/`, `tools/`, `data/`, `.github/`, no ruff/ty config, no `[dependency-groups]`/extras; `pyproject.toml` has `dependencies = []`, `.python-version` = `3.14`, `uv.lock` minimal; `upstream/` submodule present with the source zip (`javac.source/target = 1.6`, 10 vendored jars) and the norming zip containing `Matzen_et_al_2010_norming_stimuli.xls`.

**Phase Type:** infrastructure

---

## Acceptance Criteria Coverage

This is an infrastructure phase. It builds the scaffold that later phases test against; it does not itself implement a design Acceptance Criterion.

**Verifies: None** — success is operational, per the design's Phase 1 "Done when":

1. `uv sync` succeeds.
2. `uv run ruff check .` and `uv run ty check .` are clean.
3. CI is green on a no-op (smoke test).
4. `data/ravens_oracle.csv` has 840 data rows.
5. The Java-spike outcome (builds: yes/no, and how) is recorded in `docs/spikes/`.

These operational checks are pinned as test-requirements where automatable (the oracle CSV contract in Task 4 is an executable test that becomes Phase 5's input contract).

---

## Decisions carried into this phase (resolved during planning)

- **Packaging = hybrid** (extras for `raster`/`ui`/`cli`/`difficulty`; `dev` group for tooling). Core stays `dependencies = []`. Consumers and Phase 8 micropip can install `raven-matrix[ui]`.
- **Pyodide-compatible package, 3.14 dev** (resolves review finding I3): `requires-python = ">=3.12"` and `ruff target-version = "py312"` so the wheel installs under the (CPython-lagging) Pyodide runtime in Phase 8 — micropip honours `requires-python`, and a `>=3.14` wheel would refuse to load in-browser, breaking AC7.1/AC7.2. `.python-version` stays `3.14` for dev; the whole package (core + app) is kept 3.12-compatible (cli/raster/tools *may* use newer idioms but aren't required to — kept uniform for wheel robustness). The `[3.12, 3.14]` CI matrix is the leakage guard. Phase 8 confirms/raises the floor against the live Pyodide version.
- **`ty` exact-pinned** (`ty==<resolved>`) and gated in CI; other dev tools use `>=` floors.
- **Oracle CSV is faithful**: 840 rows including the duplicate `Stimulus Name` `A4_1`; all six columns verbatim; legend/data boundary found by detecting the header row, not a fixed offset. Contract numbers (840 rows, 553 distinct `Structure`, 839 distinct `Stimulus Name`) are asserted by a test.
- **Spike completes on a recorded outcome, not a successful build.** Outcome lives in `docs/spikes/` (not `.notes/`).

---

<!-- START_TASK_1 -->
### Task 1: Project metadata, build backend, dependency model, tool config, package skeleton

**Files:**
- Modify: `pyproject.toml` (currently 7 lines: `[project]` only)
- Create: `src/raven_matrix/__init__.py`
- Create: `src/raven_matrix/py.typed`

**Step 1: Rewrite `pyproject.toml`**

Replace the file with the following. Leave version pins as `>=` floors except `ty` (pinned in Step 3). `uv` will resolve and lock exact versions.

```toml
[project]
name = "raven-matrix"
version = "0.1.0"
description = "Python 3.14 port of the Sandia Generated Matrix Tool — generates Raven-style progressive-matrix puzzles with normed difficulty"
readme = "README.md"
# Floor is the Pyodide-installable version (NOT 3.14): the WASM runtime (Phase 8)
# lags CPython, and micropip honours requires-python — a >=3.14 wheel would refuse
# to install in-browser. Dev runs 3.14 (.python-version); the package stays
# 3.12-compatible so the wheel loads under Pyodide. Confirm/raise the floor against
# the actual Pyodide version in Phase 8.
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
raster = []            # SVG→PNG backend chosen in Phase 6
ui = ["marimo"]        # Phase 7 reactive app
cli = ["typer"]        # Phase 7 CLI
difficulty = []        # reserved — Phase-later difficulty classifier

[project.scripts]
# raven-matrix CLI entry point is wired in Phase 7 (cli extra)

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/raven_matrix"]

[dependency-groups]
dev = [
    "pytest>=8",
    "ruff>=0.6",
    "hypothesis>=6",
    "xlrd>=2.0",        # dev-only: reads the .xls oracle source (Task 4)
    # "ty==X.Y.Z" is appended in Step 3 once uv resolves it
]

[tool.ruff]
line-length = 88
target-version = "py312"   # keep the whole package Pyodide-compatible (see requires-python)
src = ["src", "tests", "tools"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", "SIM"]

[tool.ty.environment]
python-version = "3.12"   # type-check against the supported floor, not the dev version

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

> Note: `raster`/`difficulty` are intentionally empty extras now — declaring the key reserves the install surface (`raven-matrix[raster]`) so later phases add members without changing the public shape. An empty extra is valid.

**Step 2: Create the package skeleton**

`src/raven_matrix/__init__.py`:
```python
"""raven-matrix: a faithful Python port of the SGMT explicit matrix builder."""

__version__ = "0.1.0"
```

`src/raven_matrix/py.typed` — empty file (PEP 561 marker so `ty`/downstream see the package as typed).

**Step 3: Install tooling and pin `ty` exactly**

```bash
uv add --group dev "pytest>=8" "ruff>=0.6" "hypothesis>=6" "xlrd>=2.0"
uv add --group dev ty
```
Then read the resolved `ty` version from `uv.lock` and rewrite its `dev` entry as an exact pin:
```bash
uv run python -c "import tomllib,pathlib; d=tomllib.loads(pathlib.Path('uv.lock').read_text()); print(next(p['version'] for p in d['package'] if p['name']=='ty'))"
```
Edit `pyproject.toml` so the `dev` group lists `"ty==<that version>"` (replace the floor `uv add` left). Re-run `uv sync` to confirm the lock is consistent.

**Step 4: Verify operationally**

```bash
uv sync
uv run python -c "import raven_matrix; print(raven_matrix.__version__)"   # -> 0.1.0
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```
Expected: `uv sync` resolves; import prints `0.1.0`; ruff and ty report no errors. If `ruff format --check` complains, run `uv run ruff format .` and re-check.

**Step 5: Commit**

```bash
git add pyproject.toml uv.lock src/raven_matrix/__init__.py src/raven_matrix/py.typed
git commit -m "chore: scaffold uv project — src package, hatchling, ruff/ty, dev group + extras"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: Smoke test (gives pytest + CI something green to run)

**Files:**
- Create: `tests/__init__.py` (empty)
- Create: `tests/test_smoke.py`

**Step 1: Create the smoke test**

`tests/test_smoke.py`:
```python
"""Greenfield smoke test: the package imports and exposes its version.

This exists so pytest (and CI) have a real green check before any feature
code lands. It is replaced in spirit by Phase 2's first real tests.
"""

import raven_matrix


def test_package_imports_with_version() -> None:
    assert raven_matrix.__version__ == "0.1.0"
```

**Step 2: Verify**

```bash
uv run pytest
```
Expected: 1 passed.

**Step 3: Commit**

```bash
git add tests/__init__.py tests/test_smoke.py
git commit -m "test: add package import smoke test"
```
<!-- END_TASK_2 -->

<!-- START_TASK_3 -->
### Task 3: GitHub Actions CI (ruff + ty + pytest on Python 3.14)

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Create the workflow**

CI runs a **`[3.12, 3.14]` matrix**: 3.14 is the dev version; **3.12 is the Pyodide floor** (`requires-python = ">=3.12"`) and its job is the guard that catches any 3.14-only syntax leaking into the package — if the core/app won't run on 3.12, the WASM bundle (Phase 8) is broken, and this job fails loudly. `--all-extras` installs the extras so later phases' tests resolve; `dev` is synced by default.

`.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.14"]   # 3.12 = Pyodide floor guard; 3.14 = dev
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: false   # core/tests must not need the upstream submodule

      - name: Install uv
        uses: astral-sh/setup-uv@v6   # bump to the current major if a newer one exists
        with:
          enable-cache: true
          python-version: ${{ matrix.python-version }}

      - name: Sync (all extras + dev)
        run: uv sync --locked --all-extras

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run ty check .

      - name: Tests
        run: uv run pytest
```

> `submodules: false` is deliberate and load-bearing: it proves the runtime + test path never depends on `upstream/` (the oracle CSV is committed, Task 4). If a later phase's test reads `upstream/`, that test is mis-placed and CI will catch it here.

**Step 2: Verify locally (act-free)**

Re-run the exact CI commands locally to confirm they pass before pushing:
```bash
uv sync --locked --all-extras
uv run ruff check . && uv run ruff format --check . && uv run ty check . && uv run pytest
```
Expected: all succeed. (CI green-on-push is confirmed after the branch is pushed/opened as a PR — note in the task record whether the first CI run was green.)

**Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add ruff + ty + pytest workflow on Python 3.14"
```
<!-- END_TASK_3 -->

<!-- START_TASK_4 -->
### Task 4: Oracle extraction tool + committed CSV + contract test

This task produces the **committed** `data/ravens_oracle.csv` and an executable test pinning its shape. The numbers asserted here (840 rows, 553 distinct `Structure`, 839 distinct `Stimulus Name`, duplicate `A4_1`) become Phase 5's input contract.

**Files:**
- Create: `tools/extract_oracle.py` (dev tool; uses xlrd)
- Create: `data/ravens_oracle.csv` (generated, then committed)
- Create: `tests/test_oracle_data.py` (reads the committed CSV with stdlib `csv` only)

**Step 1: Write `tools/extract_oracle.py`**

Reads the `.xls` straight out of the submodule zip (no manual extraction; reproducible in any checkout), drops the legend block by finding the header row, and writes all six columns verbatim for every stimulus row.

```python
"""Dev-only: extract the Matzen et al. (2010) norming oracle to a committed CSV.

Reads Matzen_et_al_2010_norming_stimuli.xls (sheet 'Stimuli') from the read-only
upstream/ submodule zip and writes data/ravens_oracle.csv with all six columns,
preserving every stimulus row (including the duplicate 'A4_1'). Run once; the CSV
is committed so the runtime/test path needs neither xlrd nor the .xls.

Usage:  uv run python tools/extract_oracle.py
"""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import xlrd

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = REPO_ROOT / "upstream" / "Matrices" / "Matzen_et_al_2010_norming_stim.zip"
XLS_NAME = "Matzen_et_al_2010_norming_stimuli.xls"
SHEET = "Stimuli"
OUT_PATH = REPO_ROOT / "data" / "ravens_oracle.csv"

# The six columns, verbatim, in sheet order. The header row is detected by the
# presence of the join key 'Stimulus Name'; everything above it is the legend.
EXPECTED_HEADER = [
    "Number of Relations",
    "Problem Subtype",
    "Structure",
    "Stimulus Name",
    "Correct Answer",
    "% Correct in Norming Study",
]
HEADER_KEY = "Stimulus Name"


def _load_sheet() -> xlrd.sheet.Sheet:
    with zipfile.ZipFile(ZIP_PATH) as zf:
        data = zf.read(XLS_NAME)
    book = xlrd.open_workbook(file_contents=data)
    return book.sheet_by_name(SHEET)


def _header_row_index(sheet: xlrd.sheet.Sheet) -> int:
    for r in range(sheet.nrows):
        row = [str(c).strip() for c in sheet.row_values(r)]
        if HEADER_KEY in row:
            return r
    raise ValueError(f"header row containing {HEADER_KEY!r} not found")


def extract_rows() -> list[list[str]]:
    sheet = _load_sheet()
    hdr = _header_row_index(sheet)
    header = [str(c).strip() for c in sheet.row_values(hdr)][: len(EXPECTED_HEADER)]
    if header != EXPECTED_HEADER:
        raise ValueError(f"unexpected header: {header!r}")
    rows: list[list[str]] = []
    for r in range(hdr + 1, sheet.nrows):
        values = sheet.row_values(r)
        cells = [_fmt(values[c]) if c < len(values) else "" for c in range(len(EXPECTED_HEADER))]
        # A data row is one whose Stimulus Name (col index 3) is non-empty.
        if cells[3].strip():
            rows.append(cells)
    return rows


def _fmt(v: object) -> str:
    # xlrd yields floats for numeric cells; render integers without a trailing .0.
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def main() -> None:
    rows = extract_rows()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(EXPECTED_HEADER)
    w.writerows(rows)
    OUT_PATH.write_text(buf.getvalue(), encoding="utf-8")
    print(f"wrote {len(rows)} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
```

**Step 2: Generate the CSV**

```bash
uv run python tools/extract_oracle.py
```
Expected output: `wrote 840 rows -> data/ravens_oracle.csv`. If the count is not 840, STOP and reconcile against the investigator finding (legend boundary / blank rows) before continuing — do not hand-edit the CSV.

**Step 3: Write the contract test** (stdlib `csv` only — proves the committed CSV needs nothing external)

`tests/test_oracle_data.py`:
```python
"""The committed oracle CSV is the Phase 5 input contract. Pin its shape.

Numbers come from the 2026-06-08 codebase investigation of the norming sheet:
840 data rows, 553 distinct Structure codes, 839 distinct Stimulus Names
(one duplicate, 'A4_1'). Read with stdlib csv only — no xlrd, no upstream/.
"""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ravens_oracle.csv"
COLUMNS = [
    "Number of Relations",
    "Problem Subtype",
    "Structure",
    "Stimulus Name",
    "Correct Answer",
    "% Correct in Norming Study",
]


def _rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_columns_verbatim() -> None:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))
    assert header == COLUMNS


def test_row_count_is_840() -> None:
    assert len(_rows()) == 840


def test_distinct_structure_codes() -> None:
    rows = _rows()
    assert len({r["Structure"] for r in rows}) == 553


def test_stimulus_names_have_one_duplicate() -> None:
    names = [r["Stimulus Name"] for r in _rows()]
    assert len(set(names)) == 839
    dupes = {n for n in names if names.count(n) > 1}
    assert dupes == {"A4_1"}


def test_correct_answer_positions_in_1_8() -> None:
    for r in _rows():
        assert 1 <= int(r["Correct Answer"]) <= 8
```

**Step 4: Verify**

```bash
uv run pytest tests/test_oracle_data.py -v
```
Expected: all pass. If `test_distinct_structure_codes` or the duplicate assertion fails, the extraction filtered rows differently than the investigation — reconcile the tool, regenerate, do not weaken the test.

**Step 5: Commit**

```bash
git add tools/extract_oracle.py data/ravens_oracle.csv tests/test_oracle_data.py
git commit -m "feat(data): extract committed 840-row Matzen oracle CSV + contract test"
```
<!-- END_TASK_4 -->

<!-- START_TASK_5 -->
### Task 5: Java build spike + recorded outcome

Timeboxed (~1–2 h). The phase completes on a **recorded outcome**, not a successful build. JDK 8 + Ant are selected by the repo-root `.envrc` (already present; `direnv allow` done). If `javac`/`ant` are absent, the outcome record says "blocked: toolchain not installed" — that is still a valid recorded outcome and does not fail the phase.

**Files:**
- Create: `docs/spikes/java-build-spike.md` (the outcome record)

**Step 1: Confirm toolchain (record, do not fail on absence)**

```bash
java -version ; javac -version ; ant -version
```
If `javac` is missing, note it and follow the repo `.envrc` guidance (Temurin JDK 8 + Ant). Record whatever is true.

**Step 2: Attempt the build (do not edit `upstream/`)**

Work in a throwaway temp dir; never modify the read-only submodule.
```bash
work=$(mktemp -d)
unzip -q "upstream/Matrices/Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip" -d "$work"
cd "$work/SandiaGeneratedMatrixTool-1.0.0-source"
ant -version && ant 2>&1 | tee build.log || true
```
If `build-impl.xml` fails, try the documented fixes (e.g. `includeantruntime="false"`) **in the temp copy only**, and if still failing, the direct-`javac` fallback:
```bash
find Source -name '*.java' > sources.txt
javac -source 1.6 -target 1.6 -cp "Dependencies/**/*.jar" -d out @sources.txt 2>&1 | tee javac.log || true
```

**Step 3: Write the outcome record**

Create the directory first: `mkdir -p docs/spikes`. Then `docs/spikes/java-build-spike.md` must state, factually:
- Toolchain versions actually present (`java`, `javac`, `ant`).
- Whether `ant` built the jar; if not, the failure signature (first error) and any fix attempted.
- Whether the direct-`javac` fallback compiled; if not, why.
- **Verdict:** golden fixtures available? `yes` / `no` / `blocked-toolchain`.
- If `yes`: the exact command that produced a runnable artifact, and a one-line note on how a headless run (`-Djava.awt.headless=true`) could emit RNG/surface fixtures (consumed later by the optional Java differential, design "Additional Considerations").
- If `no`/`blocked`: state that RNG-driven surface/distractor behaviour stays best-effort-faithful and unverified — acceptable, it sits outside the equivalence bar.

**Step 4: Verify + commit**

The record exists and states a verdict (this is the phase's Done-when #5).
```bash
cd /home/brian/people/Mark/raven-matrix/.worktrees/raven-builder
git add docs/spikes/java-build-spike.md
git commit -m "docs(spike): record upstream Java build outcome for golden fixtures"
```
<!-- END_TASK_5 -->

---

## Phase 1 completion check

- [ ] `uv sync` clean; `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check .` clean.
- [ ] `uv run pytest` green (smoke + oracle contract).
- [ ] `data/ravens_oracle.csv` committed with exactly 840 rows; contract test green.
- [ ] CI workflow present; the local re-run of CI commands passes (note first real CI run status).
- [ ] `docs/spikes/java-build-spike.md` records a yes/no/blocked verdict.
- [ ] `ty` is exact-pinned in the `dev` group.
