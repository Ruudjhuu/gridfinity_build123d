import testutils
from gridfinity_build123d import (
    BasePlateBlockFull,
    BasePlateEqual,
    BottomCorners,
    BottomMiddle,
    BottomSides,
    GridfinityRefinedConnectionCutout,
    GridfinityRefinedMagnetHolePressfit,
    GridfinityRefinedScrewHole,
)


class RefinedBaseTest(testutils.UtilTestCase):
    def test_refined(self) -> None:
        part = BasePlateEqual(
            size_x=2,
            size_y=3,
            baseplate_block=BasePlateBlockFull(
                bottom_height=3,
                features=[
                    GridfinityRefinedScrewHole(BottomMiddle()),
                    GridfinityRefinedMagnetHolePressfit(BottomCorners()),
                ],
            ),
            features=GridfinityRefinedConnectionCutout(BottomSides(nr_x=2, nr_y=3)),
        )

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((84, 126, 7.65), bbox.size, 5)
        self.assertAlmostEqual(25953.3508979137, part.area)
        self.assertAlmostEqual(30090.400157643642, part.volume)
