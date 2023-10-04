from typing import Union, Optional

from build123d import *  # pylint: disable=wildcard-import, unused-wildcard-import

from .constants import gridfinity_standard


class Base(BasePartObject):
    def __init__(
        self,
        magnets: bool = False,
        screwholes: bool = False,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as part:
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

            with BuildSketch() as rectangle:
                RectangleRounded(
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.radius,
                )

            extrude_height = (
                profile.sketch.bounding_box().max.Z
                + gridfinity_standard.bottom.platform_height
            )
            extrude(to_extrude=rectangle.face(), amount=extrude_height)

            path = part.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)

            if magnets or screwholes:
                bot_plane = part.faces().sort_by(Axis.Z)[0]
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
        super().__init__(part.part, rotation, align, mode)


class StackProfile(BaseSketchObject):
    """Creates a profile of the Gridfinity stack."""

    def __init__(
        self,
        rotation: float = 0,
        align: Union[Align, tuple[Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildSketch() as sketch:
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
        super().__init__(sketch.face(), rotation, align, mode)
