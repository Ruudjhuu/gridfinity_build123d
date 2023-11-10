from build123d import BuildPart, BuildSketch, Polyline, BuildLine, make_face, fillet
from gridfinity_build123d import Bin, Base, MagnetHole, ScrewHole

from gridfinity_build123d.utils import Utils, Direction
from gridfinity_build123d.bin import (
    Label,
    Compartment,
    CompartmentsEqual,
    Compartments,
    StackingLip,
)

import testutils


class BinTest(testutils.UtilTestCase):
    def test_bin_standard(self) -> None:
        with BuildPart() as part:
            Base(grid_x=2, grid_y=2, features=[MagnetHole(), ScrewHole()])

            cmp_type = [Compartment(features=[Label()])] * 8
            compartments = CompartmentsEqual(div_x=3, div_y=2, compartment_list=cmp_type)
            Bin(
                face=Utils.get_face_by_direction(Direction.TOP),
                height=Utils.remaining_gridfinity_height(5),
                compartments=compartments,
                lip=StackingLip(),
            )

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 83.5, 39.11715738752539), bbox.size, 6)
        self.assertEqual(52698.90834191521, part.part.area)
        self.assertEqual(85901.69007299552, part.part.volume)

    def test_bin_unequal(self) -> None:
        pass
        with BuildPart():
            Base(grid_x=3, grid_y=3, features=[MagnetHole(), ScrewHole()])

            cmp_type = [Compartment(features=[Label()])] * 7
            cmp_placement = [
                [1, 1, 2, 6, 3],
                [1, 1, 5, 6, 5],
                [1, 1, 4, 6, 7],
            ]
            compartments = Compartments(grid=cmp_placement, compartment_list=cmp_type)
            Bin(
                face=Utils.get_face_by_direction(Direction.TOP),
                height=Utils.remaining_gridfinity_height(5),
                compartments=compartments,
                lip=StackingLip(),
            )

    def test_bin_weird_shape(self) -> None:
        pass
        with BuildPart():
            Base(grid_x=3, grid_y=3, features=[MagnetHole(), ScrewHole()])
            with BuildSketch() as sketch:
                with BuildLine():
                    Polyline((0, 0), (100, 0), (100, 100), (50, 100), (50, 50), (0, 50), close=True)
                make_face()
                fillet(sketch.sketch.vertices(), radius=2)
            cmp_type = [Compartment(features=[Label()])] * 7
            cmp_placement = [
                [1, 1, 2, 6, 3],
                [1, 1, 5, 6, 5],
                [1, 1, 4, 6, 7],
            ]
            compartments = Compartments(grid=cmp_placement, compartment_list=cmp_type)
            Bin(
                face=Utils.get_face_by_direction(Direction.TOP),
                height=Utils.remaining_gridfinity_height(5),
                compartments=compartments,
                lip=StackingLip(),
            )
