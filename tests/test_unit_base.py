import unittest
from unittest.mock import ANY, MagicMock, patch

import mocks
import testutils
from build123d import BuildPart, Vector

from gridfinity_build123d.base import Base, BaseBlock, BaseBlockPlatform, BaseEqual
from gridfinity_build123d.features import ObjectFeature


@patch("gridfinity_build123d.base.Utils.create_bin_platform", autospec=True)
@patch("gridfinity_build123d.base.BaseBlock", autospec=True)
class BaseTest(unittest.TestCase):
    def test_base(self, base_mock: MagicMock, platform_mock: MagicMock) -> None:
        base_mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = base_mock_box.create
        platform_mock_box = mocks.BoxAsMock(10, 10, 5)
        platform_mock.side_effect = platform_mock_box.create

        with BuildPart() as part:
            Base()

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 20, 10), bbox.size)
        self.assertAlmostEqual(20 * 20 * 5 + 10 * 10 * 5, part.part.volume)

    def test_base_1_2(self, base_mock: MagicMock, platform_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create
        platform_mock_box = mocks.BoxAsMock(10, 10, 5)
        platform_mock.side_effect = platform_mock_box.create

        with BuildPart() as part:
            Base([[True], [True]])

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 62, 10), bbox.size)
        self.assertAlmostEqual(20 * 20 * 5 * 2 + 10 * 10 * 5, part.part.volume)

    def test_base_2_1(self, base_mock: MagicMock, platform_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create
        platform_mock_box = mocks.BoxAsMock(10, 10, 5)
        platform_mock.side_effect = platform_mock_box.create

        with BuildPart() as part:
            Base([[True, True]])

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(62, 20, 10), bbox.size)
        self.assertAlmostEqual(20 * 20 * 5 * 2 + 10 * 10 * 5, part.part.volume)

    def test_base_2_2(self, base_mock: MagicMock, platform_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create
        platform_mock_box = mocks.BoxAsMock(10, 10, 5)
        platform_mock.side_effect = platform_mock_box.create

        with BuildPart() as part:
            Base([[True, True], [True, True]])

        base_mock.assert_called_once_with(features=[], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(62, 62, 10), bbox.size)
        self.assertAlmostEqual(20 * 20 * 5 * 4 + 10 * 10 * 5, part.part.volume)

    def test_base_magnet_screw(self, base_mock: MagicMock, platform_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create
        platform_mock_box = mocks.BoxAsMock(10, 10, 5)
        platform_mock.side_effect = platform_mock_box.create
        feature_1 = MagicMock()
        feature_2 = MagicMock()

        with BuildPart() as part:
            Base([[True]], features=[feature_1, feature_2])

        base_mock.assert_called_once_with(features=[feature_1, feature_2], mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 20, 10), bbox.size)
        self.assertAlmostEqual(20 * 20 * 5 + 10 * 10 * 5, part.part.volume)


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
        self.assertEqual(Vector(41.5, 41.5, 5.0035533905933), bbox.size)
        self.assertAlmostEqual(7296.618846481421, part.part.volume)

    def test_baseblock_one_feature(self) -> None:
        feature = MagicMock(spec=ObjectFeature)

        with BuildPart() as part:
            BaseBlock(features=feature)

        feature.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(41.5, 41.5, 5.0035533905933), bbox.size)
        self.assertAlmostEqual(7296.618846481421, part.part.volume)

    def test_baseblock_multiple_features(self) -> None:
        feature_1 = MagicMock(spec=ObjectFeature)
        feature_2 = MagicMock(spec=ObjectFeature)

        with BuildPart() as part:
            BaseBlock(features=[feature_1, feature_2])

        feature_1.apply.assert_called_once()
        feature_2.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(41.5, 41.5, 5.0035533905933), bbox.size)
        self.assertAlmostEqual(7296.618846481421, part.part.volume)


class BaseBlockPlatformTest(testutils.UtilTestCase):
    def test_baseblockplatform(self) -> None:
        with BuildPart() as part:
            BaseBlockPlatform()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42, 42, 7.8035533905933), bbox.size)
        self.assertAlmostEqual(12235.818846481427, part.part.volume)

    def test_baseblockplatform_one_feature(self) -> None:
        feature = MagicMock(spec=ObjectFeature)

        with BuildPart() as part:
            BaseBlockPlatform(features=feature)

        feature.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42, 42, 7.8035533905933), bbox.size)
        self.assertAlmostEqual(12235.818846481427, part.part.volume)

    def test_baseblockplatform_multiple_features(self) -> None:
        feature_1 = MagicMock(spec=ObjectFeature)
        feature_2 = MagicMock(spec=ObjectFeature)

        with BuildPart() as part:
            BaseBlockPlatform(features=[feature_1, feature_2])

        feature_1.apply.assert_called_once()
        feature_2.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42, 42, 7.8035533905933), bbox.size)
        self.assertAlmostEqual(12235.818846481427, part.part.volume)
