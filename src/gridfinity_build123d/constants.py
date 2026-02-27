# ruff: noqa:N801
"""Gridfinity standard constants."""

from dataclasses import dataclass


@dataclass
class gridfinity_standard:
    """Gridfinity standard constants."""

    @dataclass
    class stacking_lip:
        """Stacking lip constants."""

        height_1: float = 0.7
        height_2: float = 1.8
        height_3_bin: float = 1.9
        height_3_base_plate: float = 2.15
        offset: float = 0.25

    @dataclass
    class grid:
        """Grid constants."""

        size: float = 42
        radius: float = 4
        tollerance: float = 0.5

    @dataclass
    class bottom:
        """Bottom constants."""

        platform_height: float = 2.8
        hole_from_side: float = 8

    @dataclass
    class magnet:
        """Magnet constants."""

        radius: float = 3.25
        thickness: float = 2.4

    @dataclass
    class screw:
        """Screw constants."""

        radius: float = 1.5
        depth: float = 6


@dataclass
class gf_bin:
    """Bin constants."""

    inner_wall: float = 0.95
    # Radius used for vertical inner fillets
    inner_radius_v: float = (
        gridfinity_standard.grid.radius - inner_wall - gridfinity_standard.grid.tollerance / 2
    )
    # Radius used for the rest of the inner fillets
    inner_radius: float = 1.2

    @dataclass
    class label:
        """Label constants."""

        width: float = 12
        angle: float = 36

    @dataclass
    class scoop:
        """Scoop contants."""

        radius: float = 5
