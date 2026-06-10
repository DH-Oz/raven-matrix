"""The 840-code round-trip sweep: a transparent pass map, inspect every miss.

# pattern: Functional Core

What this module IS. ``round_trip(code)`` runs one published ``Structure`` code
through the full ``parse_code -> build -> label`` path and reports whether the
produced label equals the code, under two -- and ONLY two -- bounded
normalisations. ``build_pass_map(rows)`` runs the sweep over the distinct codes of
the oracle CSV and returns a per-code result map. The CLI ``oracle`` command
(Phase 7) reuses ``build_pass_map``.

Honest bound (DR6 -- necessary, not sufficient). The sweep is a CONSISTENCY check
on a ``parse_code``/``label`` pair written by the same author. A real bug can hide
as a mutually-compensating parse+label error (the parser builds the wrong thing,
the labeller mislabels it back to the input), so a green sweep does NOT prove the
labeller faithful. The independent guard is the Task-3 hand-derived table
(``tests/test_hand_derived_labels.py``), whose expected codes are read from the
published Matzen codes/PNGs, not from this port. This sweep's job is the weaker but
real one: account for EVERY one of the 553 distinct codes -- each either passes or
is an inspected, reasoned entry in ``docs/oracle_exclusions.md``. No silent gaps.

The two permitted normalisations (no others -- a code that fails for any other
reason is a MISS to inspect, never a normalisation to invent):

1. Logic ``7`` strip. ``label`` emits the LogicTransform digit ``7`` on a logic
   layer (``X7``/``Y7``/``Z7``), but the published logic codes are bare (``X`` /
   ``Y`` / ``Z``). Strip a single trailing ``7`` from each ``_``-separated layer
   segment of the produced label. (AC2.3.)

2. Supplemental-led carrier ``A`` strip (ADR-0002). A supplemental relation places
   no base surface features of its own, and ``SGMLayerGenerator.generateLayer``
   always creates a base first, so ``parse_code`` injects an implicit constant
   ShapeRepetition carrier for a supplemental-led code (one starting B/C/D/E). The
   faithful ``label`` then emits that carrier's ``A1`` prefix, which the norming
   code omits (it names only the supplemental). When -- and ONLY when -- the
   PUBLISHED segment is supplemental-led, strip a single leading ``A<digit>`` from
   the produced segment. Keying on the PUBLISHED code's shape (not the produced
   output) means this can only ever remove the always-present injected carrier; it
   can never absorb a wrong supplemental, because the supplemental letters/digits
   that follow are still compared verbatim.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from raven_matrix.builder import build
from raven_matrix.label import label, parse_code

_BASE_LETTERS = frozenset({"A", "X", "Y", "Z"})


@dataclass(frozen=True, slots=True)
class RoundTripResult:
    """One code's round-trip outcome.

    Attributes
    ----------
    code:
        The published ``Structure`` code that was fed in.
    produced:
        The label ``parse_code -> build -> label`` produced, AFTER the logic-``7``
        strip but BEFORE the carrier-``A`` strip (so the raw produced label is
        visible for inspection of any miss).
    passed:
        ``True`` iff the code round-trips under the permitted normalisations.
    mode:
        ``"exact"`` (normalised produced already equals the code),
        ``"carrier-normalised"`` (equal after the supplemental-led carrier strip),
        or ``"fail"`` (neither -- a miss to inspect, or a CA1 escalation).
    reason:
        ``None`` on pass; a human-readable delta on fail (a CA1 escalation message,
        or the produced-vs-code mismatch).
    """

    code: str
    produced: str
    passed: bool
    mode: str
    reason: str | None


def _strip_trailing_logic_digit(label_text: str) -> str:
    """Strip a trailing ``7`` from each ``_``-separated layer segment.

    ``X7`` -> ``X``; ``A1_X7`` -> ``A1_X``. Only a trailing ``7`` is removed, and
    only per segment; every other character is untouched.
    """
    return "_".join(
        segment[:-1] if segment.endswith("7") else segment
        for segment in label_text.split("_")
    )


def _strip_supplemental_led_carrier(code: str, produced: str) -> str | None:
    """Strip the injected carrier ``A<digit>`` from supplemental-led segments.

    For each ``_``-separated segment pair, when the PUBLISHED ``code`` segment is
    supplemental-led (its first letter is not a base letter A/X/Y/Z, i.e. it starts
    B/C/D/E) AND the produced segment starts with a leading ``A<digit>``, drop that
    leading ``A<digit>`` from the produced segment. Returns the rejoined produced
    label, or ``None`` if the segment counts differ (then no carrier comparison is
    meaningful and the caller treats it as a fail).

    The strip is gated on the PUBLISHED segment's shape, never the produced output,
    so it removes only the always-present injected carrier and cannot mask a wrong
    supplemental (ADR-0002).
    """
    code_segments = code.split("_")
    produced_segments = produced.split("_")
    if len(code_segments) != len(produced_segments):
        return None
    rebuilt: list[str] = []
    for code_segment, produced_segment in zip(
        code_segments, produced_segments, strict=True
    ):
        supplemental_led = bool(code_segment) and code_segment[0] not in _BASE_LETTERS
        has_carrier = (
            len(produced_segment) >= 2
            and produced_segment[0] == "A"
            and produced_segment[1].isdigit()
        )
        if supplemental_led and has_carrier:
            rebuilt.append(produced_segment[2:])
        else:
            rebuilt.append(produced_segment)
    return "_".join(rebuilt)


def round_trip(code: str, *, seed: int = 0) -> RoundTripResult:
    """Round-trip one ``Structure`` code: ``parse_code -> build -> label``.

    Computes ``produced = label(build(parse_code(code), seed))`` (then strips the
    logic ``7``), asserts the built matrix is 3x3 (CA1), and decides the outcome:

    1. exact -- the normalised produced label already equals ``code``.
    2. carrier-normalised -- equal after stripping the supplemental-led carrier
       ``A<digit>`` (ADR-0002), applied only where the PUBLISHED segment is
       supplemental-led.
    3. fail -- neither; ``reason`` describes the delta. A non-3x3 built matrix is a
       CA1 escalation: ``mode == "fail"`` with an ``ESCALATE`` reason (the Vertical
       fix-to-paper and other divergences are inert only while square-3x3).
    """
    config = parse_code(code)
    matrix = build(config, seed=seed)

    # CA1: the built matrix must be square 3x3. A non-3x3 matrix would un-mask the
    # Phase 3 Vertical fix-to-paper (and other 3x3-masked upstream divergences), so
    # surface it as a distinct, loud failure -- never a silent exclusion.
    num_rows = len(matrix.cells)
    num_columns = len(matrix.cells[0]) if matrix.cells else 0
    if num_rows != 3 or num_columns != 3:
        return RoundTripResult(
            code=code,
            produced=label(matrix),
            passed=False,
            mode="fail",
            reason=(
                f"non-3x3 built matrix ({num_rows}x{num_columns}) -- ESCALATE: the "
                f"Vertical fix-to-paper and other 3x3-masked divergences could now "
                f"produce real oracle mismatches"
            ),
        )

    produced = _strip_trailing_logic_digit(label(matrix))

    if produced == code:
        return RoundTripResult(
            code=code, produced=produced, passed=True, mode="exact", reason=None
        )

    carrier_stripped = _strip_supplemental_led_carrier(code, produced)
    if carrier_stripped == code:
        return RoundTripResult(
            code=code,
            produced=produced,
            passed=True,
            mode="carrier-normalised",
            reason=None,
        )

    return RoundTripResult(
        code=code,
        produced=produced,
        passed=False,
        mode="fail",
        reason=f"produced {produced!r} != code {code!r} (carrier-strip did not match)",
    )


def code_row_counts(rows: Sequence[Mapping[str, str]]) -> dict[str, int]:
    """How many oracle rows share each distinct ``Structure`` code.

    Lets a caller weight per-code pass/fail by stimulus coverage (the 840 rows map
    onto 553 distinct codes), e.g. to report row coverage out of 840.
    """
    return dict(Counter(row["Structure"] for row in rows))


def build_pass_map(
    rows: Sequence[Mapping[str, str]], *, seed: int = 0
) -> dict[str, RoundTripResult]:
    """Round-trip every DISTINCT ``Structure`` code across ``rows``.

    Returns ``{code: RoundTripResult}`` over the distinct codes (one entry per
    distinct code, not per row). Pair with ``code_row_counts`` to recover the
    840-row coverage. ``rows`` is the ``csv.DictReader`` output of the oracle CSV.
    """
    distinct_codes = sorted({row["Structure"] for row in rows})
    return {code: round_trip(code, seed=seed) for code in distinct_codes}
