"""The hand-derived label table — the PRIMARY correctness anchor (Task 3, AC2.1).

This is the phase's hard correctness gate. Each ``(BuilderConfig, expected_code)``
entry in ``tests.data.hand_derived_labels`` has an ``expected_code`` worked out BY
HAND from three independent reference frames (DR6):

1. the Matzen et al. (2010) naming convention (CLAUDE.md "Naming scheme"),
2. the published ``Structure`` codes in ``data/ravens_oracle.csv`` (ground truth),
3. the published norming PNGs (for the ``B`` shading cases, where the FillRep vs
   ChangeFill palette breaks the aliasing tie).

NONE of the expected codes is read from the Java labeller or from ``label()``'s
output. The provenance of every entry lives in a comment beside it in the data
module, citing a real ``Stimulus Name``/``Structure`` row (or PNG) — except the
single labeller-internal-consistency entry (``A6``), which is flagged as NOT an
externally-grounded anchor because no published stimulus pairs shape-repetition
with corner-out.

If an entry mismatches, the rule (Task 3) is: investigate BOTH the port and the
hand-derivation; do NOT edit the expected code to match ``label()``. Only change a
value if the convention/CSV/PNG justifies it.

This test passing is the phase's correctness proof.
"""

from __future__ import annotations

import pytest

from raven_matrix.builder import BuilderConfig, build
from raven_matrix.label import label
from tests.data.hand_derived_labels import HAND_DERIVED_LABELS, HandDerivedEntry


@pytest.mark.parametrize(
    "entry",
    HAND_DERIVED_LABELS,
    ids=[entry.label_id for entry in HAND_DERIVED_LABELS],
)
def test_hand_derived_label_matches_port(entry: HandDerivedEntry) -> None:
    """``label(build(config, seed=0))`` equals the hand-derived ``expected_code``.

    ``seed=0`` is fixed (the structure features — hence the label — do not depend
    on the surface-feature RNG, but pinning the seed keeps the build deterministic
    for the record).
    """
    config: BuilderConfig = entry.config
    matrix = build(config, seed=0)
    assert label(matrix) == entry.expected_code


def test_table_has_expected_coverage() -> None:
    """The table covers every Task-3 anchor (guards against silent deletion)."""
    expected_codes = {entry.expected_code for entry in HAND_DERIVED_LABELS}
    # ShapeRep on each published direction + the labeller-internal corner-out.
    assert {"A1", "A2", "A3", "A4", "A6"} <= expected_codes
    # Image-grounded shading: FillRep H/V + both diagonals, and ChangeFill
    # corner-out (B3/B4 grounded in the 3-level palettes of PNG B3_1/B4_1).
    assert {"A1B1", "A1B2", "A1B3", "A1B4", "A1B5"} <= expected_codes
    # The three supplementals (each grounded in a published C*/D*/E* code).
    assert {"A1C2", "A1D4", "A1E5"} <= expected_codes
    # Logic relations, pre-normalisation (the Logic transform emits the '7').
    assert {"X7", "Y7", "Z7"} <= expected_codes


def test_exactly_one_entry_is_not_externally_grounded() -> None:
    """The DR6 contract: exactly one entry (``A6``) is labeller-internal only.

    Every other entry must be anchored to a published stimulus (CSV row / PNG).
    Making the count a hard assertion stops a future entry from silently slipping
    in with ``externally_grounded=False`` and quietly weakening the independent
    reference frame.
    """
    not_grounded = [e for e in HAND_DERIVED_LABELS if not e.externally_grounded]
    assert [e.expected_code for e in not_grounded] == ["A6"]
