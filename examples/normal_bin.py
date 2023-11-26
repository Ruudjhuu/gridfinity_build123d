from build123d import BuildPart
from gridfinity_build123d import (
    BaseEqual,
    MagnetHole,
    ScrewHole,
    Bin,
    Utils,
    CompartmentsEqual,
    Compartment,
    Sweep,
    Label,
    StackingLip,
    Direction,
)

with BuildPart() as part:
    BaseEqual(grid_x=3, grid_y=1, features=[MagnetHole(), ScrewHole()])
    Bin(
        face=Utils.get_face_by_direction(Direction.TOP),
        height=Utils.remaining_gridfinity_height(units=6),
        compartments=CompartmentsEqual(
            div_x=5, div_y=1, compartment_list=Compartment(features=[Label(), Sweep()])
        ),
        lip=StackingLip(),
    )

part.part.export_stl("bin_3x1x6.stl")
