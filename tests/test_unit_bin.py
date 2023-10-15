import unittest
from unittest.mock import patch, MagicMock, call

from build123d import BuildPart, Vector, Box, Location, Rectangle

from gridfinity_build123d.bin import BinPart, Compartment, CompartmentType, CompartmentGrid

import mocks

# Not needed for testing but handy for developing
try:
    from ocp_vscode import set_port  # type: ignore

    set_port(3939)
except ImportError:
    # ignore if not installed
    pass


class BinPartTest(unittest.TestCase):
    def test_binpart(self) -> None:
        face = Rectangle(50, 50).face()
        cutter = Box(30, 40, 15)
        height = 30

        with BuildPart() as part:
            BinPart(face, cutter, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(50, 50, height), bbox.size)
        self.assertEqual(56999.999999999985, part.part.volume)

    def test_binpart_2_boxes(self) -> None:
        face = Rectangle(100, 100).face()
        cutter = Box(30, 40, 15)
        cutter.location = Location((20, 20))
        cutter2 = Box(20, 30, 10)
        cutter2.location = Location((-20, -20))
        cutters = [cutter, cutter2]
        height = 30

        with BuildPart() as part:
            BinPart(face, cutters, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(100, 100, height), bbox.size)
        self.assertEqual(275999.99999999994, part.part.volume)


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
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                type_list=type_list,
            )

        comp_mock.assert_called_once_with(
            size_x=94.0, size_y=94.0, height=50, comp_type=type_list[0]
        )
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000, part.part.volume)

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
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                type_list=type_list,
            )

        comp_mock.assert_has_calls(
            [
                call(size_x=14.833333333333334, size_y=94.0, height=50, comp_type=type_list[0]),
                call(size_x=30.666666666666668, size_y=94.0, height=50, comp_type=type_list[1]),
                call(size_x=46.5, size_y=94.0, height=50, comp_type=type_list[2]),
            ]
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(73.33333333333334, 10, 10), bbox.size)
        self.assertAlmostEqual(3000, part.part.volume)

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
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                type_list=type_list,
            )

        comp_mock.assert_has_calls(
            [
                call(size_x=46.5, size_y=94.0, height=50, comp_type=type_list[0]),
                call(size_x=22.75, size_y=46.5, height=50, comp_type=type_list[1]),
                call(size_x=22.75, size_y=94.0, height=50, comp_type=type_list[2]),
                call(size_x=22.75, size_y=46.5, height=50, comp_type=type_list[3]),
            ]
        )
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(69.375, 57.5, 10), bbox.size)
        self.assertAlmostEqual(4000, part.part.volume)


class CompartmentTest(unittest.TestCase):
    def test_compartment(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35823.124620015966, part.part.volume)

    def test_compartment_sweep(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height, comp_type=CompartmentType.SWEEP)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35638.245130779884, part.part.volume)

    def test_compartment_label(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height, comp_type=CompartmentType.LABEL)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(31012.54761553973, part.part.volume)

    def test_compartment_sweep_and_label(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment(size_x, size_y, height, comp_type=CompartmentType.LABEL_SWEEP)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(30827.668126303644, part.part.volume)
