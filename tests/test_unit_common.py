import unittest

from build123d import BuildSketch, Vector

from gridfinity_build123d.common import Grid, StackProfile


class GridTest(unittest.TestCase):
    def test_grid_1_1(self) -> None:
        grid = Grid(1, 1)

        self.assertEqual(1, grid.X)
        self.assertEqual(42, grid.X_mm)
        self.assertEqual(41.5, grid.X_mm_real)

        self.assertEqual(1, grid.Y)
        self.assertEqual(42, grid.Y_mm)
        self.assertEqual(41.5, grid.Y_mm_real)

    def test_grid_1_2(self) -> None:
        grid = Grid(1, 2)

        self.assertEqual(1, grid.X)
        self.assertEqual(42, grid.X_mm)
        self.assertEqual(41.5, grid.X_mm_real)

        self.assertEqual(2, grid.Y)
        self.assertEqual(84, grid.Y_mm)
        self.assertEqual(83.5, grid.Y_mm_real)

    def test_grid_2_1(self) -> None:
        grid = Grid(2, 1)

        self.assertEqual(2, grid.X)
        self.assertEqual(84, grid.X_mm)
        self.assertEqual(83.5, grid.X_mm_real)

        self.assertEqual(1, grid.Y)
        self.assertEqual(42, grid.Y_mm)
        self.assertEqual(41.5, grid.Y_mm_real)


class StackProfileTest(unittest.TestCase):
    def test_profile(self) -> None:
        """Test creation of stacking profile"""
        with BuildSketch() as sketch:
            StackProfile()

        bbox = sketch.sketch.bounding_box()
        self.assertEqual(Vector(2.5999999999999996, 4.4, 0), bbox.size)
        self.assertEqual(6.8, sketch.sketch.area)
