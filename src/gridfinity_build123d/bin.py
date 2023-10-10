"""bin.

Module containg classes and cutters which can be used to create a bin
"""
from typing import Union, Iterable

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
                    gridfinity_standard.grid.size * grid.X,
                    gridfinity_standard.grid.size * grid.Y,
                    gridfinity_standard.grid.radius,
                )
            extrude(amount=height)

            for cut in cutter:
                with Locations((0, 0, part.part.bounding_box().max.Z - cut.bounding_box().max.Z)):
                    add(cut, mode=Mode.SUBTRACT)

        super().__init__(part.part, rotation, align, mode)


class BinCompartment(BasePartObject):
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
        sweep: bool = False,
        label: bool = False,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        sweep_radius = 5
        inner_fillet = 1

        with BuildPart() as part:
            Box(
                size_x,
                size_y,
                height,
            )

            if sweep:
                face_bottom = part.faces().sort_by(Axis.Z)[0]
                edge_bottom_front = face_bottom.edges().sort_by(Axis.Y)[0]
                fillet(edge_bottom_front, radius=sweep_radius)

            if label:
                face_top = part.faces().sort_by(Axis.Z)[-1]
                edge_top_back = face_top.edges().sort_by(Axis.Y)[-1]
                chamfer(edge_top_back, length=10, length2=5)

            # fillet side rings and bottom left over edges
            sorted_faces = part.faces().sort_by(Axis.X)
            left_face = sorted_faces[0]
            right_face = sorted_faces[-1]
            face_bottom = part.faces().sort_by(Axis.Z)[0]
            fillet_edges = []
            fillet_edges += left_face.edges() + right_face.edges() + face_bottom.edges()

            fillet(fillet_edges, inner_fillet)

        super().__init__(part.part, rotation, align, mode)
