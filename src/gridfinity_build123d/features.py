"""Generate gridfinity bases."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, override

from bd_warehouse.thread import Thread  # pyright: ignore[reportMissingTypeStubs]
from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    CounterBoreHole,
    CounterSinkHole,
    Cylinder,
    Hole,
    Line,
    Locations,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Polyline,
    RadiusArc,
    RegularPolygon,
    Rotation,
    RotationLike,
    SagittaArc,
    Transition,
    add,  # pyright: ignore[reportUnknownVariableType]
    chamfer,
    extrude,
    fillet,
    make_face,
    mirror,
    sweep,
)

from .constants import gf_bin, gridfinity_standard
from .utils import ObjectCreate

if TYPE_CHECKING:
    from .feature_locations import FeatureLocation


class Feature(ABC):
    """Feature Interface."""

    @abstractmethod
    def apply(self, context: BuildPart) -> None:
        """Apply a feature to the context.

        Args:
            context (BuildPart): Context part to apply feature to.
        """
        raise NotImplementedError  # pragma: no cover


class ObjectFeature(Feature, ObjectCreate, ABC):
    """Feature created by standalone object.

    Feature which creates standalone object and is dependend on a Feature Location for
    placement.
    """

    def __init__(self, feature_location: FeatureLocation | None) -> None:
        """Construct ObjectFeature.

        Args:
            feature_location (FeatureLocation): Location of the feature when applied.
        """
        self._feature_location: FeatureLocation | None = feature_location

    @override
    def apply(self, context: BuildPart) -> None:
        if self._feature_location:
            context_part = context.part
            if not isinstance(context_part, Part):  # pragma: no cover
                msg = "Context has no part"
                raise ValueError(msg)

            with self._feature_location.apply_to(context_part):
                _ = self.create_obj()
        else:
            _ = self.create_obj()


class ContextFeature(Feature, ABC):
    """Feature created by context builder.

    This feature is created by depending on the active context builder.
    """


class HoleFeature(ObjectFeature):
    """Hole Feature."""

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float,
        depth: float,
    ) -> None:
        """Create a Hole baseblock feature.

        Args:
            radius (float): radius
            depth (float): depth
            feature_location (FeatureLocation): Location of feature.
        """
        super().__init__(feature_location)
        self.radius: float = radius
        self.depth: float = depth

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            _ = Hole(radius=self.radius, depth=self.depth, mode=Mode.ADD)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class PolygonHoleFeature(ObjectFeature):
    """Polygon Hole Feature."""

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float,
        depth: float,
        sides: int,
    ) -> None:
        """Create a Polygon Hole baseblock feature.

        Args:
            radius (float): radius of inscribed circle.
            depth (float): depth
            sides (int): number of sides of polygon
            feature_location (FeatureLocation): Location of feature.
        """
        super().__init__(feature_location)
        self.radius: float = radius
        self.sides: int = sides
        self.depth: float = depth

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            with BuildSketch():
                _ = RegularPolygon(
                    radius=self.radius,
                    side_count=self.sides,
                    major_radius=False,
                    mode=Mode.ADD,
                )
            _ = extrude(amount=self.depth, both=True)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class ScrewHole(HoleFeature):
    """Screw hole feature."""

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float = gridfinity_standard.screw.radius,
        depth: float = gridfinity_standard.screw.depth,
    ) -> None:
        """Create a ScrewHole baseblock feature.

        Args:
            feature_location (FeatureLocation): Location of feature.
            radius (float): radius
            depth (float): depth
        """
        super().__init__(feature_location, radius, depth)


class MagnetHole(HoleFeature):
    """Magnet hole feature."""

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float = gridfinity_standard.magnet.radius,
        depth: float = gridfinity_standard.magnet.thickness,
    ) -> None:
        """Create a MagnetHole feature.

        Args:
            feature_location (FeatureLocation): Location of feature.
            radius (float): radius
            depth (float): depth

        """
        super().__init__(feature_location, radius, depth)


class ScrewHoleCountersink(ScrewHole):
    """Screw hole countersink feature."""

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float = 1.75,
        counter_sink_radius: float = 4.25,
        depth: float = gridfinity_standard.screw.depth,
        counter_sink_angle: float = 82,
    ) -> None:
        """Create a Countersink ScrewHole feature.

        Args:
            feature_location (FeatureLocation): Location of feature.
            radius (float, optional): radius. Defaults to 1.75.
            counter_sink_radius (float, optional): radius of countersink. Default to 4.25.
            depth (float, optional): depth. Defaults to gridfinity_standard.screw.depth.
            counter_sink_angle(float, optional): angle of contoursink in degrees. Defaults to 82.
        """
        super().__init__(feature_location, radius, depth)
        self.counter_sink_radius: float = counter_sink_radius
        self.counter_sink_angle: float = counter_sink_angle

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            _ = CounterSinkHole(
                radius=self.radius,
                counter_sink_radius=self.counter_sink_radius,
                depth=self.depth,
                counter_sink_angle=self.counter_sink_angle,
                mode=Mode.ADD,
            )

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class ScrewHoleCounterbore(ScrewHole):
    """Screw hole counterbore feature."""

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float = gridfinity_standard.screw.radius,
        counter_bore_radius: float = gridfinity_standard.screw.radius * 1.5,
        counter_bore_depth: float = 2,
        depth: float = gridfinity_standard.screw.depth,
    ) -> None:
        """Create a CounterBore ScrewHole feature.

        Args:
            feature_location (FeatureLocation): Location of feature.
            radius (float, optional): radius. Defaults to gridfinity_standard.screw.radius.
            counter_bore_radius (float, optional): counter bore radius. Defaults to
                gridfinity_standard.screw.radius * 1.5.
            counter_bore_depth (float, optional): counter bore depth. Defaults to 2.
            depth (float, optional): depth. Defaults to gridfinity_standard.screw.depth.
        """
        super().__init__(feature_location, radius, depth)
        self.counter_bore_radius: float = counter_bore_radius
        self.counter_bore_depth: float = counter_bore_depth

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildPart() as part:
            _ = CounterBoreHole(
                radius=self.radius,
                counter_bore_radius=self.counter_bore_radius,
                counter_bore_depth=self.counter_bore_depth,
                depth=self.depth,
                mode=Mode.ADD,
            )

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class GridfinityRefinedConnectionCutout(ObjectFeature):
    """Gridfinity refined conecction cutout.

    Cutout shape used to connect two objects with a GridfinityRefinedConnector.
    """

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        middle_width = 6 / 2
        middle_height = 3
        thickness = 3

        with BuildPart() as part:
            with BuildSketch() as sketch:
                with BuildLine():
                    l0 = Line((0, 0), (middle_width, 0))
                    l1 = Line(l0 @ 1, (middle_width, middle_height))
                    l2 = Line(l1 @ 1, ((l1 @ 1).X + 4, (l1 @ 1).Y + 3))
                    l3 = Line(l2 @ 1, ((l2 @ 1).X, (l2 @ 1).Y + 3))
                    _ = Line(l3 @ 1, (0, (l3 @ 1).Y))

                    _ = mirror(about=Plane.YZ)
                _ = make_face()
            _ = extrude(sketch.sketch, -thickness)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class GridfinityRefinedScrewHole(ScrewHoleCountersink):
    """Refined screw hole.

    Gridfinity refined baseplate middle screw hole.
    """

    def __init__(
        self,
        feature_location: FeatureLocation,
        radius: float = 8,
        counter_sink_radius: float = 10.5,
        depth: float = 6,
        counter_sink_angle: float = 90,
    ) -> None:
        """Construct refined screw hole.

        Args:
            feature_location (FeatureLocation): Location of the feature.
            radius (float, optional): Radius of the hole. Defaults to 8.
            counter_sink_radius (float, optional): Radius of countersink. Defaults to 10.5.
            depth (float, optional): Depth of the hole. Defaults to 6.
            counter_sink_angle (float, optional): Angle of countersink. Defaults to 90.
        """
        super().__init__(
            feature_location,
            radius,
            counter_sink_radius,
            depth,
            counter_sink_angle,
        )


class GridfinityRefinedThreadedScrewHole(ScrewHoleCountersink):
    """Gridfinity refined threaded screwhole for bins."""

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        apex_radius = 15.5 / 2
        apex_width = 0.24
        root_radius = 13.8 / 2
        root_width = 1.21
        pitch = root_width + 0.29
        length = 4

        with BuildPart() as part:
            _ = Cylinder(
                root_radius,
                length,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
            _ = Thread(
                apex_radius,
                apex_width,
                root_radius,
                root_width,
                pitch,
                length,
                apex_offset=0,
                end_finishes=("chamfer", "chamfer"),
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class GridfinityRefinedMagnetHolePressfit(ObjectFeature):
    """Refined magnet hole.

    Gridfinity Refined pressfit magnet hole.
    """

    def __init__(
        self,
        feature_location: FeatureLocation | None,
        radius: float = 3.05,
        depth: float = 2.4,
        slit_length: float = 0.1,
        slit_width: float = 10.1,
        slit_depth: float = 2,
        chamfer: float = 0.6,
    ) -> None:
        """Construct Gridfinity Refined pressfit magnet hole.

        Args:
            feature_location (FeatureLocation | None): Location of the hole.
            radius (float, optional): Radius of the hole. Defaults to 3.05.
            depth (float, optional): depth of the hole. Defaults to 2.4.
            slit_length (float, optional): Length of the slit. Defaults to 0.1.
            slit_width (float, optional): Width of the slit. Defaults to 10.1.
            slit_depth (float, optional): Depth of the slit. Defaults to 2.
            chamfer (float, optional): Chamfer. Defaults to 0.6.
        """
        super().__init__(feature_location)
        self._radius: float = radius
        self._depth: float = depth
        self._slit_length: float = slit_length
        self._slit_width: float = slit_width
        self._slit_depth: float = slit_depth
        self._chamfer: float = chamfer

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        with BuildSketch() as profile:
            with BuildLine():
                _ = Polyline((0, 0), (0, -self._chamfer), (self._chamfer, 0), close=True)
            _ = make_face()

        with BuildPart() as part:
            with BuildSketch():
                with BuildLine():
                    ln1 = CenterArc((0, 0), self._radius, 135, 180 + 90)
                    ln2 = Line(ln1 @ 1, (0, self._radius + self._radius / 2))
                    _ = Line(ln2 @ 1, ln1 @ 0)
                _ = make_face()
            _ = extrude(amount=-self._depth)

            with BuildSketch(Plane.XZ) as sweep_sketch, Locations((self._radius, 0)):
                _ = add(profile)
            _ = sweep(
                sweep_sketch.sketch,
                part.faces().sort_by(Axis.Z)[-1].outer_wire(),
                # Should be Transition.RIGHT, but that fails. Round is the next best thing.
                transition=Transition.ROUND,
            )

            with Locations(Plane(part.faces().sort_by(Axis.Z)[0])):
                _ = Box(
                    self._slit_width,
                    self._slit_length,
                    self._slit_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                )

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class GridfinityRefinedMagnetHoleSide(ObjectFeature):
    """Gridfinity refined magnet hole pushed in from the side for bins."""

    @override
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.SUBTRACT,
    ) -> BasePartObject:
        thickness = 1.9
        radius = 5.86 / 2
        width_small = (5.86 - 1.68 * 2) / 2
        bottom_thickness = 0.6

        with BuildSketch() as sketch:
            with BuildLine():
                ln1 = RadiusArc((-radius, 0), (-width_small, 2.65), radius)
                ln2 = Line(ln1 @ 1, ((ln1 @ 1).X * -1, (ln1 @ 1).Y))
                ln3 = RadiusArc(ln2 @ 1, (radius, 0), radius)
                _ = Polyline(
                    ln3 @ 1,
                    ((ln3 @ 1).X, -3.5),
                    ((ln3 @ 1).X + 1.47, -5.9),
                    ((ln1 @ 0).X, -5.9),
                    ln1 @ 0,
                )
            _ = make_face()

        with BuildSketch() as sketch2:
            with BuildLine():
                _ = add(ln2)
                lnn1 = Line(ln2 @ 0, ((ln2 @ 0).X, (ln2 @ 0).Y + 4.3))
                lnn2 = SagittaArc(lnn1 @ 1, ((ln2 @ 1).X, (lnn1 @ 1).Y), 1.25)
                _ = Line(lnn2 @ 1, ln2 @ 1)
            _ = make_face()

        with BuildPart() as part, Locations(Rotation(0, 0, -135)):
            with Locations((0, 0, -bottom_thickness)):
                _ = add(sketch)
            _ = extrude(amount=-thickness)
            _ = add(sketch2)
            _ = extrude(amount=-thickness - bottom_thickness)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class Weighted(ObjectFeature):
    """Weigthed cutout feature for baseplates."""

    def __init__(
        self,
        feature_location: FeatureLocation,
    ) -> None:
        """Construct Weighted feature.

        Args:
            feature_location (FeatureLocation): Location of feature.
        """
        super().__init__(feature_location)

    @override
    def create_obj(
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
                _ = SagittaArc(ln1 @ 0, ln1 @ 1, appendix_width / 2)
            _ = make_face()

        with BuildPart() as part:
            _ = Box(size, size, height, align=(Align.CENTER, Align.CENTER, Align.MAX))
            with PolarLocations(size / 2, 4):
                _ = add(sketch)
            _ = extrude(amount=appendix_height, dir=(0, 0, -1))

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)


class CompartmentFeature(ContextFeature, ABC):
    """Context feature for a Compartment."""


class Label(CompartmentFeature):
    """Label feature for compartments."""

    _max_angle: int = 90

    def __init__(self, angle: float = gf_bin.label.angle) -> None:
        """Construct label feature.

        Args:
            angle (float, optional): angle of the label. Defaults to gf_bin.label.angle.
        """
        if not 0 <= angle <= self._max_angle:
            msg = "Label angle needs to be between 0 and 90"
            raise ValueError(msg)

        self.angle: float = angle or 0.0000001

    @override
    def apply(self, context: BuildPart) -> None:
        face_top = context.faces().sort_by(Axis.Z)[-1]
        edge_top_back = face_top.edges().sort_by(Axis.Y)[-1]
        try:
            _ = chamfer(
                edge_top_back,
                length=gf_bin.label.width,
                angle=self.angle,
                reference=face_top,
            )
            chamfer_face = context.faces().sort_by(Axis.Z)[-2]
            _ = extrude(
                to_extrude=chamfer_face,
                amount=1,
                dir=(0, 0, -1),
                mode=Mode.SUBTRACT,
            )
        except ValueError as exp:
            msg = "Label could not be created, Parent object too small"
            raise ValueError(msg) from exp


class Scoop(CompartmentFeature):
    """Compartment Scoop feature."""

    def __init__(
        self,
        radius: float = gf_bin.scoop.radius,
        wall_correction: float = 0,
    ) -> None:
        """Construct Compartment Scoop feature.

        Args:
            radius (float, optional): Radius of the scoop. Defaults to gf_bin.scoop.radius.
            wall_correction (float, optional): Makes wall of sweep side thicker. Can be used to
                compesate for the stacking lid so one smooth ramp is created to make it easier to
                    pick items out of a bin.
        """
        self.radius: float = radius
        self.wall_correction: float = wall_correction

    @override
    def apply(self, context: BuildPart) -> None:
        if self.wall_correction:
            face_front = context.faces().sort_by(Axis.Y)[0]
            _ = extrude(face_front, amount=-self.wall_correction, mode=Mode.SUBTRACT)

        face_bottom = context.faces().sort_by(Axis.Z)[0]
        edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]

        try:
            _ = fillet(edge_bottom_front, radius=self.radius)
        except ValueError as exp:
            msg = "Scoop could not be created, Parent object too small"
            raise ValueError(msg) from exp
