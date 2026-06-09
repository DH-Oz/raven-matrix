# raven-matrix

Last verified: 2026-06-08

## Mission

Port the Sandia Generated Matrix Tool (SGMT) to Python 3.14 so it generates
Raven-style progressive-matrix puzzles. Stretch goal: run the generator in the
browser via WebAssembly (Pyodide or MicroPython-WASM) — wanted if feasible.
Requested by Mark (via Brian). Upstream is Sandia/DOE under BSD-3 — free to port
with attribution.

## Provenance

- Software: Sandia Generated Matrix Tool (SGMT) v1.0.0, first open-source
  release (dated 2011-01-10).
- OSTI `code-54699` · DOI `10.11578/dc.20210416.34` · BSD-3-Clause ·
  © 2010 Sandia Corporation (Contract DE-AC04-94AL85000).
- Authors: Zachary Benz, Kevin Dixon (`Main.java` by Justin Basilico).
- Paper: Matzen et al. (2010), "Recreating Raven's: Software for systematically
  generating large numbers of Raven-like matrix problems with normed
  properties," *Behavior Research Methods*.
- Mark recalled "JavaScript"; the source is **Java**. Settled.

## Upstream source map — `upstream/Matrices/` (submodule, READ-ONLY)

- `Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip` —
  the Java source we port FROM (NetBeans project, package
  `gov.sandia.cognition.generator.matrix`).
- `Matzen_et_al_2010_norming_stim.zip` — the QA oracle (see below).

**Read the Java here — do NOT unzip.** The source is extracted to a committed,
read-only mirror at `reference/sgmt-source/`: the port source under
`Source/gov/sandia/cognition/generator/matrix/…` and the JUnit spec under
`Test/…`. Grep and read from there. The zip above stays sealed as the provenance
artifact; never re-unzip it ad hoc. Re-derive the mirror only with
`bash tools/extract_upstream.sh`. The Matzen paper (when needed) is at
`docs/papers/matzen-2010-recreating-ravens.pdf`.

Java structure (≈72 source files):

- Core model: `SGMMatrix`, `SGM{Base,Composite,Derived}Cell`, `SGMLayer`,
  `SGMFeature`, `SGMLocation`, `SGMMatrixSize`.
- `structure/` — the **relations** (logic). Base: LogicalAND/OR/XOR,
  ShapeRepetition. Supplemental: ApplyRotation, ApplyScaling, ChangeFillPattern,
  FillPatternRepetition, TranslationalNumerosity.
- `surface/` — **shapes**: Diamond, Ellipse, Line, Rectangle, Tee, Trapezoid,
  Triangle.
- `fillpattern/` — Black, White, Grey10/40/75.
- `locationtransform/` — Horizontal, Vertical, Diagonal (both), TopLeftCornerOut,
  Logic.
- Generation: `SGMMatrixSetGenerator`, `SGMLayerGenerator`.
- Difficulty/norming: `SGMMatrixDifficultyClassifier`, `SGMScore`,
  `SGMScoreDistribution`.
- Rendering (Java2D → PNG): `AbstractSGMImage`, `SGMCellImage`,
  `SGMMatrixImage`, `SGMAnswerChoicesImage`, `RasterSettings`.
- `ui/` Swing: `SGMBuilderFrame`, `ImagePanel`.
- JUnit tests: `SGMMatrixSetGeneratorTest`, `SGMMatrixDifficultyClassifierTest`,
  `TopLeftCornerOutSGMLocationTransformTest` — **port these first; they are the
  executable spec.**

Heads-up: `Main.java` is an empty stub. The release is GUI-driven; a headless
batch path must be reconstructed from `SGMMatrixSetGenerator` + `SGMBuilderFrame`.

Third-party Java deps (context for reading the source): Cognitive Foundry 3.0.2,
MTJ 0.9.9 (linear algebra), xstream 1.3.1 (XML serialisation), swing-layout.

## QA target (acceptance oracle) — data/logic equivalence

Decided (Brian, 2026-06-08): the bar is **data/logic equivalence, not pixel
reproduction**. The norm spreadsheet is logic-identical to the PNGs and is the
machine-checkable oracle; the PNGs are renderings of it.

`Matzen_et_al_2010_norming_stim.zip`:

- ≈840 problem/answer PNG pairs (`X.png` + `X_Answers.png`) in "1 Layer Stim"
  (193 files), "2 Layer Stim" (369), "3 Layer Stim" (1001), "Logic Stim" (121).
- `Matzen_et_al_2010_norming_stimuli.xls`, sheet `Stimuli`: 845 data rows, one
  per stimulus, columns: `Number of Relations` · `Problem Subtype` ·
  `Structure` · `Stimulus Name` · `Correct Answer` · `% Correct in Norming
  Study`. `Stimulus Name` == the PNG basename (the join key). Sheet
  `Experimental Lists` holds the 20 counterbalanced norming lists.

Naming scheme (decoded from the sheet legend):

- Letter = relation: A Shape · B Shading · C Orientation · D Size · E Number
  repetition.
- Digit = direction of repetition: 1 horizontal · 2 vertical · 3 BL→TR diag ·
  4 TL→BR diag · 5 outward-from-top-left. (Shape repetition excludes direction 5.)
- Logic transforms: X OR · Y AND · Z XOR.
- `A1B2C4` composes one layer per letter; layer count = the "… Layer Stim" folder.

Maps onto the Java source:

- relation letter → `structure/` (ShapeRepetition; ChangeFillPattern /
  FillPatternRepetition; ApplyRotation; ApplyScaling; TranslationalNumerosity).
- direction digit → `locationtransform/` (Horizontal, Vertical,
  DiagonalBottomLeftTopRight, DiagonalTopLeftBottomRight, TopLeftCornerOut).
- X/Y/Z → Logical OR/AND/XOR + `LogicSGMLocationTransform`.

Two oracles fall out:

1. Structural — for each `Stimulus Name`, the port (given its `Structure` code)
   must produce a matrix with the same relations/directions/layers and the same
   `Correct Answer` position.
2. Normative — the ported `SGMMatrixDifficultyClassifier` should track the
   `% Correct` column (the empirical difficulty).

Caveat: a `Structure` code fixes the *relations*, but the concrete surface
realisation and the eight distractors may involve generator RNG; reproducing
exact distractor sets is a stretch (seeds unpublished). Equivalence is judged on
structure + correct-answer position + difficulty, per the decision above.

## Tech stack

- Python 3.14 (`.python-version`), managed by uv.
- Dependencies: none yet (greenfield). Chosen during design.

## Commands

- `git submodule update --init` — fetch upstream after a fresh clone.
- `uv sync` — create/refresh the environment.
- `uv run <…>` — run within the project env.

## Repo layout

- `upstream/Matrices/` — vendored Sandia source + norming data (submodule).
  READ-ONLY reference; never edit, never port edits back into it.
- `pyproject.toml`, `.python-version`, `uv.lock` — uv project config.
- `docs/design-plans/` — design docs land here (created during design).
- Python package — not created yet; the design decides the layout.

## Boundaries

- Never edit `upstream/Matrices/` — it is the immutable source we port FROM.
- Don't commit unless Brian asks.

## Design decisions

Locked constraints the port must honour (rationale, not task state):

- Replication bar = data/logic equivalence, not pixel reproduction (see QA
  target).
- Rendering = SVG is canonical; rasterise ("render down") to PNG when a bitmap
  is needed. Favours a dependency-light, pure-Python renderer.
- Option parity = whatever its form, the interface must expose the same
  generation options as upstream SGMT: relation types, directions, layer
  composition, logic transforms, and answer/difficulty settings (the controls
  in `ui/SGMBuilderFrame`).
- Spec precedence = the Matzen et al. (2010) paper is the fundamental spec. When
  the Java source and the paper genuinely disagree because of a source bug,
  follow the paper and fix the bug; record the divergence (code comment + test +
  ADR). First instance: upstream compares fills by `getDescription()`, where
  Grey10/Grey40 both report "Red" (a bug — the paper specifies five distinct
  fill patterns), so the port keeps the five shadings distinct. See
  `src/raven_matrix/model.py` `Fill` / `SurfaceFeature.value_equals`.

Design state, aspirations, and still-open questions live in `.notes/`, not here.

## Workflow

Follows the denubis brainstorm → design → implement flow:

1. Brainstorm the port (skill: `brainstorming` / `starting-a-design-plan`).
2. Write the design to `docs/design-plans/` (skill: `design-write`).
3. Implementation plan (skill: `starting-an-implementation-plan`), then execute
   task-by-task with TDD.

Port the JUnit tests first — they are the executable specification.
