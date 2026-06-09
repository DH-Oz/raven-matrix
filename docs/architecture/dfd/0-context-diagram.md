# Context Diagram (Level 0)

> System boundary: raven-builder (SGMT Python port, v1)

> **Status note:** Phase 1 has landed. The Matzen-oracle and upstream-fixture
> citations below now point at committed artifacts; the builder/labeller/renderer/UI
> citations stay prospective (they point at the design plan
> `docs/design-plans/2026-06-08-raven-builder.md`) until those phases land.

## Diagram

```mermaid
flowchart LR
    Researcher[Researcher]
    Oracle[(Matzen norming oracle\n840 codes / %correct)]
    Upstream[Upstream SGMT Java\nread-only reference]
    Browser[Browser / WASM host]

    P0((0.0\nraven-builder))

    Researcher -->|"BuilderConfig / Structure code / seed"| P0
    P0 -->|"Matrix SVG + 8 answers, Structure code"| Researcher
    Oracle -->|"840 Structure codes (CSV)"| P0
    P0 -->|"N/840 consistency report"| Researcher
    Upstream -.->|"reference behaviour + (best-effort) golden fixtures"| P0
    P0 -->|"static WASM bundle (marimo app)"| Browser
    Browser -->|"in-browser config/seed (stretch)"| P0
```

## External Entities

| Entity | Description | Inputs to System | Outputs from System |
|--------|-------------|-----------------|---------------------|
| Researcher | The human reproducing/constructing matrix stimuli, via the Python API, the typer CLI, or the marimo app | `BuilderConfig` or `Structure` code + seed | Matrix SVG + 8 answer choices, the `Structure` code, an `N/840` oracle report (`docs/design-plans/2026-06-08-raven-builder.md`, pending-commit) |
| Matzen norming oracle | The committed `data/ravens_oracle.csv` extracted from the published xls (840 stimuli) | 840 `Structure` codes + `%correct` | Consumed by the structural-oracle harness (`data/ravens_oracle.csv`, 840 rows, commit `f0edc54`; note the `A4_1` 1:2 join-key anomaly — see `../constraints.md`) |
| Upstream SGMT Java | The read-only Java the port is derived from; also the source of best-effort golden fixtures (Phase-1 spike) | Reference behaviour; optional captured fixtures | — (dev-time only) (golden fixtures committed at `tests/golden/*.json` + `tools/golden/`, see `docs/spikes/golden-fixtures.md`; upstream `SGMMatrixSetGeneratorTest` cannot run as-shipped — its `SerializedMatrixSGMDifficultyClassifier.xml` is absent) |
| Browser / WASM host | Pyodide-in-browser hosting the marimo app (concluding phase) | The exported static bundle + the `raven-matrix` PyPI wheel | An interactive in-browser UI (`docs/design-plans/2026-06-08-raven-builder.md`, pending-commit) |

## System Boundary

**In scope:** the explicit matrix *builder* (option parity with `SGMBuilderFrame`),
`java.util.Random` port, structure features + location transforms, labeller +
parser + structural oracle, SVG rendering, compat toggles, the typer CLI, the
marimo app, and its WASM export.

**Out of scope (deferred):** the difficulty classifier, the random batch
`SGMMatrixSetGenerator`, and the normative oracle (a later release, own
`difficulty` dependency group). Exact pixels / distractor sets / JVM-byte-
identical RNG (need unpublished seeds). The Phase-1 spike confirmed the
upstream difficulty classifier's serialized form is not shipped, so this
deferral is also a hard external constraint, not only a scoping choice.

## Cross-References

- **Parent:** None (top-level diagram)
- **Children:** none yet (decompose subsystems — builder, labeller/oracle,
  renderer, UI — when code lands)
- **Related issues:** None
- **Related commits:** Phase 1 — scaffold `78c36fb`, oracle CSV `f0edc54`, CI `e9b0a6d`, golden fixtures `245fcad`/`4e066c2`.
