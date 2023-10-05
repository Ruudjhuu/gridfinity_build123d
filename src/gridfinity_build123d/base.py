"""Generate gridfinity bases."""
from typing import Union
from dataclasses import dataclass

from build123d import (
    RotationLike,
    Align,
    BuildPart,
    BuildSketch,
    BuildLine,
    Locations,
    BasePartObject,
    BaseSketchObject,
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
    Circle,
    Polyline,
    make_face,
)

from .constants import gridfinity_standard


@dataclass
class Grid:
    """Represents grid units."""

    X: int  # pylint: disable=invalid-name
    Y: int  # pylint: disable=invalid-name


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
        grid: Grid,
        magnets: bool = False,
        screwholes: bool = False,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as base:
            with GridLocations(
                gridfinity_standard.grid.size,
                gridfinity_standard.grid.size,
                grid.X,
                grid.Y,
            ):
                BaseBlock(magnets, screwholes)

            bbox = base.part.bounding_box()
            with BuildSketch() as rect:
                RectangleRounded(
                    bbox.size.X - gridfinity_standard.grid.tollerance,
                    bbox.size.Y - gridfinity_standard.grid.tollerance,
                    gridfinity_standard.grid.radius,
                )
            extrude(to_extrude=rect.sketch, amount=bbox.size.Z, mode=Mode.INTERSECT)

        super().__init__(base.part, rotation, align, mode)


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
        magnets: bool = False,
        screwholes: bool = False,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as baseblock:
            # Create stack profile with offset
            with BuildSketch(Plane.XZ) as profile:
                with Locations(
                    (
                        gridfinity_standard.grid.size / 2
                        - gridfinity_standard.stacking_lip.offset,
                        0,
                    )
                ):
                    StackProfile(align=(Align.MAX, Align.MIN))
                    offset(
                        amount=gridfinity_standard.stacking_lip.offset,
                        kind=Kind.INTERSECTION,
                    )

            # Create block
            with BuildSketch() as rect:
                RectangleRounded(
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.radius,
                )
            extrude(to_extrude=rect.face(), amount=profile.sketch.bounding_box().max.Z)

            # sweep profile
            path = baseblock.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)

            # add platform on top
            with BuildSketch(baseblock.faces().sort_by(Axis.Z)[-1]) as rect2:
                Rectangle(gridfinity_standard.grid.size, gridfinity_standard.grid.size)
            extrude(
                to_extrude=rect2.sketch,
                amount=gridfinity_standard.bottom.platform_height,
            )

            # create magnet and screw holes
            if magnets or screwholes:
                bot_plane = baseblock.faces().sort_by(Axis.Z)[0]
                distance = (
                    bot_plane.bounding_box().size.X
                    - 2 * gridfinity_standard.bottom.hole_from_side
                )

                if magnets:
                    with BuildSketch() as magnet_holes:
                        with GridLocations(distance, distance, 2, 2):
                            Circle(gridfinity_standard.magnet.size / 2)
                    extrude(
                        to_extrude=magnet_holes.faces(),
                        amount=gridfinity_standard.magnet.thickness,
                        mode=Mode.SUBTRACT,
                    )
                if screwholes:
                    with BuildSketch() as magnet_holes:
                        with GridLocations(distance, distance, 2, 2):
                            Circle(gridfinity_standard.screw.size / 2)
                    extrude(
                        to_extrude=magnet_holes.faces(),
                        amount=gridfinity_standard.screw.depth,
                        mode=Mode.SUBTRACT,
                    )
        super().__init__(baseblock.part, rotation, align, mode)


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
