# raven-builder Implementation Plan — Phase 2: JavaRandom + domain model

**Goal:** A behaviour-faithful `java.util.Random` port (`rng.py`) verified against golden JVM vectors, and the pure-Python value model (`model.py`): enums, frozen value dataclasses, and an identity-equality `SurfaceFeature` with an explicit `value_equals` plus a `contains_check` helper.

**Architecture:** Both modules are zero-dependency functional core. `JavaRandom` reimplements the 48-bit LCG exactly (only `nextInt(bound)` and `nextBoolean` are reachable upstream — source-verified). `model.py` re-models the Java domain idiomatically: `Shape`/`Fill`/`BaseRelation`/`Supplemental`/`Direction` enums; frozen value dataclasses `MatrixSize`/`Location`/`Point` (these carry `equals`+`hashCode` upstream, so value semantics are faithful); and `SurfaceFeature` as a plain identity class (no `__eq__`/`__hash__` override → Python gives identity `==` and id-hash, matching Java's missing `hashCode`), with `value_equals()` and a module-level `contains_check()` mirroring the upstream hand-rolled loops.

**Tech Stack:** Python (dev 3.14, package floor 3.12 — see Phase 1 decisions) stdlib only (`dataclasses`, `enum`). Tests: pytest + hypothesis. Golden RNG vectors generated from the local JDK (single-file source launch, or the JDK-8 the Phase-1 `.envrc` selects).

**Scope:** Phase 2 of 8 from `docs/design-plans/2026-06-08-raven-builder.md`.

**Codebase verified:** 2026-06-08 (codebase-investigator over the extracted upstream Java). DR3 confirmed: `nextInt(bound)` ×34, `nextBoolean()` ×2, no other Random methods; single seeded instance; index/`List`-driven consumption (deterministic). DR7 confirmed: `equals(SGMSurfaceFeature)` typed overload, no `hashCode`; hand-rolled `containsCheck` (SGMMatrix.java:575–596) and `containsFeatureCheck` (SGMBaseCell.java:188–200). Fill RGBA/alpha captured exactly; Grey10/Grey40 both report description `"Red"` (a quirk — carried faithfully, no flag yet, per decision).

**Phase Type:** functionality

---

## Acceptance Criteria Coverage

### raven-builder.AC4: Determinism
- **raven-builder.AC4.2 Success:** `JavaRandom` reproduces known `java.util.Random` vectors for `nextInt(bound)` (incl. the power-of-two and rejection-loop edges) and `nextBoolean`.

### raven-builder.AC1: Option parity with SGMBuilderFrame
- **raven-builder.AC1.5 Equality (DR7):** value-equal-but-distinct `SurfaceFeature`s are treated as distinct under identity in logic/dedup contexts; `value_equals()` returns true for them where the upstream hand-rolls a value check.

> AC4.1/AC4.3 (full build determinism) are realised in Phase 4 once `build()` exists; Phase 2 establishes the RNG foundation they depend on.

---

## Decisions carried into this phase (resolved during planning)

- **`SurfaceFeature` = plain identity class** + `value_equals()` + module-level `contains_check()`. `MatrixSize`/`Location`/`Point` = frozen value dataclasses. Dedup is **list-based only** — never route `SurfaceFeature` through a Python `set` into output (determinism caveat).
- **`JavaRandom`** = explicit-mask 48-bit LCG hand-port; golden vectors generated from a real JDK (version-independent: the algorithm is frozen Java SE spec).
- **Fill `"Red"` quirk** carried verbatim and test-pinned as faithful-to-code; **no compat flag** until a consumer shows it matters.

---

<!-- START_SUBCOMPONENT_A (tasks 1-2): JavaRandom -->

<!-- START_TASK_1 -->
### Task 1: Golden `java.util.Random` vectors (committed fixture)

**Verifies:** raven-builder.AC4.2 (provides the reference data the next task tests against)

**Files:**
- Create: `tools/gen_rng_vectors.java` (dev tool; single-file source program)
- Create: `tests/fixtures/java_random_vectors.json` (generated, committed)

**Why generate from the JVM:** `java.util.Random` is specified by the Java SE javadoc and unchanged since Java 1.0, so vectors from any JDK (the local one, or the JDK-8 the Phase-1 `.envrc` selects) are authoritative for the JDK-6-era SGMT. This removes any circularity (we do not derive the reference from our own port).

**Step 1: Write `tools/gen_rng_vectors.java`**

Emit, as JSON, for a set of seeds and bounds: the first N `nextInt(bound)` draws and the first N `nextBoolean()` draws. Cover the edges AC4.2 names — a **power-of-two** bound (8) and a **non-power-of-two** bound (7, exercises the rejection loop) — plus a large bound and `Integer.MAX_VALUE`-adjacent bound.

```java
import java.util.Random;

public class gen_rng_vectors {
    public static void main(String[] args) {
        long[] seeds = {0L, 1L, 42L, -1L, 123456789L};
        int[] bounds = {1, 2, 7, 8, 9, 256, 1000, 2147483646};
        int n = 20;
        StringBuilder sb = new StringBuilder();
        sb.append("{\n  \"nextInt\": [\n");
        boolean firstBlock = true;
        for (long seed : seeds) {
            for (int bound : bounds) {
                Random r = new Random(seed);
                if (!firstBlock) sb.append(",\n");
                firstBlock = false;
                sb.append("    {\"seed\": ").append(seed)
                  .append(", \"bound\": ").append(bound).append(", \"draws\": [");
                for (int i = 0; i < n; i++) {
                    if (i > 0) sb.append(", ");
                    sb.append(r.nextInt(bound));
                }
                sb.append("]}");
            }
        }
        sb.append("\n  ],\n  \"nextBoolean\": [\n");
        firstBlock = true;
        for (long seed : seeds) {
            Random r = new Random(seed);
            if (!firstBlock) sb.append(",\n");
            firstBlock = false;
            sb.append("    {\"seed\": ").append(seed).append(", \"draws\": [");
            for (int i = 0; i < n; i++) {
                if (i > 0) sb.append(", ");
                sb.append(r.nextBoolean());
            }
            sb.append("]}");
        }
        sb.append("\n  ]\n}\n");
        System.out.print(sb);
    }
}
```

**Step 2: Generate the fixture**

```bash
mkdir -p tests/fixtures
java tools/gen_rng_vectors.java > tests/fixtures/java_random_vectors.json
```
If `java <file>.java` fails with a compiler-not-found error (a JRE-only runtime), the JDK-8 selected by the repo `.envrc` (the Phase-1 toolchain) provides single-file launch — confirm `java -version` resolves to the JDK and retry. Sanity-check the JSON parses:
```bash
uv run python -c "import json,pathlib; d=json.loads(pathlib.Path('tests/fixtures/java_random_vectors.json').read_text()); print(len(d['nextInt']),'nextInt blocks,',len(d['nextBoolean']),'nextBoolean blocks')"
```
Expected: `40 nextInt blocks, 5 nextBoolean blocks`.

**Step 3: Commit**

```bash
git add tools/gen_rng_vectors.java tests/fixtures/java_random_vectors.json
git commit -m "test(rng): generate golden java.util.Random vectors from the JVM"
```
<!-- END_TASK_1 -->

<!-- START_TASK_2 -->
### Task 2: `rng.py` — `JavaRandom` (TDD against the golden fixture)

**Verifies:** raven-builder.AC4.2

**Files:**
- Create: `src/raven_matrix/rng.py`
- Test: `tests/test_rng.py` (unit, value-pinned against the fixture)

**Consumer:** every stochastic draw in Phase 4's `build()` (shapes/sizes/fills/answers) calls this. Phase 4 is the call site; no orphaned API.

**Step 1 (RED): write the failing test**

`tests/test_rng.py` reads `tests/fixtures/java_random_vectors.json` and, for each block, constructs `JavaRandom(seed)` and asserts the produced `next_int(bound)` / `next_boolean()` sequence equals the recorded draws. Add explicit edge assertions called out by AC4.2: the power-of-two bound (8) fast path and the non-power-of-two bound (7) rejection loop both match. Run and watch it fail (no `rng` module yet).

**Step 2 (GREEN): implement `rng.py`**

Faithful 48-bit LCG. Mask after every update; convert the `(int)` casts to signed 32-bit.

```python
"""A faithful port of java.util.Random — only the methods SGMT uses.

The algorithm is mandated by the Java SE specification (unchanged since Java 1.0):
a 48-bit linear congruential generator. Upstream uses only nextInt(bound) and
nextBoolean (source-verified), so that is all we expose, plus the protected next()
they are built on.
"""

from __future__ import annotations

_MULTIPLIER = 0x5DEECE66D
_ADDEND = 0xB
_MASK = (1 << 48) - 1


def _to_int32(value: int) -> int:
    """Interpret the low 32 bits as a signed Java int."""
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value & 0x80000000 else value


class JavaRandom:
    """java.util.Random with the SGMT-reachable surface."""

    __slots__ = ("_seed",)

    def __init__(self, seed: int) -> None:
        self.set_seed(seed)

    def set_seed(self, seed: int) -> None:
        self._seed = (seed ^ _MULTIPLIER) & _MASK

    def next(self, bits: int) -> int:
        """The protected next(int bits): advance state, return top `bits` as signed int32."""
        self._seed = (self._seed * _MULTIPLIER + _ADDEND) & _MASK
        return _to_int32(self._seed >> (48 - bits))

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound must be positive")
        # Power-of-two fast path.
        if (bound & -bound) == bound:
            return (bound * self.next(31)) >> 31
        # Rejection loop for uniformity.
        while True:
            bits = self.next(31)
            val = bits % bound
            if bits - val + (bound - 1) >= 0:
                return val

    def next_boolean(self) -> bool:
        return self.next(1) != 0
```

> Note on `next(31)`: it returns a non-negative value (top bit clear), so `_to_int32` is a no-op there; it matters for `next()` generality and keeps the port literal. The power-of-two branch mirrors `(int)((bound * (long)next(31)) >> 31)`; Python's arbitrary-precision ints make the intermediate exact.

**Step 3 (GREEN): run the tests**

```bash
uv run pytest tests/test_rng.py -v
```
Expected: all fixture blocks pass, including the bound=8 and bound=7 edges.

**Step 4: type + lint + commit**

```bash
uv run ty check . && uv run ruff check .
git add src/raven_matrix/rng.py tests/test_rng.py
git commit -m "feat(rng): faithful java.util.Random port (nextInt/nextBoolean) vs golden vectors"
```
<!-- END_TASK_2 -->
<!-- END_SUBCOMPONENT_A -->

<!-- START_SUBCOMPONENT_B (tasks 3-4): domain model -->

<!-- START_TASK_3 -->
### Task 3: `model.py` — enums + frozen value dataclasses

**Verifies:** (foundation for AC1.* and AC5.*; the Fill RGBA/alpha + `"Red"` quirk are pinned here)

**Files:**
- Create: `src/raven_matrix/model.py` (enums + value dataclasses portion)
- Test: `tests/test_model_values.py` (unit)

**Consumers:** `Shape`/`Fill` → Phase 4 surface/fill generators + Phase 6 renderer; `BaseRelation`/`Supplemental`/`Direction` → Phase 3 transforms + Phase 4 structure + Phase 5 parser/labeller; `MatrixSize`/`Location`/`Point` → Phase 3 transforms + Phase 4 builder.

**Implementation:**

- `Shape(Enum)`: `DIAMOND, ELLIPSE, LINE, RECTANGLE, TEE, TRAPEZOID, TRIANGLE` (the 7 upstream surface features). Each member carries its canonical description string (e.g. `DIAMOND` → `"Diamond"`).
- `Fill(Enum)`: five members, each a frozen record of `(r, g, b, a, description)` with the **exact** upstream values:
  - `BLACK = (0.0, 0.0, 0.0, 0.75, "Black")`
  - `WHITE = (1.0, 1.0, 1.0, 0.0, "White")`  *(alpha 0 → transparent)*
  - `GREY10 = (0.1, 0.1, 0.1, 0.6, "Red")`  *(description quirk — faithful-to-code)*
  - `GREY40 = (0.4, 0.4, 0.4, 0.5, "Red")`  *(description quirk — faithful-to-code)*
  - `GREY75 = (0.75, 0.75, 0.75, 0.4, "Grey75")`
  > Use the investigator's exact literals; if any description string for BLACK/WHITE/GREY75 differs in the source from the above, take the **source** value (the executor should re-read the five `*SGMFillPattern.java` files to confirm each `getDescription()` literal before pinning the test). The only quirk we are committing to carry is Grey10/Grey40 → `"Red"`.
- `BaseRelation(Enum)`: `SHAPE_REPETITION, LOGICAL_OR, LOGICAL_AND, LOGICAL_XOR`.
- `Supplemental(Enum)`: `ROTATION, SCALING, CHANGE_FILL, FILL_REPETITION, NUMEROSITY`.
- `Direction(IntEnum)`: `HORIZONTAL=1, VERTICAL=2, DIAGONAL_BL_TR=3, DIAGONAL_TL_BR=4, TOP_LEFT_CORNER_OUT=5` (the base-direction digits from the Matzen naming scheme; the labeller's `1/2` swap and corner-out→`6` are Phase 5 concerns, not encoded here).
- Frozen value dataclasses (`@dataclass(frozen=True, slots=True)`): `MatrixSize(num_rows: int, num_columns: int)`, `Location(row: int, column: int)`, `Point(x: float, y: float)`. Frozen dataclasses give value `__eq__`/`__hash__` for free — faithful to the upstream which defines `equals`+`hashCode` on these.

**Testing (describe — task-implementor writes the code):**
- Each enum has exactly the members above (guards against accidental additions/omissions).
- `Fill` RGBA+alpha+description are exactly the pinned literals — including `Fill.GREY10.description == "Red"` and `Fill.GREY40.description == "Red"` (faithful-to-code), and `Fill.WHITE.a == 0.0`.
- `MatrixSize`, `Location`, `Point` are value-equal for equal fields and hashable (`{MatrixSize(3,3)} == {MatrixSize(3,3)}`).

**Verification + commit:**
```bash
uv run pytest tests/test_model_values.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/model.py tests/test_model_values.py
git commit -m "feat(model): enums (Shape/Fill/relations/Direction) + value dataclasses"
```
<!-- END_TASK_3 -->

<!-- START_TASK_4 -->
### Task 4: `model.py` — `SurfaceFeature` (identity), `value_equals`, `contains_check`, containers

**Verifies:** raven-builder.AC1.5

**Files:**
- Modify: `src/raven_matrix/model.py` (append the feature + container types)
- Test: `tests/test_model_features.py` (unit)

**Consumers:** `SurfaceFeature`/`value_equals`/`contains_check` → Phase 4 logic relations (OR/AND/XOR) + distractor dedup; `Cell`/`Layer`/`Matrix` → Phase 4 `build()` populates them, Phase 6 renders them, Phase 5 labels them.

**Implementation:**

- `SurfaceFeature`: a **plain class** (NOT a dataclass) so it keeps Python's default identity `__eq__` and id-based `__hash__` — exactly mirroring the upstream's missing `hashCode` and typed-overload `equals`. Fields (from `AbstractSGMSurfaceFeature`): `shape: Shape`, `fill: Fill`, `scale: float`, `rotation: float`, `position: Point` (and any shape-specific state the custom check needs). Provide:
  - `value_equals(self, other: SurfaceFeature) -> bool` — compares `scale`, `rotation`, `position.x`, `position.y`, `shape` (the upstream `getDescription()` of the feature), `fill`, and the shape-specific custom check. This mirrors `AbstractSGMSurfaceFeature.equals(SGMSurfaceFeature)` + `customEqualsCheck`.
  - Do **not** define `__eq__`/`__hash__`.
- Module-level helpers mirroring the upstream hand-rolled loops:
  - `contains_check(features: list[SurfaceFeature], item: SurfaceFeature) -> bool` — returns True iff some element `value_equals` item (skipping `None`). This is the **feature-list** helper, mirroring `SGMBaseCell.containsFeatureCheck` (SGMBaseCell.java:188). **It is distinct from** the upstream **cell-list** helper `SGMMatrix.containsCheck(List<SGMCell>, SGMCell)` (SGMMatrix.java:575) — that one is a separate **Phase-4** artifact (`_contains_cell`, with a cell-level `_cell_value_equals`) used for distractor dedup over whole `Cell`s. Do not conflate them: the Phase-4 cell helper *uses* this feature-list helper internally (a cell equals another iff feature counts match and each feature is `contains_check`-present).
- Containers (data holders; populated in Phase 4):
  - `Cell`: `surface_features: list[SurfaceFeature]`, `location: Location` (mutable list — built incrementally; do not freeze).
  - `Layer`: a `MatrixSize`-shaped grid of `Cell` (e.g. `cells: list[list[Cell]]`) plus `structures: list` (structure features added in Phase 4).
  - `Matrix`: `cells: list[list[Cell]]` (the composited 3×3), `answer_choices: list[Cell]`, `correct_answer_position: int`, `layers: list[Layer]`.
  > Keep containers minimal here — just enough shape for Phase 4 to fill. Do not add behaviour the design hasn't called for (YAGNI).

**Testing (describe — task-implementor writes the code):**
- **AC1.5 identity:** two `SurfaceFeature`s built with identical field values are `!=` under `==` (identity), and `b not in [a]` (list `in` uses `==` → identity), but `a.value_equals(b)` is True.
- **AC1.5 contains_check:** `contains_check([a], b)` is True for value-equal distinct `a`,`b`; False when no element is value-equal; `None` elements are skipped without error.
- A `SurfaceFeature` is usable as a `dict` key / `set` member by identity (hashable), and two value-equal features occupy two distinct slots — documents the determinism rule that dedup must stay list-based.

**Verification + commit:**
```bash
uv run pytest tests/test_model_features.py -v && uv run ty check . && uv run ruff check .
git add src/raven_matrix/model.py tests/test_model_features.py
git commit -m "feat(model): identity SurfaceFeature + value_equals + contains_check + containers"
```
<!-- END_TASK_4 -->
<!-- END_SUBCOMPONENT_B -->

---

## Phase 2 completion check

- [ ] `JavaRandom` reproduces every golden-vector block, incl. bound=8 (power-of-two) and bound=7 (rejection loop) and `nextBoolean` (AC4.2).
- [ ] `SurfaceFeature` is identity-equal, `value_equals` does value comparison, `contains_check` finds value-equal members (AC1.5).
- [ ] Fill RGBA/alpha pinned exactly; Grey10/Grey40 description `"Red"` carried faithfully (test-pinned).
- [ ] `MatrixSize`/`Location`/`Point` are frozen value dataclasses.
- [ ] `uv run pytest`, `uv run ty check .`, `uv run ruff check .` all clean.
- [ ] No `SurfaceFeature` routed through a `set` into any output path (determinism rule).
