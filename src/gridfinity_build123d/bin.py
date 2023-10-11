"""bin.

Module containg classes and cutters which can be used to create a bin
"""
from __future__ import annotations
from typing import Union, Iterable, List, Tuple
from enum import Enum

from build123d import (
    BasePartObject,
    RotationLike,
    Align,
    Mode,
    BuildPart,
    Box,
    Locations,
    BuildSketch,
    RectangleRounded,
    extrude,
    add,
    Solid,
    fillet,
    Axis,
    chamfer,
)

from .base import Grid
from .constants import gridfinity_standard


class BinPart(BasePartObject):
    """Create the top part of a bin.

    Args:
        grid (Grid): Gridfinity grid definition
        cutter (Union[Solid, Iterable[Solid]]): Object(s) to be cut out.
        height (int): Height of the bin part
        rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
        mode (Mode, optional): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        grid: Grid,
        cutter: Union[Solid, Iterable[Solid]],
        height: int,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        cutter = cutter if isinstance(cutter, Iterable) else [cutter]

        with BuildPart() as part:
            with BuildSketch():
                RectangleRounded(
                    grid.X_mm_real,
                    grid.Y_mm_real,
                    gridfinity_standard.grid.radius,
                )
            extrude(amount=height)

            for cut in cutter:
                with Locations((0, 0, part.part.bounding_box().max.Z - cut.bounding_box().max.Z)):
                    add(cut, mode=Mode.SUBTRACT)

        super().__init__(part.part, rotation, align, mode)


class CompartmentGrid(BasePartObject):
    """CompartmentGrid.

    Creates compartments according to type_list and aranges them according to the grid.
    Example:
        grid = [
            [1,1,2,3,3],
            [1,1,2,4,4]
        ]
        type_list = [
            CompartmentType.NORMAL,
            CompartmentType.SWEEP,
            CompartmentType.LABEL,
            CompartmentType.LABEL_SWEEP,
        ]

        Will generate 4 compartments. One compartment is a square and takes 4 slots which is of
        type NORMAL. The second compartment is a rectangle using two slots in the y axis
        direction of type SWEEP.The third compartment is a rectangle using 2 slots in the x
        axis direction of type LABEL. The fourt compartment is a rectangle in the x axis
        direction of type LABEL_SWEEP.

        The size of the compartments and exact location is calulated on basis of the total size
        of the grid arangement (size_x and size_y)


    Args:
        size_x (int): Size on the x axis
        size_y (int): size on the y axis
        height (int): Height of compartments
        wall_thickness (int): Space between aranged compartments
        grid (List[List[int]]): Configuration for arangement of compartments
        type_list (List[CompartmentType]): List of types of compartments
        rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
        mode (Mode, optional): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        size_x: int,
        size_y: int,
        height: int,
        wall_thickness: int,
        grid: List[List[int]],
        type_list: List[CompartmentType],
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        size_unit_x = size_x / len(grid[0])
        size_unit_y = size_y / len(grid)

        with BuildPart() as part:
            numbers_proccesed = []
            for r_index, row in enumerate(grid):
                for c_index, item in enumerate(row):
                    if item != 0 and item not in numbers_proccesed:
                        numbers_proccesed.append(item)

                        print(f"{r_index},{c_index}: {item}")
                        units_x = self._count_same_row(c_index, row)
                        units_y = self._count_same_column((r_index, c_index), grid)

                        middle_x = (c_index + c_index + units_x) / 2
                        middle_y = (r_index + r_index + units_y) / 2

                        loc_x = self._map_range(middle_x, 0, len(grid[0]), 0, size_x)
                        loc_y = self._map_range(middle_y, 0, len(grid), 0, size_y) * -1

                        with Locations((loc_x, loc_y)):
                            Compartment(
                                size_x=size_unit_x * units_x - wall_thickness,
                                size_y=size_unit_y * units_y - wall_thickness,
                                height=height,
                                comp_type=type_list[item - 1],
                            )

        super().__init__(part=part.part, rotation=rotation, align=align, mode=mode)

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


class CompartmentType(Enum):
    """Types of compartments."""

    NORMAL = 1
    LABEL = 2
    SWEEP = 3
    LABEL_SWEEP = 4


class Compartment(BasePartObject):
    """Create Bincompartment usualy used as a bin cutter.

    Args:
        size_x (float): size on x axis
        size_y (float): size on y axis
        height (float): height of the compartment
        sweep (bool, optional): Enable sweep radius in bottom low corner. Defaults to False.
        label (bool, optional): Enable lable for compartment. Defaults to False.
        rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
        mode (Mode, optional): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        size_x: float,
        size_y: float,
        height: float,
        comp_type: CompartmentType = CompartmentType.NORMAL,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        sweep_radius = 5

        with BuildPart() as part:
            Box(
                size_x,
                size_y,
                height,
            )

            if comp_type in [CompartmentType.SWEEP, CompartmentType.LABEL_SWEEP]:
                face_bottom = part.faces().sort_by(Axis.Z)[0]
                edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]
                fillet(edge_bottom_front, radius=sweep_radius)

            if comp_type in [CompartmentType.LABEL, CompartmentType.LABEL_SWEEP]:
                face_top = part.faces().sort_by(Axis.Z)[-1]
                edge_top_back = face_top.edges().sort_by(Axis.Y)[-1]
                chamfer(edge_top_back, length=10, length2=5)

            # fillet side rings and bottom left over edges
            sorted_faces = part.faces().sort_by(Axis.X)
            left_face = sorted_faces[0]
            right_face = sorted_faces[-1]
            face_bottom = part.faces().sort_by(Axis.Z)[0]
            fillet_edges = left_face.edges() + right_face.edges() + face_bottom.edges()

            fillet(fillet_edges, gridfinity_standard.g_bin.inner_radius)

        super().__init__(part.part, rotation, align, mode)
