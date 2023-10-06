from typing import Union, Any
from dataclasses import dataclass
from build123d import Box, RotationLike, Align, Mode, BasePartObject


@dataclass
class BoxAsMock:
    length: float
    width: float
    height: float
    rotation: RotationLike = (0, 0, 0)
    align: Union[Align, tuple[Align, Align, Align]] = (
        Align.CENTER,
        Align.CENTER,
        Align.CENTER,
    )
    mode: Mode = Mode.ADD

    def create(  # pylint: disable=unused-argument
        self, *args: Any, **kwargs: Any
    ) -> BasePartObject:
        return Box(self.length, self.width, self.height, self.rotation, self.align, self.mode)
