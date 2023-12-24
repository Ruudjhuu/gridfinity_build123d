"""baseplate.

Module containg classes to create baseplates.
"""
from __future__ import annotations

from math import isclose
from typing import TYPE_CHECKING, Iterable

from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    BuildSketch,
    Mode,
    RotationLike,
    add,
    extrude,
    fillet,
    make_face,
)

from gridfinity_build123d.utils import ObjectCreate, StackProfile, Utils

if TYPE_CHECKING:
    from gridfinity_build123d.features import BasePlateFeature


class BasePlateBlock(ObjectCreate):
    """Single base plate block used to construct a bigger baseplate."""

    def __init__(
        self,
        features: BasePlateFeature | list[BasePlateFeature] | None = None,
    ) -> None:
        """Baseplateblock interface.

        Args:
            features (Union[BasePlateFeature, List[BasePlateFeature]], optional): Baseplate features.
                Defaults to None.
            something (int): an random integer
        """
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
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Overwrites BasePlateBlock.create_obj."""
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
                feature.apply(part)

        return BasePartObject(part.part, rotation, align, mode)


class BasePlateBlockSkeleton(BasePlateBlock):
    """Placeholder for future skeletonized baseplate."""

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        raise NotImplementedError  # pragma: no cover


class BasePlateBlockFull(BasePlateBlock):
    """Baseplate block with a full bottom."""

    def __init__(
        self,
        bottom_height: float = 6.4,
        features: BasePlateFeature | list[BasePlateFeature] | None = None,
    ) -> None:
        """Construct BaseplateBlock.

        Args:
            bottom_height (float): The hieght of the bottom part. Defaults to 6.4
            features (Union[BasePlateFeature, List[BasePlateFeature]], optional): Baseplate features.
                Defaults to None.
        """
        super().__init__(features)
        self.bottom_height = bottom_height

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        with BuildPart() as part:
            BasePlateBlockFrame().create_obj()
            with BuildSketch():
                bot_face = part.faces().sort_by(Axis.Z)[0]
                make_face(bot_face.outer_wire())
            extrude(amount=self.bottom_height, dir=(0, 0, -1))

            for feature in self.features:
                feature.apply(part)

        return BasePartObject(part.part, rotation, align, mode)


class BasePlate(BasePartObject):
    """Base plate object constructed from grid definition."""

    def __init__(
        self,
        grid: list[list[bool]],
        baseplate_block: BasePlateBlock | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """ConstructBasePlate.

        Create a baseplate according to grid pattern.

        Args:
            grid (list[list[bool]]): Pattern for creating baseplate
            baseplate_block (BasePlateBlock): Type of baseplateblock to construct a complete
                baseplate.
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to (0, 0, 0).
            mode (Mode): combination mode. Defaults to Mode.ADD.
        """
        if baseplate_block is None:
            baseplate_block = BasePlateBlockFrame()

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
    """Rectangular BasePlate."""

    def __init__(
        self,
        size_x: int,
        size_y: int,
        baseplate_block: BasePlateBlock | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct recatngular BasePlate.

        Create a baseplate according to grid pattern.

        Args:
            size_x (int): x size of baseplate
            size_y (int): y size of baseplate
            baseplate_block (BasePlateBlock): Type of baseplateblock to construct a complete
                baseplate.
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to None.
            mode (Mode): combination mode. Defaults to Mode.ADD.
        """
        if baseplate_block is None:
            baseplate_block = BasePlateBlockFrame()

        grid: list[list[bool]] = [[True] * size_x for _ in range(size_y)]
        super().__init__(grid, baseplate_block, rotation, align, mode)
