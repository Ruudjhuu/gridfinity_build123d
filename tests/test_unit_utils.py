from unittest import TestCase

from build123d import BuildPart, Box, add, Vector, BuildSketch

from gridfinity_build123d.utils import Utils, Attach


class UtilsTest(TestCase):
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
