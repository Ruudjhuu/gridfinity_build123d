from __future__ import annotations

from unittest import TestCase

from build123d import Vector


class UtilTestCase(TestCase):
    def assertVectorAlmostEqual(  # pylint: disable=invalid-name
        self,
        compare: tuple[float, float, float],
        vector: Vector,
        places: int | None = None,
    ) -> None:
        try:
            self.assertAlmostEqual(compare[0], vector.X, places)
            self.assertAlmostEqual(compare[1], vector.Y, places)
            self.assertAlmostEqual(compare[2], vector.Z, places)
        except AssertionError as e:  # pragma: no cover
            msg = f"{Vector(compare)} != {vector}"
            raise AssertionError(msg) from e
