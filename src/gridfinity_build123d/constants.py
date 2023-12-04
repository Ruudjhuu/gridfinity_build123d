# pylint: disable=invalid-name

"""Gridfinity standard constants."""

from dataclasses import dataclass


@dataclass
class gridfinity_standard:
    """Gridfinity standard constants."""

    @dataclass
    class stacking_lip:
        """Stacking lip constants."""

        height_1 = 0.7
        height_2 = 1.8
        height_3_bin = 1.9
        height_3_base_plate = 2.15
        offset = 0.25

    @dataclass
    class grid:
        """Grid constants."""

        size = 42
        radius = 4
        tollerance = 0.5

    @dataclass
    class bottom:
        """Bottom constants."""

        platform_height = 2.8
        hole_from_side = 8

    @dataclass
    class magnet:
        """Magnet constants."""

        radius = 3.25
        thickness = 2.4

    @dataclass
    class screw:
        """Screw constants."""

        radius = 1.5
        depth = 6


@dataclass
class gf_bin:
    """Bin constants."""

    inner_radius = 1.8
    inner_wall = 1.2

    @dataclass
    class label:
        """Label constants."""

        width = 12
        angle = 36

    @dataclass
    class sweep:
        """Sweep contants."""

        radius = 5
