import unittest
from unittest.mock import ANY, MagicMock, patch

import mocks
import testutils
from build123d import BuildPart, Vector

from gridfinity_build123d.base import Base, BaseBlock, BaseEqual
from gridfinity_build123d.features import ObjectFeature


@patch("gridfinity_build123d.base.BaseBlock", autospec=True)
class BaseTest(unittest.TestCase):
    def test_base(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base()

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 19.5, 5), bbox.size)
        self.assertAlmostEqual(1840.8932334555323, part.part.volume)

    def test_base_1_2(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base([[True], [True]])

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 39.5, 5), bbox.size)
        self.assertAlmostEqual(3790.893233455532, part.part.volume)

    def test_base_2_1(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base([[True, True]])

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(39.5, 19.5, 5), bbox.size)
        self.assertAlmostEqual(3790.893233455532, part.part.volume)

    def test_base_2_2(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base([[True, True], [True, True]])

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(39.5, 39.5, 5), bbox.size)
        self.assertAlmostEqual(7740.893233455531, part.part.volume)

    def test_base_magnet_screw(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create
        feature_1 = MagicMock()
        feature_2 = MagicMock()

        with BuildPart() as part:
            Base([[True]], features=[feature_1, feature_2])

        base_mock.assert_called_once_with(features=[feature_1, feature_2], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 19.5, 5), bbox.size)
        self.assertAlmostEqual(1840.8932334555323, part.part.volume)


@patch("gridfinity_build123d.base.Base.__init__")
class BaseEqualTest(unittest.TestCase):
    def test_base(self, base_mock: MagicMock) -> None:
        features = MagicMock()

        BaseEqual(2, 3, features=features)

        base_mock.assert_called_once_with(
            [[True, True], [True, True], [True, True]],
            features,
            ANY,
            ANY,
            ANY,
        )


class BaseBlockTest(testutils.UtilTestCase):
    def test_baseblock(self) -> None:
        with BuildPart() as part:
            BaseBlock()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(12240.821519721352, part.part.volume)

    def test_baseblock_one_feature(self) -> None:
        feature = MagicMock(spec=ObjectFeature)

        with BuildPart() as part:
            BaseBlock(features=feature)

        feature.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(12240.821519721352, part.part.volume)

    def test_baseblock_multiple_features(self) -> None:
        feature_1 = MagicMock(spec=ObjectFeature)
        feature_2 = MagicMock(spec=ObjectFeature)

        with BuildPart() as part:
            BaseBlock(features=[feature_1, feature_2])

        feature_1.apply.assert_called_once()
        feature_2.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(12240.821519721352, part.part.volume)
