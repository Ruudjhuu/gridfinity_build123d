import testutils

from gridfinity_build123d import (
    Base,
    BaseEqual,
    Bin,
    BottomCorners,
    Label,
    MagnetHole,
    ScrewHole,
)
from gridfinity_build123d.bin import StackingLip
from gridfinity_build123d.compartments import (
    Compartment,
    Compartments,
    CompartmentsEqual,
)


class BinTest(testutils.UtilTestCase):
    def test_bin_standard(self) -> None:
        part = Bin(
            base=BaseEqual(
                grid_x=2,
                grid_y=2,
                features=[
                    MagnetHole(BottomCorners()),
                    ScrewHole(BottomCorners()),
                ],
            ),
            height_in_units=5,
            compartments=CompartmentsEqual(
                div_x=3,
                div_y=2,
                compartment_list=Compartment(features=Label()),
            ),
            lip=StackingLip(),
        )

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((83.5, 83.5, 39.11715738752539), bbox.size, 5)
        self.assertAlmostEqual(52109.547064557606, part.area)
        self.assertAlmostEqual(77389.77243336473, part.volume)

    def test_bin_different_compartments(self) -> None:
        cmp_placement = [
            [1, 1, 2, 6, 3],
            [1, 1, 5, 6, 5],
            [1, 1, 4, 6, 7],
        ]
        part = Bin(
            base=BaseEqual(
                grid_x=3,
                grid_y=3,
                features=[
                    MagnetHole(BottomCorners()),
                    ScrewHole(BottomCorners()),
                ],
            ),
            height_in_units=5,
            compartments=Compartments(
                grid=cmp_placement,
                compartment_list=Compartment(features=Label()),
            ),
            lip=StackingLip(),
        )

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((125.5, 125.5, 39.11715738752539), bbox.size, 6)
        self.assertAlmostEqual(93165.2920812887, part.area, 6)
        self.assertAlmostEqual(178103.94250675887, part.volume, 6)

    def test_bin_random_shape(self) -> None:
        base_grid = [
            [True, True, True],
            [True, False, False],
            [True, True, True],
            [False, False, True],
            [True, True, True],
        ]

        cmp_placement = [
            [1, 1, 2],
            [3, 0, 0],
            [3, 4, 7],
            [0, 0, 7],
            [5, 5, 6],
        ]

        part = Bin(
            base=Base(
                grid=base_grid,
                features=[
                    MagnetHole(BottomCorners()),
                    ScrewHole(BottomCorners()),
                ],
            ),
            height_in_units=5,
            compartments=Compartments(
                grid=cmp_placement,
                compartment_list=Compartment(features=[Label()]),
                outer_wall=1.2,
                inner_wall=2.4,
            ),
            lip=StackingLip(),
        )

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((125.5, 209.5, 39.11715728752539), bbox.size, 6)
        self.assertAlmostEqual(127460.07556303134, part.area, 5)
        self.assertAlmostEqual(206846.8044154954, part.volume, 5)
