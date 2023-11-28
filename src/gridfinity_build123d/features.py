"""Generate gridfinity bases."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union
from build123d import (
    RotationLike,
    Align,
    BuildPart,
    BasePartObject,
    Mode,
    Cylinder,
    extrude,
    fillet,
    Axis,
    chamfer,
)

from .constants import gridfinity_standard, gf_bin
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


class ContextFeature(ABC):
    """Interface for feature using a builder context."""

    @abstractmethod
    def create(self) -> None:
        """Apply the feature to the object in context."""
        raise NotImplementedError  # pragma: no cover


class CompartmentFeature(ContextFeature):
    """Context feature for a Comopartment."""


class Label(CompartmentFeature):
    """Compartment Label feature.

    Args:
        angle (float, optional): angle of the label. Defaults to gf_bin.label.angle.
    """

    def __init__(self, angle: float = gf_bin.label.angle) -> None:
        if not (0 <= angle <= 90):
            raise ValueError("Label angle needs to be between 0 and 90")
        self.angle = angle if angle else 0.0000001

    def create(self) -> None:
        context: BuildPart = BuildPart._get_context(  # pylint: disable=protected-access
            "Label.create"
        )
        if context is None:
            raise RuntimeError("Label must have an active builder context")
        if not context._obj:  # pylint: disable=protected-access
            raise ValueError("Context has no object")

        face_top = context.faces().sort_by(Axis.Z)[-1]
        edge_top_back = face_top.edges().sort_by(Axis.Y)[-1]
        try:
            chamfer(
                edge_top_back,
                length=gf_bin.label.width,
                angle=self.angle,
                reference=face_top,
            )
            chamfer_face = context.faces().sort_by(Axis.Z)[-2]
            extrude(to_extrude=chamfer_face, amount=1, dir=(0, 0, -1), mode=Mode.SUBTRACT)
        except ValueError as exp:
            raise ValueError("Label could not be created, Parent object too small") from exp


class Sweep(CompartmentFeature):
    """Compartment Sweep feature.

    Args:
        radius (float, optional): Radius of the sweep. Defaults to gf_bin.sweep.radius.
    """

    def __init__(self, radius: float = gf_bin.sweep.radius) -> None:
        self.radius = radius

    def create(self) -> None:
        context: BuildPart = BuildPart._get_context(  # pylint: disable=protected-access
            "Label.create"
        )
        face_bottom = context.faces().sort_by(Axis.Z)[0]
        edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]
        try:
            fillet(edge_bottom_front, radius=self.radius)
        except ValueError as exp:
            raise ValueError("Sweep could not be created, Parent object too small") from exp
