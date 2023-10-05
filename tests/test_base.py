import unittest
from build123d import BuildPart, Vector, BuildSketch
import gridfinity_build123d

# Not needed for testing but handy for developing
try:
    from ocp_vscode import set_port  # type: ignore

    set_port(3939)
except ImportError:
    # ignore if not installed
    pass


class BaseTest(unittest.TestCase):
    def test_base(self) -> None:
        with BuildPart() as part:
            gridfinity_build123d.base.Base(gridfinity_build123d.base.Grid(1, 1))

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(41.5000002, 41.5000002, 7.803553490593282), bbox.size)
        self.assertEqual(11866.900539226841, part.part.volume)

    def test_base_1_3(self) -> None:
        with BuildPart() as part:
            gridfinity_build123d.base.Base(gridfinity_build123d.base.Grid(1, 3))

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(41.5000002, 125.5000002, 7.803553490593282), bbox.size)
        self.assertEqual(35995.14186616732, part.part.volume)

    def test_base_3_1(self) -> None:
        with BuildPart() as part:
            gridfinity_build123d.base.Base(gridfinity_build123d.base.Grid(3, 1))

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(125.5000002, 41.5000002, 7.803553490593282), bbox.size)
        self.assertEqual(35995.1418661573, part.part.volume)

    def test_base_3_3(self) -> None:
        with BuildPart() as part:
            gridfinity_build123d.base.Base(gridfinity_build123d.base.Grid(3, 3))

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(125.5000002, 125.5000002, 7.803553490593282), bbox.size)
        self.assertEqual(108622.32795093776, part.part.volume)

    def test_base_2_2_magnet_screw(self) -> None:
        with BuildPart() as part:
            gridfinity_build123d.base.Base(gridfinity_build123d.base.Grid(2, 2), True, True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(83.5000002, 83.5000002, 7.803553490593282), bbox.size)
        self.assertEqual(46438.49766741423, part.part.volume)


class BaseBlockTest(unittest.TestCase):
    def test_baseblock(self) -> None:
        """Test creation of a default baseblock."""
        with BuildPart() as part:
            gridfinity_build123d.base.BaseBlock()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(12124.736189562584, part.part.volume)

    def test_baseblock_magnets(self) -> None:
        """Test creation of a basebock with magnet holes."""
        with BuildPart() as part:
            gridfinity_build123d.base.BaseBlock(magnets=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11806.178694488577, part.part.volume)

    def test_baseblock_screw_holes(self) -> None:
        """Test creation of a basebock with screw holes."""
        with BuildPart() as part:
            gridfinity_build123d.base.BaseBlock(screwholes=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11955.090186268735, part.part.volume)

    def test_baseblock_magnet_and_screw_holes(self) -> None:
        """Test creation of a basebock with magnet and screw holes."""
        with BuildPart() as part:
            gridfinity_build123d.base.BaseBlock(magnets=True, screwholes=True)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42.0, 42.0, 7.803553390593281), bbox.size)
        self.assertEqual(11704.391092512273, part.part.volume)


class StackProfileTest(unittest.TestCase):
    def test_profile(self) -> None:
        """Test creation of stacking profile"""
        with BuildSketch() as sketch:
            gridfinity_build123d.base.StackProfile()

        bbox = sketch.sketch.bounding_box()
        self.assertEqual(Vector(2.5999999999999996, 4.4, 0), bbox.size)
        self.assertEqual(6.8, sketch.sketch.area)
