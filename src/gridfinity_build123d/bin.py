"""Module containg classes and cutters which can be used to create a bin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Edge,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Polyline,
    RotationLike,
    Shape,
    Wire,
    add,  # pyright: ignore[reportUnknownVariableType]
    extrude,
    fillet,
    make_face,
    sweep,
)

from .utils import Direction, StackProfile, Utils

if TYPE_CHECKING:
    from .compartments import Compartments


class Bin(BasePartObject):
    """Gridfinity Bin object."""

    def __init__(
        self,
        base: Part,
        height: float = 0,
        height_in_units: int = 0,
        compartments: Compartments | None = None,
        lip: StackingLip | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a bin object.

        Args:
            base (Part): Base object on which the bin is constructed.
            height (float, optional): Height of the bin in mm. Can't be used when height_in_units is
                defined.Defaults to 0.
            height_in_units (int, optional): Heigth defined by gridfinity units. Can't be used when
                height is defined. Defaults to 0.
            compartments (Compartments | None, optional): Compartments of the bin, Defaults to None.
            lip (StackingLip, optional): A lip object which should be added. Size added due to the
                lib is not included in "height. Defaults to None.
            rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
            mode (Mode, optional): combination mode. Defaults to Mode.ADD.
        """
        if height and height_in_units:
            msg = "height or height_in_units can be defined, not both"
            raise ValueError(msg)

        with BuildPart() as part:
            _ = add(base)
            if not part.part:  # pragma: no cover
                msg = "Part is empty"
                raise RuntimeError(msg)
            if height_in_units:
                bin_height = height_in_units * 7 - base.bounding_box().size.Z
            else:
                bin_height = height

            face = part.faces().sort_by(Axis.Z)[-1]

            if not face.length:  # pragma: no cover
                msg = "Face has no length"
                raise RuntimeError(msg)
            if not face.width:  # pragma: no cover
                msg = "face has no width"
                raise RuntimeError(msg)

            _ = extrude(to_extrude=face, amount=bin_height)
            if compartments:
                part_bbox = part.part.bounding_box()
                with Locations((0, 0, part_bbox.max.Z)):
                    _ = compartments.create(
                        size_x=face.length,
                        size_y=face.width,
                        height=bin_height,
                        mode=Mode.SUBTRACT,
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )

            if lip:
                with Locations((0, 0, part.part.bounding_box().max.Z)):
                    _ = lip.create(
                        Utils.get_face_by_direction(part, Direction.TOP).outer_wire(),
                    )

        super().__init__(part.part, rotation, align, mode)


class StackingLip:
    """StackingLip."""

    def create(
        self,
        path: Wire,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create StackingLip 3d object.

        Args:
            path (Wire): Path to sweep over.
            rotation (RotationLike | optional): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to None.
            mode (Mode, optional): combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: 3d object
        """
        _ = path.move(Location((0, 0, -path.center().Z)))
        with BuildSketch() as profile:
            _ = StackProfile(StackProfile.ProfileType.BIN)
            vertex = profile.vertices().sort_by(Axis.Y)[-1]
            _ = fillet(vertex, 0.2)
            with BuildLine():
                pt1_height = 1.2
                that_one_point_x = 1.65
                that_one_point_y = 1.65
                width = profile.sketch.bounding_box().max.X

                _ = Polyline(
                    (0, 0),
                    (0, -pt1_height),
                    (that_one_point_x, -pt1_height - that_one_point_y),
                    (width, -pt1_height - that_one_point_y),
                    (width, 0),
                    close=True,
                )
            _ = make_face()
        with BuildPart() as part:
            with BuildSketch(Plane.XZ) as sweep_sketch:

                def edge_filter(shape: Shape[Edge]) -> bool:
                    inner_edge = shape.edge()
                    if not inner_edge:  # pragma: no cover
                        raise TypeError

                    return bool(inner_edge.find_intersection_points(Axis.X))

                edge = path.edges().sort_by(Axis.X).filter_by(edge_filter).sort_by(Axis.X)[-1]
                point = edge.find_intersection_points(Axis.X)[0]

                with (
                    Locations((point.X, point.Z)),
                    Locations(
                        (-profile.sketch.bounding_box().max.X, 0),
                    ),
                ):
                    _ = add(profile)
            _ = sweep(sections=sweep_sketch.sketch, path=path)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)
