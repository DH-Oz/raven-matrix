"""Dev-only: extract the Matzen et al. (2010) norming oracle to a committed CSV.

Reads Matzen_et_al_2010_norming_stimuli.xls (sheet 'Stimuli') from the read-only
upstream/ submodule zip and writes data/ravens_oracle.csv with all six columns,
preserving every stimulus row (including the duplicate 'A4_1'). Run once; the CSV
is committed so the runtime/test path needs neither xlrd nor the .xls.

Usage:  uv run python tools/extract_oracle.py
"""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import xlrd

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = REPO_ROOT / "upstream" / "Matrices" / "Matzen_et_al_2010_norming_stim.zip"
XLS_NAME = "Matzen_et_al_2010_norming_stimuli.xls"
SHEET = "Stimuli"
OUT_PATH = REPO_ROOT / "data" / "ravens_oracle.csv"

# The six columns, verbatim, in sheet order. The header row is detected by the
# presence of the join key 'Stimulus Name'; everything above it is the legend.
EXPECTED_HEADER = [
    "Number of Relations",
    "Problem Subtype",
    "Structure",
    "Stimulus Name",
    "Correct Answer",
    "% Correct in Norming Study",
]
HEADER_KEY = "Stimulus Name"


def _load_sheet() -> xlrd.sheet.Sheet:
    with zipfile.ZipFile(ZIP_PATH) as zf:
        data = zf.read(XLS_NAME)
    book = xlrd.open_workbook(file_contents=data)
    return book.sheet_by_name(SHEET)


def _header_row_index(sheet: xlrd.sheet.Sheet) -> int:
    for r in range(sheet.nrows):
        row = [str(c).strip() for c in sheet.row_values(r)]
        if HEADER_KEY in row:
            return r
    raise ValueError(f"header row containing {HEADER_KEY!r} not found")


def extract_rows() -> list[list[str]]:
    sheet = _load_sheet()
    hdr = _header_row_index(sheet)
    header = [str(c).strip() for c in sheet.row_values(hdr)][: len(EXPECTED_HEADER)]
    if header != EXPECTED_HEADER:
        raise ValueError(f"unexpected header: {header!r}")
    rows: list[list[str]] = []
    for r in range(hdr + 1, sheet.nrows):
        values = sheet.row_values(r)
        cells = [
            _fmt(values[c]) if c < len(values) else ""
            for c in range(len(EXPECTED_HEADER))
        ]
        # A data row is one whose Stimulus Name (col index 3) is non-empty.
        if not cells[3].strip():
            continue
        # The sheet repeats the column-header line as interior section separators
        # (one per "… Diagonal or Outward Relation" subtype block; some carry the
        # subtype label in col 0, so they are not byte-identical to the header).
        # Every such repeat puts the literal HEADER_KEY in the join-key column —
        # the same signal _header_row_index uses — and no real stimulus does.
        # Drop them by content, not by a fixed offset.
        if cells[3].strip() == HEADER_KEY:
            continue
        rows.append(cells)
    return rows


def _fmt(v: object) -> str:
    # xlrd yields floats for numeric cells; render integers without a trailing .0.
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def main() -> None:
    rows = extract_rows()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(EXPECTED_HEADER)
    w.writerows(rows)
    OUT_PATH.write_text(buf.getvalue(), encoding="utf-8")
    print(f"wrote {len(rows)} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
