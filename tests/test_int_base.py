import testutils
from gridfinity_build123d import (
    Base,
    BaseEqual,
    Corners,
    Direction,
    MagnetHole,
    ScrewHole,
)


class BaseTest(testutils.UtilTestCase):
    def test_base_default(self) -> None:
        part = BaseEqual(grid_x=2, grid_y=3)

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)
        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(24921.63727353625, part.area)
        self.assertAlmostEqual(73106.17327094806, part.volume)

    def test_base_magnets(self) -> None:
        part = BaseEqual(
            grid_x=2,
            grid_y=3,
            features=MagnetHole(Corners(Direction.BOT)),
        )

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(26097.84956304029, part.area)
        self.assertAlmostEqual(71194.82830050986, part.volume)

    def test_base_magnets_and_screws(self) -> None:
        part = BaseEqual(
            grid_x=2,
            grid_y=3,
            features=[
                MagnetHole(Corners(Direction.BOT)),
                ScrewHole(Corners(Direction.BOT)),
            ],
        )

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)
        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(26912.15037885079, part.area)
        self.assertAlmostEqual(70584.10268864287, part.volume)

    def test_base_grid(self) -> None:
        grid = [[True, True], [True, False]]
        part = Base(grid)
        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 83.5, 7.803553390593281), bbox.size, 6)
        self.assertAlmostEqual(12736.480548641217, part.area, 6)
        self.assertAlmostEqual(36447.00110003971, part.volume, 6)
