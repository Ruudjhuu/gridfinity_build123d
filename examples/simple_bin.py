from build123d import BuildPart
from gridfinity_build123d import (
    BaseEqual,
    Bin,
    Utils,
    CompartmentsEqual,
    Compartment,
    Direction,
)

with BuildPart() as part:
    BaseEqual(grid_x=2, grid_y=1)
    Bin(
        face=Utils.get_face_by_direction(Direction.TOP),
        height=Utils.remaining_gridfinity_height(units=3),
        compartments=CompartmentsEqual(compartment_list=[Compartment()]),
    )

part.part.export_stl("bin_2x1x3.stl")
