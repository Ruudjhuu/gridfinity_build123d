"""baseplate.

Module containg classes to create baseplates.
"""
from typing import Iterable, Union, List
from math import isclose

from build123d import (
    BasePartObject,
    RotationLike,
    Axis,
    Align,
    Mode,
    BuildPart,
    BuildSketch,
    Box,
    fillet,
    add,
    extrude,
    make_face,
)

from .features import BasePlateFeature
from .utils import Utils, StackProfile, ObjectCreate


class BasePlateBlock(ObjectCreate):
    """Base plate block interface.

    Args:
        features (Union[BasePlateFeature, List[BasePlateFeature]], optional): Baseplate features.
            Defaults to None.
    """

    def __init__(self, features: Union[BasePlateFeature, List[BasePlateFeature]] = None) -> None:
        if not features:
            features = []

        self.features = features if isinstance(features, Iterable) else [features]


class BasePlateBlockFrame(BasePlateBlock):
    """Most simple kind of baseplate, only the bare minimum.

    Args:
        features (Union[BasePlateFeature, List[BasePlateFeature]], optional): Baseplate features.
            Defaults to None.
    """

    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        with BuildPart() as block:
            Utils.create_profile_block(StackProfile.ProfileType.PLATE)

        with BuildPart() as part:
            Box(
                42,
                42,
                block.part.bounding_box().size.Z,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            add(block.part, mode=Mode.SUBTRACT)

            for feature in self.features:
                feature.apply()

        return BasePartObject(part.part, rotation, align, mode)


class BasePlateBlockSkeleton(BasePlateBlock):
    """Placeholder for future skeletonized baseplate."""

    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        raise NotImplementedError()  # pragma: no cover


class BasePlateBlockFull(BasePlateBlock):
    """Baseplate block with a full bottom.

    Args:
        features (Union[BasePlateFeature, List[BasePlateFeature]], optional): Baseplate features.
            Defaults to None.
    """

    def __init__(
        self,
        bottom_height: float = 6.4,
        features: Union[BasePlateFeature, List[BasePlateFeature]] = None,
    ) -> None:
        super().__init__(features)
        self.bottom_height = bottom_height

    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        with BuildPart() as part:
            BasePlateBlockFrame().create_obj()
            with BuildSketch():
                bot_face = part.faces().sort_by(Axis.Z)[0]
                make_face(bot_face.outer_wire())
            extrude(amount=self.bottom_height, dir=(0, 0, -1))

            for feature in self.features:
                feature.apply()

        return BasePartObject(part.part, rotation, align, mode)


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
        baseplate_block: BasePlateBlock = BasePlateBlockFrame(),
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as part:
            Utils.place_by_grid(baseplate_block.create_obj(mode=Mode.PRIVATE), grid)

            z_height = part.part.bounding_box().size.Z

            wires = (
                part.edges()
                .filter_by(Axis.Z)
                .filter_by(lambda edge: isclose(edge.length, z_height))
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
        baseplate_block: BasePlateBlock = BasePlateBlockFrame(),
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        grid: List[List[bool]] = []
        for _ in range(size_y):
            grid.append([True] * size_x)
        super().__init__(grid, baseplate_block, rotation, align, mode)
