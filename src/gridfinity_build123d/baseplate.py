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
    BuildLine,
    BuildPart,
    BuildSketch,
    Line,
    Mode,
    Plane,
    RotationLike,
    add,
    extrude,
    fillet,
    make_face,
    mirror,
)

from gridfinity_build123d.utils import ObjectCreate, StackProfile, Utils

if TYPE_CHECKING:
    from gridfinity_build123d.features import Feature


class BasePlateBlock(ObjectCreate):
    """Single base plate block used to construct a bigger baseplate."""

    def __init__(
        self,
        features: Feature | list[Feature] | None = None,
    ) -> None:
        """Baseplateblock interface.

        Args:
            features (Feature | list[Feature] | None, optional): Baseplate
                features. Defaults to None.
        """
        if not features:
            features = []

        self.features = features if isinstance(features, Iterable) else [features]


class BasePlateBlockFrame(BasePlateBlock):
    """Most simple kind of baseplate, only the bare minimum.

    Args:
        features (BasePlateFeature | list[BasePlateFeature] | None, optional): Baseplate
            features. Defaults to None.
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


class BasePlateBlockFull(BasePlateBlock):
    """Baseplate block with a full bottom."""

    def __init__(
        self,
        bottom_height: float = 6.4,
        features: Feature | list[Feature] | None = None,
    ) -> None:
        """Construct BaseplateBlock.

        Args:
            bottom_height (float): The hieght of the bottom part. Defaults to 6.4.
            features (Feature | list[Feature] | None, optional): Baseplate
                features. Defaults to None.
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
            frame = BasePlateBlockFrame().create_obj(mode=Mode.PRIVATE)
            with BuildSketch():
                bot_face = frame.faces().sort_by(Axis.Z)[0]
                make_face(bot_face.outer_wire())
            extrude(amount=self.bottom_height, dir=(0, 0, -1))

            for feature in self.features:
                feature.apply(part)

            add(frame)

        return BasePartObject(part.part, rotation, align, mode)


class BasePlateBlockSkeleton(BasePlateBlockFull):
    """Placeholder for future skeletonized baseplate."""

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        length = 36.3
        nodge = 9.4
        radius = 4.25
        length_s = length / 2 - nodge
        length_l = length / 2

        with BuildPart() as part:
            super().create_obj()
            with BuildSketch():
                with BuildLine() as line:
                    ln1 = Line((0, length_l), (length_s, length_l))
                    ln2 = Line(ln1 @ 1, (length_s, length_s))
                    ln3 = Line(ln2 @ 1, (length_l, length_s))
                    Line(ln3 @ 1, (length_l, 0))
                    vertex = line.vertices().sort_by_distance((length / 4, length / 4))[0]
                    fillet(vertex, radius)
                    mirror(about=Plane.XZ)
                    mirror(about=Plane.YZ)

                make_face()
            extrude(amount=-self.bottom_height, mode=Mode.SUBTRACT)
        return BasePartObject(part.part, rotation, align, mode)


class BasePlate(BasePartObject):
    """Base plate object constructed from grid definition."""

    def __init__(
        self,
        grid: list[list[bool]],
        baseplate_block: BasePlateBlock | None = None,
        features: Feature | list[Feature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """ConstructBasePlate.

        Create a baseplate according to grid pattern.

        Args:
            grid (list[list[bool]]): Pattern for creating baseplate.
            baseplate_block (BasePlateBlock | None, optional): Type of baseplateblock to construct a
                complete baseplate. Defaults to None.
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            features (Feature | list[Feature]): Features applied to the basePlate. Defaults to None.
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to (0, 0, 0).
            mode (Mode): combination mode. Defaults to Mode.ADD.
        """
        if baseplate_block is None:
            baseplate_block = BasePlateBlockFrame()

        if not features:
            features = []

        self.features = features if isinstance(features, Iterable) else [features]

        with BuildPart() as part:
            Utils.place_by_grid(baseplate_block.create_obj(mode=Mode.PRIVATE), grid)

            z_height = part.part.bounding_box().size.Z

            wires = (
                part.edges()
                .filter_by(Axis.Z)
                .filter_by(lambda edge: isclose(edge.length, z_height))
            )
            fillet(wires, 4)

            for feature in self.features:
                feature.apply(part)

        super().__init__(part.part, rotation, align, mode)


class BasePlateEqual(BasePlate):
    """Rectangular BasePlate."""

    def __init__(
        self,
        size_x: int = 1,
        size_y: int = 1,
        baseplate_block: BasePlateBlock | None = None,
        features: Feature | list[Feature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct recatngular BasePlate.

        Create a baseplate according to grid pattern.

        Args:
            size_x (int, optional): x size of baseplate. Defaults to 1.
            size_y (int, optional): y size of baseplate. Defaults to 1.
            baseplate_block (BasePlateBlock | None, optional): Type of baseplateblock to construct a
                complete baseplate.
            features (Feature | list[Feature]): Features applied to the basePlate. Defaults to None.
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to None.
            mode (Mode): combination mode. Defaults to Mode.ADD.
        """
        if baseplate_block is None:
            baseplate_block = BasePlateBlockFrame()

        grid: list[list[bool]] = [[True] * size_x for _ in range(size_y)]
        super().__init__(grid, baseplate_block, features, rotation, align, mode)
