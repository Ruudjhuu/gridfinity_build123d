"""Gridfinity specific common classes."""
from dataclasses import dataclass


from .constants import gridfinity_standard


@dataclass
class Grid:
    """Represents grid units."""

    X: int  # pylint: disable=invalid-name
    Y: int  # pylint: disable=invalid-name

    @property
    def X_mm(self) -> float:  # pylint: disable=invalid-name
        """X size in mm.

        Returns:
            float: size in mm
        """
        return self.X * gridfinity_standard.grid.size

    @property
    def Y_mm(self) -> float:  # pylint: disable=invalid-name
        """Y size in mm.

        Returns:
            float: size in mm
        """
        return self.Y * gridfinity_standard.grid.size

    @property
    def X_mm_real(self) -> float:  # pylint: disable=invalid-name
        """X size in mm.

        The calculation of the real size takes tolarances in account.

        Returns:
            float: size in mm
        """
        return self.X * gridfinity_standard.grid.size - gridfinity_standard.grid.tollerance

    @property
    def Y_mm_real(self) -> float:  # pylint: disable=invalid-name
        """Y size in mm.

        The calculation of the real size takes tolarances in account.

        Returns:
            float: size in mm
        """
        return self.Y * gridfinity_standard.grid.size - gridfinity_standard.grid.tollerance
