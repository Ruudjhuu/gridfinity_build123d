from build123d import BuildPart
from gridfinity_build123d import BasePlateEqual

import testutils


class BasePlateTest(testutils.UtilTestCase):
    def test_base_plate_skeleton(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=3)
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((84, 126, 4.65), bbox.size)
        self.assertEqual(9935.172368218784, part.part.area)
        self.assertEqual(7684.943883967003, part.part.volume)
