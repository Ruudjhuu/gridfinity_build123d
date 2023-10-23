import unittest
from unittest.mock import patch, MagicMock, ANY
from build123d import BuildPart, Vector
from gridfinity_build123d.base import Base, BaseBlock
from gridfinity_build123d.common import Grid
import mocks


@patch("gridfinity_build123d.base.BaseBlock", autospec=True)
class BaseTest(unittest.TestCase):
    def test_base(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(1, 1))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 19.5, 5), bbox.size)
        self.assertEqual(1840.8932334555323, part.part.volume)

    def test_base_1_2(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(1, 2))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 39.5, 5), bbox.size)
        self.assertEqual(3790.893233455532, part.part.volume)

    def test_base_2_1(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(2, 1))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(39.5, 19.5, 5), bbox.size)
        self.assertEqual(3790.893233455532, part.part.volume)

    def test_base_2_2(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(2, 2))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(39.5, 39.5, 5), bbox.size)
        self.assertEqual(7740.893233455531, part.part.volume)

    def test_base_magnet_screw(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(1, 1), True, True)

        base_mock.assert_called_once_with(magnets=True, screwholes=True, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 19.5, 5), bbox.size)
        self.assertEqual(1840.8932334555323, part.part.volume)


class BaseBlockTest(unittest.TestCase):
    def test_baseblock(self) -> None:
        """Test creation of a default baseblock."""
        with BuildPart() as part:
            BaseBlock()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(12240.821519721352, part.part.volume)

    def test_baseblock_magnets(self) -> None:
        """Test creation of a basebock with magnet holes."""
        with BuildPart() as part:
            BaseBlock(magnets=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11922.264024647338, part.part.volume)

    def test_baseblock_screw_holes(self) -> None:
        """Test creation of a basebock with screw holes."""
        with BuildPart() as part:
            BaseBlock(screwholes=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(12071.175516427502, part.part.volume)

    def test_baseblock_magnet_and_screw_holes(self) -> None:
        """Test creation of a basebock with magnet and screw holes."""
        with BuildPart() as part:
            BaseBlock(magnets=True, screwholes=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11820.476422671034, part.part.volume)
