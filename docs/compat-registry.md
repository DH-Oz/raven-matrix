# Compat registry

Known divergences between the faithful-to-code port and the faithful-to-design
port, each gated by a field of `CompatFlags` (`src/raven_matrix/compat.py`).

This table is **self-enforcing**: `tests/test_compat_registry.py` asserts that
every `CompatFlags` field has exactly one row here (matched by the flag name in
the first column), and that no row names a flag absent from `CompatFlags`. Add a
flag → add its row, or the build fails.

**Default polarity:** most flags default *faithful-to-code* (reproduce what the
Java actually does, since the oracle was generated with it). The exception is
`relocate_correct_answer`, which defaults *faithful-to-design* because the design
makes the correct-answer position an explicit `build()` input, so honouring the
configured position wins by default.

| Flag | Divergence | Default | Source |
| --- | --- | --- | --- |
| line_shape_enabled | Upstream comments the Line shape out of generation, so Line never appears and the shape draw is `nextInt(6)`. `False` reproduces that (faithful-to-code); `True` re-enables Line (shape draw widens to `nextInt(7)`). | `False` (faithful-to-code) | `SGMSurfaceFeatureGenerator.java:164` (live `nextInt(6)`), `:197-201` (commented-out Line case) |
| relocate_correct_answer | Upstream relocates the correct-answer position on blank-pad and draws a conditional `nextInt(positionInAnswerChoices)`. `False` honours the configured position and skips that block (faithful-to-design, one fewer draw for relocating configs); `True` replicates the upstream relocation. | `False` (faithful-to-design) | `SGMMatrix.java:531-548` (relocation block; draw at l.538) |
