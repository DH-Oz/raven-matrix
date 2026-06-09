"""Base structure-feature relations, ported from ``structure/base``.

A base relation decides what surface features each *base* cell of a layer holds
and how a derived cell's features follow from its parent's. There are two kinds:

- ``ShapeRepetition`` (``ShapeRepetitionSGMStructureFeature.java``): a fixed list
  of per-base-location feature lists, cycled by ``base_index % len``; derived
  cells inherit the parent's features unchanged.
- the logic operations ``LogicalAND`` / ``LogicalOR`` / ``LogicalXOR``
  (``Logical*SGMStructureFeature.java`` over
  ``AbstractLogicOperationSGMStructureFeature.java``): a non-traversing special
  case. Their ``LocationTransform`` is the partial ``LogicLocationTransform``,
  which seeds the top-left 2x2 block but refuses ``next``/``parent``. The builder
  derives each remaining cell from TWO prior cells via ``combine_surface_features``.

DR7 — identity in logic. The logic set operations use Python identity membership
(``in``/``is`` over ``SurfaceFeature``, whose ``==`` is identity) and SHARE
feature instances, so the upstream ``List.contains`` reference-identity semantics
are preserved (bug-catalog ``core-logicop-contains-identity`` /
``base-logic-identity-works-only-by-sharing``: the Java logic ops are correct
only because the same instances propagate uncloned). A value-equal-but-distinct
instance is therefore treated as ABSENT.

Sources (reference/sgmt-source/Source/.../structure/base):
- ``ShapeRepetitionSGMStructureFeature.java`` l.94-105.
- ``AbstractLogicOperationSGMStructureFeature.java`` l.62-188 (base-location
  assignment ctor + single-arg throw).
- ``LogicalANDSGMStructureFeature.java`` l.66-84,
  ``LogicalORSGMStructureFeature.java`` l.74-97,
  ``LogicalXORSGMStructureFeature.java`` l.65-91.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from raven_matrix.model import SurfaceFeature
from raven_matrix.rng import JavaRandom
from raven_matrix.transforms.base import LocationTransform
from raven_matrix.transforms.logic import LogicLocationTransform


class BaseStructureFeature(ABC):
    """A base relation: it owns a ``LocationTransform`` and seeds/derives cells.

    ``provide_base_surface_features(base_index)`` returns the feature list for the
    transform's base location at ``base_index``. ``transform_surface_features``
    derives a non-base cell's features from its parent's (the single prior cell).
    Logic operations are the exception: they override traversal (see
    ``LogicOperation``).
    """

    def __init__(self, location_transform: LocationTransform) -> None:
        self.location_transform = location_transform

    @abstractmethod
    def provide_base_surface_features(
        self, base_index: int
    ) -> list[SurfaceFeature]: ...

    @abstractmethod
    def transform_surface_features(
        self, surface_features_at_previous_location: list[SurfaceFeature]
    ) -> list[SurfaceFeature]: ...


class ShapeRepetition(BaseStructureFeature):
    """Repeat a per-base-location feature list, cycling by ``base_index % len``.

    Port of ``ShapeRepetitionSGMStructureFeature``. ``base_surface_features`` is a
    list of feature lists, one per base location of the transform;
    ``provide_base_surface_features`` returns
    ``base_surface_features[base_index % len]`` (l.94-99). Derived cells inherit
    the parent's features unchanged (l.101-105).
    """

    def __init__(
        self,
        location_transform: LocationTransform,
        base_surface_features: list[list[SurfaceFeature]],
    ) -> None:
        super().__init__(location_transform)
        self._base_surface_features = base_surface_features

    def provide_base_surface_features(self, base_index: int) -> list[SurfaceFeature]:
        # baseSurfaceFeatures.get(idx % size) (ShapeRepetition...java:97-98).
        size = len(self._base_surface_features)
        return self._base_surface_features[base_index % size]

    def transform_surface_features(
        self, surface_features_at_previous_location: list[SurfaceFeature]
    ) -> list[SurfaceFeature]:
        # return surfaceFeaturesAtPreviousLocation (l.104).
        return surface_features_at_previous_location


class LogicOperation(BaseStructureFeature):
    """Abstract logic relation over two prior cells (AND/OR/XOR).

    Port of ``AbstractLogicOperationSGMStructureFeature``. The constructor runs
    the stochastic base-location assignment (l.62-156): each base location is
    given a subset of the base feature instances, looping until every feature is
    used and every base location is populated. The features are SHARED (the same
    instances passed in), so the logic set operations can compare by identity.

    The single-arg ``transform_surface_features`` is the throwing special case
    (l.167-175); the real derivation is ``combine_surface_features`` over two
    prior cells, implemented per subclass.
    """

    def __init__(
        self,
        location_transform: LogicLocationTransform,
        base_surface_features: list[SurfaceFeature],
        rng: JavaRandom,
    ) -> None:
        super().__init__(location_transform)
        self._base_surface_features = base_surface_features
        self._assignments = self._assign_base_locations(
            location_transform, base_surface_features, rng
        )

    @staticmethod
    def _assign_base_locations(
        location_transform: LogicLocationTransform,
        base_surface_features: list[SurfaceFeature],
        rng: JavaRandom,
    ) -> dict[int, list[SurfaceFeature]]:
        """Port the assignment loop (AbstractLogicOperation ctor l.72-155).

        Draws are unconditional and preserve the upstream RNG stream: per base
        location, ``next_int(n+1)`` picks how many features to add, then each add
        draws ``next_int(n)`` to choose one. The loop repeats whole passes until
        every feature is used at least once and every base location is populated.

        Divergence (bug-catalog ``base-logic-dedup-typemismatch``, FIX-TO-PAPER):
        upstream guards a repeat-add with ``list.contains(featureIndex)`` on a
        feature list (an int-vs-feature type mismatch that is always false), so a
        location could collect the same feature twice and corrupt the set into a
        multiset. The fix checks feature membership, not the integer index. The
        guard gates only the *add*, never a draw, so the RNG stream is unchanged.
        """
        num_features = len(base_surface_features)
        num_locations = len(location_transform.base_locations())
        assignments: dict[int, list[SurfaceFeature]] = {}
        assigned_feature_ids: set[int] = set()
        populated_locations: set[int] = set()

        done = False
        while not done:
            for location_index in range(num_locations):
                # nextInt(numBaseFeatures + 1): allowed to add zero (l.89).
                count = rng.next_int(num_features + 1)
                for _ in range(count):
                    # nextInt(numBaseFeatures): pick a feature (l.93).
                    feature_index = rng.next_int(num_features)
                    feature = base_surface_features[feature_index]
                    bucket = assignments.get(location_index)
                    if bucket is None:
                        # First feature for this location: unconditional (l.122-129).
                        assignments[location_index] = [feature]
                        populated_locations.add(location_index)
                        assigned_feature_ids.add(id(feature))
                    elif not _contains_by_value(bucket, feature):
                        # FIX-TO-PAPER membership guard (see docstring).
                        bucket.append(feature)
                        populated_locations.add(location_index)
                        assigned_feature_ids.add(id(feature))
            # Stop once every feature is used and every location populated (l.150-154).
            if (
                len(assigned_feature_ids) >= num_features
                and len(populated_locations) >= num_locations
            ):
                done = True
        return assignments

    def provide_base_surface_features(self, base_index: int) -> list[SurfaceFeature]:
        # Return the assigned (shared) instances for this base location (l.159-165).
        return self._assignments[base_index]

    def transform_surface_features(
        self, surface_features_at_previous_location: list[SurfaceFeature]
    ) -> list[SurfaceFeature]:
        # The single-arg transform is the throwing special case (l.167-175).
        raise NotImplementedError(
            "logic operation structure features perform their transform over "
            "two previous locations; use combine_surface_features"
        )

    @abstractmethod
    def combine_surface_features(
        self,
        cell_one: list[SurfaceFeature],
        cell_two: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        """Derive features from two prior cells (the two-arg variant, l.177-179)."""


def _contains_by_value(
    features: list[SurfaceFeature], item: SurfaceFeature
) -> bool:
    """Value membership for the assignment dedup (bug-catalog FIX-TO-PAPER)."""
    return any(f.value_equals(item) for f in features)


def _contains_by_identity(
    features: list[SurfaceFeature], item: SurfaceFeature
) -> bool:
    """Identity membership for the logic set ops (DR7).

    Mirrors Java ``List.contains`` dispatching through ``Object.equals``
    (reference identity), faithful only because instances are shared uncloned.
    """
    return any(f is item for f in features)


class LogicalAND(LogicOperation):
    """AND: features of cell-one also (by identity) in cell-two.

    Port of ``LogicalANDSGMStructureFeature.transformSurfaceFeatures`` (l.66-84).
    """

    def combine_surface_features(
        self,
        cell_one: list[SurfaceFeature],
        cell_two: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        return [f for f in cell_one if _contains_by_identity(cell_two, f)]


class LogicalOR(LogicOperation):
    """OR: cell-one features, then cell-two features not already present.

    Port of ``LogicalORSGMStructureFeature.transformSurfaceFeatures`` (l.74-97).
    Membership is by identity, so a cell-two feature is appended only if no
    cell-one feature is the same instance.
    """

    def combine_surface_features(
        self,
        cell_one: list[SurfaceFeature],
        cell_two: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        result = list(cell_one)
        for feature in cell_two:
            if not _contains_by_identity(result, feature):
                result.append(feature)
        return result


class LogicalXOR(LogicOperation):
    """XOR: features in exactly one of the two cells (by identity).

    Port of ``LogicalXORSGMStructureFeature.transformSurfaceFeatures`` (l.65-91):
    cell-one features absent from cell-two, then cell-two features absent from
    cell-one.
    """

    def combine_surface_features(
        self,
        cell_one: list[SurfaceFeature],
        cell_two: list[SurfaceFeature],
    ) -> list[SurfaceFeature]:
        result = [f for f in cell_one if not _contains_by_identity(cell_two, f)]
        result.extend(f for f in cell_two if not _contains_by_identity(cell_one, f))
        return result
