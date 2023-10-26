"""Generate gridfinity bases."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List
from build123d import (
    RotationLike,
    Align,
    BuildPart,
    BuildSketch,
    Locations,
    BasePartObject,
    Mode,
    GridLocations,
    RectangleRounded,
    extrude,
    Plane,
    offset,
    Kind,
    sweep,
    Axis,
    Rectangle,
    add,
    Location,
    fillet,
    Cylinder,
)

from .constants import gridfinity_standard
from .common import StackProfile


class Base(BasePartObject):
    """Base.

    Create gridfinity Base object.

    Args:
        grid (Grid): Grid object containg units of length
        magnets (bool, optional): True to create holes for magnets. Defaults to False.
        screwholes (bool, optional): True to create holes for screws. Defaults to False.
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        grid_x: int,
        grid_y: int,
        features: List[BaseBlockFeature] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        if not features:
            features = []

        with BuildPart() as base:
            base_block = BaseBlock(features=features, mode=Mode.PRIVATE)
            base_block_bbox = base_block.bounding_box()
            with GridLocations(
                base_block_bbox.size.X,
                base_block_bbox.size.Y,
                grid_x,
                grid_y,
            ):
                add(base_block)

        with BuildPart() as cutter:
            with BuildSketch(Location((0, 0, base.part.bounding_box().max.Z))) as sketch:
                add(base.faces().sort_by(Axis.Z)[-1])
                fillet(objects=sketch.vertices(), radius=gridfinity_standard.grid.radius)
                offset(amount=-gridfinity_standard.grid.tollerance / 2)
            extrude(amount=base.part.bounding_box().size.Z, dir=(0, 0, -1))

        with BuildPart() as part:
            add(base)
            add(cutter, mode=Mode.INTERSECT)

        super().__init__(part.part, rotation, align, mode)


class BaseBlock(BasePartObject):
    """BaseBlock.

    Create a single baseblock with rectangular platform. The rectangular platform makes it
    posible to stack the blocks in x and y direction. After creating an array it is meant to
    cut the platform to size.

    Args:
        magnets (bool, optional): True to create holes for magnets. Defaults to False.
        screwholes (bool, optional): True to create holes for screws. Defaults to False.
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        features: List[BaseBlockFeature] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        if not features:
            features = []

        with BuildPart() as baseblock:
            # Create stack profile with offset
            with BuildSketch(Plane.XZ) as profile:
                with Locations(
                    (
                        gridfinity_standard.grid.size / 2 - gridfinity_standard.stacking_lip.offset,
                        0,
                    )
                ):
                    StackProfile(align=(Align.MAX, Align.MIN))
                    offset(
                        amount=gridfinity_standard.stacking_lip.offset,
                        kind=Kind.INTERSECTION,
                    )

            with BuildSketch() as rect:
                RectangleRounded(
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.radius,
                )
            extrude(to_extrude=rect.face(), amount=profile.sketch.bounding_box().max.Z)

            path = baseblock.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)

            with BuildSketch(baseblock.faces().sort_by(Axis.Z)[-1]) as rect2:
                Rectangle(gridfinity_standard.grid.size, gridfinity_standard.grid.size)
            extrude(
                to_extrude=rect2.sketch,
                amount=gridfinity_standard.bottom.platform_height,
            )

            if features:
                bot_plane = baseblock.faces().sort_by(Axis.Z)[0]
                distance = (
                    bot_plane.bounding_box().size.X - 2 * gridfinity_standard.bottom.hole_from_side
                )

                with GridLocations(distance, distance, 2, 2):
                    for feature in features:
                        feature.create(align=(Align.CENTER, Align.CENTER, Align.MIN))

        super().__init__(baseblock.part, rotation, align, mode)


class _IGridfinityObject(ABC):
    @abstractmethod
    def create(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create the build123d 3d object.

        Args:
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: The build123d 3d object
        """
        raise NotImplementedError


class BaseBlockFeature(_IGridfinityObject):
    """This type is accepted for baseblock features."""


class Hole(BaseBlockFeature):
    """Create a Hole baseblock feature.

    Args:
        radius (float): radius
        depth (float): depth
    """

    def __init__(self, radius: float, depth: float) -> None:
        self.radius = radius
        self.depth = depth

    def create(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            Cylinder(radius=self.radius, height=self.depth)
        return BasePartObject(part.part, rotation=rotation, align=align, mode=mode)


class ScrewHole(Hole):
    """Create a ScrewHole baseblock feature.

    Args:
        radius (float): radius
        depth (float): depth
    """

    def __init__(
        self,
        radius: float = gridfinity_standard.screw.radius,
        depth: float = gridfinity_standard.screw.depth,
    ) -> None:
        super().__init__(radius, depth)


class MagnetHole(Hole):
    """Create a MagnetHole baseblock feature.

    Args:
        radius (float): radius
        depth (float): depth
    """

    def __init__(
        self,
        radius: float = gridfinity_standard.magnet.radius,
        depth: float = gridfinity_standard.magnet.thickness,
    ) -> None:
        super().__init__(radius, depth)
