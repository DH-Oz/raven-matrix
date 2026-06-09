"""The committed oracle CSV is the Phase 5 input contract. Pin its shape.

Numbers come from the 2026-06-08 codebase investigation of the norming sheet:
840 data rows, 553 distinct Structure codes, 839 distinct Stimulus Names
(one duplicate, 'A4_1'). Read with stdlib csv only — no xlrd, no upstream/.
"""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ravens_oracle.csv"
COLUMNS = [
    "Number of Relations",
    "Problem Subtype",
    "Structure",
    "Stimulus Name",
    "Correct Answer",
    "% Correct in Norming Study",
]


def _rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_columns_verbatim() -> None:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))
    assert header == COLUMNS


def test_row_count_is_840() -> None:
    assert len(_rows()) == 840


def test_distinct_structure_codes() -> None:
    rows = _rows()
    assert len({r["Structure"] for r in rows}) == 553


def test_stimulus_names_have_one_duplicate() -> None:
    names = [r["Stimulus Name"] for r in _rows()]
    assert len(set(names)) == 839
    dupes = {n for n in names if names.count(n) > 1}
    assert dupes == {"A4_1"}


def test_correct_answer_positions_in_1_8() -> None:
    for r in _rows():
        assert 1 <= int(r["Correct Answer"]) <= 8
