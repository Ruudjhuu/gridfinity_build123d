from unittest.mock import MagicMock, patch

import testutils
from build123d import Align, Axis, Box, BuildPart, Mode, Part
from gridfinity_build123d.feature_locations import (
    Corners,
    FaceDirection,
    Middle,
)
from gridfinity_build123d.utils import Direction
from parameterized import parameterized  # type: ignore[import-untyped]


class FaceDirectionTest(testutils.UtilTestCase):
    @parameterized.expand(
        [
            ["TOP", Direction.TOP, Axis.Z, -1],
            ["BOT", Direction.BOT, Axis.Z, 0],
            ["LEFT", Direction.LEFT, Axis.X, 0],
            ["RIGHT", Direction.RIGHT, Axis.X, -1],
            ["FRONT", Direction.FRONT, Axis.Y, 0],
            ["BACK", Direction.BACK, Axis.Y, -1],
        ],
    )  # type: ignore[misc]
    def test_facedirection(
        self,
        name: str,  # noqa:ARG002
        direction: Direction,
        axis: Axis,
        index: int,
    ) -> None:
        with BuildPart() as part:
            Box(20, 20, 20)
            location = FaceDirection(direction)
            with location.apply_to(part):
                Box(
                    1,
                    1,
                    1,
                    mode=Mode.SUBTRACT,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                )
        self.assertEqual(1, len(part.faces().sort_by(axis)[index].inner_wires()))
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((20, 20, 20), bbox.size)
        self.assertAlmostEqual(7999, part.part.volume)

    def test_facedirection_none(self) -> None:
        with BuildPart() as part:
            Box(20, 20, 20, align=Align.CENTER)
            location = FaceDirection()
            with location.apply_to(part):
                Box(
                    1,
                    1,
                    1,
                    mode=Mode.SUBTRACT,
                    align=Align.CENTER,
                )
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((20, 20, 20), bbox.size)
        self.assertAlmostEqual(7999, part.part.volume)


class MiddleTest(testutils.UtilTestCase):
    @patch("gridfinity_build123d.feature_locations.FaceDirection.apply_to")
    def test_middle_apply_to(self, fdir_mock: MagicMock) -> None:
        direction = MagicMock(spec=Direction)
        part = MagicMock(spec=Part)
        with Middle(direction).apply_to(part):
            pass
        fdir_mock.assert_called_once_with(part)


class CornersTest(testutils.UtilTestCase):
    def test_corners_default(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            context = Corners(Direction.TOP)
            with context.apply_to(part):
                Box(
                    1,
                    1,
                    1,
                    mode=Mode.SUBTRACT,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                )

        self.assertEqual(4, len(part.faces().sort_by(Axis.Z)[-1].inner_wires()))
        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertAlmostEqual(124996, part.part.volume)
