"""Module containg classes and cutters which can be used to create a bin."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Part,
    Plane,
    Polyline,
    RotationLike,
    Wire,
    add,
    extrude,
    fillet,
    make_face,
    sweep,
)

from .constants import gf_bin
from .utils import Direction, StackProfile, Utils

if TYPE_CHECKING:
    from .features import CompartmentFeature


class Bin(BasePartObject):
    """Gridfinity Bin object."""

    def __init__(
        self,
        base: Part,
        height: float = 0,
        height_in_units: int = 0,
        compartments: Compartments = None,
        lip: StackingLip = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a bin object.

        Args:
            base (Part): Base object on which the bin is constructed.
            height (float): Height of the bin in mm. Can't be used when height_in_units is defined.
            heihgt_in_units (int): Heigth defined by gridfinity units. Can't be used when height is
                defined.
            compartments (Compartments): Compartments of the bin, Defaults to None.
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
            add(base)
            if height_in_units:
                bin_height = height_in_units * 7 - part.part.bounding_box().size.Z
            else:
                bin_height = height

            face = part.faces().sort_by(Axis.Z)[-1]
            extrude(to_extrude=face, amount=bin_height)
            if compartments:
                part_bbox = part.part.bounding_box()
                with Locations((0, 0, part_bbox.max.Z)):
                    compartments.create(
                        size_x=face.length,
                        size_y=face.width,
                        height=bin_height,
                        mode=Mode.SUBTRACT,
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )

            if lip:
                lip.create(
                    Utils.get_face_by_direction(part, Direction.TOP).outer_wire(),
                )

        super().__init__(part.part, rotation, align, mode)


class StackingLip:
    """StackingLip.

    Sweeps around the wire with a stacking lip profice to create the lip object

    Args:
        path (Wire): Wire to follow
        rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
        mode (Mode, optional): combination mode. Defaults to Mode.ADD.
    """

    def create(
        self,
        path: Wire,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create StackingLip 3d object.

        Args:
            path (Wire): Path to sweep over
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to None.
            mode (Mode): combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: 3d object
        """
        with BuildSketch() as profile:
            StackProfile(StackProfile.ProfileType.BIN)
            vertex = profile.vertices().sort_by(Axis.Y)[-1]
            fillet(vertex, 0.2)
            with BuildLine():
                pt1_height = 1.2
                that_one_point_x = 1.65
                that_one_point_y = 1.65
                width = profile.sketch.bounding_box().max.X

                Polyline(
                    (0, 0),
                    (0, -pt1_height),
                    (that_one_point_x, -pt1_height - that_one_point_y),
                    (width, -pt1_height - that_one_point_y),
                    (width, 0),
                    close=True,
                )
            make_face()
        with BuildPart() as part:
            with BuildSketch(Plane.XZ) as sweep_sketch:
                right_edge_center = path.edges().sort_by(Axis.X)[-1].center()
                with Locations((right_edge_center.X, right_edge_center.Z)), Locations(
                    (-profile.sketch.bounding_box().max.X, 0),
                ):
                    add(profile)
            sweep(sections=sweep_sketch.sketch, path=path)

        return BasePartObject(part.part, rotation, align, mode)


class Compartment:
    """Compartment object used as cutter for bins."""

    def __init__(
        self,
        features: CompartmentFeature | list[CompartmentFeature] | None = None,
    ):
        """Create Compartment.

        Args:
            features (List[CompartmentContextFeature], optional): compartment feature list. Defaults
                to None.
        """
        if not features:
            features = []

        self.features = features if isinstance(features, Iterable) else [features]

    def create(
        self,
        size_x: float,
        size_y: float,
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create Compartment object.

        Args:
            size_x (float): Size x
            size_y (float): Size y
            height (float): height of compartment
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to None.
            mode (Mode): combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: 3d object
        """
        with BuildPart() as part:
            Box(
                size_x,
                size_y,
                height,
            )

            for feature in self.features:
                feature.create(part)

            fillet_edges = [
                i
                for i in part.edges()
                if i not in part.faces().sort_by(Axis.Z)[-1].edges()
            ]

            fillet(fillet_edges, gf_bin.inner_radius)

        return BasePartObject(part.part, rotation, align, mode)


class Compartments:
    """Compartments collection.

    Creates compartments according to type_list and aranges them according to the grid.

    Example:
        grid = [
            [1,1,2,3,3],
            [1,1,2,4,4]
        ]
        compartment_list = [
            Compartment(),
            Compartment(features=[Sweep()]),
            Compartment(features=[Label()]),
            Compartment(),
        ]
        Will generate 4 compartments.
        One compartment is a square and takes 4 slots. The second
        compartment is a rectangle with a Sweep using two slots in the y axis direction.The third
        compartment is a rectangle with a Label using 2 slots in the x axis direction. The fourth
        compartment is a rectangle in the x axis direction.
        The size of the compartments and exact location is calculated on basis of the total size
        of the grid arangement
    """

    def __init__(
        self,
        grid: list[list[int]] | None = None,
        compartment_list: Compartment | list[Compartment] | None = None,
        inner_wall: float = 1.2,
        outer_wall: float = 0.95,
    ):
        """Construct grid collection.

        Args:
            grid (List[List[int]]): Configuration for arangement of compartments
            compartment_list (List[CompartmentType]): List of types of compartments
            inner_wall (float): Space between aranged compartments
            outer_wall (float): Offset outside generrated arangement
        """
        if grid is None:
            grid = [[1]]
        if compartment_list is None:
            compartment_list = Compartment()

        self.inner_wall = inner_wall
        self.outer_wall = outer_wall
        self.grid = grid
        self.compartment_list = compartment_list

    def create(
        self,
        size_x: float,
        size_y: float,
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] = Align.CENTER,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create compartments object.

        Args:
            size_x (float): size on the x axis
            size_y (float): size on the y axis
            height (float): Height of compartments
            rotation (RotationLike): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]]): align min, center, or max
                of object. Defaults to None.
            mode (Mode): combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: 3d object
        """
        distribute_area_x = size_x - self.outer_wall * 2 + self.inner_wall
        distribute_area_y = size_y - self.outer_wall * 2 + self.inner_wall

        size_unit_x = distribute_area_x / len(self.grid[0])
        size_unit_y = distribute_area_y / len(self.grid)

        with BuildPart() as part:
            numbers_proccesed = []
            for r_index, row in enumerate(self.grid):
                for c_index, item in enumerate(row):
                    if item != 0 and item not in numbers_proccesed:
                        numbers_proccesed.append(item)

                        units_x = self._count_same_row(c_index, row)
                        units_y = self._count_same_column((r_index, c_index), self.grid)

                        middle_x = (c_index + c_index + units_x) / 2
                        middle_y = (r_index + r_index + units_y) / 2

                        loc_x = self._map_range(
                            middle_x,
                            0,
                            len(self.grid[0]),
                            0,
                            distribute_area_x,
                        )
                        loc_y = (
                            self._map_range(
                                middle_y,
                                0,
                                len(self.grid),
                                0,
                                distribute_area_y,
                            )
                            * -1
                        )

                        with Locations((loc_x, loc_y)):
                            if isinstance(self.compartment_list, Iterable):
                                self.compartment_list[item - 1].create(
                                    size_x=size_unit_x * units_x - self.inner_wall,
                                    size_y=size_unit_y * units_y - self.inner_wall,
                                    height=height,
                                )
                            else:
                                self.compartment_list.create(
                                    size_x=size_unit_x * units_x - self.inner_wall,
                                    size_y=size_unit_y * units_y - self.inner_wall,
                                    height=height,
                                )

        return BasePartObject(part=part.part, rotation=rotation, align=align, mode=mode)

    @staticmethod
    def _map_range(
        x: float,
        in_min: float,
        in_max: float,
        out_min: float,
        out_max: float,
    ) -> float:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def _count_same_row(r_index: int, row: list[int]) -> int:
        number = row[r_index]
        count = 0
        for item in row[r_index:]:
            if number == item:
                count += 1
            else:
                return count

        return count

    @staticmethod
    def _count_same_column(index: tuple[int, int], grid: list[list[int]]) -> int:
        number = grid[index[0]][index[1]]
        count = 0
        for row in grid[index[0] :]:
            if row[index[1]] == number:
                count += 1
            else:
                return count
        return count


class CompartmentsEqual(Compartments):
    """Equal spaced compartment collection."""

    def __init__(
        self,
        compartment_list: Compartment | list[Compartment] | None = None,
        div_x: int = 1,
        div_y: int = 1,
        inner_wall: float = 1.2,
        outer_wall: float = 0.95,
    ) -> None:
        """Generate equal spaced compartment collection.

        Args:
            div_x (int): number of compartments in x direction
            div_y (int): number of compartments in y dirction
            compartment_list (Union[Compartment, List[Compartment]]): List of compartments
            inner_wall (float, optional): wall thickness between compartments. Defaults to 1.2.
            outer_wall (float, optional): wall thickness around compartments. Defaults to 0.95.
        """
        if compartment_list is None:
            compartment_list = Compartment()
        grid = []
        bin_nr = 1
        for _ in range(div_y):
            row = []
            for _ in range(div_x):
                row.append(bin_nr)
                bin_nr += 1
            grid.append(row)
        super().__init__(
            grid=grid,
            compartment_list=compartment_list,
            inner_wall=inner_wall,
            outer_wall=outer_wall,
        )
