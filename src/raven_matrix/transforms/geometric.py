"""Geometric location transforms (Horizontal, Vertical, diagonals, corner-out).

Each class is a faithful port of the matching
``gov.sandia.cognition.generator.matrix.locationtransform`` Java class. The
branch structure of ``TopLeftCornerOut.next_location`` mirrors the Java
``createNextLocation`` (tall vs wide-or-square branches) so the value-pinned
JUnit traversal sequences reproduce exactly.
"""

from __future__ import annotations

from raven_matrix.model import Location

from .base import LocationTransform


class TopLeftCornerOut(LocationTransform):
    """Diagonal wavefront moving outward from the top-left corner.

    Port of ``TopLeftCornerOutSGMLocationTransform``. The single base location is
    the top-left corner; ``next_location`` wraps diagonally up-and-right; and
    ``parent_location`` is the plain "cell above, else cell to the left" rule --
    NOT the inverse of ``next_location`` (bug-catalog
    ``loc-tlco-getparent-no-bottomrow-special``: replicate; the JUnit test pins
    the exact parents).
    """

    description = "Top Left Corner Out"

    def _populate_base_locations(self) -> list[Location]:
        # Only one base location - the top left corner.
        return [Location(0, 0)]

    def next_location(self, location: Location) -> Location:
        # To move outward from the top left corner we wrap around diagonally
        # moving up and to the right.
        rows = self.size.num_rows
        cols = self.size.num_columns
        loc_row = location.row
        loc_col = location.column

        if loc_row == rows - 1 and loc_col == cols - 1:
            # In bottom right corner.
            row = 0
            column = 0
        elif rows > cols:
            # More rows than columns.
            if loc_row == 0:
                # Anywhere in first row.
                row = loc_col + 1
                column = 0
            elif loc_col < cols - 1:
                # Not in first row or last column.
                row = loc_row - 1
                column = loc_col + 1
            else:
                # Anywhere in last column except first row.
                row = loc_row + cols
                if row >= rows:
                    row = rows - 1
                    column = loc_col - (rows - loc_row - 2)
                else:
                    column = 0
        else:
            # More columns than rows, or square matrix.
            if loc_row > 0 and loc_col < cols - 1:
                # Not in first row or last column.
                row = loc_row - 1
                column = loc_col + 1
            elif loc_col == cols - 1:
                # Anywhere in last column.
                row = rows - 1
                column = loc_col - (rows - loc_row - 2)
            else:
                # Anywhere in first row except for last column.
                row = loc_col + 1
                if row >= rows:
                    row = rows - 1
                    column = loc_col - (rows - 2)
                else:
                    column = 0

        return Location(row, column)

    def parent_location(self, location: Location) -> Location:
        # If the location is the base location (top left corner), there is no
        # parent.
        if location.row == 0 and location.column == 0:
            raise ValueError(
                "TopLeftCornerOut: the base location (top-left corner) has no "
                "parent location"
            )

        # Parent location is one above the current location, unless there are
        # none above, in which case it is the one to the left.
        if location.row > 0:
            return Location(location.row - 1, location.column)
        return Location(location.row, location.column - 1)
