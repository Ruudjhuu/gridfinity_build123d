"""Generate gridfinity bases."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Location,
    Mode,
    Rectangle,
    RotationLike,
    add,
    extrude,
    fillet,
    offset,
)

from .constants import gridfinity_standard
from .utils import StackProfile, Utils

if TYPE_CHECKING:
    from .features import BaseBlockFeature


class Base(BasePartObject):
    """Gridfinity Base objec.

    Basis for bins and other gridfinity modules. This is the part that fits in the Baseplates.
    """

    def __init__(
        self,
        grid: list[list[bool]],
        features: BaseBlockFeature | list[BaseBlockFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a gridfinity base.

        Args:
            grid (Grid): Grid pattern.
            features (BaseBlockFeature): compatible features list.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        if not features:
            features = []

        features = features if isinstance(features, Iterable) else [features]

        with BuildPart() as base:
            base_block = BaseBlock(features=features, mode=Mode.PRIVATE)
            Utils.place_by_grid(base_block, grid)

            top_face = base.faces().sort_by(Axis.Z)[-1]
            edges = (
                base.edges()
                .filter_by(Axis.Z)
                .filter_by(
                    lambda edge: any(
                        True
                        for vertex in edge.vertices()
                        if vertex in top_face.vertices()
                    ),
                )
            )
            fillet(objects=edges, radius=gridfinity_standard.grid.radius)

        with BuildPart() as cutter:
            with BuildSketch(Location((0, 0, base.part.bounding_box().max.Z))):
                add(base.faces().sort_by(Axis.Z)[-1])
                offset(amount=-gridfinity_standard.grid.tollerance / 2)
            extrude(amount=base.part.bounding_box().size.Z, dir=(0, 0, -1))

        with BuildPart() as part:
            add(base)
            add(cutter, mode=Mode.INTERSECT)

        super().__init__(part.part, rotation, align, mode)


class BaseEqual(Base):
    """Gridfinity rectangular base object."""

    def __init__(
        self,
        grid_x: int,
        grid_y: int,
        features: BaseBlockFeature | list[BaseBlockFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct a rectangular Base object.

        Args:
            grid_x (int): Number of grid units on x axis
            grid_y (int): Number of grid units on y axis
            features (BaseBlockFeature): List of BaseBlockFeatures
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        grid = []
        for _ in range(grid_y):
            grid += [[True] * grid_x]
        super().__init__(grid, features, rotation, align, mode)


class BaseBlock(BasePartObject):
    """BaseBlock.

    Create a single baseblock with rectangular platform. The rectangular platform makes it
    posible to stack the blocks in x and y direction. After creating an array it is meant to
    cut the platform to size.
    """

    def __init__(
        self,
        features: BaseBlockFeature | list[BaseBlockFeature] | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """Construct BaseBlock.

        Args:
            features (BaseBlockFeature): List of BaseBlockFeatures
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        if not features:
            features = []

        features = features if isinstance(features, Iterable) else [features]

        with BuildPart() as baseblock:
            Utils.create_profile_block(
                StackProfile.ProfileType.BIN,
                gridfinity_standard.stacking_lip.offset,
            )

            with BuildSketch(baseblock.faces().sort_by(Axis.Z)[-1]) as rect2:
                Rectangle(gridfinity_standard.grid.size, gridfinity_standard.grid.size)
            extrude(
                to_extrude=rect2.sketch,
                amount=gridfinity_standard.bottom.platform_height,
            )

            for feature in features:
                feature.apply(baseblock)

        super().__init__(baseblock.part, rotation, align, mode)
