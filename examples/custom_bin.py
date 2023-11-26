from build123d import BuildPart

from gridfinity_build123d import (
    BaseEqual,
    MagnetHole,
    ScrewHole,
    Compartment,
    Label,
    Compartments,
    Bin,
    Utils,
    StackingLip,
    Direction,
)

with BuildPart() as part:
    BaseEqual(grid_x=3, grid_y=3, features=[MagnetHole(), ScrewHole()])

    cmp_type = Compartment(features=Label())
    cmp_placement = [
        [1, 1, 2, 6, 3],
        [1, 1, 5, 6, 5],
        [1, 1, 4, 6, 7],
    ]
    compartments = Compartments(grid=cmp_placement, compartment_list=cmp_type)
    Bin(
        face=Utils.get_face_by_direction(Direction.TOP),
        height=Utils.remaining_gridfinity_height(5),
        compartments=compartments,
        lip=StackingLip(),
    )

part.part.export_stl("bin.stl")
