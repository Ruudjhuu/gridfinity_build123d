from parameterized import parameterized
from math import pi
from unittest.mock import MagicMock, patch

import testutils

from gridfinity_build123d.features import HoleFeature, ScrewHole, MagnetHole


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


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class MagnetHoleTest(testutils.UtilTestCase):
    def test_screw_hole(self, hole_mock: MagicMock) -> None:
        MagnetHole()
        hole_mock.assert_called_once_with(3.25, 2.4)
