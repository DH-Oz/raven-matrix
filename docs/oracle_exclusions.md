# Oracle round-trip exclusions

This file is the regression guard for the 840-code round-trip sweep
(`src/raven_matrix/oracle.py`, `tests/test_oracle_sweep.py`, AC2.2).

## What this file is

The sweep runs every distinct `Structure` code through
`parse_code -> build -> label` and checks the produced label equals the input
code, under two — and only two — bounded normalisations
(`oracle.round_trip`):

1. **Logic `7` strip.** `label` emits the LogicTransform digit `7` on a logic
   layer (`X7`/`Y7`/`Z7`); the published logic codes are bare (`X`/`Y`/`Z`).
2. **Supplemental-led carrier `A` strip (ADR-0002).** A supplemental-led code
   (one starting `B`/`C`/`D`/`E`) has no named base, so `parse_code` injects an
   implicit constant ShapeRepetition carrier; the faithful `label` re-emits that
   carrier's `A1` prefix, which the norming code omits. The strip is keyed on the
   **published** code's shape, so it removes only the always-present injected
   carrier and can never absorb a wrong supplemental.

A code that fails for any **other** reason is a **miss**. The test fails on any
miss that is not listed below. Resolving a miss means reading the upstream source,
explaining the cause, and either fixing the port or recording a reasoned exclusion
here — or escalating to the user if it looks like a real bug rather than a modeling
gap. **Do not invent a normalisation to force the sweep green.** Each entry below
must cite a source-read reason; the test also fails on any **stale** exclusion (a
listed code that actually passes), so this list cannot mask a regression.

The sweep is a consistency check on a parser/labeller pair written by the same
author — necessary, not sufficient (DR6). The independent guard is the Task-3
hand-derived table (`tests/test_hand_derived_labels.py`).

## Exclusions

**None — all 553 distinct codes pass (269 exact + 284 carrier-normalised),
covering all 840 oracle rows.**

With the `ab00bc8` `parse_code` digit-swap fix and the `81f4fa2` + ADR-0002
constant-carrier decision, the round-trip decomposes with **zero unexplained
residual**: 269 codes match exactly, and the remaining 284 differ only by the
leading carrier `A1` that the faithful labeller emits and the norming code omits
(stripped by the supplemental-led carrier normalisation above). No code requires an
inspected exclusion.

| Code | Inspected reason (source-read) |
| ---- | ------------------------------ |
| _none_ | — |

Any future miss MUST be added to this table with a real, source-read reason (or
escalated as a suspected bug). The single-cell `_none_` sentinel row above is not a
code (it is not backtick-quoted), so the test's exclusion parser ignores it.
