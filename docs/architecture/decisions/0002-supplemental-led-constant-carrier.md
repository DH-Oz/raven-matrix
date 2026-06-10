# ADR 0002: Supplemental-led codes build a constant carrier shape (norming PNGs) vs the 2011 source's distinct-shape ShapeRep base

- **Status:** Proposed (2026-06-10)
- **Phase:** 5 (labeller + `parse_code` naming-scheme inverse)
- **Branch:** `raven-builder`

## Context

A Matzen `Structure` code names its relations by letter (`A` shape, `B` shading,
`C` orientation, `D` size, `E` number) and direction by digit. Some codes name a
shape relation (`A1`, `A1B2C4`, …); many do not — the **supplemental-led** codes
(`C1`, `D2`, `E5`, `C1D2E3`, `B1`, …). A supplemental relation provides no base
surface features of its own (it only rewrites features a base already placed), and
`SGMLayerGenerator.generateLayer` always creates a base structure feature first.
So `parse_code` injects an **implicit `ShapeRepetition` base** for any
supplemental-led code, giving the supplemental something to act on (see the module
note in `src/raven_matrix/label.py`).

The question this ADR settles: **what carrier does that implicit base draw?**

- The 2011 shipped Java source
  (`reference/sgmt-source/.../structure/base/BaseSGMStructureFeatureGenerator.java`,
  `createBasicBaseSurfaceFeatures`) sets `uniqueShapes=true` on every path, so a
  ShapeRepetition base is **always three distinct shapes**. The port replicates
  this faithfully on its golden-tested unconstrained generator.
- The 2008 published norming stimuli (the QA ground truth — the PNGs the paper
  normed) instead show a **single constant carrier shape** for supplemental-led
  codes: one figure, with only the named supplemental varying across the grid.

Verified by inspecting the 1-Layer norming PNGs:

- `1 Layer Stim/C1_1.png` — ONE shape, orientation rotating (Rotation only).
- `1 Layer Stim/C2_1.png` — ONE shape, orientation rotating along the other axis.
- `1 Layer Stim/D1_1.png` — ONE shape, scaling (Size only).
- `1 Layer Stim/E1_1.png` — ONE shape, repeating outward (Number only).

By contrast the shape-relation PNGs (`A1_1.png`, `A1B2C4_1.png`, …) show three
distinct carrier shapes, matching the 2011 source.

This is a genuine **source-vs-norming divergence**. CLAUDE.md's spec-precedence
rule makes the Matzen et al. (2010) paper and its normed PNGs the fundamental
spec: where the Java source and the norming disagree because of a source choice,
the port follows the norming and records the divergence (code comment + test +
this ADR). The precedent is the fill-`getDescription` collapse and the
divergences table in `docs/architecture/constraints.md`.

If the implicit base drew three distinct shapes, a supplemental-led stimulus would
silently embed a hidden shape relation (a second, unnamed `A`-like axis of
variation), contradicting both the code's stated single relation and the PNG.

## Decision

`parse_code` marks the implicit base injected for supplemental-led codes with a
new `LayerConfig.base_constant_shape = True`. The builder's
`_build_shape_repetition` gains a `constant: bool = False` parameter: when `True`
it draws ONE surface feature and places it (value-equal) at every base location,
so the ShapeRepetition base is a single constant carrier shape.

The change is scoped to that one path:

- `base_constant_shape` defaults `False`, so the **unconstrained generator, the
  golden fixtures, and every explicit-base config** keep the faithful three
  distinct shapes (`uniqueShapes=true` behaviour untouched).
- An **explicit base** (`A…`, an active shape relation) and logic bases
  (`X`/`Y`/`Z`, which never use ShapeRepetition) stay at `False`.
- Only `parse_code`'s implicit base for supplemental-led codes flips it to `True`.

The acceptance bar remains **data/logic equivalence, not pixel parity**: the
divergence concerns how many distinct carrier shapes the base introduces, which is
structural, not cosmetic.

## Consequences

- Supplemental-led codes now build matrices whose only varying axis is the named
  supplemental, matching the norming PNGs. `build_from_code("C1"/"D1"/"E1")` yields
  exactly one distinct shape across the grid (`tests/test_constant_carrier.py`).
- Explicit shape-relation codes are unchanged: `A1` and `A1C2` keep three distinct
  shapes, and `A1C2` still round-trips through `label()`
  (`tests/test_constant_carrier.py`, regression guards; the existing
  `tests/test_parse_code.py` round-trip family stays green).
- The labeller is unaffected: a constant-carrier ShapeRepetition still emits the
  `A`-letter, so the documented round-trip modeling gap for supplemental-led codes
  (a code with no base letter does not relabel to itself) is unchanged.
- RNG alignment: the constant path draws ONE surface feature where the distinct
  path could draw several (it redraws on a repeated shape). This only affects the
  supplemental-led `parse_code` path, whose absolute draw sequence was never
  pinned to an oracle (seeds unpublished); determinism for a fixed seed is
  preserved.
- This divergence should be back-filled into the
  `docs/architecture/constraints.md` spec-precedence divergences table alongside
  Grey10/40, `loc-vertical-parent-wrap`, etc., once accepted (Status: Proposed).
