from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from build123d import Align, BasePartObject, Box, Mode, RotationLike


@dataclass
class BoxAsMock:
    def __init__(
        self,
        length: float,
        width: float,
        height: float,
        rotation: RotationLike = None,
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = None,
    ) -> None:
        self.length = length
        self.width = width
        self.height = height
        self.rotation = rotation
        self.align = align
        self.mode = mode

        self.created_objects: list[BasePartObject] = []

    def create(
        self,
        *args: Any,  # noqa: ANN401,ARG002
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
        **kwargs: Any,  # noqa: ANN401,ARG002
    ) -> BasePartObject:
        self.rotation = rotation if not self.rotation else self.rotation
        self.align = align if not self.align else self.align
        self.mode = mode if not self.mode else self.mode

        obj = Box(
            self.length,
            self.width,
            self.height,
            self.rotation,
            self.align,
            self.mode,
        )
        self.created_objects.append(obj)
        return obj
