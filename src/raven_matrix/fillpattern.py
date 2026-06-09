"""Fill-pattern generation, ported from the upstream fillpattern package.

The base catalogue and the supplemental cycles are pinned verbatim against the
Java source so the seeded draw order matches the oracle generator.

Sources (reference/sgmt-source/Source/.../fillpattern and structure/supplemental):
- ``BASE_FILL_CATALOGUE`` / ``generate_fill`` ↔ ``SGMFillPatternGenerator.java``
  lines 60-86: the single-arg ``generateFillPattern(Random)`` draws
  ``nextInt(3)`` and switches case 0 → White (l.74-76), case 1 → Grey75
  (l.77-79), case 2 → Black (l.80-82).
- ``FILL_REP_CYCLE`` ↔ ``SupplementalSGMStructureFeatureGenerator.java`` lines
  222-231: the list handed to ``FillPatternRepetitionSGMStructureFeature`` is
  ``add(White); add(Black); add(Grey75)`` (l.224-226).
- ``CHANGE_FILL_CYCLE`` ↔ ``SupplementalSGMStructureFeatureGenerator.java`` lines
  253-264: the list handed to ``ChangeFillPatternSGMStructureFeature`` is
  ``add(White); add(Grey75); add(Grey40); add(Grey10); add(Black)`` (l.255-259).
"""

from __future__ import annotations

from raven_matrix.model import Fill
from raven_matrix.rng import JavaRandom

# Base catalogue in upstream draw order (SGMFillPatternGenerator.java:74-83).
# The single-arg overload only ever produces these three fills.
BASE_FILL_CATALOGUE: list[Fill] = [Fill.WHITE, Fill.GREY75, Fill.BLACK]

# Supplemental cycles (SupplementalSGMStructureFeatureGenerator.java).
# ChangeFillPattern walks all five shadings (l.255-259).
CHANGE_FILL_CYCLE: list[Fill] = [
    Fill.WHITE,
    Fill.GREY75,
    Fill.GREY40,
    Fill.GREY10,
    Fill.BLACK,
]
# FillPatternRepetition cycles three fills (l.224-226).
FILL_REP_CYCLE: list[Fill] = [Fill.WHITE, Fill.BLACK, Fill.GREY75]


def generate_fill(rng: JavaRandom) -> Fill:
    """Draw a base fill, mirroring ``SGMFillPatternGenerator.generateFillPattern``.

    Ports the single-arg overload (``SGMFillPatternGenerator.java:60-86``): a
    single ``nextInt(3)`` indexes the base catalogue. Consumes exactly one draw.

    Parameters
    ----------
    rng : JavaRandom
        The shared generator stream; advanced by one ``next_int(3)`` draw.

    Returns
    -------
    Fill
        ``BASE_FILL_CATALOGUE[rng.next_int(3)]``.
    """
    return BASE_FILL_CATALOGUE[rng.next_int(3)]
