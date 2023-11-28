from parameterized import parameterized
from math import pi
from unittest.mock import MagicMock, patch
from build123d import BuildPart, Box, Axis

import testutils

from gridfinity_build123d.features import HoleFeature, ScrewHole, MagnetHole, Label, Sweep


class HoleFeatureTest(testutils.UtilTestCase):
    @parameterized.expand([[1, 2], [3, 4], [10, 2]])
    def test_hole_feature(self, radius: float, depth: float) -> None:
        part = HoleFeature(radius, depth).create()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((radius * 2, radius * 2, depth), bbox.size)
        self.assertAlmostEqual(radius**2 * pi * depth, part.volume)


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class ScrewHoleTest(testutils.UtilTestCase):
    def test_screw_hole(self, hole_mock: MagicMock) -> None:
        ScrewHole()
        hole_mock.assert_called_once_with(1.5, 6)

    def test_screw_hole_values(self, hole_mock: MagicMock) -> None:
        ScrewHole(2, 3)
        hole_mock.assert_called_once_with(2, 3)


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class MagnetHoleTest(testutils.UtilTestCase):
    def test_screw_hole(self, hole_mock: MagicMock) -> None:
        MagnetHole()
        hole_mock.assert_called_once_with(3.25, 2.4)

    def test_screw_hole_values(self, hole_mock: MagicMock) -> None:
        MagnetHole(2, 3)
        hole_mock.assert_called_once_with(2, 3)


class LabelTest(testutils.UtilTestCase):
    def test_label(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Label().create()

        top_face = part.faces().filter_by(Axis.Z)[-1]
        self.assertEqual(50 - 12, top_face.width)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(121784.44689918072, part.part.volume)

    def test_label_angle(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Label(10).create()

        top_face = part.faces().filter_by(Axis.Z)[-1]
        self.assertEqual(50 - 12, top_face.width)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(123765.22286944953, part.part.volume)

    def test_label_angle_zero(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Label(0).create()

        top_face = part.faces().filter_by(Axis.Z)[-1]
        self.assertEqual(50 - 12, top_face.width)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(124399.99999371683, part.part.volume)

    def test_label_too_small_box(self) -> None:
        with BuildPart():
            Box(10, 10, 10)
            self.assertRaises(ValueError, Label().create)

    def test_label_empty_context(self) -> None:
        with BuildPart():
            self.assertRaises(ValueError, Label().create)

    def test_label_no_context(self) -> None:
        self.assertRaises(RuntimeError, Label().create)

    def test_label_unvalid_angle(self) -> None:
        self.assertRaises(ValueError, Label, -1)
        self.assertRaises(ValueError, Label, 91)


class SweepTest(testutils.UtilTestCase):
    def test_sweep(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Sweep().create()

        bot_face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
        self.assertAlmostEqual(50 - 5, bot_face.width)

        front_face = part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        self.assertAlmostEqual(50 - 5, front_face.length)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(124731.74770424681, part.part.volume)

    def test_sweep_radius(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Sweep(20).create()

        bot_face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
        self.assertAlmostEqual(50 - 20, bot_face.width)

        front_face = part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        self.assertAlmostEqual(50 - 20, front_face.length)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(120707.96326794896, part.part.volume)

    def test_sweep_small_box(self) -> None:
        with BuildPart():
            Box(4, 4, 4)
            self.assertRaises(ValueError, Sweep().create)
