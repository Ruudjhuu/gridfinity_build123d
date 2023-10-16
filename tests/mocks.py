from typing import Union, Any, List
from dataclasses import dataclass
from build123d import Box, RotationLike, Align, Mode, BasePartObject


@dataclass
class BoxAsMock:
    def __init__(self, length: float, width: float, height: float) -> None:
        self.length = length
        self.width = width
        self.height = height
        self.created_objects: List[BasePartObject] = []

    def create(  # pylint: disable=unused-argument
        self,
        *args: Any,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
        **kwargs: Any
    ) -> BasePartObject:
        obj = Box(self.length, self.width, self.height, rotation, align, mode)
        self.created_objects.append(obj)
        return obj
