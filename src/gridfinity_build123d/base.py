"""Generate gridfinity bases."""
from __future__ import annotations
from typing import Union, List
from build123d import (
    RotationLike,
    Align,
    BuildPart,
    BuildSketch,
    BasePartObject,
    Mode,
    GridLocations,
    extrude,
    offset,
    Axis,
    Rectangle,
    add,
    Location,
    fillet,
    Cylinder,
)

from .constants import gridfinity_standard
from .utils import StackProfile, GridfinityObjectCreate, Utils


class Base(BasePartObject):
    """Base.

    Create gridfinity Base object.

    Args:
        grid (Grid): Grid pattern.
        features (BaseBlockFeature): compatible features list.
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        grid: List[List[bool]],
        features: List[BaseBlockFeature] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        if not features:
            features = []

        with BuildPart() as base:
            base_block = BaseBlock(features=features, mode=Mode.PRIVATE)
            Utils.place_by_grid(base_block, grid)

            top_face = base.faces().sort_by(Axis.Z)[-1]
            edges = (
                base.edges()
                .filter_by(Axis.Z)
                .filter_by(
                    lambda edge: any(
                        True for vertex in edge.vertices() if vertex in top_face.vertices()
                    )
                )
            )
            fillet(objects=edges, radius=gridfinity_standard.grid.radius)

        with BuildPart() as cutter:
            with BuildSketch(Location((0, 0, base.part.bounding_box().max.Z))):
                add(base.faces().sort_by(Axis.Z)[-1])
                offset(amount=-gridfinity_standard.grid.tollerance / 2)
            extrude(amount=base.part.bounding_box().size.Z, dir=(0, 0, -1))

        with BuildPart() as part:
            add(base)
            add(cutter, mode=Mode.INTERSECT)

        super().__init__(part.part, rotation, align, mode)


class BaseEqual(Base):
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
        grid = []
        for _ in range(0, grid_y):
            grid += [[True] * grid_x]
        super().__init__(grid, features, rotation, align, mode)


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
            Utils.create_profile_block(
                StackProfile.ProfileType.BIN, gridfinity_standard.stacking_lip.offset
            )

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


class BaseBlockFeature(GridfinityObjectCreate):
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
