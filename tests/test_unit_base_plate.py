from unittest.mock import MagicMock, patch, ANY

from build123d import BuildPart

from gridfinity_build123d.baseplate import BasePlate, BasePlateEqual, BasePlateBlock

import testutils
import mocks


class BasePlateBlockTest(testutils.UtilTestCase):
    def test_base_plate_block(self) -> None:
        with BuildPart() as part:
            BasePlateBlock()
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((42, 42, 4.65), bbox.size)
        self.assertAlmostEqual(1291.4682317566535, part.part.volume)


@patch("gridfinity_build123d.baseplate.Utils.place_by_grid", autospec=True)
@patch("gridfinity_build123d.baseplate.BasePlateBlock", autospec=True)
class BasePlateTest(testutils.UtilTestCase):
    def test_base_plate(self, bplate_mock: MagicMock, place_mock: MagicMock) -> None:
        bplate_box = mocks.BoxAsMock(20, 20, 20)
        place_box = mocks.BoxAsMock(10, 10, 10)
        bplate_mock.side_effect = bplate_box.create
        place_mock.side_effect = place_box.create

        grid = [[True, False]]
        with BuildPart() as part:
            BasePlate(grid)

        bplate_mock.assert_called_once()
        place_mock.assert_called_once_with(bplate_box.created_objects[0], grid)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(862.6548245743672, part.part.volume)


@patch("gridfinity_build123d.baseplate.BasePlate.__init__")
class BasePlateEqualTest(testutils.UtilTestCase):
    def test_base_plate_equal(self, bplate_mock: MagicMock) -> None:
        BasePlateEqual(size_x=2, size_y=3)
        bplate_mock.assert_called_once_with(
            [[True, True], [True, True], [True, True]], ANY, ANY, ANY
        )
