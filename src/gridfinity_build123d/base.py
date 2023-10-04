from typing import Union, Optional

from build123d import *  # pylint: disable=wildcard-import, unused-wildcard-import

from .constants import gridfinity_standard


class Base(BasePartObject):
    _size = 42
    _radius = 7.5
    _platform_height = 1
    _profile_offset = 0.25

    def __init__(
        self,
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
