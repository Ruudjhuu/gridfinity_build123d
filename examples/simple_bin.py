"""Example for creating the most simple bin.

This bin does not have any features and just one compartment.
"""
from build123d import BuildPart
from gridfinity_build123d import (
    BaseEqual,
    Bin,
    Compartment,
    CompartmentsEqual,
    Direction,
    Utils,
)

with BuildPart() as part:
    BaseEqual(grid_x=2, grid_y=1)
    Bin(
        face=Utils.get_face_by_direction(part, Direction.TOP),
        height=Utils.remaining_gridfinity_height(part, units=3),
        compartments=CompartmentsEqual(compartment_list=Compartment()),
    )

part.part.export_stl("bin_2x1x3.stl")
