# ADR 0001: Renderer draws a uniform base shape size scaled by `feature.scale`

- **Status:** Proposed (2026-06-09)
- **Phase:** 6 (SVG rendering)
- **Branch:** `raven-renderer`

## Context

`SurfaceFeature` (Phase 2 model) carries `shape, fill, scale, rotation, position`
and **no per-feature width or height**. The upstream Java
`SGMSurfaceFeatureGenerator` instead randomises width and height *independently*,
each drawn from `{1/4, 1/2, 3/4} × cellPixelSize`. The port collapsed those two
free parameters into a single `scale` scalar when the model was designed.

The Phase 6 renderer therefore has no size to read from a feature. It must pick a
base extent and let `scale` vary it.

## Decision

`render/svg.py` draws every shape at a fixed base extent
`BASE = cell_pixel_size / 2` (half-extent 64px at the 256px default), centred on
`feature.position`. Per-feature size variation is expressed only through
`feature.scale`, applied — together with `rotation` — by the affine transform
`translate(pos) rotate(deg) scale(s) translate(-pos)`. Paint is fill (RGBA alpha,
White → `fill-opacity="0"`) then a 2px black stroke.

The acceptance bar is **data/logic equivalence, not pixel parity** with Java2D.

## Consequences

- A single `scale` cannot represent the independent width ≠ height stretching the
  Java generator could produce. If any relation turns out to depend on a
  non-uniform aspect ratio, the fix belongs in the **Phase 2 model** (restore a
  size field), not in the renderer.
- The contract **"`build()` sets `feature.scale` so that `BASE · scale` is the
  intended on-screen extent"** is **unverified on this branch** — Phase 4's
  `build()` does not exist here; all Phase 6 tests hand-build matrices. This
  assumption must be checked end-to-end at merge-back (see the merge-back checks).
- Well-formedness tests cannot detect a wrong base size or a wrong `scale`
  semantic: an over- or under-sized shape still parses. Detection is deferred to
  the Phase 7 visual UAT ("Visual correctness, deferred from Phase 6").

## Verify at merge-back (end-to-end, once Phase 4 `build()` is available)

1. **Scale/BASE contract:** render real generator output and confirm features at
   distinct `scale` values render as visibly distinct extents, and that the
   absolute sizes read as sensible Raven shapes (the Phase 7 visual UAT covers
   the human-judgment half).
2. **Multi-feature render order:** confirm cells with stacked features (2- and
   3-layer stimuli) emit in a deterministic, correct paint order (SVG document
   order = painter's model); opaque fills must not silently occlude a feature the
   Java reference would have shown.
3. **Position coordinate space:** the renderer reads `feature.position` as
   absolute pixels and sizes shapes from its own `RasterSettings.cell_pixel_size`
   (default 256). The Phase-1 golden fixtures place features in a 100px cell. So
   `build()` must emit `position` in the same `cell_pixel_size` the renderer is
   configured with, or a normalisation step is required. Confirm the two cell
   sizes agree at integration (positions are absolute pixels, not normalised, so
   a mismatch silently mis-places every feature while still parsing). Surfaced by
   the Phase-6 coherence review (Medium).
4. **Rotation unit (now pinned on the render side):** the renderer emits
   `feature.rotation` directly as the SVG `rotate()` degree argument — the model
   stores **degrees** (mirroring Java `getRotation() % 360`). This was a defect
   (`degrees(feature.rotation)`) found and fixed in the Phase-6 coherence review,
   and is now guarded by the AC5.1 rotation fitness function. The remaining
   cross-phase contract: confirm `build()` stores rotation in **degrees** (the
   `ApplyRotation` supplemental accumulates integer degrees upstream), so the two
   sides agree.
