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

### Known data anomalies

Discovered during Phase 1 (oracle extraction + the Java build spike, 2026-06-09):

| Anomaly | Detail | Handling |
|---------|--------|----------|
| `A4_1` join-key collision | `data/ravens_oracle.csv` has two rows named `A4_1`, both `Structure = A4` and both 0.75 % correct, but `Correct Answer` 2 vs 1. CLAUDE.md oracle #1 joins `Stimulus Name → Correct Answer`, so this name is 1:2 ambiguous. | The Phase-5 structural oracle keys on `Structure` (so it survives), but `A4_1` is a candidate for the Phase-5 documented exclusion list / needs a tiebreaker. |
| Upstream difficulty classifier unavailable | `SerializedMatrixSGMDifficultyClassifier.xml`, loaded by the upstream `SGMMatrixSetGeneratorTest`, is absent everywhere in the source distribution (exhaustive `find`). The upstream test cannot run as-shipped and the 37-feature predictor cannot be deserialized. | Reinforces v1's deferral of difficulty + `SGMMatrixSetGenerator`; the hand-derived label table (DR6) stays the primary correctness anchor. |

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
| 2026-06-09 | Known data anomalies | Added the `A4_1` join-key collision and the absent upstream classifier-XML findings | Discovered during Phase 1 (oracle extraction + Java spike) |
