"""The 840-code round-trip sweep: a transparent pass map, inspect every miss.

What this gate IS (and is NOT). The sweep runs every distinct ``Structure`` code
through ``parse_code -> build -> label`` and checks the produced label equals the
input code (after two bounded normalisations: the logic ``7`` strip and the single
supplemental-led carrier ``A`` strip; see ``oracle.round_trip``). It is a
CONSISTENCY check on a parser/labeller pair written by the same author, so it is
**necessary, not sufficient** (DR6): a real bug can hide as a mutually-compensating
parse+label error. The independent guard is the Task-3 hand-derived table
(``tests/test_hand_derived_labels.py``), grounded in the published codes/PNGs.

The discipline this test enforces: every distinct code must PASS, or be listed in
``docs/oracle_exclusions.md`` with an inspected reason. A miss not in that list
fails the test (the "inspect every miss" gate); a stale exclusion (a listed code
that actually passes) also fails (no exclusion may mask a regression). With the
``ab00bc8``/``81f4fa2`` fixes + ADR-0002, the exclusion list is EMPTY: all 553
distinct codes pass (269 exact + 284 carrier-normalised).
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import pytest

from raven_matrix.oracle import build_pass_map, round_trip

_ROOT = Path(__file__).resolve().parent.parent
_CSV_PATH = _ROOT / "data" / "ravens_oracle.csv"
_EXCLUSIONS_PATH = _ROOT / "docs" / "oracle_exclusions.md"


def _rows() -> list[dict[str, str]]:
    with _CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _distinct_codes() -> list[str]:
    return sorted({r["Structure"] for r in _rows()})


def _excluded_codes() -> set[str]:
    """Codes listed in ``docs/oracle_exclusions.md`` as inspected non-passes.

    The exclusions file is a markdown table whose first column is a backtick-quoted
    code (e.g. ``| `C3` | ApplyRotation provides no base feature ... |``). Parse the
    leading backtick-quoted token of each table row. A row whose first cell is the
    literal "none" (the empty-list sentinel) is skipped.
    """
    if not _EXCLUSIONS_PATH.exists():
        return set()
    codes: set[str] = set()
    row_pattern = re.compile(r"^\|\s*`([^`]+)`\s*\|")
    for line in _EXCLUSIONS_PATH.read_text(encoding="utf-8").splitlines():
        match = row_pattern.match(line)
        if match:
            codes.add(match.group(1))
    return codes


_DISTINCT_CODES = _distinct_codes()


@pytest.mark.parametrize("code", _DISTINCT_CODES)
def test_every_distinct_code_passes_or_is_excluded(code: str) -> None:
    """Each distinct code passes (exact or carrier-normalised) OR is excluded.

    A failing code absent from ``oracle_exclusions.md`` fails here -- the
    inspect-every-miss gate. With the current fixes no code is excluded, so this is
    equivalently "every distinct code passes".
    """
    result = round_trip(code)
    if result.passed:
        return
    excluded = _excluded_codes()
    assert code in excluded, (
        f"code {code!r} failed the round-trip ({result.mode}: {result.reason}) and "
        f"is NOT in docs/oracle_exclusions.md. Inspect it: read the source, then "
        f"either fix the port or record a reasoned exclusion (or escalate a "
        f"suspected bug). Do not invent a normalisation to force green."
    )


def test_no_stale_exclusions() -> None:
    """Every code listed in ``oracle_exclusions.md`` must actually fail.

    A stale exclusion (a listed code that now passes) would mask a future
    regression in that code, so the presence of any passing excluded code fails.
    """
    excluded = _excluded_codes()
    stale = [code for code in excluded if round_trip(code).passed]
    assert not stale, (
        f"stale exclusions in docs/oracle_exclusions.md (these codes pass and must "
        f"be removed from the list): {stale}"
    )


def test_ca1_every_built_matrix_is_3x3() -> None:
    """CA1: every built matrix is 3x3 -- fail loudly otherwise (ESCALATE).

    The Phase 3 Vertical fix-to-paper (and other 3x3-masked upstream divergences)
    are inert ONLY while every matrix is square 3x3. A non-3x3 built matrix is an
    escalation, not a silent exclusion: the round_trip mode is "fail" with an
    ESCALATE reason, and this test surfaces it.
    """
    offenders = [
        (code, result.reason)
        for code in _DISTINCT_CODES
        if (result := round_trip(code)).mode == "fail"
        and result.reason is not None
        and "ESCALATE" in result.reason
    ]
    assert not offenders, (
        f"non-3x3 built matrices -- ESCALATE (the Vertical fix-to-paper and other "
        f"3x3-masked divergences could now produce real mismatches): {offenders}"
    )


@pytest.mark.parametrize("code", ["X", "Y", "Z"])
def test_ac2_3_logic_codes_pass_via_trailing_7_strip(code: str) -> None:
    """AC2.3: the three logic codes pass via the trailing-``7`` normalisation.

    ``label`` emits ``X7``/``Y7``/``Z7`` (the LogicTransform digit); the round-trip
    strips the trailing ``7`` so the bare published logic code matches exactly. The
    stored ``produced`` is the post-strip form, so it equals the bare ``code`` and
    the mode is "exact" -- demonstrating the ``7`` strip (not the carrier strip)
    closed the gap.
    """
    result = round_trip(code)
    assert result.passed
    assert result.mode == "exact"
    assert result.produced == code


def test_full_sweep_pass_counts_553_and_840() -> None:
    """N_pass / 553 distinct and row coverage / 840 -- expect 553/553 and 840/840.

    Emits the headline numbers to test output and asserts full coverage. ``-rP``
    (or ``-s``) surfaces the print; the asserts are the real gate.
    """
    rows = _rows()
    pass_map = build_pass_map(rows)

    assert len(pass_map) == 553, f"expected 553 distinct codes, got {len(pass_map)}"

    n_pass = sum(1 for result in pass_map.values() if result.passed)
    exact = sum(1 for result in pass_map.values() if result.mode == "exact")
    carrier = sum(
        1 for result in pass_map.values() if result.mode == "carrier-normalised"
    )

    row_counts = Counter(r["Structure"] for r in rows)
    row_coverage = sum(
        row_counts[code] for code, result in pass_map.items() if result.passed
    )

    print(
        f"\noracle sweep: {n_pass}/553 distinct codes pass "
        f"({exact} exact + {carrier} carrier-normalised); "
        f"row coverage {row_coverage}/840"
    )

    assert n_pass == 553
    assert exact == 269
    assert carrier == 284
    assert row_coverage == 840
