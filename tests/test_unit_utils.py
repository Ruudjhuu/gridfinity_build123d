from unittest import TestCase

from build123d import BuildPart, Box, add, Vector, BuildSketch, Axis

from gridfinity_build123d.utils import Utils, Attach, StackProfile, Direction


class StackProfileTest(TestCase):
    def test_profile(self) -> None:
        """Test creation of stacking profile"""
        with BuildSketch() as sketch:
            StackProfile()

        bbox = sketch.sketch.bounding_box()
        self.assertEqual(Vector(2.5999999999999996, 4.4, 0), bbox.size)
        self.assertEqual(6.8, sketch.sketch.area)


class UtilsAttachTest(TestCase):
    def test_attach_top(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.TOP)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 20), bbox.size)
        self.assertEqual(15, bbox.max.Z)

    def test_attach_bottom(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.BOTTOM)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 20), bbox.size)
        self.assertEqual(-15, bbox.min.Z)

    def test_attach_left(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.LEFT)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 10, 10), bbox.size)
        self.assertEqual(-15, bbox.min.X)

    def test_attach_right(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.RIGHT)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 10, 10), bbox.size)
        self.assertEqual(15, bbox.max.X)

    def test_attach_front(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.FRONT)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 20, 10), bbox.size)
        self.assertEqual(-15, bbox.min.Y)

    def test_attach_back(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.BACK)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 20, 10), bbox.size)
        self.assertEqual(15, bbox.max.Y)

    def test_attach_top_offset(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(box, Attach.TOP, 5)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 25), bbox.size)
        self.assertEqual(20, bbox.max.Z)

    def test_attach_no_context(self) -> None:
        obj = Box(10, 10, 10)
        self.assertRaises(RuntimeError, Utils.attach, obj, Attach.TOP)

    def test_attach_wrong_context(self) -> None:
        obj = Box(10, 10, 10)
        with BuildSketch():
            self.assertRaises(RuntimeError, Utils.attach, obj, Attach.TOP)

    def test_attach_empty_context(self) -> None:
        obj = Box(10, 10, 10)
        with BuildPart():
            self.assertRaises(ValueError, Utils.attach, obj, Attach.TOP)


class UtilsFaceByDirectionTest(TestCase):
    def test_utils_face_by_direction_top(self) -> None:
        with BuildPart():
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Z)[-1].center_location,
                Utils.get_face_by_direction(Direction.TOP).center_location,
            )

    def test_utils_face_by_direction_bot(self) -> None:
        with BuildPart():
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Z)[0].center_location,
                Utils.get_face_by_direction(Direction.BOT).center_location,
            )

    def test_utils_face_by_direction_right(self) -> None:
        with BuildPart():
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.X)[-1].center_location,
                Utils.get_face_by_direction(Direction.RIGHT).center_location,
            )

    def test_utils_face_by_direction_left(self) -> None:
        with BuildPart():
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.X)[0].center_location,
                Utils.get_face_by_direction(Direction.LEFT).center_location,
            )

    def test_utils_face_by_direction_back(self) -> None:
        with BuildPart():
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Y)[-1].center_location,
                Utils.get_face_by_direction(Direction.BACK).center_location,
            )

    def test_utils_face_by_direction_front(self) -> None:
        with BuildPart():
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Y)[0].center_location,
                Utils.get_face_by_direction(Direction.FRONT).center_location,
            )

    def test_utils_face_by_direction_no_context(self) -> None:
        self.assertRaises(RuntimeError, Utils.get_face_by_direction, Direction.FRONT)

    def test_utils_face_by_direction_wrong_builder(self) -> None:
        with BuildSketch():
            self.assertRaises(RuntimeError, Utils.get_face_by_direction, Direction.FRONT)

    def test_utils_face_by_direction_empty_builder(self) -> None:
        with BuildPart():
            self.assertRaises(ValueError, Utils.get_face_by_direction, Direction.FRONT)


class UtilsRemainingGridfinityHeightTest(TestCase):
    def test_remaining_gridfinity_height(self) -> None:
        with BuildPart():
            Box(10, 10, 10)
            self.assertEqual(4 * 7 - 10, Utils.remaining_gridfinity_height(4))

    def test_remaining_gridfinity_height_no_object(self) -> None:
        with BuildPart():
            self.assertEqual(4 * 7, Utils.remaining_gridfinity_height(4))

    def test_remaining_gridfinity_no_builder(self) -> None:
        self.assertRaises(RuntimeError, Utils.remaining_gridfinity_height, 4)

    def test_remaining_gridfinity_wrong_builder(self) -> None:
        with BuildSketch():
            self.assertRaises(RuntimeError, Utils.remaining_gridfinity_height, 4)
