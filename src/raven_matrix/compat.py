"""Compatibility toggles for known code-vs-design divergences.

Each field flips one place where the faithful-to-code port and the
faithful-to-design port disagree. The defaults are deliberately mixed (see the
note in ``docs/compat-registry.md``): most flags default faithful-to-code, but
``relocate_correct_answer`` defaults faithful-to-design because the design makes
the correct-answer position an explicit input.

The registry-completeness test (``tests/test_compat_registry.py``) asserts that
every field here has exactly one row in ``docs/compat-registry.md``, so a new
flag cannot land without being documented.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompatFlags:
    """Toggles selecting faithful-to-code vs faithful-to-design behaviour.

    Parameters
    ----------
    line_shape_enabled : bool, default False
        The upstream surface generator comments Line out
        (``SGMSurfaceFeatureGenerator.java:197-201``), so the default
        (``False``) is faithful-to-code: Line is never drawn and the shape draw
        is ``next_int(6)``. ``True`` re-enables Line as a sixth-index case and
        widens the shape draw to ``next_int(7)``.
    relocate_correct_answer : bool, default False
        The upstream relocates the correct-answer position on blank-pad
        (``SGMMatrix.java:531-548``). The default (``False``) is
        faithful-to-design: honour the configured position. ``True`` replicates
        the upstream relocation (and the conditional ``next_int`` draw it makes).
    """

    line_shape_enabled: bool = False
    relocate_correct_answer: bool = False


DEFAULT_FLAGS = CompatFlags()
