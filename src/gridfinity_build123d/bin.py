"""bin.

Module containg classes and cutters which can be used to create a bin
"""
from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Union, Iterable, List, Tuple

from build123d import (
    BasePartObject,
    RotationLike,
    Align,
    Mode,
    BuildPart,
    BuildSketch,
    BuildLine,
    Box,
    Locations,
    extrude,
    add,
    fillet,
    Axis,
    chamfer,
    Face,
    Plane,
    Polyline,
    make_face,
    Wire,
    sweep,
)


from .constants import gf_bin
from .utils import Utils, StackProfile, Direction


class Bin(BasePartObject):
    """Create a bin.

    Args:
        face (Face): Faceon which the bin is located (usualy top face of a base)
        height (float): Height of the bin
        compartments (Compartments): Compartments of the bin
        lip (StackingLip, optional): A lip object which should be added. Size added due to the lib
            is not included in "height. Defaults to None.
        rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
        of object. Defaults to None.
        mode (Mode, optional): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        face: Face,
        height: float,
        compartments: Compartments,
        lip: StackingLip = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as part:
            extrude(to_extrude=face, amount=height)

            part_bbox = part.part.bounding_box()
            with Locations((0, 0, part_bbox.max.Z)):
                compartments.create(
                    size_x=face.length,
                    size_y=face.width,
                    height=height,
                    mode=Mode.SUBTRACT,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                )

            if lip:
                lip.create(Utils.get_face_by_direction(Direction.TOP).wire())

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
        align: Union[Align, tuple[Align, Align, Align]] = None,
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
            StackProfile()
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
                with Locations(
                    (
                        path.bounding_box().max.X - profile.sketch.bounding_box().max.X,
                        path.bounding_box().max.Z,
                    )
                ):
                    add(profile)
            sweep(sections=sweep_sketch.sketch, path=path)

        return BasePartObject(part.part, rotation, align, mode)


class Compartment:
    """Create Compartment.

    Args:
        features (List[CompartmentContextFeature], optional): compartment feature list. Defaults to
            None.
    """

    def __init__(self, features: List[CompartmentContextFeature] = None):
        if not features:
            features = []

        self.features = features

    def create(
        self,
        size_x: float,
        size_y: float,
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
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
                feature.apply()

            fillet_edges = [
                i for i in part.edges() if i not in part.faces().sort_by(Axis.Z)[-1].edges()
            ]

            fillet(fillet_edges, gf_bin.inner_radius)

        return BasePartObject(part.part, rotation, align, mode)


class Compartments:
    """CompartmentGrid.

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


        outer_wall: float,

        height (float): Height of compartments
        inner_wall (float): Space between aranged compartments
        outer_wall (float): Offset outside generrated arangement
        grid (List[List[int]]): Configuration for arangement of compartments
        type_list (List[CompartmentType]): List of types of compartments

    """

    def __init__(
        self,
        grid: List[List[int]] = None,
        compartment_list: Union[Compartment, List[Compartment]] = Compartment(),
        inner_wall: float = 1.2,
        outer_wall: float = 0.95,
    ):
        if not grid:
            grid = [[1]]

        self.inner_wall = inner_wall
        self.outer_wall = outer_wall
        self.grid = grid
        self.compartment_list = (
            compartment_list if isinstance(compartment_list, Iterable) else [compartment_list]
        )

    def create(
        self,
        size_x: float,
        size_y: float,
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = Align.CENTER,
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
                            middle_x, 0, len(self.grid[0]), 0, distribute_area_x
                        )
                        loc_y = (
                            self._map_range(middle_y, 0, len(self.grid), 0, distribute_area_y) * -1
                        )

                        with Locations((loc_x, loc_y)):
                            self.compartment_list[item - 1].create(
                                size_x=size_unit_x * units_x - self.inner_wall,
                                size_y=size_unit_y * units_y - self.inner_wall,
                                height=height,
                            )

        return BasePartObject(part=part.part, rotation=rotation, align=align, mode=mode)

    @staticmethod
    def _map_range(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def _count_same_row(r_index: int, row: List[int]) -> int:
        number = row[r_index]
        count = 0
        for item in row[r_index:]:
            if number == item:
                count += 1
            else:
                return count

        return count

    @staticmethod
    def _count_same_column(index: Tuple[int, int], grid: List[List[int]]) -> int:
        number = grid[index[0]][index[1]]
        count = 0
        for row in grid[index[0] :]:
            if row[index[1]] == number:
                count += 1
            else:
                return count
        return count


class CompartmentsEqual(Compartments):
    """Generate equal spaced compartments.

    Args:
        div_x (int): number of compartments in x direction
        div_y (int): number of compartments in y dirction
        compartment_list (Union[Compartment, List[Compartment]]): List of compartments
        inner_wall (float, optional): wall thickness between compartments. Defaults to 1.2.
        outer_wall (float, optional): wall thickness around compartments. Defaults to 0.95.
    """

    def __init__(
        self,
        compartment_list: Union[Compartment, List[Compartment]] = Compartment(),
        div_x: int = 1,
        div_y: int = 1,
        inner_wall: float = 1.2,
        outer_wall: float = 0.95,
    ) -> None:
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


class ContextFeature(ABC):
    """Interface for feature using a builder context."""

    @abstractmethod
    def apply(self) -> None:
        """Apply the feature to the object in context."""
        raise NotImplementedError  # pragma: no cover


class CompartmentContextFeature(ContextFeature):
    """Context feature for a Comopartment."""


class Label(CompartmentContextFeature):
    """Compartment Label feature.

    Args:
        angle (float, optional): angle of the label. Defaults to gf_bin.label.angle.
    """

    def __init__(self, angle: float = gf_bin.label.angle) -> None:
        self.angle = angle

    def apply(self) -> None:
        context: BuildPart = BuildPart._get_context(  # pylint: disable=protected-access
            "Label.create"
        )

        face_top = context.faces().sort_by(Axis.Z)[-1]
        edge_top_back = face_top.edges().sort_by(Axis.Y)[-1]
        chamfer(edge_top_back, length=gf_bin.label.width, angle=180 - 90 - self.angle)
        chamfer_face = context.faces().sort_by(Axis.Z)[-2]
        extrude(to_extrude=chamfer_face, amount=1, dir=(0, 0, -1), mode=Mode.SUBTRACT)


class Sweep(CompartmentContextFeature):
    """Compartment Sweep feature.

    Args:
        radius (float, optional): Radius of the sweep. Defaults to gf_bin.sweep.radius.
    """

    def __init__(self, radius: float = gf_bin.sweep.radius) -> None:
        self.radius = radius

    def apply(self) -> None:
        context: BuildPart = BuildPart._get_context(  # pylint: disable=protected-access
            "Label.create"
        )
        face_bottom = context.faces().sort_by(Axis.Z)[0]
        edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]
        fillet(edge_bottom_front, radius=self.radius)
