# Quality Constraints

Measurable limits on system behaviour. Each constraint has a metric, a target,
and a verification method. (Bootstrapped from the design plan
`docs/design-plans/2026-06-08-raven-builder.md`.)

## Correctness / Fidelity

| Constraint | Metric | Target | Verification |
|-----------|--------|--------|-------------|
| Equivalence bar | Data/logic equivalence (structure), not pixels | Structure matches; pixels need not | The structural oracle + hand-derived label table (`raven-builder.AC2.*`) |
| Structural consistency | `Structure` codes that round-trip (code→config→matrix→label→code) | All 840 outside the documented exclusion list | The oracle harness over `data/ravens_oracle.csv` (`raven-builder.AC2.2`) |
| Labeller correctness | Hand-derived label table matches paper/published-code rules | 100% of the ~12 cases | The hand-derived table test (`raven-builder.AC2.1`) |
| Location-transform fidelity | TopLeftCornerOut coordinate sequences | Exact match to the JUnit spec, all 8 sizes | The ported pinned test (`raven-builder.AC3.1`) |
| Behaviour faithfulness | "Build what is" at the behaviour level | Outputs match upstream code; bugs preserved behind toggles | The test suite + best-effort Java differential |

## Determinism

| Constraint | Metric | Target | Verification |
|-----------|--------|--------|-------------|
| Seeded determinism | Same config + seed → identical output | Identical across runs (and not dependent on `id()`/address ordering) | `raven-builder.AC4.1`; list-based identity dedup (DR7) |
| RNG fidelity | `JavaRandom` vs `java.util.Random` vectors | Exact match (incl. power-of-two + rejection edges) | `raven-builder.AC4.2` |

## Portability

| Constraint | Metric | Target | Verification |
|-----------|--------|--------|-------------|
| Pure-Python core | Core runtime dependencies | Zero (stdlib only); WASM-loadable | `pyproject.toml` core deps empty; core never imports marimo/typer/raster |
| In-browser run | The marimo app under WASM | Loads + generates in-browser | `raven-builder.AC7.*` (concluding phase; live Pages is stretch) |

## Security

| Constraint | Requirement | Verification |
|-----------|-------------|-------------|
| Upstream immutability | Never edit `upstream/Matrices/` | It is a read-only submodule; the port reads, never writes it |

## Capacity

| Constraint | Metric | Current | Limit | Verification |
|-----------|--------|---------|-------|-------------|
| Oracle set size | Stimuli covered | 840 | — | The committed `data/ravens_oracle.csv` row count |

## Constraint History

| Date | Constraint | Change | Reason |
|------|-----------|--------|--------|
| 2026-06-08 | (all) | Initial bootstrap from the design plan | Greenfield design finalisation |
