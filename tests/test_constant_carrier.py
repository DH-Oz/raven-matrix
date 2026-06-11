"""Constant-carrier fidelity for supplemental-led codes (ADR 0002).

The published Matzen norming PNGs (dated 2008) build a SINGLE constant carrier
shape for any stimulus whose ``Structure`` code does NOT name a shape relation
(the supplemental-led codes: ``C1``, ``D2``, ``E5``, ``C1D2E3``, ``B1`` …). Each
1-Layer PNG (verified by inspecting ``1 Layer Stim/{C1,C2,D1,E1}_1.png``) shows
ONE shape, with only the named supplemental varying across the grid (one ellipse
rotating, one triangle scaling, one tee repeating). By contrast a shape-relation
code (``A1``, ``A1B2C4`` …) shows three distinct carrier shapes.

The 2011 shipped Java source always makes the ShapeRepetition base three distinct
shapes (``BaseSGMStructureFeatureGenerator.createBasicBaseSurfaceFeatures``,
``uniqueShapes=true`` on every path). This is a source-vs-norming divergence
handled per CLAUDE.md's spec-precedence rule: the port's ``parse_code`` implicit
base builds a CONSTANT carrier so the built matrix matches the norming PNGs, while
the golden-tested unconstrained generator keeps the distinct-shape behaviour.

These tests derive "distinct shapes" the way the other suites read a built matrix:
collect ``feature.shape`` across every cell's ``surface_features``.
"""

from __future__ import annotations

import pytest

from raven_matrix.builder import build_from_code
from raven_matrix.label import label
from raven_matrix.model import Matrix


def _distinct_shape_count(matrix: Matrix) -> int:
    """Count distinct ``feature.shape`` values across the whole 3x3 grid."""
    shapes = set()
    for row in matrix.cells:
        for cell in row:
            for feature in cell.surface_features:
                shapes.add(feature.shape)
    return len(shapes)


# ---------------------------------------------------------------------------
# Supplemental-led codes -> ONE constant carrier shape (matches norming PNGs).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", ["C1", "D1", "E1"])
def test_supplemental_led_code_has_one_carrier_shape(code: str) -> None:
    # The implicit ShapeRepetition base is a constant carrier: only the named
    # supplemental varies, so the grid holds exactly ONE distinct shape.
    matrix = build_from_code(code, seed=0)
    assert _distinct_shape_count(matrix) == 1


# ---------------------------------------------------------------------------
# Explicit-base codes -> THREE distinct shapes (active shape relation, UNCHANGED).
# ---------------------------------------------------------------------------


def test_explicit_shape_relation_keeps_three_shapes() -> None:
    # A1 is an EXPLICIT shape relation -> three distinct carrier shapes, as the
    # 2011 source and the golden path produce. Must stay GREEN.
    matrix = build_from_code("A1", seed=0)
    assert _distinct_shape_count(matrix) == 3


def test_explicit_base_with_supplemental_keeps_three_shapes() -> None:
    # A1C2: explicit A base (active shape relation) -> three distinct shapes,
    # AND the code still round-trips through label().
    matrix = build_from_code("A1C2", seed=0)
    assert _distinct_shape_count(matrix) == 3
    assert label(matrix) == "A1C2"
