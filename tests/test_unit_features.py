from __future__ import annotations

from math import pi
from unittest.mock import ANY, MagicMixin, MagicMock, patch

import mocks
import testutils
from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    Mode,
    Part,
    RotationLike,
)
from gridfinity_build123d.features import (
    Feature,
    HoleFeature,
    Label,
    MagnetHole,
    ScrewHole,
    ScrewHoleCounterbore,
    ScrewHoleCountersink,
    Sweep,
    Weighted,
)
from gridfinity_build123d.feature_locations import FeatureLocation
from gridfinity_build123d.utils import Direction
from parameterized import parameterized  # type: ignore[import-untyped]


class FeatureTest(testutils.UtilTestCase):
    def test_feature_apply(self) -> None:
        class TestFeature(Feature):
            def create_obj(
                self,
                rotation: RotationLike = None,  # noqa:ARG002
                align: Align | tuple[Align, Align, Align] | None = None,  # noqa:ARG002
                mode: Mode = None,  # noqa:ARG002
            ) -> BasePartObject:
                # Dummy Code
                return Box(1, 1, 1)  # pragma: no cover

        context = MagicMock(spec=BuildPart)
        context.part = MagicMock(spec=Part)
        f_location = MagicMock(spec=FeatureLocation)
        feature = TestFeature(f_location)
        feature.apply(context)
        f_location.apply_to.assert_called_once_with(context.part)

    def test_feature_apply_no_location(self) -> None:
        class TestFeature(Feature):
            def create_obj(
                self,
                rotation: RotationLike = None,  # noqa:ARG002
                align: Align | tuple[Align, Align, Align] | None = None,  # noqa:ARG002
                mode: Mode = None,  # noqa:ARG002
            ) -> BasePartObject:
                return Box(1, 1, 1)

        context = MagicMock(spec=BuildPart)
        context.part = MagicMock(spec=Part)
        feature = TestFeature(None)
        with BuildPart() as part:
            feature.apply(context)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((1, 1, 1), bbox.size)
        self.assertAlmostEqual(1, part.part.volume)


class HoleFeatureTest(testutils.UtilTestCase):
    @parameterized.expand([[1, 2], [3, 4], [10, 2]])  # type: ignore[misc]
    def test_hole_feature(self, radius: float, depth: float) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        part = HoleFeature(f_loc, radius, depth).create_obj()

        bbox = part.bounding_box()

        # build123d Hole creates a negative of twice the depth size
        self.assertVectorAlmostEqual((radius * 2, radius * 2, depth * 2), bbox.size)
        self.assertAlmostEqual(radius**2 * pi * depth * 2, part.volume)


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class ScrewHoleTest(testutils.UtilTestCase):
    def test_screw_hole(self, hole_mock: MagicMock) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        ScrewHole(f_loc)
        hole_mock.assert_called_once_with(f_loc, 1.5, 6)

    def test_screw_hole_values(self, hole_mock: MagicMock) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        ScrewHole(f_loc, 2, 3)
        hole_mock.assert_called_once_with(f_loc, 2, 3)


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class MagnetHoleTest(testutils.UtilTestCase):
    def test_magnet_hole(self, hole_mock: MagicMock) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        MagnetHole(f_loc)
        hole_mock.assert_called_once_with(f_loc, 3.25, 2.4)

    def test_magnet_hole_values(self, hole_mock: MagicMock) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        MagnetHole(f_loc, 2, 3)
        hole_mock.assert_called_once_with(f_loc, 2, 3)


class ScrewHoleCountersinkTest(testutils.UtilTestCase):
    def test_screw_hole_countersink(self) -> None:
        f_loc = MagicMock(spec=FeatureLocation)

        part = ScrewHoleCountersink(f_loc).create_obj()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((8.5, 8.5, 12), bbox.size)
        self.assertAlmostEqual(456.54773188858275, part.volume)

    @patch("gridfinity_build123d.features.CounterSinkHole")
    def test_screw_hole_countersink_args(self, hole_mock: MagicMock) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        hole_mock.side_effect = mocks.BoxAsMock(1, 1, 1).create

        radius = 1
        counter_sink_radius = 2
        depth = 3
        counter_sink_angle = 4
        ScrewHoleCountersink(
            f_loc,
            radius=radius,
            counter_sink_radius=counter_sink_radius,
            depth=depth,
            counter_sink_angle=counter_sink_angle,
        ).create_obj()

        hole_mock.assert_called_once_with(
            radius=radius,
            counter_sink_radius=counter_sink_radius,
            depth=depth,
            counter_sink_angle=counter_sink_angle,
            mode=ANY,
        )


class ScrewHoleCounterboreTest(testutils.UtilTestCase):
    def test_screw_hole_counterbore(self) -> None:
        f_loc = MagicMock(spec=FeatureLocation)

        part = ScrewHoleCounterbore(f_loc).create_obj()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((4.5, 4.5, 12), bbox.size)
        self.assertAlmostEqual(155.50883635269474, part.volume)

    @patch("gridfinity_build123d.features.CounterBoreHole")
    def test_screw_hole_counterbore_args(self, hole_mock: MagicMock) -> None:
        f_loc = MagicMock(spec=FeatureLocation)
        hole_mock.side_effect = mocks.BoxAsMock(1, 1, 1).create

        radius = 1
        counter_bore_radius = 2
        counter_bore_depth = 4
        depth = 3
        ScrewHoleCounterbore(
            f_loc,
            radius=radius,
            counter_bore_radius=counter_bore_radius,
            counter_bore_depth=counter_bore_depth,
            depth=depth,
        ).create_obj()

        hole_mock.assert_called_once_with(
            radius=radius,
            counter_bore_radius=counter_bore_radius,
            counter_bore_depth=counter_bore_depth,
            depth=depth,
            mode=ANY,
        )


class WeightedTest(testutils.UtilTestCase):
    def test_weigthed(self) -> None:
        f_loc = MagicMock(spec=FeatureLocation)

        part = Weighted(f_loc).create_obj()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((38.4, 38.4, 4.0), bbox.size)
        self.assertAlmostEqual(2347.820069221863, part.volume)


class LabelTest(testutils.UtilTestCase):
    def test_label(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Label().create(part)

        top_face = part.faces().filter_by(Axis.Z)[-1]
        self.assertEqual(50 - 12, top_face.width)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(121784.44689918072, part.part.volume)

    def test_label_angle(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Label(10).create(part)

        top_face = part.faces().filter_by(Axis.Z)[-1]
        self.assertEqual(50 - 12, top_face.width)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(123765.22286944953, part.part.volume)

    def test_label_angle_zero(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Label(0).create(part)

        top_face = part.faces().filter_by(Axis.Z)[-1]
        self.assertEqual(50 - 12, top_face.width)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(124399.99999371683, part.part.volume)

    def test_label_too_small_box(self) -> None:
        with BuildPart() as part:
            Box(10, 10, 10)
            self.assertRaises(ValueError, Label().create, part)

    def test_label_unvalid_angle(self) -> None:
        self.assertRaises(ValueError, Label, -1)
        self.assertRaises(ValueError, Label, 91)


class SweepTest(testutils.UtilTestCase):
    def test_sweep(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Sweep().create(part)

        bot_face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
        self.assertAlmostEqual(50 - 5, bot_face.width)

        front_face = part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        self.assertAlmostEqual(50 - 5, front_face.length)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(124731.74770424681, part.part.volume)

    def test_sweep_radius(self) -> None:
        with BuildPart() as part:
            Box(50, 50, 50)
            Sweep(20).create(part)

        bot_face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
        self.assertAlmostEqual(50 - 20, bot_face.width)

        front_face = part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        self.assertAlmostEqual(50 - 20, front_face.length)

        bbox = part.part.bounding_box()
        self.assertVectorAlmostEqual((50, 50, 50), bbox.size)
        self.assertEqual(120707.96326794896, part.part.volume)

    def test_sweep_small_box(self) -> None:
        with BuildPart() as part:
            Box(4, 4, 4)
            self.assertRaises(ValueError, Sweep().create, part)
