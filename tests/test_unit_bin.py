from __future__ import annotations

import unittest
from unittest.mock import MagicMock

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
    StackingLip,
)
from gridfinity_build123d.compartments import Compartments


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

    def test_bin_height_in_units(self) -> None:
        base = Box(10, 10, 1)
        cmp_mock = MagicMock(spec=Compartments)

        with BuildPart() as part:
            Bin(base=base, height_in_units=4, compartments=cmp_mock)

        cmp_mock.create.assert_called_once_with(
            size_x=10.0,
            size_y=10.0,
            height=27,
            mode=Mode.SUBTRACT,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 28), bbox.size)
        self.assertAlmostEqual(2800, part.part.volume)

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

    def test_bin_height_and_height_in_units(self) -> None:
        self.assertRaises(
            ValueError,
            Bin,
            base=MagicMock(),
            height=5,
            height_in_units=2,
        )


class StackingLipTest(testutils.UtilTestCase):
    def test_stackinglip(self) -> None:
        with BuildSketch() as sketch:
            RectangleRounded(100, 100, 5)

        with BuildPart() as part:
            StackingLip().create(sketch.wire())

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((100, 100, 6.967157), bbox.size, 6)
        self.assertAlmostEqual(4928.067652835152, part.part.volume)
