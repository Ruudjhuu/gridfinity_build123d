from __future__ import annotations

from math import pi
from unittest.mock import ANY, MagicMock, patch

import mocks
import testutils
from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    CenterOf,
    Mode,
    RotationLike,
)
from gridfinity_build123d.features import (
    Feature,
    FeatureLocation,
    HoleFeature,
    Label,
    MagnetHole,
    ScrewHole,
    ScrewHoleCounterbore,
    ScrewHoleCountersink,
    Sweep,
    Weighted,
)
from parameterized import parameterized  # type: ignore[import-untyped]


class FeatureLocationTest(testutils.UtilTestCase):
    def test_feature_location_apply_BOTTOM_CONRNERS(self) -> None:
        feature_box = mocks.BoxAsMock(
            1,
            1,
            1,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

        with BuildPart() as part:
            Box(10, 10, 10)
            FeatureLocation.apply(
                part,
                feature_box.create,
                FeatureLocation.BOTTOM_CORNERS,
            )

        bot_face = part.faces().sort_by(Axis.Z)[0]
        self.assertEqual(4, len(bot_face.inner_wires()))
        for wire in bot_face.inner_wires():
            center = wire.center(CenterOf.BOUNDING_BOX)
            self.assertAlmostEqual(3, abs(center.X))
            self.assertAlmostEqual(3, abs(center.Y))

        bbox = part.part.bounding_box()

        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000 - 1 * 4, part.part.volume)

    def test_feature_location_apply_BOTTOM_MIDDLE(self) -> None:
        feature_box = mocks.BoxAsMock(
            1,
            1,
            1,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

        with BuildPart() as part:
            Box(10, 10, 10)
            FeatureLocation.apply(
                part,
                feature_box.create,
                FeatureLocation.BOTTOM_MIDDLE,
            )

        bot_face = part.faces().sort_by(Axis.Z)[0]
        self.assertEqual(1, len(bot_face.inner_wires()))
        for wire in bot_face.inner_wires():
            center = wire.center(CenterOf.BOUNDING_BOX)
            self.assertAlmostEqual(0, center.X)
            self.assertAlmostEqual(0, center.Y)

        bbox = part.part.bounding_box()

        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000 - 1, part.part.volume)

    def test_feature_location_apply_TOP_CONRNERS(self) -> None:
        feature_box = mocks.BoxAsMock(
            1,
            1,
            1,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

        with BuildPart() as part:
            Box(10, 10, 10)
            FeatureLocation.apply(part, feature_box.create, FeatureLocation.TOP_CORNERS)

        top_face = part.faces().sort_by(Axis.Z)[-1]
        self.assertEqual(4, len(top_face.inner_wires()))
        for wire in top_face.inner_wires():
            center = wire.center(CenterOf.BOUNDING_BOX)
            self.assertAlmostEqual(3, abs(center.X))
            self.assertAlmostEqual(3, abs(center.Y))

        bbox = part.part.bounding_box()

        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000 - 1 * 4, part.part.volume)

    def test_feature_location_apply_TOP_MIDDLE(self) -> None:
        feature_box = mocks.BoxAsMock(
            1,
            1,
            1,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

        with BuildPart() as part:
            Box(10, 10, 10)
            FeatureLocation.apply(part, feature_box.create, FeatureLocation.TOP_MIDDLE)

        top_face = part.faces().sort_by(Axis.Z)[-1]
        self.assertEqual(1, len(top_face.inner_wires()))
        for wire in top_face.inner_wires():
            center = wire.center(CenterOf.BOUNDING_BOX)
            self.assertAlmostEqual(0, center.X)
            self.assertAlmostEqual(0, center.Y)

        bbox = part.part.bounding_box()

        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000 - 1, part.part.volume)

    def test_feature_location_apply_CORNERS(self) -> None:
        feature_box = mocks.BoxAsMock(
            1,
            1,
            1,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

        with BuildPart() as part:
            Box(10, 10, 10)
            FeatureLocation.apply(part, feature_box.create, FeatureLocation.CORNERS)

        bbox = part.part.bounding_box()

        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000 - 1 * 4, part.part.volume)

    def test_feature_location_apply_UNDEFINED(self) -> None:
        feature_box = mocks.BoxAsMock(
            1,
            1,
            1,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT,
        )

        with BuildPart() as part:
            Box(10, 10, 10)
            FeatureLocation.apply(part, feature_box.create, FeatureLocation.UNDEFINED)

        bbox = part.part.bounding_box()

        self.assertVectorAlmostEqual((10, 10, 10), bbox.size)
        self.assertAlmostEqual(1000 - 1, part.part.volume)


class FeatureTest(testutils.UtilTestCase):
    @patch("gridfinity_build123d.features.FeatureLocation.apply")
    def test_feature_apply(self, apply_mock: MagicMock) -> None:
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
        f_location = MagicMock(spec=FeatureLocation)
        feature = TestFeature(f_location)
        feature.apply(context)
        apply_mock.assert_called_once_with(context, feature.create_obj, f_location)


class HoleFeatureTest(testutils.UtilTestCase):
    @parameterized.expand([[1, 2], [3, 4], [10, 2]])  # type: ignore[misc]
    def test_hole_feature(self, radius: float, depth: float) -> None:
        part = HoleFeature(radius, depth).create_obj()

        bbox = part.bounding_box()

        # build123d Hole creates a negative of twice the depth size
        self.assertVectorAlmostEqual((radius * 2, radius * 2, depth * 2), bbox.size)
        self.assertAlmostEqual(radius**2 * pi * depth * 2, part.volume)


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class ScrewHoleTest(testutils.UtilTestCase):
    def test_screw_hole(self, hole_mock: MagicMock) -> None:
        ScrewHole()
        hole_mock.assert_called_once_with(1.5, 6, FeatureLocation.BOTTOM_CORNERS)

    def test_screw_hole_values(self, hole_mock: MagicMock) -> None:
        ScrewHole(2, 3)
        hole_mock.assert_called_once_with(2, 3, FeatureLocation.BOTTOM_CORNERS)


@patch("gridfinity_build123d.features.HoleFeature.__init__")
class MagnetHoleTest(testutils.UtilTestCase):
    def test_screw_hole(self, hole_mock: MagicMock) -> None:
        MagnetHole()
        hole_mock.assert_called_once_with(3.25, 2.4, FeatureLocation.CORNERS)

    def test_screw_hole_values(self, hole_mock: MagicMock) -> None:
        MagnetHole(2, 3)
        hole_mock.assert_called_once_with(2, 3, FeatureLocation.CORNERS)


class ScrewHoleCountersinkTest(testutils.UtilTestCase):
    def test_screw_hole_countersink(self) -> None:
        part = ScrewHoleCountersink().create_obj()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((8.5, 8.5, 12), bbox.size)
        self.assertAlmostEqual(456.54773188858275, part.volume)

    @patch("gridfinity_build123d.features.CounterSinkHole")
    def test_screw_hole_countersink_args(self, hole_mock: MagicMock) -> None:
        hole_mock.side_effect = mocks.BoxAsMock(1, 1, 1).create

        radius = 1
        counter_sink_radius = 2
        depth = 3
        counter_sink_angle = 4
        ScrewHoleCountersink(
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
        part = ScrewHoleCounterbore().create_obj()

        bbox = part.bounding_box()
        self.assertVectorAlmostEqual((4.5, 4.5, 12), bbox.size)
        self.assertAlmostEqual(155.50883635269474, part.volume)

    @patch("gridfinity_build123d.features.CounterBoreHole")
    def test_screw_hole_counterbore_args(self, hole_mock: MagicMock) -> None:
        hole_mock.side_effect = mocks.BoxAsMock(1, 1, 1).create

        radius = 1
        counter_bore_radius = 2
        counter_bore_depth = 4
        depth = 3
        ScrewHoleCounterbore(
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
        part = Weighted().create_obj()

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
