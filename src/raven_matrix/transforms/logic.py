"""The Logic location transform: a non-traversing special case.

Port of ``LogicSGMLocationTransform``. Logic-operation structure features
(AND/OR/XOR) do not use a location transform to walk the grid; instead they
seed the 2x2 top-left block, and the layer builder derives the rest. Calling
``next_location`` or ``parent_location`` is therefore unsupported (upstream
throws ``UnsupportedOperationException``; the port raises
``NotImplementedError``). The grid must be at least 3x3.
"""

from __future__ import annotations

from raven_matrix.model import Location

from .base import LocationTransform


class LogicLocationTransform(LocationTransform):
    """Seeds the top-left 2x2 block; refuses to traverse.

    Consumer contract (Phase 4 ``build()`` and any traversal caller): this is a
    PARTIAL ``LocationTransform``. ``base_locations()`` is valid, but
    ``next_location`` / ``parent_location`` raise ``NotImplementedError``. A
    caller must detect a logic-operation structure feature and consume the 2x2
    seed directly; it must never drive this transform through the generic
    next/parent traversal loop. Note ``make_location_transform`` never returns
    this class (Logic is selected by the structure layer, not a direction
    digit), so a caller only encounters it deliberately.
    """

    description = "Logic"

    def _validate(self) -> None:
        if self.size.num_rows < 3 or self.size.num_columns < 3:
            raise ValueError(
                "LogicLocationTransform requires a matrix of at least 3x3; "
                f"got {self.size.num_rows}x{self.size.num_columns}"
            )

    def _populate_base_locations(self) -> list[Location]:
        # The top-left four cells define the starting point for a logic
        # operation structure feature.
        return [Location(0, 0), Location(0, 1), Location(1, 0), Location(1, 1)]

    def next_location(self, location: Location) -> Location:
        raise NotImplementedError(
            "Logic operation structure features are a special case that does "
            "not use the location transform to determine the next location"
        )

    def parent_location(self, location: Location) -> Location:
        raise NotImplementedError(
            "Logic operation structure features are a special case that does "
            "not use the location transform to determine the prior location"
        )
