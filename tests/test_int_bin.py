import testutils
from build123d import BuildPart
from gridfinity_build123d import Base, BaseEqual, Bin, Label, MagnetHole, ScrewHole
from gridfinity_build123d.bin import (
    Compartment,
    Compartments,
    CompartmentsEqual,
    StackingLip,
)
from gridfinity_build123d.utils import Direction, Utils


class BinTest(testutils.UtilTestCase):
    def test_bin_standard(self) -> None:
        with BuildPart() as part:
            BaseEqual(grid_x=2, grid_y=2, features=[MagnetHole(), ScrewHole()])

            cmp_type = Compartment(features=Label())
            compartments = CompartmentsEqual(
                div_x=3,
                div_y=2,
                compartment_list=cmp_type,
            )
            Bin(
                face=Utils.get_face_by_direction(part, Direction.TOP),
                height=Utils.remaining_gridfinity_height(part.part, 5),
                compartments=compartments,
                lip=StackingLip(),
            )

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 83.5, 39.11715738752539), bbox.size, 6)
        self.assertAlmostEqual(52184.71853839394, part.part.area)
        self.assertAlmostEqual(77131.4210499689, part.part.volume)

    def test_bin_different_compartments(self) -> None:
        with BuildPart() as part:
            BaseEqual(grid_x=3, grid_y=3, features=[MagnetHole(), ScrewHole()])
            cmp_type = Compartment(features=Label())
            cmp_placement = [
                [1, 1, 2, 6, 3],
                [1, 1, 5, 6, 5],
                [1, 1, 4, 6, 7],
            ]
            compartments = Compartments(grid=cmp_placement, compartment_list=cmp_type)
            Bin(
                face=Utils.get_face_by_direction(part, Direction.TOP),
                height=Utils.remaining_gridfinity_height(part.part, 5),
                compartments=compartments,
                lip=StackingLip(),
            )

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((125.5, 125.5, 39.11715738752539), bbox.size, 6)
        self.assertAlmostEqual(93236.35216913944, part.part.area)
        self.assertAlmostEqual(177834.82625303385, part.part.volume)

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
            cmp_type = Compartment(features=[Label()])
            cmp_placement = [
                [1, 1, 2],
                [3, 0, 0],
                [3, 4, 7],
                [0, 0, 7],
                [5, 5, 6],
            ]
            compartments = Compartments(
                grid=cmp_placement,
                compartment_list=cmp_type,
                outer_wall=1.2,
                inner_wall=2.4,
            )
            Bin(
                face=Utils.get_face_by_direction(part, Direction.TOP),
                height=Utils.remaining_gridfinity_height(part.part, 5),
                compartments=compartments,
                lip=StackingLip(),
            )

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((125.5, 209.5, 39.11715728752539), bbox.size, 6)
        self.assertAlmostEqual(127529.55165258361, part.part.area, 5)
        self.assertAlmostEqual(206666.87451716806, part.part.volume, 5)
