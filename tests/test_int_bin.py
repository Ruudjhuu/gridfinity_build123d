from build123d import BuildPart
from gridfinity_build123d import Bin, Base, MagnetHole, ScrewHole, BaseEqual

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
            BaseEqual(grid_x=2, grid_y=2, features=[MagnetHole(), ScrewHole()])

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
        self.assertAlmostEqual(52698.90834191521, part.part.area)
        self.assertAlmostEqual(85901.69007299552, part.part.volume)

    def test_bin_different_compartments(self) -> None:
        with BuildPart() as part:
            BaseEqual(grid_x=3, grid_y=3, features=[MagnetHole(), ScrewHole()])
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

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((125.5, 125.5, 39.11715738752539), bbox.size, 6)
        self.assertAlmostEqual(93907.58222849401, part.part.area)
        self.assertAlmostEqual(188455.98521784923, part.part.volume)

    def test_bin_random_shape(self) -> None:
        with BuildPart() as part:
            base_grid = [
                [True, True, True],
                [True, False, False],
                [True, True, True],
                [False, False, True],
                [True, True, True],
            ]
            Base(grid=base_grid, features=[MagnetHole(), ScrewHole()])
            cmp_type = [Compartment(features=[Label()])] * 7
            cmp_placement = [
                [1, 1, 2],
                [3, 0, 0],
                [3, 4, 7],
                [0, 0, 7],
                [5, 5, 6],
            ]
            compartments = Compartments(
                grid=cmp_placement, compartment_list=cmp_type, outer_wall=1.2, inner_wall=2.4
            )
            Bin(
                face=Utils.get_face_by_direction(Direction.TOP),
                height=Utils.remaining_gridfinity_height(5),
                compartments=compartments,
                lip=StackingLip(),
            )

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((125.5, 209.5, 39.11715728752539), bbox.size, 6)
        self.assertAlmostEqual(129498.15931818407, part.part.area)
        self.assertAlmostEqual(226612.36960795842, part.part.volume)
