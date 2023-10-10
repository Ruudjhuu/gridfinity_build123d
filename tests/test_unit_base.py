import unittest
from unittest.mock import patch, MagicMock, ANY
from build123d import BuildPart, Vector, BuildSketch
from gridfinity_build123d.base import Base, BaseBlock, Grid, StackProfile
import mocks

# Not needed for testing but handy for developing
try:
    from ocp_vscode import set_port  # type: ignore

    set_port(3939)
except ImportError:
    # ignore if not installed
    pass


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
        self.assertEqual(1659.8229338221292, part.part.volume)

    def test_base_1_2(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(1, 2))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 39.5, 5), bbox.size)
        self.assertEqual(3609.822933822129, part.part.volume)

    def test_base_2_1(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(2, 1))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(39.5, 19.5, 5), bbox.size)
        self.assertEqual(3609.822933822129, part.part.volume)

    def test_base_2_2(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(2, 2))

        base_mock.assert_called_once_with(magnets=False, screwholes=False, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(39.5, 39.5, 5), bbox.size)
        self.assertEqual(7559.822933822127, part.part.volume)

    def test_base_magnet_screw(self, base_mock: MagicMock) -> None:
        mock_box = mocks.BoxAsMock(20, 20, 5)
        base_mock.side_effect = mock_box.create

        with BuildPart() as part:
            Base(Grid(1, 1), True, True)

        base_mock.assert_called_once_with(magnets=True, screwholes=True, mode=ANY)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(19.5, 19.5, 5), bbox.size)
        self.assertEqual(1659.8229338221292, part.part.volume)


class BaseBlockTest(unittest.TestCase):
    def test_baseblock(self) -> None:
        """Test creation of a default baseblock."""
        with BuildPart() as part:
            BaseBlock()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(12124.736189562584, part.part.volume)

    def test_baseblock_magnets(self) -> None:
        """Test creation of a basebock with magnet holes."""
        with BuildPart() as part:
            BaseBlock(magnets=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11806.178694488577, part.part.volume)

    def test_baseblock_screw_holes(self) -> None:
        """Test creation of a basebock with screw holes."""
        with BuildPart() as part:
            BaseBlock(screwholes=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11955.090186268735, part.part.volume)

    def test_baseblock_magnet_and_screw_holes(self) -> None:
        """Test creation of a basebock with magnet and screw holes."""
        with BuildPart() as part:
            BaseBlock(magnets=True, screwholes=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11704.391092512273, part.part.volume)


class StackProfileTest(unittest.TestCase):
    def test_profile(self) -> None:
        """Test creation of stacking profile"""
        with BuildSketch() as sketch:
            StackProfile()

        bbox = sketch.sketch.bounding_box()
        self.assertEqual(Vector(2.5999999999999996, 4.4, 0), bbox.size)
        self.assertEqual(6.8, sketch.sketch.area)
