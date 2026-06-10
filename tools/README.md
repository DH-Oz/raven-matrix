# Developer tools

Small scripts that support development and QA. None are part of the shipped
package; they are run on demand.

## `render_preview.py` — visual QA for the renderer

Renders sample matrices to PNG (and SVG) so a human can *look* at the renderer's
output — the project's automated tests assert SVG structure, never appearance, so
visual regressions (a wrong fill, an invisible answer choice, a mis-rotated shape)
only show up by eye. This harness is where the Phase-6 "Visual correctness" UAT
lives until the Phase-7 app provides the user-facing path.

```bash
uv run --all-extras python tools/render_preview.py          # gallery + build previews
uv run --all-extras python tools/render_preview.py gallery  # hand-built coverage only
uv run --all-extras python tools/render_preview.py build --seed 7
```

Output lands in `previews/` (gitignored). The `gallery` mode is a deterministic
hand-built sweep of all 7 shapes and 5 fills; the `build` mode renders real
`build()` output (so it doubles as an end-to-end pipeline check). Requires the
`raster` extra for PNG output (`--all-extras` installs it).

## `extract_upstream.sh` — re-derive the read-only source mirror

Re-extracts the vendored Sandia source/test into `reference/sgmt-source/` from the
sealed provenance zip. See the top-level `CLAUDE.md` (upstream source map) for when
and why. The committed mirror is the thing to read; this only regenerates it.

## Common commands (no task runner yet)

```bash
uv sync --all-extras          # environment incl. the raster backend
uv run pytest                 # full suite
uv run ty check .             # types
uv run ruff check .           # lint
```
