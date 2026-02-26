import testutils

from gridfinity_build123d import (
    Base,
    BaseEqual,
    BottomCorners,
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
        self.assertAlmostEqual(25006.586730587333, part.area)
        self.assertAlmostEqual(73087.8132896235, part.volume)

    def test_base_magnets(self) -> None:
        part = BaseEqual(
            grid_x=2,
            grid_y=3,
            features=MagnetHole(BottomCorners()),
        )

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(26182.799020091374, part.area)
        self.assertAlmostEqual(71176.46831917949, part.volume)

    def test_base_magnets_and_screws(self) -> None:
        part = BaseEqual(
            grid_x=2,
            grid_y=3,
            features=[
                MagnetHole(BottomCorners()),
                ScrewHole(BottomCorners()),
            ],
        )

        self.assertTrue(part.is_valid)
        self.assertTrue(part.is_manifold)
        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 125.5, 7.803553390593281), bbox.size)
        self.assertAlmostEqual(26771.708922859758, part.area)
        self.assertAlmostEqual(70734.78589210319, part.volume)

    def test_base_grid(self) -> None:
        grid = [[True, True], [True, False]]
        part = Base(grid)
        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 83.5, 7.803553390593281), bbox.size, 6)
        self.assertAlmostEqual(12760.445457710146, part.area, 6)
        self.assertAlmostEqual(36439.15675017939, part.volume, 6)
