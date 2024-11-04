import testutils
from build123d import Align, Axis, Box, BuildPart, CenterOf, Mode, Vector

from gridfinity_build123d.feature_locations import (
    BottomCorners,
    BottomMiddle,
    BottomSides,
    TopCorners,
    TopMiddle,
)


class TopMiddleTest(testutils.UtilTestCase):
    def test_topmiddle(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)
            with TopMiddle().apply_to(part.part):
                Box(
                    1,
                    1,
                    1,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT,
                )

        wires = part.faces().sort_by(Axis.Z)[-1].inner_wires()
        self.assertEqual(1, len(wires))

        self.assertEqual(Vector(0, 0, 15), wires[0].center(CenterOf.BOUNDING_BOX))

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 1, part.part.volume)


class BottomMiddleTest(testutils.UtilTestCase):
    def test_bottommiddle(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)
            with BottomMiddle().apply_to(part.part):
                Box(
                    1,
                    1,
                    1,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT,
                )
        wires = part.faces().sort_by(Axis.Z)[0].inner_wires()
        self.assertEqual(1, len(wires))

        self.assertEqual(Vector(0, 0, -15), wires[0].center(CenterOf.BOUNDING_BOX))

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 1, part.part.volume)


class BottomCornersTest(testutils.UtilTestCase):
    def test_bottomcorners(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)

            with BottomCorners().apply_to(part.part):
                Box(
                    1,
                    1,
                    1,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT,
                )

        faces = part.faces().sort_by(Axis.Z)[0].inner_wires()

        self.assertEqual(4, len(faces))
        locations = [
            Vector(17, 17, -15),
            Vector(-17, 17, -15),
            Vector(17, -17, -15),
            Vector(-17, -17, -15),
        ]

        for face in faces:
            self.assertIn(face.center(CenterOf.BOUNDING_BOX), locations)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 4, part.part.volume)


class TopCornersTest(testutils.UtilTestCase):
    def test_topcorners(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)

            with TopCorners().apply_to(part.part):
                Box(
                    1,
                    1,
                    1,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT,
                )

        faces = part.faces().sort_by(Axis.Z)[-1].inner_wires()

        self.assertEqual(4, len(faces))
        locations = [
            Vector(17, 17, 15),
            Vector(-17, 17, 15),
            Vector(17, -17, 15),
            Vector(-17, -17, 15),
        ]

        for face in faces:
            self.assertIn(face.center(CenterOf.BOUNDING_BOX), locations)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 4, part.part.volume)


class BottomSidesTest(testutils.UtilTestCase):
    def test_bottomsides(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)

            with BottomSides(offset=1).apply_to(
                part.part,
            ):
                Box(
                    1,
                    2,
                    3,
                    align=(Align.CENTER, Align.MIN, Align.MAX),
                    mode=Mode.SUBTRACT,
                )

        wires = part.faces().sort_by(Axis.Z)[0].inner_wires()

        self.assertEqual(4, len(wires))
        locations = [
            Vector(23, 0, -15),
            Vector(-23, 0, -15),
            Vector(0, 23, -15),
            Vector(0, -23, -15),
        ]

        for face in wires:
            self.assertIn(face.center(CenterOf.BOUNDING_BOX), locations)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 4 * 3 * 2, part.part.volume)

    def test_bottomsides_offset(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)

            with BottomSides(offset=2).apply_to(
                part.part,
            ):
                Box(
                    1,
                    2,
                    3,
                    align=(Align.CENTER, Align.MIN, Align.MAX),
                    mode=Mode.SUBTRACT,
                )

        wires = part.faces().sort_by(Axis.Z)[0].inner_wires()

        self.assertEqual(4, len(wires))
        locations = [
            Vector(22, 0, -15),
            Vector(-22, 0, -15),
            Vector(0, 22, -15),
            Vector(0, -22, -15),
        ]

        for face in wires:
            self.assertIn(face.center(CenterOf.BOUNDING_BOX), locations)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 4 * 3 * 2, part.part.volume)

    def test_bottomsides_multi_side(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 30)

            with BottomSides(nr_x=2, nr_y=3, offset=1).apply_to(
                part.part,
            ):
                Box(
                    1,
                    2,
                    3,
                    align=(Align.CENTER, Align.MIN, Align.MAX),
                    mode=Mode.SUBTRACT,
                )

        wires = part.faces().sort_by(Axis.Z)[0].inner_wires()

        self.assertEqual(10, len(wires))
        wire_locs = [
            Vector(-12.5, -23.0, -15.0),
            Vector(-23.0, -(16 + 2 / 3), -15.0),
            Vector(12.5, -23.0, -15.0),
            Vector(23.0, -(16 + 2 / 3), -15.0),
            Vector(-23.0, 0, -15.0),
            Vector(-23.0, 16 + 2 / 3, -15.0),
            Vector(-12.5, 23.0, -15.0),
            Vector(23.0, 0, -15.0),
            Vector(23.0, 16 + 2 / 3, -15.0),
            Vector(12.5, 23.0, -15.0),
        ]

        for wire in wires:
            self.assertAlmostIn(wire.center(CenterOf.BOUNDING_BOX), wire_locs)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 30), bbox.size)
        self.assertAlmostEqual(50 * 50 * 30 - 10 * 3 * 2, part.part.volume)
