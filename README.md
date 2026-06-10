# raven-matrix

A Python port of the **Sandia Generated Matrix Tool (SGMT)** that generates
Raven-style progressive-matrix puzzles with normed difficulty.

Upstream: [sandialabs/Matrices](https://github.com/sandialabs/Matrices)
(SGMT v1.0, OSTI `code-54699`, DOI `10.11578/dc.20210416.34`, BSD-3-Clause,
© 2010 Sandia Corporation). The original software is Java; this is a
from-scratch Python reimplementation. Upstream is vendored read-only at
`upstream/Matrices/` (git submodule).

Reference: Matzen et al. (2010), "Recreating Raven's: Software for
systematically generating large numbers of Raven-like matrix problems with
normed properties," *Behavior Research Methods*.

## What works now

- **Generator core** — composes matrices from a Matzen Structure code (e.g.
  `A1B2C4`) or from explicit relation choices: base relations (shape repetition,
  logical OR/AND/XOR), repetition directions (1-5), and supplemental relations
  (rotation, scaling, fill change/repetition, numerosity), in one or two layers.
- **typer CLI** — `raven-matrix build` (from a code or explicit flags) and
  `raven-matrix oracle` (look a code up in the committed norming oracle and
  report its round-trip status).
- **marimo reactive app** — a live control panel with full `SGMBuilderFrame`
  option parity plus a "build from code" mode, an in-app option reference, and
  SVG save buttons (problem / answers / both, with optional header fields).
- **Rendering** — SVG is the canonical output; PNG is available by rasterising
  the SVG (the optional `raster` extra).

The replication bar is **data/logic equivalence, not pixel reproduction**: the
port reproduces the upstream relations, directions, layers, and correct-answer
position, checked against the committed norming oracle.

## Prerequisites

You need [uv](https://docs.astral.sh/uv/) and git — nothing else. uv installs a
suitable Python and every dependency for you; you do not set up a virtualenv or
install Python yourself.

## Get the code

```
git clone https://github.com/DH-Oz/raven-matrix.git
cd raven-matrix
```

## Install

```
uv sync --extra ui --extra cli --extra raster
```

`uv` fetches a suitable Python automatically (the package floor is 3.12; the
dev pin is 3.14). Pick only the extras you need: `ui` for the app, `cli` for the
command line, `raster` for PNG output. The first `uv run …` below also syncs on
demand, so you can skip this step and go straight to running.

The git submodule is **not needed to run** — the norming oracle is committed as a
CSV. `git submodule update --init` is only required to regenerate that data or to
run the full upstream-derived test suite.

## Run

The reactive app:

```
uv run --extra ui marimo edit app.py
```

The CLI:

```
uv run raven-matrix build --code A1B2C4 --seed 0
uv run raven-matrix oracle --code A1
```

`build` writes SVG to stdout (or `--out PATH`); explicit flags
(`--relation`, `--direction`, `--supplemental TYPE:DIR`, `--layers`,
`--position`, `--seed`) are an alternative to `--code`. `--png` emits a PNG
instead of SVG and needs the `raster` extra (`uv sync --extra raster`, or run
under `uv run --extra raster ...`).

## Regenerate the oracle CSV

```
uv run python tools/extract_oracle.py
```

This rebuilds the committed norming oracle from the upstream spreadsheet, so it
needs the submodule (`git submodule update --init`).

## Hosting

Online hosting (PyPI publication plus an in-browser WebAssembly build of the app)
is a later, optional phase. Everything above runs locally without it.

## Licence

BSD-3-Clause, with Sandia attribution, matching upstream.
