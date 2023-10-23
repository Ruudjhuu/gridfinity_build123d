"""Gridfinity specific common classes."""
from dataclasses import dataclass

from typing import Union
from build123d import BaseSketchObject, Align, Mode, BuildSketch, BuildLine, Polyline, make_face

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


class StackProfile(BaseSketchObject):
    """StackProfile.

    Create a profile of the gridfinity stacking system. Usualy used in the sweep function.

    Args:
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        rotation: float = 0,
        align: Union[Align, tuple[Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildSketch() as profile:
            with BuildLine():
                Polyline(
                    (0, 0),
                    (
                        gridfinity_standard.stacking_lip.height_1,
                        gridfinity_standard.stacking_lip.height_1,
                    ),
                    (
                        gridfinity_standard.stacking_lip.height_1,
                        gridfinity_standard.stacking_lip.height_1
                        + gridfinity_standard.stacking_lip.height_2,
                    ),
                    (
                        gridfinity_standard.stacking_lip.height_1
                        + gridfinity_standard.stacking_lip.height_3,
                        gridfinity_standard.stacking_lip.height_1
                        + gridfinity_standard.stacking_lip.height_2
                        + gridfinity_standard.stacking_lip.height_3,
                    ),
                    (
                        gridfinity_standard.stacking_lip.height_1
                        + gridfinity_standard.stacking_lip.height_3,
                        0,
                    ),
                    close=True,
                )
            make_face()
        super().__init__(profile.face(), rotation, align, mode)
