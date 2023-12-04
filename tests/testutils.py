from unittest import TestCase
from typing import Tuple

from build123d import Vector


class UtilTestCase(TestCase):
    def assertVectorAlmostEqual(  # pylint: disable=invalid-name
        self,
        compare: Tuple[float, float, float],
        vector: Vector,
        places: int = None,
    ) -> None:
        try:
            self.assertAlmostEqual(compare[0], vector.X, places)
            self.assertAlmostEqual(compare[1], vector.Y, places)
            self.assertAlmostEqual(compare[2], vector.Z, places)
        except AssertionError as e:  # pragma: no cover
            raise AssertionError(f"{Vector(compare)} != {vector}") from e  # pragma: no cover
