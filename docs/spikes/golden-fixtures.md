# Golden JVM fixtures — spike follow-on

**Date:** 2026-06-09
**Status:** Both deliverables emitted (deliverable 2 succeeded within the
timebox), plus a fill-pattern fixture added as a coherence-review follow-on (M1).

This is a Phase-1 spike follow-on (authorised directly, not a numbered phase
task). The Java build spike (`docs/spikes/java-build-spike.md`) established that
the upstream SGMT jar builds on the local JDK 8. This follow-on uses that to emit
**committed golden fixtures**: deterministic JVM outputs the Python port verifies
against LATER, without needing a JVM at test time.

## Standing rule

**Fixtures are consumed without the JVM.** The JSON files under `tests/golden/`
are committed and read by the Python test suite using stdlib `json` only. The JVM,
JDK 8, Ant, and the upstream jar are needed ONLY to *regenerate* the fixtures, never
to consume them. CI (which builds with `submodules: false`) never touches Java.

The Phase-2/Phase-4 tests own the assertions that consume these files. This spike
emits the data and the regen tooling; it deliberately writes **no** Python tests
that consume the fixtures (a single optional `json.load` validity check is the only
Python allowed, and none was added — the shell regen path keeps the Python lint
surface clean).

## Regeneration

One reproducible, idempotent command (requires JDK 8 on PATH; `JAVA_HOME` may be
unset — the script falls back to PATH `java`/`javac` after confirming they report
`1.8`):

```bash
tools/golden/regenerate.sh
```

It (1) verifies `javac` and `java` are JDK 8, (2) compiles + runs
`tools/golden/JavaRandomDump.java` (no jar needed) to write
`tests/golden/javarandom_vectors.json`, and (3) if `tools/golden/SgmtDump.java`
exists, extracts the upstream source zip to a **temp dir**, builds the jar there
with `ant -Djavac.compilerargs="-Xlint:none" clean jar`, compiles the drivers
against it, and runs them headless (`-Djava.awt.headless=true`) to write
`tests/golden/sgmt_matrices.json` and `tests/golden/fill_patterns.json`. The jar
is built **once** and reused for both SGMT-jar-dependent drivers (`SgmtDump`,
`FillDump`). `upstream/` is never modified.

**Determinism (verified):** running `regenerate.sh` twice yields byte-identical
JSON for all three files (sha256 unchanged; `git status` clean on the committed
JSON after a re-run). The JSON is hand-formatted in Java with a fixed key order,
two-space indent, LF newlines, and no trailing whitespace, so regeneration is
byte-stable.

## Deliverable 1 — `java.util.Random` golden vectors

**File:** `tests/golden/javarandom_vectors.json`
**Source:** `tools/golden/JavaRandomDump.java` (depends ONLY on `java.util.Random`
— never the SGMT jar, so it stays robust regardless of the upstream build).

### Why these seeds and bounds

Upstream SGMT uses **only** `Random.nextInt(bound)` and `Random.nextBoolean()`
(source-verified; phase_02 DR3). The fixture therefore covers exactly those two
methods.

- **Seeds:** `0, 1, 42, 2024, -1, 123456789`. A spread including the trivial seed
  0, small seeds, one **negative** (`-1`, exercises the sign handling in the
  `(seed ^ MULTIPLIER)` scramble), and one **large** positive (`123456789`).
- **`nextInt` bounds:** `2, 3, 5, 6`. `2` is a power of two (the fast path,
  `(bound * next(31)) >> 31`); `3`, `5`, `6` are non-powers-of-two that drive the
  **rejection loop**. These are the small bounds the surface/location/shape draws
  use. (Phase 4's `build()` call sites consume bounds in this family.)
- **`nextBoolean`:** covers the width/height swap upstream performs.
- **Per (seed, method, bound):** a **freshly-seeded** `new Random(seed)` and the
  first **1000** values. Each combination uses its own fresh `Random` so Phase 2
  can verify each method **independently** (no shared stream state across blocks).

### Schema

```json
{
  "seeds": [0, 1, 42, 2024, -1, 123456789],
  "vectors": [
    {"seed": 0, "method": "nextInt", "bound": 2, "count": 1000, "values": [1, 1, 0, ...]},
    ...
    {"seed": 0, "method": "nextBoolean", "bound": null, "count": 1000, "values": [true, true, false, ...]},
    ...
  ]
}
```

- Top-level object: `"seeds"` (the seed list) and `"vectors"` (a list of blocks).
- Each block: `"seed"` (int), `"method"` (`"nextInt"` | `"nextBoolean"`),
  `"bound"` (int for `nextInt`, `null` for `nextBoolean`), `"count"` (1000),
  `"values"` (the draws — JSON ints for `nextInt`, JSON `true`/`false` for
  `nextBoolean`).
- 30 blocks total: 6 seeds × (4 `nextInt` bounds + 1 `nextBoolean`).

> Note: this spike's schema (1000 draws, bounds 2/3/5/6, seeds incl. 2024) is the
> authoritative golden RNG fixture. The phase_02.md Task-1 draft sketched a smaller
> placeholder (20 draws, different bounds, a different path); Phase 2 should consume
> THIS file (`tests/golden/javarandom_vectors.json`) and treat the phase_02 code
> block as illustrative only.

## Deliverable 2 — SGMT matrix fixtures (EMITTED)

**File:** `tests/golden/sgmt_matrices.json`
**Source:** `tools/golden/SgmtDump.java` (built against the jar).
**Outcome:** **Emitted** — a clean, small headless driver was feasible inside the
timebox. 5 configs × one fixed seed (42).

### How it drives the generator (and what it bypasses)

`SGMMatrixSetGenerator.generateMatrices(RasterSettings)` is the upstream entry
point, but it is **not** cleanly headless as-shipped:

- Its constructor requires a non-null `SGMMatrixDifficultyClassifier`, and the
  upstream JUnit `SGMMatrixSetGeneratorTest` loads that classifier from a
  serialized XStream file `SerializedMatrixSGMDifficultyClassifier.xml` — **which
  is not present anywhere in the source distribution** (confirmed by an
  exhaustive `find` over the extracted tree). So the upstream test itself cannot
  run as-shipped.
- Inside `generateMatrices`, the classifier is used **only** for the outer
  accept/reject loop: `score = classifier.evaluate(matrix)` then
  `scoreDistribution.addSGMScore(score)` decides whether to keep the matrix and
  when the requested score distribution is satisfied. It does **not** influence
  the structure, surface realisation, or answer layout of any individual matrix.

The deterministic core that *does* build a matrix is classifier-free:
`SGMLayerGenerator.generateLayer(size, maxStruct, cellPx, random)` (a static method
taking a seeded `Random`) and `new SGMMatrix(size, numAnswers, correctPos, layers,
random)`. `SgmtDump` therefore replicates **one** `generateMatrices` iteration,
byte-faithful to the upstream RNG-consumption order:

```
numLayers        = random.nextInt(maxLayersPerMatrix) + 1   // SGMMatrixSetGenerator:144
correctAnswerPos = random.nextInt(numAnswerChoices)         // SGMMatrixSetGenerator:150
layers           = generateLayer(...) x numLayers           // :156
matrix           = new SGMMatrix(size, numAnswers, pos, layers, random)  // :164
// upstream `continue` guard (:171): re-draw if too few answer choices
```

This consumes RNG in exactly the upstream order, so the Python port replicating
that order reproduces these matrices. (Verified: with seed 42 the recorded
`layer_count` values 1/2/3 match an independent trace of `nextInt(maxLayers)+1`,
and `correct_answer_position` 0 matches `nextInt(8)` on the seed-42 stream.)

### Configs

Each is `(maxLayersPerMatrix, maxStructureFeaturesPerLayer, numAnswerChoices)` on a
3×3 matrix, `cellPixelSize=100`, seed 42:

| max_layers | max_structure_features | num_answers |
|-----------:|-----------------------:|------------:|
| 1 | 1 | 8 |
| 1 | 2 | 8 |
| 2 | 1 | 8 |
| 2 | 2 | 8 |
| 3 | 2 | 8 |

These exercise single-layer base relations, supplemental features (Numerosity),
and multi-layer logic composition (Logical AND on a Logic location transform).

**Seeding note:** Each config entry is an independent cold-start from seed 42 —
`generate()` calls `new Random(SEED)` per invocation, so the five matrices are
five independent draws, not five consecutive draws from one continuing stream
(upstream `SGMMatrixSetGenerator.generateMatrices` uses one `Random` across the
whole run). This matches Phase 4's intended API, where `build(config, seed,
flags)` seeds its own `JavaRandom` per call, so a cold-start fixture is the
correct oracle for `build()`. Single-stream matrix-set behaviour (the outer
accept/reject loop) belongs to the classifier-driven orchestration that is out
of scope here and is not tested by these fixtures.

### Schema

```json
{
  "seed": 42,
  "matrix_size": {"rows": 3, "cols": 3},
  "cell_pixel_size": 100,
  "matrices": [
    {
      "config": {"max_layers": 1, "max_structure_features": 1, "num_answer_choices": 8},
      "layer_count": 1,
      "correct_answer_position": 0,
      "structure": [
        {"layer": 0, "features": [{"relation": "Shape Repetition", "direction": "Horizontal"}]}
      ],
      "cells": [
        {"row": 0, "col": 0, "surface_features": [
          {"shape": "Rectangle", "fill": "Black", "scale": 1, "rotation": 0, "x": 50, "y": 50}
        ]},
        ...  // 9 cells, row-major
      ],
      "answer_choices": [
        {"slot": 0, "surface_features": [ ... ]},
        ...  // num_answer_choices slots; a null surface_features marks a blank pad
      ]
    },
    ...
  ]
}
```

- `relation` = the structure feature's `getDescription()` (e.g. `"Shape
  Repetition"`, `"Numerosity"`, `"Logical AND"`); `direction` = its
  `getLocationTransform().getDescription()` (e.g. `"Horizontal"`, `"Logic"`,
  `"Diagonal Bottom Left to Top Right"`). Both read by reflection because
  `getDescription()` is on the concrete classes, not the interfaces.
- `cells` = the composited 3×3 grid in row-major order; each surface feature
  records `shape` (description), `fill` (description — note the upstream Grey10/
  Grey40 → `"Red"` quirk surfaces here verbatim), `scale`, `rotation`, and
  position `x`/`y`.
- `answer_choices` = the generated distractors plus the correct answer in slot
  order; `correct_answer_position` indexes the correct slot. A slot whose
  `surface_features` is `null` is a blank pad (upstream pads when it cannot
  generate enough distinct distractors).

### Caveats for the consumer

- This is the **classifier-free** generation core, so it carries **no difficulty
  score** (`SGMScore`). Difficulty/normative checks remain a later, separate
  concern (the difficulty classifier needs the unshipped serialized XML or a
  programmatic reconstruction — a Phase-later task).
- The fixture pins **structure + surface + answer layout** for a fixed seed, which
  is exactly the data/logic-equivalence bar (CLAUDE.md QA target). It is a
  best-effort RNG differential, not part of the acceptance gate; the upstream RNG
  seeds behind the published norming PNGs are themselves unpublished.

## Deliverable 2b — fill-pattern fixture (coherence review M1)

**File:** `tests/golden/fill_patterns.json`
**Source:** `tools/golden/FillDump.java` (built against the jar — reuses the jar
`regenerate.sh` already builds for `SgmtDump`; no second build).

### What it anchors and why

The seed-42 `sgmt_matrices.json` matrices never drew the Grey fills, so the
upstream fill quirks had **no golden anchor**. This fixture instantiates all five
`fillpattern/` classes directly and records, for each, its Java class name,
`getDescription()`, and the exact 8-bit RGBA of `getPaint()` (a `java.awt.Color`,
so the float channels are rounded by AWT). Phase 2's `Fill` enum must reproduce
these exactly. The anchored facts:

- **Grey10 and Grey40 both report `getDescription()` == `"Red"`** — a genuine
  upstream quirk (carried faithfully, no compat flag), not a typo on our side.
- **White is fully transparent: alpha 0** (`new Color(1,1,1,0)`).
- **Grey75 reports `"Grey"`** (not `"Grey75"` — the phase_02 draft guessed
  `"Grey75"`; the JVM is authoritative, so Phase 2 should pin `"Grey"`).
- Exact alphas (the float→8-bit rounding AWT applies): Black 191 (0.75),
  Grey10 153 (0.6), Grey40 128 (0.5), Grey75 102 (0.4), White 0 (0.0).

Recorded values (canonical order `[White, Grey10, Grey40, Grey75, Black]`):

| class | description | rgba |
|-------|-------------|------|
| `WhiteSGMFillPattern` | `White` | `[255, 255, 255, 0]` |
| `Grey10SGMFillPattern` | `Red` | `[26, 26, 26, 153]` |
| `Grey40SGMFillPattern` | `Red` | `[102, 102, 102, 128]` |
| `Grey75SGMFillPattern` | `Grey` | `[191, 191, 191, 102]` |
| `BlackSGMFillPattern` | `Black` | `[0, 0, 0, 191]` |

### Schema

```json
{
  "fills": [
    {"class": "WhiteSGMFillPattern", "description": "White", "rgba": [255, 255, 255, 0]},
    {"class": "Grey10SGMFillPattern", "description": "Red", "rgba": [26, 26, 26, 153]},
    {"class": "Grey40SGMFillPattern", "description": "Red", "rgba": [102, 102, 102, 128]},
    {"class": "Grey75SGMFillPattern", "description": "Grey", "rgba": [191, 191, 191, 102]},
    {"class": "BlackSGMFillPattern", "description": "Black", "rgba": [0, 0, 0, 191]}
  ]
}
```

- Top-level object with one key, `"fills"` — a list in the canonical order
  `[White, Grey10, Grey40, Grey75, Black]`.
- Each entry: `"class"` (the Java simple class name), `"description"`
  (`getDescription()`), `"rgba"` (a 4-int array `[red, green, blue, alpha]`, each
  0–255, the alpha last).
- Consumed **without a JVM** (stdlib `json`), like the other fixtures.

## Phase-4 head-start (API findings)

For whoever wires the full generator later:

- **Entry point:** `SGMMatrixSetGenerator(SGMScoreDistribution, SGMMatrixSize,
  int maxLayersPerMatrix, int maxStructureFeaturesPerLayer, int numAnswerChoices,
  SGMMatrixDifficultyClassifier, long seed)` then `.generateMatrices(RasterSettings)`.
- **Blocker to a full headless run:** the mandatory `SGMMatrixDifficultyClassifier`
  is loaded in the upstream test from `SerializedMatrixSGMDifficultyClassifier.xml`,
  which is **not in the distribution**. To run the *full* distribution-filling loop,
  that classifier must be reconstructed programmatically (see
  `SGMMatrixDifficultyClassifier.java`, 636 lines) or its serialized form sourced.
- **Deterministic core (no classifier needed):** `SGMLayerGenerator.generateLayer`
  and `new SGMMatrix(...)`, both `Random`-driven — this is what `SgmtDump` uses.
- **Model getters used:** `SGMMatrix.getSGMCells()` (`SGMCell[][]`),
  `.getSGMLayers()`, `.getCorrectAnswerPosition()`, `.getAnswerChoices()`,
  `.getNumAnswerChoicesGenerated()`; `SGMLayer.getStructureFeatures()`;
  `SGMStructureFeature.getLocationTransform()`; `SGMCell.getSurfaceFeatures()`;
  `SGMSurfaceFeature.getScale()/.getRotation()/.getPosition()/.getFillPattern()`;
  `getDescription()` on the concrete surface/structure/fill/location classes (via
  reflection — not on the interfaces).
```
