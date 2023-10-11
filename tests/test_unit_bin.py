import unittest
from unittest.mock import patch, MagicMock, call

from build123d import BuildPart, Vector, Box, Location

from gridfinity_build123d.bin import BinPart, Compartment, CompartmentType, CompartmentGrid
from gridfinity_build123d.base import Grid

import mocks

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
        self.assertEqual(Vector(83.5, 83.5, height), bbox.size)
        self.assertEqual(189718.93760293277, part.part.volume)

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
        self.assertEqual(Vector(83.5, 83.5, height), bbox.size)
        self.assertEqual(183718.93760293277, part.part.volume)


@patch("gridfinity_build123d.bin.Compartment", autospec=True)
class CompartmentGridTest(unittest.TestCase):
    def test_compartmentgrid_one_compartment(self, comp_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.side_effect = mock_box.create

        grid = [[1]]
        type_list = [CompartmentType.NORMAL]

        with BuildPart() as part:
            CompartmentGrid(
                size_x=100,
                size_y=100,
                height=50,
                wall_thickness=3,
                grid=grid,
                type_list=type_list,
            )

        comp_mock.assert_called_once_with(
            size_x=97.0, size_y=97.0, height=50, comp_type=type_list[0]
        )
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 10), bbox.size)
        self.assertEqual(999.9999999999998, part.part.volume)

    def test_compartmentgrid_one_row(self, comp_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.side_effect = mock_box.create

        grid = [[1, 2, 2, 3, 3, 3]]
        type_list = [CompartmentType.NORMAL, CompartmentType.SWEEP, CompartmentType.LABEL]

        with BuildPart() as part:
            CompartmentGrid(
                size_x=100,
                size_y=100,
                height=50,
                wall_thickness=3,
                grid=grid,
                type_list=type_list,
            )

        comp_mock.assert_has_calls(
            [
                call(size_x=13.666666666666668, size_y=97.0, height=50, comp_type=type_list[0]),
                call(size_x=30.333333333333336, size_y=97.0, height=50, comp_type=type_list[1]),
                call(size_x=47.0, size_y=97.0, height=50, comp_type=type_list[2]),
            ]
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(77, 10, 10), bbox.size)
        self.assertEqual(2999.9999999999986, part.part.volume)

    def test_compartmentgrid_multirow(self, comp_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.side_effect = mock_box.create

        grid = [[1, 1, 2, 3], [1, 1, 4, 3]]
        type_list = [
            CompartmentType.NORMAL,
            CompartmentType.SWEEP,
            CompartmentType.LABEL,
            CompartmentType.LABEL_SWEEP,
        ]

        with BuildPart() as part:
            CompartmentGrid(
                size_x=100,
                size_y=100,
                height=50,
                wall_thickness=3,
                grid=grid,
                type_list=type_list,
            )

        comp_mock.assert_has_calls(
            [
                call(size_x=47.0, size_y=97.0, height=50, comp_type=type_list[0]),
                call(size_x=22.0, size_y=47.0, height=50, comp_type=type_list[1]),
                call(size_x=22.0, size_y=97.0, height=50, comp_type=type_list[2]),
                call(size_x=22.0, size_y=47.0, height=50, comp_type=type_list[3]),
            ]
        )
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(72, 60, 10), bbox.size)
        self.assertEqual(3999.9999999999986, part.part.volume)


class CompartmentTest(unittest.TestCase):
    def test_binpart(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35783.642486130215, part.part.volume)

    def test_binpart_sweep(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height, comp_type=CompartmentType.SWEEP)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35598.76299687089, part.part.volume)

    def test_binpart_label(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height, comp_type=CompartmentType.LABEL)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(34788.79103368599, part.part.volume)

    def test_binpart_sweep_and_label(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height, comp_type=CompartmentType.LABEL_SWEEP)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(34603.91154445353, part.part.volume)
