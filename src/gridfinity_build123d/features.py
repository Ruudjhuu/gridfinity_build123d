"""Generate gridfinity bases."""
from __future__ import annotations
from typing import Union
from build123d import (
    RotationLike,
    Align,
    BuildPart,
    BasePartObject,
    Mode,
    Cylinder,
)

from .constants import gridfinity_standard
from .utils import GridfinityObjectCreate


class BaseBlockFeature(GridfinityObjectCreate):
    """This type is accepted for baseblock features."""


class HoleFeature(BaseBlockFeature):
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


class ScrewHole(HoleFeature):
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


class MagnetHole(HoleFeature):
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
