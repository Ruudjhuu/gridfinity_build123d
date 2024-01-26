from __future__ import annotations

from unittest import TestCase
from unittest.util import safe_repr

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

    def _isclose(self, a: float, b: float, places: int) -> bool:
        diff = abs(a - b)
        if round(diff, places) == 0:
            return True
        return False

    def _vec_almost_equal(self, vec_a: Vector, vec_b: Vector, places: int) -> bool:
        return all(
            [
                self._isclose(vec_a.X, vec_b.X, places),
                self._isclose(vec_a.Y, vec_b.Y, places),
                self._isclose(vec_a.Z, vec_b.Z, places),
            ],
        )

    def assertAlmostIn(
        self,
        input_vec: Vector,
        vec_list: list[Vector],
        places: int = 7,
    ) -> None:
        rtn = any(
            self._vec_almost_equal(input_vec, vector, places) for vector in vec_list
        )
        if not rtn:
            msg = f"{safe_repr(input_vec)} not found in {safe_repr(vec_list)} within {places} places"
            raise AssertionError(msg)
