import testutils
from build123d import Axis, BuildPart

from gridfinity_build123d import (
    BasePlateBlockFrame,
    BasePlateBlockFull,
    BasePlateBottomSideRound,
    BasePlateEqual,
    BottomCorners,
    BottomMiddle,
    Direction,
    MagnetHole,
    ScrewHoleCountersink,
    TopCorners,
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
                        MagnetHole(TopCorners()),
                        ScrewHoleCountersink(BottomCorners()),
                        Weighted(BottomMiddle()),
                    ],
                ),
            )
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((126.0, 84.0, 11.05), bbox.size)
        self.assertAlmostEqual(32629.38237429975, part.part.area)
        self.assertAlmostEqual(57020.96113525161, part.part.volume)

    def test_base_plate_bottom_side_round_direction(self) -> None:
        base_plate = BasePlateEqual(size_x=2, size_y=2)
        base_plate_rounded = BasePlateEqual(
            size_x=2,
            size_y=2,
            features=BasePlateBottomSideRound(
                radius=1,
                direction=[
                    Direction.FRONT,
                    Direction.BACK,
                    Direction.LEFT,
                    Direction.RIGHT,
                ],
            ),
        )
        base_plate_side_rounded = BasePlateEqual(
            size_x=2,
            size_y=2,
            features=BasePlateBottomSideRound(radius=1, direction=Direction.FRONT),
        )

        bbox = base_plate.bounding_box()
        bbox_rounded = base_plate_rounded.bounding_box()
        self.assertVectorAlmostEqual(
            (bbox.size.X, bbox.size.Y, bbox.size.Z),
            bbox_rounded.size,
            places=6,
        )

        self.assertLess(base_plate_side_rounded.volume, base_plate.volume)
        self.assertLess(base_plate_rounded.volume, base_plate_side_rounded.volume)

    def test_base_plate_bottom_side_round_front_only_does_not_change_back(self) -> None:
        """Make sure when we round only the front, the back face area is unchanged."""
        base_plate = BasePlateEqual(size_x=2, size_y=2)
        front_rounded = BasePlateEqual(
            size_x=2,
            size_y=2,
            features=BasePlateBottomSideRound(radius=1, direction=Direction.FRONT),
        )

        base_faces_y = base_plate.faces().filter_by(Axis.Y).sort_by(Axis.Y)
        rounded_faces_y = front_rounded.faces().filter_by(Axis.Y).sort_by(Axis.Y)

        # FRONT is min-Y, BACK is max-Y.
        self.assertLess(rounded_faces_y[0].area, base_faces_y[0].area)
        self.assertAlmostEqual(rounded_faces_y[-1].area, base_faces_y[-1].area, places=6)
