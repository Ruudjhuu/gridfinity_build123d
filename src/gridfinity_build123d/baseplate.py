"""baseplate.

Module containg classes to create baseplates.
"""
from typing import Union, List
from math import isclose

from build123d import (
    BasePartObject,
    RotationLike,
    Axis,
    Align,
    Mode,
    BuildPart,
    Box,
    fillet,
    add,
)

from .utils import Utils, StackProfile


class BasePlateBlock(BasePartObject):
    """Single BasePlate block.

    Args:
        rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
        mode (Mode): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        with BuildPart() as part:
            Utils.create_profile_block(StackProfile.ProfileType.PLATE)

        with BuildPart() as final:
            Box(
                42,
                42,
                part.part.bounding_box().size.Z,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            add(part.part, mode=Mode.SUBTRACT)

        super().__init__(final.part, rotation, align, mode)


class BasePlate(BasePartObject):
    """BasePlate.

    Create a baseplate according to grid pattern.

    Args:
        grid (List[List[bool]]): Pattern for creating baseplate
        rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to (0, 0, 0).
        mode (Mode): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        grid: List[List[bool]],
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as part:
            Utils.place_by_grid(BasePlateBlock(mode=Mode.PRIVATE), grid)

            wires = (
                part.edges()
                .filter_by(Axis.Z)
                .filter_by(lambda edge: isclose(edge.length, part.part.bounding_box().size.Z))
            )
            fillet(wires, 4)
        super().__init__(part.part, rotation, align, mode)


class BasePlateEqual(BasePlate):
    """BasePlate.

    Create a baseplate according to grid pattern.

    Args:
        size_x (int): x size of baseplate
        size_y (int): y size of baseplate
        rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to (0, 0, 0).
        mode (Mode): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        size_x: int,
        size_y: int,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        grid: List[List[bool]] = []
        for _ in range(size_y):
            grid.append([True] * size_x)
        super().__init__(grid, rotation, align, mode)
