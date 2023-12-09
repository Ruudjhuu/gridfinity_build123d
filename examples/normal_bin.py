"""Example for generating a standar bin.

This bin more or less represent the "default" bin downloadable from Zacks objects. It contains one
compartments with label and sweep features. The base contains the default magnet and screw holes.
"""
from build123d import BuildPart
from gridfinity_build123d import (
    BaseEqual,
    Bin,
    Compartment,
    CompartmentsEqual,
    Direction,
    Label,
    MagnetHole,
    ScrewHole,
    StackingLip,
    Sweep,
    Utils,
)

with BuildPart() as part:
    BaseEqual(grid_x=3, grid_y=1, features=[MagnetHole(), ScrewHole()])
    Bin(
        face=Utils.get_face_by_direction(part, Direction.TOP),
        height=Utils.remaining_gridfinity_height(part, units=6),
        compartments=CompartmentsEqual(
            div_x=5,
            div_y=1,
            compartment_list=Compartment(features=[Label(), Sweep()]),
        ),
        lip=StackingLip(),
    )

part.part.export_stl("bin_3x1x6.stl")
