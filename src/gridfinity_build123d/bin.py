"""bin.

Module containg classes and cutters which can be used to create a bin
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Union, Iterable, List, Tuple
from enum import Enum

from build123d import (
    BasePartObject,
    RotationLike,
    Align,
    Mode,
    BuildPart,
    Box,
    Locations,
    extrude,
    add,
    Solid,
    fillet,
    Axis,
    chamfer,
    Face,
    Part,
)

from .constants import gf_bin


class CompartmentType(Enum):
    """Types of compartments."""

    NORMAL = 1
    LABEL = 2
    SWEEP = 3
    LABEL_SWEEP = 4


class Bin(BasePartObject):
    """Bin.

    Create a bin object with compartments. Sizes are calulated from the top lane of the base object

    Args:
        base (Base): Base grid object
        div_x (int, optional): Devision of compartents in x direction. Defaults to 1.
        div_y (int, optional): Devision of compartments in y direction. Defaults to 1.
        unit_z (int, optional): Height of bin in gridfinity units. Defaults to 3.
        comp_type (CompartmentType, optional): Type of compartments. Defaults to
            CompartmentType.NORMAL.
        rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): align min, center, or max
            of object. Defaults to None.
        mode (Mode, optional): combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        base: Union[Part, Solid],
        div_x: int = 1,
        div_y: int = 1,
        unit_z: int = 3,
        comp_type: CompartmentType = CompartmentType.NORMAL,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        base_height = base.bounding_box().size.Z
        height = unit_z * 7 - base_height

        with BuildPart() as part:
            add(base)

            grid = []
            bin_nr = 1
            for _ in range(div_y):
                row = []
                for _ in range(div_x):
                    row.append(bin_nr)
                    bin_nr += 1
                grid.append(row)

            face = part.faces().sort_by(Axis.Z)[-1]

            cutter = CompartmentGrid(
                size_x=face.bounding_box().size.X,
                size_y=face.bounding_box().size.Y,
                height=height,
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                type_list=[comp_type] * (bin_nr - 1),
                mode=Mode.PRIVATE,
            )

            with Locations((0, 0, base.bounding_box().max.Z)):
                BinPart(
                    face,
                    cutter=cutter,
                    height=height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        super().__init__(part.part, rotation, align, mode)


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
        face: Face,
        cutter: Union[Solid, Iterable[Solid]],
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        cutter = cutter if isinstance(cutter, Iterable) else [cutter]

        with BuildPart() as part:
            extrude(to_extrude=face, amount=height)

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
        size_x (float): Size on the x axis
        size_y (float): size on the y axis
        height (float): Height of compartments
        inner_wall (float): Space between aranged compartments
        outer_wall (float): Offset outside generrated arangement
        grid (List[List[int]]): Configuration for arangement of compartments
        type_list (List[CompartmentType]): List of types of compartments
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
        inner_wall: float,
        outer_wall: float,
        grid: List[List[int]],
        type_list: List[CompartmentType],
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = Align.CENTER,
        mode: Mode = Mode.ADD,
    ):
        distribute_area_x = size_x - outer_wall * 2 + inner_wall
        distribute_area_y = size_y - outer_wall * 2 + inner_wall

        size_unit_x = distribute_area_x / len(grid[0])
        size_unit_y = distribute_area_y / len(grid)

        with BuildPart() as part:
            numbers_proccesed = []
            for r_index, row in enumerate(grid):
                for c_index, item in enumerate(row):
                    if item != 0 and item not in numbers_proccesed:
                        numbers_proccesed.append(item)

                        units_x = self._count_same_row(c_index, row)
                        units_y = self._count_same_column((r_index, c_index), grid)

                        middle_x = (c_index + c_index + units_x) / 2
                        middle_y = (r_index + r_index + units_y) / 2

                        loc_x = self._map_range(middle_x, 0, len(grid[0]), 0, distribute_area_x)
                        loc_y = self._map_range(middle_y, 0, len(grid), 0, distribute_area_y) * -1

                        with Locations((loc_x, loc_y)):
                            Compartment(
                                size_x=size_unit_x * units_x - inner_wall,
                                size_y=size_unit_y * units_y - inner_wall,
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
        with BuildPart() as part:
            Box(
                size_x,
                size_y,
                height,
            )

            # NOTE: Keep the label (chamfer) the first feature, as no direction can be chosen for
            # the chamfer there is a chance an asymentric chamfer is flipped if a different object
            # is processed. Should be fixed in build123d pull request #345 which is not merged when
            # this is written.
            if comp_type in [CompartmentType.LABEL, CompartmentType.LABEL_SWEEP]:
                face_top = part.faces().sort_by(Axis.Z)[-1]
                edge_top_back = face_top.edges().sort_by(Axis.Y)[-1]
                chamfer(
                    edge_top_back, length=gf_bin.label.width, angle=180 - 90 - gf_bin.label.angle
                )
                chamfer_face = part.faces().sort_by(Axis.Z)[-2]
                extrude(to_extrude=chamfer_face, amount=1, dir=(0, 0, -1), mode=Mode.SUBTRACT)

            if comp_type in [CompartmentType.SWEEP, CompartmentType.LABEL_SWEEP]:
                face_bottom = part.faces().sort_by(Axis.Z)[0]
                edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]
                fillet(edge_bottom_front, radius=gf_bin.sweep.radius)

            # get all edges exept edges from top face
            fillet_edges = [
                i for i in part.edges() if i not in part.faces().sort_by(Axis.Z)[-1].edges()
            ]

            fillet(fillet_edges, gf_bin.inner_radius)

        super().__init__(part.part, rotation, align, mode)
