"""Supplemental structure-feature relations, ported from ``structure/supplemental``.

A supplemental relation modifies the surface features a base relation already
placed in a layer. Up to three may stack atop a non-logic base (logic bases
forbid supplementals, bug-catalog ``gen-supplemental-disabled-when-logic-base``).
Each has two hooks (``AbstractSupplementalSGMStructureFeature``):

- ``provide_base_surface_features(base_index, existing)`` — the features for a
  base cell, given what the base relation placed there (``existing``).
- ``transform_surface_features(previous, existing)`` — the features for a derived
  cell, given the parent cell's features (``previous``) and ``existing``.

The five supplementals:

- ``ApplyRotation`` / ``ApplyScaling`` extend the repetition pattern
  (``AbstractRepetitionSGMStructureFeature``): base returns ``existing`` as-is;
  derived clones each existing feature and rewrites one parameter from the
  parent's FIRST feature — rotation ADDITIVELY (``+45``), scale MULTIPLICATIVELY
  (``*0.66``).
- ``ChangeFillPattern`` / ``FillPatternRepetition`` clone existing features and
  rewrite the fill: ChangeFill sets base -> ``cycle[0]`` and derived ->
  ``cycle[(index_of(parent.fill)+1) % len]``; FillRep sets base ->
  ``cycle[idx % len]`` and derived -> the parent's fill.
- ``TranslationalNumerosity`` multiplies ``existing[0]`` into a non-overlapping
  grid: ``initial_numerosity`` copies at base, ``len(previous)+1`` at derived.

Clones are fresh ``SurfaceFeature`` instances (numerosity and the fill/scale/rot
supplementals mutate them for layout), so they are NOT part of the identity-logic
path. The clone copies width/height correctly, fixing the upstream
``surface-clone-drops-size-rect-ellipse`` bug (FIX-TO-PAPER): the Java copy
constructor drops the private width/height for Rectangle/Ellipse, collapsing size
comparisons; the paper treats size as a real attribute, so we carry it through.

Pinned params (SupplementalSGMStructureFeatureGenerator.java):
- rotate amount 45 (l.234-235), scale amount 0.66 (l.213),
- ChangeFill cycle [White,Grey75,Grey40,Grey10,Black] (l.255-259),
- FillRep cycle [White,Black,Grey75] (l.224-226),
- initial numerosity 1-2 (l.243-244, MAX_INITIAL_NUMEROSITY = 2).

Sources (reference/sgmt-source/Source/.../structure/supplemental):
- ``AbstractRepetitionSGMStructureFeature.java`` l.82-142.
- ``ApplyRotationSGMStructureFeature.java`` l.90-98.
- ``ApplyScalingSGMStructureFeature.java`` l.80-87.
- ``ChangeFillPatternSGMStructureFeature.java`` l.62-107.
- ``FillPatternRepetitionSGMStructureFeature.java`` l.87-130.
- ``TranslationalNumerositySGMStructureFeature.java`` l.89-215.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from raven_matrix.model import Fill, MatrixSize, Point, SurfaceFeature
from raven_matrix.transforms.base import LocationTransform
from raven_matrix.transforms.geometric import TopLeftCornerOut

# Initial numerosity is drawn nextInt(2)+1 -> 1 or 2
# (SupplementalSGMStructureFeatureGenerator.java:140,243-244).
MAX_INITIAL_NUMEROSITY = 2


def _clone(feature: SurfaceFeature) -> SurfaceFeature:
    """A fresh copy of every slot, including width/height (FIX-TO-PAPER).

    The Java copy constructor drops the private width/height for Rectangle and
    Ellipse (bug-catalog ``surface-clone-drops-size-rect-ellipse``); we copy them
    so size stays a real, comparable attribute per the paper.
    """
    return SurfaceFeature(
        shape=feature.shape,
        fill=feature.fill,
        scale=feature.scale,
        rotation=feature.rotation,
        position=feature.position,
        width=feature.width,
        height=feature.height,
    )


class SupplementalStructureFeature(ABC):
    """A supplemental relation: owns a ``LocationTransform`` and two hooks."""

    def __init__(self, location_transform: LocationTransform) -> None:
        self.location_transform = location_transform

    @abstractmethod
    def provide_base_surface_features(
        self, base_index: int, existing: list[SurfaceFeature]
    ) -> list[SurfaceFeature]: ...

    @abstractmethod
    def transform_surface_features(
        self,
        surface_features_at_previous_location: list[SurfaceFeature],
        existing: list[SurfaceFeature],
    ) -> list[SurfaceFeature]: ...


class _AbstractRepetition(SupplementalStructureFeature):
    """Repeat one parameter from the parent's first feature onto each clone.

    Port of ``AbstractRepetitionSGMStructureFeature`` (l.82-142). Base cells pass
    ``existing`` through unchanged (l.82-87). Derived cells clone each existing
    feature and apply the per-subclass transform, sourcing the repeated parameter
    from ``previous[0]`` only (the cew-2008 "first feature only" workaround,
    bug-catalog ``repetition-firstfeature-only``).
    """

    def provide_base_surface_features(
        self, base_index: int, existing: list[SurfaceFeature]
    ) -> list[SurfaceFeature]:
        return existing

    def transform_surface_features(
        self,
        surface_features_at_previous_location: list[SurfaceFeature],
        existing: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        source = surface_features_at_previous_location[0]
        transformed: list[SurfaceFeature] = []
        for feature in existing:
            clone = _clone(feature)
            self._apply_transform(clone, source)
            transformed.append(clone)
        return transformed

    @abstractmethod
    def _apply_transform(
        self, feature: SurfaceFeature, previous_location_feature: SurfaceFeature
    ) -> None:
        """Rewrite the repeated parameter on ``feature`` in place."""


class ApplyRotation(_AbstractRepetition):
    """derived.rotation = rotate_amount + parent.rotation (ADDITIVE).

    Port of ``ApplyRotationSGMStructureFeature.applyTransform`` (l.95-96). The
    generator pins ``rotate_amount = 45``.
    """

    def __init__(
        self, location_transform: LocationTransform, rotate_amount: int
    ) -> None:
        super().__init__(location_transform)
        self._rotate_amount = rotate_amount

    def _apply_transform(
        self, feature: SurfaceFeature, previous_location_feature: SurfaceFeature
    ) -> None:
        feature.rotation = self._rotate_amount + previous_location_feature.rotation


class ApplyScaling(_AbstractRepetition):
    """derived.scale = scale_amount * parent.scale (MULTIPLICATIVE).

    Port of ``ApplyScalingSGMStructureFeature.applyTransform`` (l.85). The
    generator pins ``scale_amount = 0.66``.
    """

    def __init__(
        self, location_transform: LocationTransform, scale_amount: float
    ) -> None:
        super().__init__(location_transform)
        self._scale_amount = scale_amount

    def _apply_transform(
        self, feature: SurfaceFeature, previous_location_feature: SurfaceFeature
    ) -> None:
        feature.scale = self._scale_amount * previous_location_feature.scale


class ChangeFillPattern(SupplementalStructureFeature):
    """Advance the fill one step along the cycle each derived cell.

    Port of ``ChangeFillPatternSGMStructureFeature`` (l.62-107). Base cells all
    take ``cycle[0]`` (l.83); derived cells take
    ``cycle[(index_of(parent.fill)+1) % len]`` (l.102-105). Both clone the
    existing feature so only the fill changes.
    """

    def __init__(
        self, location_transform: LocationTransform, base_fill_patterns: list[Fill]
    ) -> None:
        super().__init__(location_transform)
        self._base_fill_patterns = base_fill_patterns

    def provide_base_surface_features(
        self, base_index: int, existing: list[SurfaceFeature]
    ) -> list[SurfaceFeature]:
        # All base locations get the first fill in the cycle (l.83).
        first = self._base_fill_patterns[0]
        transformed: list[SurfaceFeature] = []
        for feature in existing:
            clone = _clone(feature)
            clone.fill = first
            transformed.append(clone)
        return transformed

    def transform_surface_features(
        self,
        surface_features_at_previous_location: list[SurfaceFeature],
        existing: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        source = surface_features_at_previous_location[0]
        cycle = self._base_fill_patterns
        # indexOf(parent.fill)+1, wrapped (l.102-104). Fills compare by enum
        # identity (Fill enum members are singletons), mirroring the upstream
        # reference-identity indexOf without the Grey10/Grey40 description bug.
        next_index = (cycle.index(source.fill) + 1) % len(cycle)
        next_fill = cycle[next_index]
        transformed: list[SurfaceFeature] = []
        for feature in existing:
            clone = _clone(feature)
            clone.fill = next_fill
            transformed.append(clone)
        return transformed


class FillPatternRepetition(SupplementalStructureFeature):
    """Cycle base fills by index; derived cells inherit the parent's fill.

    Port of ``FillPatternRepetitionSGMStructureFeature`` (l.87-130). Base cells
    take ``cycle[base_index % len]`` (l.108-110); derived cells take the parent's
    fill (l.128). Both clone the existing feature so only the fill changes.
    """

    def __init__(
        self, location_transform: LocationTransform, base_fill_patterns: list[Fill]
    ) -> None:
        super().__init__(location_transform)
        self._base_fill_patterns = base_fill_patterns

    def provide_base_surface_features(
        self, base_index: int, existing: list[SurfaceFeature]
    ) -> list[SurfaceFeature]:
        cycle = self._base_fill_patterns
        fill = cycle[base_index % len(cycle)]
        transformed: list[SurfaceFeature] = []
        for feature in existing:
            clone = _clone(feature)
            clone.fill = fill
            transformed.append(clone)
        return transformed

    def transform_surface_features(
        self,
        surface_features_at_previous_location: list[SurfaceFeature],
        existing: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        # Derived cells inherit the parent's fill (l.128).
        parent_fill = surface_features_at_previous_location[0].fill
        transformed: list[SurfaceFeature] = []
        for feature in existing:
            clone = _clone(feature)
            clone.fill = parent_fill
            transformed.append(clone)
        return transformed


class TranslationalNumerosity(SupplementalStructureFeature):
    """Multiply ``existing[0]`` into a non-overlapping grid of copies.

    Port of ``TranslationalNumerositySGMStructureFeature`` (l.89-215). Base cells
    get ``initial_numerosity`` copies; derived cells get ``len(previous)+1``
    copies (the deliberate ``<=`` off-by-one, bug-catalog
    ``numerosity-transform-count-offbyone``). The constructor computes the layout:

    - ``num_positions``: ``ceil(sqrt(rows+cols-1))`` for TopLeftCornerOut, else
      ``ceil(sqrt(max(rows,cols) + (initial_numerosity-1)))`` (l.100-117).
    - ``position_step_size = cell_pixel_size / (num_positions + 1)`` (l.119-121).
    - ``scaling = 0.75 / num_positions`` (l.123).

    Base path OVERWRITES each clone's scale to ``scaling`` (l.153); derived path
    MULTIPLIES (``scaling * scale``) (l.201) — the verified base/transform
    asymmetry (bug-catalog ``numerosity-scale-base-vs-transform-mismatch``).
    """

    def __init__(
        self,
        location_transform: LocationTransform,
        cell_pixel_size: int,
        matrix_size: MatrixSize,
        initial_numerosity: int,
    ) -> None:
        super().__init__(location_transform)
        self._cell_pixel_size = cell_pixel_size
        self._initial_numerosity = initial_numerosity

        max_dimension = max(matrix_size.num_rows, matrix_size.num_columns)
        if isinstance(location_transform, TopLeftCornerOut):
            self._num_positions = math.ceil(
                math.sqrt(matrix_size.num_rows + matrix_size.num_columns - 1)
            )
        else:
            self._num_positions = math.ceil(
                math.sqrt(max_dimension + (initial_numerosity - 1))
            )
        self._position_step_size = cell_pixel_size / (self._num_positions + 1)
        self._scaling = 0.75 / self._num_positions

    def _layout(self, features: list[SurfaceFeature], *, multiply_scale: bool) -> None:
        """Place each feature on the non-overlapping grid (l.148-164 / l.196-212)."""
        column_position = 0
        row_position = 0
        for feature in features:
            if multiply_scale:
                feature.scale = self._scaling * feature.scale
            else:
                feature.scale = self._scaling
            feature.position = Point(
                (column_position + 1) * self._position_step_size,
                (row_position + 1) * self._position_step_size,
            )
            column_position += 1
            if column_position >= self._num_positions:
                column_position = 0
                row_position += 1

    def provide_base_surface_features(
        self, base_index: int, existing: list[SurfaceFeature]
    ) -> list[SurfaceFeature]:
        # initial_numerosity clones of existing[0], scale OVERWRITTEN (l.142-164).
        source = existing[0]
        features = [_clone(source) for _ in range(self._initial_numerosity)]
        self._layout(features, multiply_scale=False)
        return features

    def transform_surface_features(
        self,
        surface_features_at_previous_location: list[SurfaceFeature],
        existing: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        # len(previous)+1 clones of existing[0], scale MULTIPLIED (l.179-214).
        source = existing[0]
        count = len(surface_features_at_previous_location) + 1
        features = [_clone(source) for _ in range(count)]
        self._layout(features, multiply_scale=True)
        return features
