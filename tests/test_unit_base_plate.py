from unittest.mock import ANY, MagicMock, patch

import mocks
import testutils
from build123d import BuildPart
from gridfinity_build123d.baseplate import (
    BasePlate,
    BasePlateBlock,
    BasePlateBlockFrame,
    BasePlateBlockFull,
    BasePlateBlockSkeleton,
    BasePlateEqual,
)
from gridfinity_build123d.features import Feature


class BasePlateBlockFrameTest(testutils.UtilTestCase):
    def test_base_plate_block_frame(self) -> None:
        with BuildPart() as part:
            BasePlateBlockFrame().create_obj()
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 4.65), bbox.size)
        self.assertAlmostEqual(1291.4682317566535, part.part.volume)

    def test_base_plate_block_frame_feature(self) -> None:
        feature = MagicMock(spec=Feature)

        with BuildPart() as part:
            BasePlateBlockFrame(features=feature).create_obj()

        feature.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 4.65), bbox.size)
        self.assertAlmostEqual(1291.4682317566535, part.part.volume)


class BasePlateBlockFullTest(testutils.UtilTestCase):
    def test_base_plate_block_frame(self) -> None:
        with BuildPart() as part:
            BasePlateBlockFull().create_obj()
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 11.05), bbox.size)
        self.assertAlmostEqual(12581.068231756662, part.part.volume)

    def test_base_plate_block_frame_height(self) -> None:
        with BuildPart() as part:
            BasePlateBlockFull(bottom_height=10).create_obj()
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 14.65), bbox.size)
        self.assertAlmostEqual(18931.46823175665, part.part.volume)

    def test_base_plate_block_frame_feature(self) -> None:
        feature = MagicMock(spec=Feature)

        with BuildPart() as part:
            BasePlateBlockFull(features=feature).create_obj()

        feature.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 11.05), bbox.size)
        self.assertAlmostEqual(12581.068231756662, part.part.volume)


@patch("gridfinity_build123d.baseplate.Utils.place_by_grid", autospec=True)
class BasePlateTest(testutils.UtilTestCase):
    def test_base_plate(self, place_mock: MagicMock) -> None:
        place_box = mocks.BoxAsMock(10, 10, 10)
        place_mock.side_effect = place_box.create

        grid = MagicMock()
        with BuildPart() as part:
            BasePlate(grid)

        place_mock.assert_called_once_with(ANY, grid)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(862.6548245743672, part.part.volume)

    def test_base_plate_bpblock(self, place_mock: MagicMock) -> None:
        place_box = mocks.BoxAsMock(10, 10, 10)
        place_mock.side_effect = place_box.create

        baseplate_block = MagicMock(spec=BasePlateBlock)
        bp_block_box = mocks.BoxAsMock(1, 1, 1)
        baseplate_block.create_obj.side_effect = bp_block_box.create

        grid = MagicMock()
        with BuildPart() as part:
            BasePlate(grid, baseplate_block)

        baseplate_block.create_obj.assert_called_once()
        place_mock.assert_called_once_with(bp_block_box.created_objects[0], grid)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(862.6548245743672, part.part.volume)

    def test_base_plate_features(self, place_mock: MagicMock) -> None:
        place_box = mocks.BoxAsMock(10, 10, 10)
        place_mock.side_effect = place_box.create
        feature = MagicMock(spec=Feature)

        grid = MagicMock()
        with BuildPart() as part:
            BasePlate(grid, features=feature)

        feature.apply.assert_called_once()

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(862.6548245743672, part.part.volume)


@patch("gridfinity_build123d.baseplate.BasePlate.__init__")
class BasePlateEqualTest(testutils.UtilTestCase):
    @patch("gridfinity_build123d.baseplate.BasePlateBlockFrame", autospec=True)
    def test_base_plate_equal(
        self,
        bplateblock_mock: MagicMock,
        bplate_mock: MagicMock,
    ) -> None:
        features = MagicMock(spec=Feature)

        BasePlateEqual(size_x=2, size_y=3, features=features)

        bplate_mock.assert_called_once_with(
            [[True, True], [True, True], [True, True]],
            bplateblock_mock.return_value,
            features,
            ANY,
            ANY,
            ANY,
        )

    def test_base_plate_equal_block(
        self,
        bplate_mock: MagicMock,
    ) -> None:
        block_mock = MagicMock(spec=BasePlateBlock)
        features = MagicMock(spec=Feature)

        BasePlateEqual(
            size_x=2,
            size_y=3,
            baseplate_block=block_mock,
            features=features,
        )

        bplate_mock.assert_called_once_with(
            [[True, True], [True, True], [True, True]],
            block_mock,
            features,
            ANY,
            ANY,
            ANY,
        )


class BasePlateBlockSkeletonTest(testutils.UtilTestCase):
    def test_baseplateblockskeleton(self) -> None:
        part = BasePlateBlockSkeleton().create_obj()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 11.05), bbox.size)
        self.assertAlmostEqual(6310.636342511634, part.volume)
