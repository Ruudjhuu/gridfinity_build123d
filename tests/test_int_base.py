from unittest import TestCase
from build123d import Vector
from gridfinity_build123d import ScrewHole, MagnetHole, Base


class BaseTest(TestCase):
    def test_base_default(self) -> None:
        part = Base(grid_x=2, grid_y=3)

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)
        bbox = part.bounding_box()
        self.assertEqual(Vector(83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertEqual(24921.63727353625, part.area)
        self.assertEqual(73106.17327094806, part.volume)

    def test_base_magnets(self) -> None:
        part = Base(grid_x=2, grid_y=3, features=[MagnetHole()])

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)
        bbox = part.bounding_box()
        self.assertEqual(Vector(83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertEqual(26097.84956304029, part.area)
        self.assertEqual(71194.82830050986, part.volume)

    def test_base_magnets_and_screws(self) -> None:
        part = Base(grid_x=2, grid_y=3, features=[MagnetHole(), ScrewHole()])

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)
        bbox = part.bounding_box()
        self.assertEqual(Vector(83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertEqual(26912.15037885079, part.area)
        self.assertEqual(70584.10268864287, part.volume)
