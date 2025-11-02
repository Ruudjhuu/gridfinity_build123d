from enum import Enum, auto
from unittest import TestCase

import testutils
from build123d import Axis, Box, BuildPart, BuildSketch, Vector, add

from gridfinity_build123d.utils import (
    Attach,
    Direction,
    StackProfile,
    UnsuportedEnumValueError,
    Utils,
)


class UnsuportedEnumValueErrorTest(testutils.UtilTestCase):
    def test_enum_value_error(self) -> None:
        class TestEnum(Enum):
            TEST_A = auto()

        # Check if no exceptions are raised
        UnsuportedEnumValueError(TestEnum.TEST_A)


class StackProfileTest(testutils.UtilTestCase):
    def test_profile_bin(self) -> None:
        with BuildSketch() as sketch:
            StackProfile(StackProfile.ProfileType.BIN)

        bbox = sketch.sketch.bounding_box()
        self.assertVectorAlmostEqual((2.6, 4.4, 0), bbox.size)
        self.assertEqual(6.8, sketch.sketch.area)

    def test_profile_plate(self) -> None:
        with BuildSketch() as sketch:
            StackProfile(StackProfile.ProfileType.PLATE)

        bbox = sketch.sketch.bounding_box()
        self.assertVectorAlmostEqual((2.85, 4.65, 0), bbox.size)
        self.assertEqual(7.9312499999999995, sketch.sketch.area)


class UtilsAttachTest(TestCase):
    def test_attach_top(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.TOP)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 20), bbox.size)
        self.assertEqual(15, bbox.max.Z)

    def test_attach_bottom(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.BOTTOM)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 20), bbox.size)
        self.assertEqual(-15, bbox.min.Z)

    def test_attach_left(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.LEFT)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 10, 10), bbox.size)
        self.assertEqual(-15, bbox.min.X)

    def test_attach_right(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.RIGHT)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(20, 10, 10), bbox.size)
        self.assertEqual(15, bbox.max.X)

    def test_attach_front(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.FRONT)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 20, 10), bbox.size)
        self.assertEqual(-15, bbox.min.Y)

    def test_attach_back(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.BACK)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 20, 10), bbox.size)
        self.assertEqual(15, bbox.max.Y)

    def test_attach_top_offset(self) -> None:
        box = Box(10, 10, 10)
        with BuildPart() as part:
            add(box)
            Utils.attach(part, box, Attach.TOP, 5)

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(10, 10, 25), bbox.size)
        self.assertEqual(20, bbox.max.Z)


class UtilsFaceByDirectionTest(TestCase):
    def test_utils_face_by_direction_top(self) -> None:
        with BuildPart() as part:
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Z)[-1].center_location,
                Utils.get_face_by_direction(part, Direction.TOP).center_location,
            )

    def test_utils_face_by_direction_bot(self) -> None:
        with BuildPart() as part:
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Z)[0].center_location,
                Utils.get_face_by_direction(part, Direction.BOT).center_location,
            )

    def test_utils_face_by_direction_right(self) -> None:
        with BuildPart() as part:
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.X)[-1].center_location,
                Utils.get_face_by_direction(part, Direction.RIGHT).center_location,
            )

    def test_utils_face_by_direction_left(self) -> None:
        with BuildPart() as part:
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.X)[0].center_location,
                Utils.get_face_by_direction(part, Direction.LEFT).center_location,
            )

    def test_utils_face_by_direction_back(self) -> None:
        with BuildPart() as part:
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Y)[-1].center_location,
                Utils.get_face_by_direction(part, Direction.BACK).center_location,
            )

    def test_utils_face_by_direction_front(self) -> None:
        with BuildPart() as part:
            box = Box(10, 10, 10)
            self.assertEqual(
                box.faces().sort_by(Axis.Y)[0].center_location,
                Utils.get_face_by_direction(part, Direction.FRONT).center_location,
            )


class UtilsGetSubclassesTest(TestCase):
    def test_get_subclass(self) -> None:
        class Base:
            pass

        class Child(Base):
            pass

        self.assertEqual(Child, Utils.get_subclasses(Base)[0])

    def test_get_subclass_recursive(self) -> None:
        class Base:
            pass

        class Child(Base):
            pass

        class ChildOfChild(Child):
            pass

        self.assertEqual([Child, ChildOfChild], Utils.get_subclasses(Base))


class UtilsPlaceByGridTest(TestCase):
    def test_place_by_grid_one(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True]]
        part = Utils.place_by_grid(box, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(10, 15, 20), bbox.size)

    def test_place_by_grid_one_row(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True, True, True]]
        part = Utils.place_by_grid(box, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 15, 20), bbox.size)

    def test_place_by_grid_one_column(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True], [True], [True]]
        part = Utils.place_by_grid(box, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(10, 45, 20), bbox.size)

    def test_place_by_grid_rows_and_columns(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True, True, True], [True, True, True], [True, True, True]]
        part = Utils.place_by_grid(box, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 45, 20), bbox.size)

    def test_place_by_grid_rows_and_columns_with_holes(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True, False, True], [True, True, True], [True, True, False]]
        part = Utils.place_by_grid(box, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 45, 20), bbox.size)

    def test_place_by_grid_nothing(self) -> None:
        box = Box(10, 15, 20)
        grid = [[False]]
        self.assertRaises(ValueError, Utils.place_by_grid, box, grid)

    def test_place_by_grid_width_length(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True, True], [True, True, True]]
        part = Utils.place_by_grid(box, grid, width=12, length=17)

        bbox = part.bounding_box()
        self.assertEqual(Vector(34, 32, 20), bbox.size)

    def test_place_by_grid_width(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True, True], [True, True, True]]
        part = Utils.place_by_grid(box, grid, width=12)

        bbox = part.bounding_box()
        self.assertEqual(Vector(34, 30, 20), bbox.size)

    def test_place_by_grid_length(self) -> None:
        box = Box(10, 15, 20)
        grid = [[True, True], [True, True, True]]
        part = Utils.place_by_grid(box, grid, length=17)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 32, 20), bbox.size)


class UtilsPlaceSketchByGridTest(TestCase):
    def test_place_sketch_by_grid_one(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True]]
        part = Utils.place_sketch_by_grid(rect, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(10, 15, 0), bbox.size)

    def test_place_sketch_by_grid_one_row(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True, True, True]]
        part = Utils.place_sketch_by_grid(rect, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 15, 0), bbox.size)

    def test_place_sketch_by_grid_one_column(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True], [True], [True]]
        part = Utils.place_sketch_by_grid(rect, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(10, 45, 0), bbox.size)

    def test_place_sketch_by_grid_rows_and_columns(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True, True, True], [True, True, True], [True, True, True]]
        part = Utils.place_sketch_by_grid(rect, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 45, 0), bbox.size)

    def test_place_sketch_by_grid_rows_and_columns_with_holes(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True, False, True], [True, True, True], [True, True, False]]
        part = Utils.place_sketch_by_grid(rect, grid)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 45, 0), bbox.size)

    def test_place_sketch_by_grid_nothing(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[False]]
        self.assertRaises(ValueError, Utils.place_sketch_by_grid, rect, grid)

    def test_place_sketch_by_grid_width_length(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True, True], [True, True, True]]
        part = Utils.place_sketch_by_grid(rect, grid, width=12, length=17)

        bbox = part.bounding_box()
        self.assertEqual(Vector(34, 32, 0), bbox.size)

    def test_place_sketch_by_grid_width(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True, True], [True, True, True]]
        part = Utils.place_sketch_by_grid(rect, grid, width=12)

        bbox = part.bounding_box()
        self.assertEqual(Vector(34, 30, 0), bbox.size)

    def test_place_sketch_by_grid_length(self) -> None:
        rect = Rectangle(10, 15)
        grid = [[True, True], [True, True, True]]
        part = Utils.place_sketch_by_grid(rect, grid, length=17)

        bbox = part.bounding_box()
        self.assertEqual(Vector(30, 32, 0), bbox.size)
