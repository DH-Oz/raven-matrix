# raven-matrix

Python 3.14 port of the **Sandia Generated Matrix Tool (SGMT)** — generates
Raven-style progressive-matrix puzzles with normed difficulty.

Upstream: [sandialabs/Matrices](https://github.com/sandialabs/Matrices)
(SGMT v1.0, OSTI `code-54699`, DOI `10.11578/dc.20210416.34`, BSD-3-Clause).
The original software is Java; this is a from-scratch Python reimplementation.
Upstream is vendored read-only at `upstream/Matrices/` (git submodule).

Reference: Matzen et al. (2010), "Recreating Raven's: Software for
systematically generating large numbers of Raven-like matrix problems with
normed properties," *Behavior Research Methods*.

## Status

Project setup. No generator code yet — design pending. See `CLAUDE.md` for
provenance, the upstream source map, the QA target, and open design questions.

## Getting started

```
git submodule update --init
uv sync
```

## Licence

The port will carry BSD-3-Clause with Sandia attribution, matching upstream.
