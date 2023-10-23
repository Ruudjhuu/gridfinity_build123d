import unittest
from unittest.mock import patch, MagicMock, call, ANY

from build123d import (
    BuildPart,
    Vector,
    Box,
    Location,
    Rectangle,
    Mode,
    Align,
    BuildSketch,
    RectangleRounded,
)

from gridfinity_build123d.bin import (
    Bin,
    BinPart,
    Compartment,
    CompartmentType,
    CompartmentGrid,
    StackingLip,
)
import mocks
import testutils


@patch("gridfinity_build123d.bin.StackingLip", autospec=True)
@patch("gridfinity_build123d.bin.CompartmentGrid", autospec=True)
@patch("gridfinity_build123d.bin.BinPart", autospec=True)
class BinTest(unittest.TestCase):
    def test_bin(
        self, binpart_mock: MagicMock, compgrid_mock: MagicMock, stacklip_mock: MagicMock
    ) -> None:
        base = Box(100, 100, 5)
        box_binpart = mocks.BoxAsMock(60, 60, 20)
        box_compgrid = mocks.BoxAsMock(50, 50, 5)
        box_stacklip = mocks.BoxAsMock(40, 40, 3)
        binpart_mock.side_effect = box_binpart.create
        compgrid_mock.side_effect = box_compgrid.create
        stacklip_mock.side_effect = box_stacklip.create

        with BuildPart() as part:
            Bin(base=base)

        compgrid_mock.assert_called_once_with(
            size_x=100,
            size_y=100,
            height=7 * 3 - 5,
            inner_wall=1.2,
            outer_wall=0.95,
            grid=[[1]],
            type_list=[CompartmentType.NORMAL],
            mode=Mode.PRIVATE,
        )

        binpart_mock.assert_called_once_with(
            ANY,
            cutter=box_compgrid.created_objects[0],
            height=16.0,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=ANY,
        )

        stacklip_mock.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(100, 100, 26.35), bbox.size)
        self.assertAlmostEqual(124160, part.part.volume)

    def test_bin_divx(
        self, binpart_mock: MagicMock, compgrid_mock: MagicMock, stacklip_mock: MagicMock
    ) -> None:
        base = Box(100, 100, 5)
        box_binpart = mocks.BoxAsMock(60, 60, 20)
        box_compgrid = mocks.BoxAsMock(50, 50, 5)
        box_stacklip = mocks.BoxAsMock(40, 40, 3)
        binpart_mock.side_effect = box_binpart.create
        compgrid_mock.side_effect = box_compgrid.create
        stacklip_mock.side_effect = box_stacklip.create

        with BuildPart() as part:
            Bin(base=base, div_x=2)

        compgrid_mock.assert_called_once_with(
            size_x=100,
            size_y=100,
            height=7 * 3 - 5,
            inner_wall=1.2,
            outer_wall=0.95,
            grid=[[1, 2]],
            type_list=[CompartmentType.NORMAL] * 2,
            mode=Mode.PRIVATE,
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(100, 100, 26.35), bbox.size)
        self.assertAlmostEqual(124160, part.part.volume)

    def test_bin_divy(
        self, binpart_mock: MagicMock, compgrid_mock: MagicMock, stacklip_mock: MagicMock
    ) -> None:
        base = Box(100, 100, 5)
        box_binpart = mocks.BoxAsMock(60, 60, 20)
        box_compgrid = mocks.BoxAsMock(50, 50, 5)
        box_stacklip = mocks.BoxAsMock(40, 40, 3)
        binpart_mock.side_effect = box_binpart.create
        compgrid_mock.side_effect = box_compgrid.create
        stacklip_mock.side_effect = box_stacklip.create

        with BuildPart() as part:
            Bin(base=base, div_y=2)

        compgrid_mock.assert_called_once_with(
            size_x=100,
            size_y=100,
            height=7 * 3 - 5,
            inner_wall=1.2,
            outer_wall=0.95,
            grid=[[1], [2]],
            type_list=[CompartmentType.NORMAL] * 2,
            mode=Mode.PRIVATE,
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(100, 100, 26.35), bbox.size)
        self.assertAlmostEqual(124160, part.part.volume)

    def test_bin_unitz(
        self, binpart_mock: MagicMock, compgrid_mock: MagicMock, stacklip_mock: MagicMock
    ) -> None:
        base = Box(100, 100, 5)
        box_binpart = mocks.BoxAsMock(60, 60, 20)
        box_compgrid = mocks.BoxAsMock(50, 50, 5)
        box_stacklip = mocks.BoxAsMock(40, 40, 3)
        binpart_mock.side_effect = box_binpart.create
        compgrid_mock.side_effect = box_compgrid.create
        stacklip_mock.side_effect = box_stacklip.create

        with BuildPart() as part:
            Bin(base=base, unit_z=6)

        compgrid_mock.assert_called_once_with(
            size_x=100,
            size_y=100,
            height=7 * 6 - 5,
            inner_wall=1.2,
            outer_wall=0.95,
            grid=[[1]],
            type_list=[CompartmentType.NORMAL],
            mode=Mode.PRIVATE,
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(100, 100, 26.35), bbox.size)
        self.assertAlmostEqual(124160, part.part.volume)

    def test_bin_comp_type(
        self, binpart_mock: MagicMock, compgrid_mock: MagicMock, stacklip_mock: MagicMock
    ) -> None:
        base = Box(100, 100, 5)
        box_binpart = mocks.BoxAsMock(60, 60, 20)
        box_compgrid = mocks.BoxAsMock(50, 50, 5)
        box_stacklip = mocks.BoxAsMock(40, 40, 3)
        binpart_mock.side_effect = box_binpart.create
        compgrid_mock.side_effect = box_compgrid.create
        stacklip_mock.side_effect = box_stacklip.create

        with BuildPart() as part:
            Bin(base=base, comp_type=CompartmentType.LABEL)

        compgrid_mock.assert_called_once_with(
            size_x=100,
            size_y=100,
            height=7 * 3 - 5,
            inner_wall=1.2,
            outer_wall=0.95,
            grid=[[1]],
            type_list=[CompartmentType.LABEL],
            mode=Mode.PRIVATE,
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(100, 100, 26.35), bbox.size)
        self.assertAlmostEqual(124160, part.part.volume)


class StackingLipTest(testutils.UtilTestCase):
    def test_stackinglip(self) -> None:
        with BuildSketch() as sketch:
            RectangleRounded(100, 100, 5)

        with BuildPart() as part:
            StackingLip(sketch.wire())

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((100, 100, 6.967157), bbox.size, 6)
        self.assertEqual(4928.067652835152, part.part.volume)


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
