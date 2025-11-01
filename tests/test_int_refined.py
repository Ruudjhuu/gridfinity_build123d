import testutils

from gridfinity_build123d import (
    BaseEqual,
    BasePlateBlockFull,
    BasePlateEqual,
    Bin,
    BottomCorners,
    BottomMiddle,
    BottomSides,
    Compartment,
    CompartmentsEqual,
    GridfinityRefinedConnectionCutout,
    GridfinityRefinedMagnetHolePressfit,
    GridfinityRefinedMagnetHoleSide,
    GridfinityRefinedScrewHole,
    GridfinityRefinedThreadedScrewHole,
)


class RefinedBaseTest(testutils.UtilTestCase):
    def test_refined_base(self) -> None:
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


class RefinedBinTest(testutils.UtilTestCase):
    def test_refined_bin(self) -> None:
        part = Bin(
            BaseEqual(
                features=[
                    GridfinityRefinedThreadedScrewHole(BottomMiddle()),
                    GridfinityRefinedMagnetHoleSide(BottomCorners()),
                ],
            ),
            height_in_units=5,
            compartments=CompartmentsEqual(Compartment()),
        )

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((41.5, 41.5, 35), bbox.size, 5)
        self.assertAlmostEqual(13695.555513234409, part.area, 5)
        self.assertAlmostEqual(15003.122870855901, part.volume, 5)
