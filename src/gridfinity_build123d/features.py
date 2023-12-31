"""Generate gridfinity bases."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Protocol

from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    CounterBoreHole,
    CounterSinkHole,
    GridLocations,
    Hole,
    Locations,
    Mode,
    PolarLocations,
    Polyline,
    RotationLike,
    SagittaArc,
    add,
    chamfer,
    extrude,
    fillet,
    make_face,
)

from .constants import gf_bin, gridfinity_standard
from .utils import ObjectCreate


class CallableCreateObj(Protocol):
    """Protocol reasambling a Feature create_obj call."""

    def __call__(
        self,
        rotation: RotationLike = ...,
        align: Align | tuple[Align, Align, Align] = ...,
        mode: Mode = ...,
    ) -> BasePartObject:
        """Create the build123d 3d object.

        Args:
            rotation (RotationLike): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]]): Align min center of max of
                object.
            mode (Mode): Combination mode.
        """
        ...  # pragma: no cover


class FeatureLocation(Enum):
    """Location where a feature should be applied."""

    BOTTOM_CORNERS = auto()
    BOTTOM_MIDDLE = auto()
    TOP_CORNERS = auto()
    TOP_MIDDLE = auto()
    CORNERS = auto()
    UNDEFINED = auto()

    @staticmethod
    def apply(
        context: BuildPart,
        create_obj: CallableCreateObj,
        location: FeatureLocation,
    ) -> None:
        """Apply an object on a location.

        This function depends on a builder context being active.

        Args:
            context (BuildPart): Context to apply feature to.
            create_obj (CallableCreateObj): Callable which creates a BasePartObject
            location (FeatureLocation): Feature Location

        Raises:
            ValueError: Unsuported feature location
        """
        bbox = context.part.bounding_box()
        corner_distance = bbox.size.X - 2 * gridfinity_standard.bottom.hole_from_side
        if location == FeatureLocation.BOTTOM_CORNERS:
            with Locations((0, 0, bbox.min.Z)), GridLocations(
                corner_distance,
                corner_distance,
                2,
                2,
            ):
                create_obj(rotation=(180, 0, 0))
        elif location == FeatureLocation.BOTTOM_MIDDLE:
            with Locations((0, 0, bbox.min.Z)):
                create_obj(rotation=(180, 0, 0))
        elif location == FeatureLocation.TOP_CORNERS:
            with Locations((0, 0, bbox.max.Z)), GridLocations(
                corner_distance,
                corner_distance,
                2,
                2,
            ):
                create_obj()
        elif location == FeatureLocation.TOP_MIDDLE:
            with Locations((0, 0, bbox.max.Z)):
                create_obj()
        elif location == FeatureLocation.CORNERS:
            with GridLocations(corner_distance, corner_distance, 2, 2):
                create_obj()
        elif location == FeatureLocation.UNDEFINED:
            create_obj()
        else:  # pragma: no cover
            msg = f"Unsuported feature location: {location}"
            raise ValueError(msg)


class Feature(ObjectCreate):
    """Feature interface."""

    def __init__(self, feature_location: FeatureLocation) -> None:
        """Construct feature.

        Args:
            feature_location (FeatureLocation): Location of the feature when applied.
        """
        self._feature_location = feature_location

    def apply(self, context: BuildPart) -> None:
        """Apply a feature."""
        FeatureLocation.apply(context, self.create_obj, self._feature_location)


class BaseBlockFeature(Feature):
    """This type is accepted for baseblock features."""

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        raise NotImplementedError  # pragma: no cover


class BasePlateFeature(Feature):
    """This type is accepted for baseplate features."""

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        raise NotImplementedError  # pragma: no cover


class HoleFeature(BaseBlockFeature, BasePlateFeature):
    """Hole Feature."""

    def __init__(
        self,
        radius: float,
        depth: float,
        feature_location: FeatureLocation = FeatureLocation.UNDEFINED,
    ) -> None:
        """Create a Hole baseblock feature.

        Args:
            radius (float): radius
            depth (float): depth
            feature_location (FeatureLocation, optional): Location of feature.
                Defaults to FeatureLocation.UNDEFINED.
        """
        super().__init__(feature_location)
        self.radius = radius
        self.depth = depth

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            Hole(radius=self.radius, depth=self.depth, mode=Mode.ADD)
        return BasePartObject(part.part, rotation, align, mode)


class ScrewHole(HoleFeature):
    """Screw hole feature."""

    def __init__(
        self,
        radius: float = gridfinity_standard.screw.radius,
        depth: float = gridfinity_standard.screw.depth,
        feature_location: FeatureLocation = FeatureLocation.BOTTOM_CORNERS,
    ) -> None:
        """Create a ScrewHole baseblock feature.

        Args:
            radius (float): radius
            depth (float): depth
            feature_location (FeatureLocation, optional): Location of feature.
                Defaults to FeatureLocation.BOTTOM_CORNERS.
        """
        super().__init__(radius, depth, feature_location)


class MagnetHole(HoleFeature):
    """Magnet hole feature."""

    def __init__(
        self,
        radius: float = gridfinity_standard.magnet.radius,
        depth: float = gridfinity_standard.magnet.thickness,
        feature_location: FeatureLocation = FeatureLocation.CORNERS,
    ) -> None:
        """Create a MagnetHole feature.

        Args:
            radius (float): radius
            depth (float): depth
            feature_location (FeatureLocation, optional): Location of feature.
                Defaults to FeatureLocation.CORNERS.
        """
        super().__init__(radius, depth, feature_location)


class ScrewHoleCountersink(ScrewHole):
    """Screw hole countersink feature."""

    def __init__(
        self,
        radius: float = 1.75,
        counter_sink_radius: float = 4.25,
        depth: float = gridfinity_standard.screw.depth,
        counter_sink_angle: float = 82,
        feature_location: FeatureLocation = FeatureLocation.BOTTOM_CORNERS,
    ) -> None:
        """Create a Countersink ScrewHole feature.

        Args:
            radius (float, optional): radius. Defaults to 1.75.
            counter_sink_radius (float, optional): radius of countersink. Default to 4.25.
            depth (float, optional): depth. Defaults to gridfinity_standard.screw.depth.
            counter_sink_angle(float, optional): angle of contoursink in degrees. Defaults to 82.
            feature_location (FeatureLocation, optional): Location of feature.
                Defaults to FeatureLocation.BOTTOM_CORNERS.
        """
        super().__init__(radius, depth, feature_location)
        self.counter_sink_radius = counter_sink_radius
        self.counter_sink_angle = counter_sink_angle

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            CounterSinkHole(
                radius=self.radius,
                counter_sink_radius=self.counter_sink_radius,
                depth=self.depth,
                counter_sink_angle=self.counter_sink_angle,
                mode=Mode.ADD,
            )
        return BasePartObject(part.part, rotation, align, mode)


class ScrewHoleCounterbore(ScrewHole):
    """Screw hole counterbore feature."""

    def __init__(
        self,
        radius: float = gridfinity_standard.screw.radius,
        counter_bore_radius: float = gridfinity_standard.screw.radius * 1.5,
        counter_bore_depth: float = 2,
        depth: float = gridfinity_standard.screw.depth,
        feature_location: FeatureLocation = FeatureLocation.BOTTOM_CORNERS,
    ) -> None:
        """Create a CounterBore ScrewHole feature.

        Args:
            radius (float, optional): radius. Defaults to gridfinity_standard.screw.radius.
            counter_bore_radius (float, optional): counter bore radius. Defaults to
                gridfinity_standard.screw.radius * 1.5.
            counter_bore_depth (float, optional): counter bore depth. Defaults to 2.
            depth (float, optional): depth. Defaults to gridfinity_standard.screw.depth.
            feature_location (FeatureLocation, optional): Location of feature.
                Defaults to FeatureLocation.BOTTOM_CORNERS.
        """
        super().__init__(radius, depth, feature_location)
        self.counter_bore_radius = counter_bore_radius
        self.counter_bore_depth = counter_bore_depth

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            CounterBoreHole(
                radius=self.radius,
                counter_bore_radius=self.counter_bore_radius,
                counter_bore_depth=self.counter_bore_depth,
                depth=self.depth,
                mode=Mode.ADD,
            )
        return BasePartObject(part.part, rotation, align, mode)


class Weighted(BasePlateFeature):
    """Weigthed cutout feature for baseplates."""

    def __init__(
        self,
        feature_location: FeatureLocation = FeatureLocation.BOTTOM_MIDDLE,
    ) -> None:
        """Construct Weighted feature.

        Args:
            feature_location (FeatureLocation, optional): Location of feature.
                Defaults to FeatureLocation.BOTTOM_MIDDLE.
        """
        super().__init__(feature_location)

    def create_obj(  # noqa: D102
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        appendix_width = 8.5
        appendix_length = 4.25
        appendix_height = 2
        size = 21.4
        height = 4
        with BuildSketch() as sketch:
            with BuildLine():
                ln1 = Polyline(
                    (appendix_length, appendix_width / 2),
                    (0, appendix_width / 2),
                    (0, -appendix_width / 2),
                    (appendix_length, -appendix_width / 2),
                )
                SagittaArc(ln1 @ 0, ln1 @ 1, appendix_width / 2)
            make_face()

        with BuildPart() as part:
            Box(size, size, height, align=(Align.CENTER, Align.CENTER, Align.MAX))
            with PolarLocations(size / 2, 4):
                add(sketch)
            extrude(amount=appendix_height, dir=(0, 0, -1))
        return BasePartObject(part.part, rotation, align, mode)


class ContextFeature(ABC):
    """Interface for feature using a builder context."""

    @abstractmethod
    def create(self, context: BuildPart) -> None:
        """Apply the feature to the object in context.

        Args:
            context (BuildPart): Context to apply the feature to.
        """
        raise NotImplementedError  # pragma: no cover


class CompartmentFeature(ContextFeature):
    """Context feature for a Compartment."""


class Label(CompartmentFeature):
    """Label feature for compartments."""

    _max_angle = 90

    def __init__(self, angle: float = gf_bin.label.angle) -> None:
        """Construct label feature.

        Args:
            angle (float, optional): angle of the label. Defaults to gf_bin.label.angle.
        """
        if not 0 <= angle <= self._max_angle:
            msg = "Label angle needs to be between 0 and 90"
            raise ValueError(msg)

        self.angle = angle if angle else 0.0000001

    def create(self, context: BuildPart) -> None:  # noqa: D102
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
            extrude(
                to_extrude=chamfer_face,
                amount=1,
                dir=(0, 0, -1),
                mode=Mode.SUBTRACT,
            )
        except ValueError as exp:
            msg = "Label could not be created, Parent object too small"
            raise ValueError(msg) from exp


class Sweep(CompartmentFeature):
    """Compartment Sweep feature."""

    def __init__(self, radius: float = gf_bin.sweep.radius) -> None:
        """Construct Compartment Sweep feature.

        Args:
            radius (float, optional): Radius of the sweep. Defaults to gf_bin.sweep.radius.
        """
        self.radius = radius

    def create(self, context: BuildPart) -> None:  # noqa: D102
        face_bottom = context.faces().sort_by(Axis.Z)[0]
        edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]
        try:
            fillet(edge_bottom_front, radius=self.radius)
        except ValueError as exp:
            msg = "Sweep could not be created, Parent object too small"
            raise ValueError(msg) from exp
