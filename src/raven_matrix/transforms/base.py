"""Location transforms: which cells share a feature, and in what order.

Faithful to ``gov.sandia.cognition.generator.matrix.locationtransform``. The
constructor validates grid constraints and populates base locations, exactly
like the Java ``AbstractSGMLocationTransform``.

Divergence from the Java init order (bug-catalog ``loc-diag-validate-after-super``):
the upstream constructor calls ``super(...)`` -- which populates base locations --
*before* the subclass size validation runs, so an invalid size transiently builds
out-of-range locations before the guard throws. We validate FIRST, then populate,
which yields the same clean raise without the transient bad state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from raven_matrix.model import Location, MatrixSize


class LocationTransform(ABC):
    """A transform over grid locations within a matrix of a fixed size.

    Subclasses declare how features propagate: ``base_locations`` are the seed
    cells, ``next_location`` walks forward along the transform, and
    ``parent_location`` walks back to the cell a feature was derived from.
    """

    description: str

    def __init__(self, size: MatrixSize) -> None:
        self.size = size
        self._validate()  # subclass hook; default no-op (see below)
        self._base_locations = self._populate_base_locations()

    def _validate(self) -> None:
        """Reject invalid sizes. Overridden by constrained transforms."""
        return None

    def base_locations(self) -> list[Location]:
        return list(self._base_locations)

    @abstractmethod
    def _populate_base_locations(self) -> list[Location]: ...

    @abstractmethod
    def next_location(self, location: Location) -> Location: ...

    @abstractmethod
    def parent_location(self, location: Location) -> Location: ...
