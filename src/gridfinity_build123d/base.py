from build123d import *

from typing import Union, Optional


class Base(BasePartObject):
    _size = 41.5
    _radius = 7.5
    _platform_height = 1

    def __init__(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as part:
            with BuildSketch(Plane.XZ) as profile:
                with Locations((self._size/2,0)):
                    StackProfile(align=(Align.MAX, Align.MIN))

            with BuildSketch() as rectangle:
                RectangleRounded(self._size, self._size, self._radius)

            extrude_height = profile.sketch.bounding_box().size.Z + self._platform_height
            extrude(to_extrude=rectangle.face(),amount=extrude_height)
            
            path = part.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)
        super().__init__(part.part, rotation, align, mode)


class StackProfile(BaseSketchObject):
    _height_1 = 0.7
    _height_2 = 1.8
    _height_3 = 1.9

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
                    (self._height_1, self._height_1),
                    (self._height_1, self._height_1 + self._height_2),
                    (
                        self._height_1 + self._height_2,
                        self._height_1 + self._height_2 + self._height_3,
                    ),
                    (self._height_1 + self._height_2, 0),
                    close=True,
                )
            make_face()
        super().__init__(sketch.face(), rotation, align, mode)
