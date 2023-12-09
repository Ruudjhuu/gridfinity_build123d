import testutils
from build123d import BuildPart
from gridfinity_build123d import (
    BasePlateBlockFrame,
    BasePlateBlockFull,
    BasePlateEqual,
    MagnetHole,
    ScrewHoleCountersink,
    Weighted,
)


class BasePlateTest(testutils.UtilTestCase):
    def test_base_plate_frame(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=3, baseplate_block=BasePlateBlockFrame())
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((84, 126, 4.65), bbox.size)
        self.assertAlmostEqual(9935.172368218784, part.part.area)
        self.assertAlmostEqual(7684.943883967003, part.part.volume)

    def test_base_plate_weighted(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(
                size_x=3,
                size_y=2,
                baseplate_block=BasePlateBlockFull(
                    features=[
                        MagnetHole(),
                        ScrewHoleCountersink(),
                        Weighted(),
                    ],
                ),
            )
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((126.0, 84.0, 11.05), bbox.size)
        self.assertAlmostEqual(32629.38237429975, part.part.area)
        self.assertAlmostEqual(57020.96113525161, part.part.volume)
