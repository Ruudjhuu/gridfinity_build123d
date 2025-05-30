"""Module containg comparment cutters and placement classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    Locations,
    Mode,
    RotationLike,
    fillet,
)

from .constants import gf_bin

if TYPE_CHECKING:
    from .features import CompartmentFeature


class Compartment:
    """Compartment object used as cutter for bins."""

    def __init__(
        self,
        features: CompartmentFeature | list[CompartmentFeature] | None = None,
    ):
        """Create Compartment.

        Args:
            features (CompartmentFeature | list[CompartmentFeature] | None, optional):
                CompartmentFeature or list of CompartmentFeatures. Defaults to None.
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
            size_x (float): Size x.
            size_y (float): Size y.
            height (float): height of compartment.
            rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to None.
            mode (Mode, optional): combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: 3d object.
        """
        with BuildPart() as part:
            Box(
                size_x,
                size_y,
                height,
            )

            for feature in self.features:
                feature.apply(part)

            fillet_edges = [
                i for i in part.edges() if i not in part.faces().sort_by(Axis.Z)[-1].edges()
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
            Compartment(features=[Scoop()]),
            Compartment(features=[Label()]),
            Compartment(),
        ]
        Will generate 4 compartments.
        One compartment is a square and takes 4 slots. The second
        compartment is a rectangle with a Scoop using two slots in the y axis direction.The third
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
            grid ( list[list[int]] | None, optional): Configuration for arangement of compartments.
                Defaults to [[1]].
            compartment_list (Compartment | list[Compartment] | None): Compartment or list of
                compartments. Defaults to None.
            inner_wall (float): Space between aranged compartments. Defaults to 1.2.
            outer_wall (float): Offset outside generrated arangement. Defaults to 0.95.
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
            rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
                of object. Defaults to Align.CENTER.
            mode (Mode, optional): combination mode. Defaults to Mode.ADD.

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
                                create_call = self.compartment_list[item - 1].create
                            else:
                                create_call = self.compartment_list.create

                            create_call(
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
            div_x (int): number of compartments in x direction. Defaults to 1.
            div_y (int): number of compartments in y dirction. Deafults to 1.
            compartment_list (Compartment | list[Compartment] | None, optional): Compartment or list
                of compartments. Defaults to Compartment().
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
