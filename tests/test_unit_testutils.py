from unittest import TestCase

import testutils
from build123d import Vector


class TestUtilsTest(TestCase):
    def test_assertAlmostIn_true_one_item(self) -> None:
        vec_a = Vector(1, 1, 1)
        vec_b = Vector(1, 1, 1)
        testutils.UtilTestCase().assertAlmostIn(vec_a, [vec_b])

    def test_assertAlmostIn_false_one_item(self) -> None:
        vec_a = Vector(1, 1, 1)
        vec_b = Vector(2, 1, 1)
        self.assertRaises(
            AssertionError,
            testutils.UtilTestCase().assertAlmostIn,
            vec_a,
            [vec_b],
        )

    def test_assertAlmostIn_true_two_item(self) -> None:
        vec_a = Vector(1, 1, 1)
        vec_b = Vector(2, 1, 1)
        vec_c = Vector(1, 1, 1)
        testutils.UtilTestCase().assertAlmostIn(vec_a, [vec_b, vec_c])

    def test_assertAlmostIn_false_two_item(self) -> None:
        vec_a = Vector(1, 1, 1)
        vec_b = Vector(2, 1, 1)
        vec_c = Vector(1, 2, 1)
        self.assertRaises(
            AssertionError,
            testutils.UtilTestCase().assertAlmostIn,
            vec_a,
            [vec_b, vec_c],
        )

    def test_assertAlmostIn_true_places(self) -> None:
        vec_a = Vector(1.00000001, 1, 1)
        vec_b = Vector(1, 1, 1)
        testutils.UtilTestCase().assertAlmostIn(vec_a, [vec_b])

    def test_assertAlmostIn_false_places(self) -> None:
        vec_a = Vector(1.0000001, 1, 1)
        vec_b = Vector(1, 1, 1)
        self.assertRaises(
            AssertionError,
            testutils.UtilTestCase().assertAlmostIn,
            vec_a,
            [vec_b],
        )
