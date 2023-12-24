from __future__ import annotations

import unittest
from unittest.mock import MagicMock, call, patch

import mocks
import testutils
from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Mode,
    RectangleRounded,
    Vector,
)
from gridfinity_build123d.bin import (
    Bin,
    Compartment,
    Compartments,
    CompartmentsEqual,
    StackingLip,
)
from gridfinity_build123d.features import CompartmentFeature


class BinTest(unittest.TestCase):
    def test_bin(self) -> None:
        base = Box(10, 10, 1)
        cmp_mock = MagicMock(spec=Compartments)

        with BuildPart() as part:
            Bin(base=base, height=20, compartments=cmp_mock)

        cmp_mock.create.assert_called_once_with(
            size_x=10.0,
            size_y=10.0,
            height=20,
            mode=Mode.SUBTRACT,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 21), bbox.size)
        self.assertAlmostEqual(2100, part.part.volume)

    def test_bin_lip(self) -> None:
        base = Box(10, 10, 1)
        cmp_mock = MagicMock(spec=Compartments)
        lip_mock = MagicMock(spec=StackingLip)

        with BuildPart() as part:
            Bin(base=base, height=20, compartments=cmp_mock, lip=lip_mock)

        cmp_mock.create.assert_called_once_with(
            size_x=10.0,
            size_y=10.0,
            height=20,
            mode=Mode.SUBTRACT,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )

        lip_mock.create.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 21), bbox.size)
        self.assertAlmostEqual(2100, part.part.volume)


class StackingLipTest(testutils.UtilTestCase):
    def test_stackinglip(self) -> None:
        with BuildSketch() as sketch:
            RectangleRounded(100, 100, 5)

        with BuildPart() as part:
            StackingLip().create(sketch.wire())

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((100, 100, 6.967157), bbox.size, 6)
        self.assertAlmostEqual(4928.067652835152, part.part.volume)


class CompartmentsTest(unittest.TestCase):
    def test_compartments_default_grid(self) -> None:
        comp_mock = MagicMock(spec=Compartment)
        comp_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.create.side_effect = comp_box.create

        cmp_type: Compartment = comp_mock

        with BuildPart() as part:
            Compartments(
                inner_wall=1,
                outer_wall=3,
                compartment_list=cmp_type,
            ).create(
                size_x=100,
                size_y=100,
                height=50,
            )

        comp_mock.create.assert_called_once_with(size_x=94.0, size_y=94.0, height=50)
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000, part.part.volume)

    @patch("gridfinity_build123d.bin.Compartment", autospec=True)
    def test_compartments_default_compartment(self, comp_mock: MagicMock) -> None:
        comp_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.return_value.create.side_effect = comp_box.create

        with BuildPart() as part:
            Compartments(
                inner_wall=1,
                outer_wall=3,
            ).create(
                size_x=100,
                size_y=100,
                height=50,
            )

        comp_mock.assert_called_once()
        comp_mock.return_value.create.assert_called_once_with(
            size_x=94.0,
            size_y=94.0,
            height=50,
        )
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000, part.part.volume)

    def test_compartments_one_compartment(self) -> None:
        comp_mock = MagicMock(spec=Compartment)
        comp_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.create.side_effect = comp_box.create

        grid = [[1]]
        comp_list: Compartment = comp_mock

        with BuildPart() as part:
            Compartments(
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                compartment_list=comp_list,
            ).create(
                size_x=100,
                size_y=100,
                height=50,
            )

        comp_mock.create.assert_called_once_with(size_x=94.0, size_y=94.0, height=50)
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000, part.part.volume)

    def test_compartments_one_row(self) -> None:
        comp_mock = MagicMock(spec=Compartment)
        comp_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.create.side_effect = comp_box.create

        grid = [[1, 2, 2, 3, 3, 3]]
        comp_list: Compartment = comp_mock

        with BuildPart() as part:
            Compartments(
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                compartment_list=comp_list,
            ).create(
                size_x=100,
                size_y=100,
                height=50,
            )

        comp_mock.create.assert_has_calls(
            [
                call(size_x=14.833333333333334, size_y=94.0, height=50),
                call(size_x=30.666666666666668, size_y=94.0, height=50),
                call(size_x=46.5, size_y=94.0, height=50),
            ],
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(73.33333333333334, 10, 10), bbox.size)
        self.assertAlmostEqual(3000, part.part.volume)

    def test_compartments_multirow(self) -> None:
        comp_mock = MagicMock(spec=Compartment)
        comp_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock.create.side_effect = comp_box.create

        grid = [[1, 1, 2, 3], [1, 1, 4, 3]]
        comp_list: Compartment = comp_mock

        with BuildPart() as part:
            Compartments(
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                compartment_list=comp_list,
            ).create(
                size_x=100,
                size_y=100,
                height=50,
            )

        comp_mock.create.assert_has_calls(
            [
                call(size_x=46.5, size_y=94.0, height=50),
                call(size_x=22.75, size_y=46.5, height=50),
                call(size_x=22.75, size_y=94.0, height=50),
                call(size_x=22.75, size_y=46.5, height=50),
            ],
        )
        bbox = part.part.bounding_box()
        self.assertEqual(Vector(69.375, 57.5, 10), bbox.size)
        self.assertAlmostEqual(4000, part.part.volume)

    def test_compartments_multiple_types(self) -> None:
        comp_mock_1 = MagicMock(spec=Compartment)
        comp_mock_2 = MagicMock(spec=Compartment)

        comp_box = mocks.BoxAsMock(10, 10, 10)
        comp_mock_1.create.side_effect = comp_box.create
        comp_mock_2.create.side_effect = comp_box.create

        grid = [[1, 2]]
        comp_list: list[Compartment] = [comp_mock_1, comp_mock_2]

        with BuildPart() as part:
            Compartments(
                inner_wall=1,
                outer_wall=3,
                grid=grid,
                compartment_list=comp_list,
            ).create(
                size_x=100,
                size_y=100,
                height=50,
            )

        comp_mock_1.create.assert_called_once_with(size_x=46.5, size_y=94.0, height=50)
        comp_mock_1.create.assert_called_once_with(size_x=46.5, size_y=94.0, height=50)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(57.5, 10.0, 10.0), bbox.size)
        self.assertAlmostEqual(2000, part.part.volume)


@patch("gridfinity_build123d.bin.Compartments.__init__", spec=Compartments)
class CompartmentsEqualTest(unittest.TestCase):
    @patch("gridfinity_build123d.bin.Compartment", autospec=True)
    def test_compartments_equal_default_compartment(
        self,
        comp_mock: MagicMock,
        comps_mock: MagicMock,
    ) -> None:
        CompartmentsEqual(
            div_x=1,
            div_y=1,
        )

        comps_mock.assert_called_once_with(
            grid=[[1]],
            compartment_list=comp_mock.return_value,
            inner_wall=1.2,
            outer_wall=0.95,
        )

    def test_compartments_equal_one(self, comps_mock: MagicMock) -> None:
        cmp_mock1 = MagicMock(spec=Compartment)
        cmp_mock2 = MagicMock(spec=Compartment)

        CompartmentsEqual(
            div_x=1,
            div_y=1,
            compartment_list=[cmp_mock1, cmp_mock2],
        )

        comps_mock.assert_called_once_with(
            grid=[[1]],
            compartment_list=[cmp_mock1, cmp_mock2],
            inner_wall=1.2,
            outer_wall=0.95,
        )

    def test_compartments_equal_one_row(self, comps_mock: MagicMock) -> None:
        cmp_mock1 = MagicMock(spec=Compartment)
        cmp_mock2 = MagicMock(spec=Compartment)

        CompartmentsEqual(
            div_x=5,
            div_y=1,
            compartment_list=[cmp_mock1, cmp_mock2],
        )

        comps_mock.assert_called_once_with(
            grid=[[1, 2, 3, 4, 5]],
            compartment_list=[cmp_mock1, cmp_mock2],
            inner_wall=1.2,
            outer_wall=0.95,
        )

    def test_compartments_equal_multi(self, comps_mock: MagicMock) -> None:
        cmp_mock1 = MagicMock(spec=Compartment)
        cmp_mock2 = MagicMock(spec=Compartment)

        CompartmentsEqual(
            div_x=5,
            div_y=5,
            compartment_list=[cmp_mock1, cmp_mock2],
        )

        comps_mock.assert_called_once_with(
            grid=[
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, 20],
                [21, 22, 23, 24, 25],
            ],
            compartment_list=[cmp_mock1, cmp_mock2],
            inner_wall=1.2,
            outer_wall=0.95,
        )


class CompartmentTest(unittest.TestCase):
    def test_compartment(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        with BuildPart() as part:
            Compartment().create(size_x, size_y, height)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertEqual(35823.124620015966, part.part.volume)

    def test_compartment_feature(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        feature = MagicMock(spec=CompartmentFeature)

        with BuildPart() as part:
            Compartment(features=feature).create(size_x, size_y, height)

        feature.create.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertAlmostEqual(35823.124620015966, part.part.volume)

    def test_compartment_multiple_features(self) -> None:
        size_x = 40
        size_y = 30
        height = 30

        feature_1 = MagicMock(spec=CompartmentFeature)
        feature_2 = MagicMock(spec=CompartmentFeature)

        with BuildPart() as part:
            Compartment(features=[feature_1, feature_2]).create(size_x, size_y, height)

        feature_1.create.assert_called_once()
        feature_2.create.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(size_x, size_y, height), bbox.size)
        self.assertAlmostEqual(35823.124620015966, part.part.volume)
