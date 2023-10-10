import unittest

from build123d import BuildPart, Vector, Box, Location

from gridfinity_build123d.bin import BinPart, BinCompartment
from gridfinity_build123d.base import Grid

from ocp_vscode import set_port  # type: ignore

set_port(3939)


class BinPartTest(unittest.TestCase):
    def test_binpart(self) -> None:
        grid = Grid(2, 2)
        cutter = Box(30, 40, 15)
        height = 30

        with BuildPart() as part:
            BinPart(grid, cutter, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(84, 84, height), bbox.size)
        self.assertEqual(192231.43760293277, part.part.volume)

    def test_binpart_2_boxes(self) -> None:
        grid = Grid(2, 2)
        cutter = Box(30, 40, 15)
        cutter.location = Location((20, 20))
        cutter2 = Box(20, 30, 10)
        cutter2.location = Location((-20, -20))
        cutters = [cutter, cutter2]
        height = 30

        with BuildPart() as part:
            BinPart(grid, cutters, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(84, 84, height), bbox.size)
        self.assertEqual(186231.43760293277, part.part.volume)


class BinCompartmentTest(unittest.TestCase):
    def test_binpart(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            BinCompartment(size_x, size_y, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35783.642486130215, part.part.volume)

    def test_binpart_sweep(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            BinCompartment(size_x, size_y, height, sweep=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35598.76299687089, part.part.volume)

    def test_binpart_label(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            BinCompartment(size_x, size_y, height, label=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(34788.79103368599, part.part.volume)

    def test_binpart_sweep_and_label(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            BinCompartment(size_x, size_y, height, sweep=True, label=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(34603.91154445353, part.part.volume)
