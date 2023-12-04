"""Generate gridfinity bases."""
from __future__ import annotations
from typing import Union, List, Iterable
from build123d import (
    RotationLike,
    Align,
    BuildPart,
    BuildSketch,
    BasePartObject,
    Mode,
    extrude,
    offset,
    Axis,
    Rectangle,
    add,
    Location,
    fillet,
)

from .constants import gridfinity_standard
from .features import BaseBlockFeature
from .utils import StackProfile, Utils


class Base(BasePartObject):
    """Base.

    Create gridfinity Base object.

    Args:
        grid (Grid): Grid pattern.
        features (BaseBlockFeature): compatible features list.
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        grid: List[List[bool]],
        features: Union[BaseBlockFeature, List[BaseBlockFeature]] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
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
                        True for vertex in edge.vertices() if vertex in top_face.vertices()
                    )
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
    """Base.

    Create gridfinity Base object.

    Args:
        grid (Grid): Grid object containg units of length
        magnets (bool, optional): True to create holes for magnets. Defaults to False.
        screwholes (bool, optional): True to create holes for screws. Defaults to False.
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        grid_x: int,
        grid_y: int,
        features: Union[BaseBlockFeature, List[BaseBlockFeature]] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        grid = []
        for _ in range(0, grid_y):
            grid += [[True] * grid_x]
        super().__init__(grid, features, rotation, align, mode)


class BaseBlock(BasePartObject):
    """BaseBlock.

    Create a single baseblock with rectangular platform. The rectangular platform makes it
    posible to stack the blocks in x and y direction. After creating an array it is meant to
    cut the platform to size.

    Args:
        magnets (bool, optional): True to create holes for magnets. Defaults to False.
        screwholes (bool, optional): True to create holes for screws. Defaults to False.
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    def __init__(
        self,
        features: Union[BaseBlockFeature, List[BaseBlockFeature]] = None,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        if not features:
            features = []

        features = features if isinstance(features, Iterable) else [features]

        with BuildPart() as baseblock:
            Utils.create_profile_block(
                StackProfile.ProfileType.BIN, gridfinity_standard.stacking_lip.offset
            )

            with BuildSketch(baseblock.faces().sort_by(Axis.Z)[-1]) as rect2:
                Rectangle(gridfinity_standard.grid.size, gridfinity_standard.grid.size)
            extrude(
                to_extrude=rect2.sketch,
                amount=gridfinity_standard.bottom.platform_height,
            )

            for feature in features:
                feature.apply()

        super().__init__(baseblock.part, rotation, align, mode)
