from __future__ import annotations

from build123d import (
    Align,
    BasePartObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Mode,
    Part,
    RotationLike,
    Solid,
    Polyline,
    make_face,
    PolarLocations,
    extrude,
    mirror,
    Plane,
    chamfer,
    Axis,
    Line,
)


class GridfinityRefinedConnector(BasePartObject):
    def __init__(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        middle_width = 5.8 / 2
        middle_height = 6.5 / 2
        thickness = 2.8
        chamfer_value = 0.4

        with BuildPart() as part:
            with BuildSketch() as sketch:
                with BuildLine():
                    l1 = Line((middle_width, 0), (middle_width, middle_height))
                    l2 = Line(l1 @ 1, ((l1 @ 1).X + 3.9, (l1 @ 1).Y + 2.92))
                    l3 = Line(l2 @ 1, ((l2 @ 1).X, (l2 @ 1).Y + 2.53))
                    Line(l3 @ 1, (0, (l3 @ 1).Y))

                    mirror(about=Plane.XZ)
                    mirror(about=Plane.YZ)

                make_face()
            extrude(sketch.sketch, thickness)
            faces = [face.edges() for face in part.faces().filter_by(Axis.Z)]
            chamfer(faces, chamfer_value)
        super().__init__(part.part, rotation, align, mode)
