"""Generate gridfinity bases."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Rectangle,
    RotationLike,
    add,  # pyright: ignore[reportUnknownVariableType]
    extrude,
)

from .constants import gridfinity_standard
from .utils import StackProfile, Utils

if TYPE_CHECKING:
    from .features import ObjectFeature


class Base(BasePartObject):
    """Gridfinity Base objec.

    Basis for bins and other gridfinity modules. This is the part that fits in the Baseplates.
    """

    def __init__(
        self,
        grid: list[list[bool]] | None = None,
        features: ObjectFeature | list[ObjectFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a gridfinity base.

        Args:
            grid (list[list[bool]],optional): Grid pattern. Defaults to [[True]].
            features (ObjectFeature | list[ObjectFeature] | None, optional): Feature or Feature
                list. Defaults to None.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        if not grid:
            grid = [[True]]
        if not features:
            features = []

        features = features if isinstance(features, Iterable) else [features]

        with BuildPart() as base:
            base_block = BaseBlock(features=features, mode=Mode.PRIVATE)
            _ = Utils.place_by_grid(
                base_block,
                grid,
                width=gridfinity_standard.grid.size,
                length=gridfinity_standard.grid.size,
            )

            top_face_1 = base.faces().sort_by(Axis.Z)[-1]
            z_top = top_face_1.bounding_box().min.Z

            with Locations((0, 0, z_top)):
                _ = Utils.create_bin_platform(
                    grid,
                    align=(
                        Align.CENTER,
                        Align.CENTER,
                        Align.MIN,
                    ),
                )

        if not base.part:  # pragma: no cover
            msg = "Base is empty"
            raise RuntimeError(msg)

        super().__init__(base.part, rotation, align, mode)


class BaseEqual(Base):
    """Gridfinity rectangular base object."""

    def __init__(
        self,
        grid_x: int = 1,
        grid_y: int = 1,
        features: ObjectFeature | list[ObjectFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a rectangular Base object.

        Args:
            grid_x (int, optional): Number of grid units on x axis. Defaults to 1.
            grid_y (int, optional): Number of grid units on y axis. Defaults to 1.
            features (ObjectFeature | list[ObjectFeature] | None, optional): ObjectFeature
                or list of ObjectFeatures. Defaults to None.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        grid: list[list[bool]] = []
        for _ in range(grid_y):
            grid += [[True] * grid_x]
        super().__init__(grid, features, rotation, align, mode)


class BaseBlock(BasePartObject):
    """BaseBlock.

    Create a single baseblock.
    """

    def __init__(
        self,
        features: ObjectFeature | list[ObjectFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct BaseBlock.

        Args:
            features (ObjectFeature | list[ObjectFeature] | None, optional): ObjectFeature
                or list of ObjectFeatures. Defaults to None.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        if not features:
            features = []

        features = features if isinstance(features, Iterable) else [features]

        with BuildPart() as baseblock:
            _ = Utils.create_profile_block(
                StackProfile.ProfileType.BIN,
                gridfinity_standard.stacking_lip.offset,
            )

            for feature in features:
                feature.apply(baseblock)

        if not baseblock.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        super().__init__(baseblock.part, rotation, align, mode)


class BaseBlockPlatform(BasePartObject):
    """BaseBlockPlatform.

    Create a single baseblock with a rectangular platform on top. The rectangular platform makes it
    posible to stack the blocks in x and y direction. After creating an array it is meant to cut or
    offset the platform to size.
    """

    def __init__(
        self,
        features: ObjectFeature | list[ObjectFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct BaseBlockPlatform.

        Args:
            features (ObjectFeature | list[ObjectFeature] | None, optional): ObjectFeature
                or list of ObjectFeatures. Defaults to None.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        if not features:
            features = []

        features = features if isinstance(features, Iterable) else [features]

        base_block = BaseBlock(features=[], rotation=rotation, mode=Mode.ADD)

        with BuildPart() as baseblock_platform:
            _ = add(base_block)

            with BuildSketch(baseblock_platform.faces().sort_by(Axis.Z)[-1]) as rect2:
                _ = Rectangle(gridfinity_standard.grid.size, gridfinity_standard.grid.size)
            _ = extrude(
                to_extrude=rect2.sketch,
                amount=gridfinity_standard.bottom.platform_height,
            )

            for feature in features:
                feature.apply(baseblock_platform)

        if not baseblock_platform.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        super().__init__(baseblock_platform.part, rotation, align, mode)
