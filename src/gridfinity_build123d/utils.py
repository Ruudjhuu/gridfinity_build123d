"""Utiity module."""
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Tuple, Union, List

from build123d import (
    Builder,
    BuildPart,
    add,
    Locations,
    Part,
    Mode,
    Align,
    RotationLike,
    Face,
    BasePartObject,
    BaseSketchObject,
    BuildSketch,
    BuildLine,
    Polyline,
    make_face,
    Axis,
    Plane,
    RectangleRounded,
    sweep,
    extrude,
    offset,
    Kind,
)

from .constants import gridfinity_standard


class ObjectCreate(ABC):
    """Interface for object forcing to implement create_obj."""

    @abstractmethod
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create the build123d 3d object.

        Args:
            rotation (RotationLike): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode): Combination mode. Defaults to Mode.ADD.

        Raises:
            NotImplementedError: Child class does not have an implementation

        Returns:
            BasePartObject: The build123d 3d object
        """
        raise NotImplementedError()  # pragma: no cover


class Direction(Enum):
    """Direction Enum.

    Direction can be converted to a tuple.
    """

    TOP = auto()
    BOT = auto()
    RIGHT = auto()
    LEFT = auto()
    BACK = auto()
    FRONT = auto()

    @staticmethod
    def to_tuple(direction: Direction) -> Tuple[int, int, int]:
        """Convert Direction to tuple.

        Args:
            direction (Direction): Direction to convert

        Raises:
            ValueError: Unkonw Direction

        Returns:
            Tuple[int, int, int]: Output tupple
        """
        if direction == Direction.TOP:
            return (0, 0, 1)

        if direction == Direction.BOT:
            return (0, 0, -1)

        if direction == Direction.RIGHT:
            return (1, 0, 0)

        if direction == Direction.LEFT:
            return (-1, 0, 0)

        if direction == Direction.BACK:
            return (0, 1, 0)

        if direction == Direction.FRONT:
            return (0, -1, 0)

        raise ValueError(f"Unkown direction {direction}")  # pragma: no cover


class Attach(Enum):
    """Attach.

    Enum for indicating a direction when attaching objects
    """

    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    BACK = auto()
    FRONT = auto()


class Utils:  # pylint: disable=too-few-public-methods
    """Utils.

    Class wrapping utility functions
    """

    @staticmethod
    def attach(part: Part, attach: Attach, offset_value: float = 0) -> None:
        """attach.

        Attaches other object acording to "attach".

        Args:
            part (Part): the part to be attached
            attach (Attach): Direction to attach
            offset_value (float): offset.

        Raises:
            RuntimeError: Attach must have an active builder context
            RuntimeError: Attach only works for BuildPart (yet)
            ValueError: Nothing to attach to
        """
        context: Builder = Builder._get_context(None)  # pylint: disable=protected-access
        if context is None:
            raise RuntimeError("Attach must have an active builder context")
        if not isinstance(context, BuildPart):
            raise RuntimeError("Attach only works for BuildPart (yet)")
        if not context._obj:  # pylint: disable=protected-access
            raise ValueError("Nothing to attach to")

        location: Tuple[float, float, float] = (0, 0, 0)

        if attach == Attach.TOP:
            location = (
                0,
                0,
                context.part.bounding_box().max.Z + -1 * part.bounding_box().min.Z + offset_value,
            )
        elif attach == Attach.BOTTOM:
            location = (
                0,
                0,
                context.part.bounding_box().min.Z + -1 * part.bounding_box().max.Z - offset_value,
            )
        elif attach == Attach.LEFT:
            location = (
                context.part.bounding_box().min.X + -1 * part.bounding_box().max.X - offset_value,
                0,
                0,
            )
        elif attach == Attach.RIGHT:
            location = (
                context.part.bounding_box().max.X + -1 * part.bounding_box().min.X + offset_value,
                0,
                0,
            )
        elif attach == Attach.FRONT:
            location = (
                0,
                context.part.bounding_box().min.Y + -1 * part.bounding_box().max.Y - offset_value,
                0,
            )
        elif attach == Attach.BACK:
            location = (
                0,
                context.part.bounding_box().max.Y + -1 * part.bounding_box().min.Y + offset_value,
                0,
            )
        else:  # pragma: nocover
            raise ValueError("Unkown attach type")  # pragma: nocover

        with Locations(location):
            add(part)

    @staticmethod
    def get_face_by_direction(direction: Direction) -> Face:
        """Get face by direction.

        Args:
            direction (Direction): Direction of face

        Raises:
            RuntimeError: get_face_by_direction must have an active builder context
            RuntimeError: get_face_by_direction only works for BuildPart
            ValueError: Nothing to get face from

        Returns:
            Face: face
        """
        context: Builder = Builder._get_context(None)  # pylint: disable=protected-access
        if context is None:
            raise RuntimeError("get_face_by_direction must have an active builder context")
        if not isinstance(context, BuildPart):
            raise RuntimeError("get_face_by_direction only works for BuildPart")
        if not context._obj:  # pylint: disable=protected-access
            raise ValueError("Nothing to get face from")

        return context.faces().sort_by(Axis((0, 0, 0), Direction.to_tuple(direction)))[-1]

    @staticmethod
    def remaining_gridfinity_height(units: int) -> float:
        """Calculate reamining height.

        Calculates the height still needed to create a gridfinity object of "units" heigh. Uses
        current builder context to calculate the remaining height.

        Args:
            units (int): Gridfinity standard z units (7mm)

        Raises:
            RuntimeError: remaining_gridfinity_height must have an active builder context
            RuntimeError: remaining_gridfinity_height only works for BuildPart

        Returns:
            float: remaining height
        """
        context: Builder = Builder._get_context(None)  # pylint: disable=protected-access
        if context is None:
            raise RuntimeError("remaining_gridfinity_height must have an active builder context")
        if not isinstance(context, BuildPart):
            raise RuntimeError("remaining_gridfinity_height only works for BuildPart")
        if not context._obj:  # pylint: disable=protected-access
            return units * 7

        return units * 7 - context.part.bounding_box().size.Z

    @staticmethod
    def get_subclasses(class_name: Any) -> List[Any]:
        """Get subclasses of a base class recursively.

        Args:
            class_name (Any): class type to get subcalsses from

        Returns:
            Any: list of child class types
        """
        classes = []

        for subclass in class_name.__subclasses__():
            classes.append(subclass)
            classes += Utils.get_subclasses(subclass)

        return classes

    @staticmethod
    def place_by_grid(
        obj: BasePartObject,
        grid: List[List[bool]],
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = Align.CENTER,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Place multiple instances of object according to grid.

        Args:
            obj (BasePartObject): object to be copied
            grid (List[List[bool]]): grid
            rotation (RotationLike): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to Align.CENTER.
            mode (Mode): Combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: gridlike object
        """
        bbox = obj.bounding_box()
        width = bbox.size.X
        length = bbox.size.Y
        with BuildPart() as part:
            for row_nr, row_value in enumerate(grid):
                for column_nr, column_value in enumerate(row_value):
                    if column_value:
                        with Locations((width * (column_nr + 1), length * -(row_nr + 1))):
                            add(obj)

        return BasePartObject(part.part, rotation, align, mode)

    @staticmethod
    def create_profile_block(
        profile_type: StackProfile.ProfileType,
        offset_value: float = 0,
        rotation: RotationLike = (0, 0, 0),
        align: Union[Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create block with stacing profile.

        Args:
            profile_type (StackProfile.ProfileType): Profile type
            offset_value (float): Offset of profile sweep. Defaults to 0.
            rotation (RotationLike): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode): Combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: _description_
        """
        with BuildPart() as part:
            with BuildSketch(Plane.XZ) as profile:
                with Locations(
                    (
                        gridfinity_standard.grid.size / 2 - offset_value,
                        0,
                    )
                ):
                    StackProfile(profile_type, align=(Align.MAX, Align.MIN))
                    if offset_value:
                        offset(
                            amount=offset_value,
                            kind=Kind.INTERSECTION,
                        )

            with BuildSketch() as rect:
                RectangleRounded(
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.size,
                    gridfinity_standard.grid.radius,
                )
            extrude(to_extrude=rect.face(), amount=profile.sketch.bounding_box().max.Z)

            path = part.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)
        return BasePartObject(part.part, rotation, align, mode)


class StackProfile(BaseSketchObject):
    """StackProfile.

    Create a profile of the gridfinity stacking system. Usualy used in the sweep function.

    Args:
        rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
        align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
            object. Defaults to None.
        mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
    """

    class ProfileType(Enum):
        """Profile Type."""

        BIN = auto()
        PLATE = auto()

    def __init__(
        self,
        stack_type: ProfileType,
        rotation: float = 0,
        align: Union[Align, tuple[Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        if stack_type == StackProfile.ProfileType.BIN:
            height_3 = gridfinity_standard.stacking_lip.height_3_bin
        elif stack_type == StackProfile.ProfileType.PLATE:
            height_3 = gridfinity_standard.stacking_lip.height_3_base_plate
        else:
            raise ValueError("Unkown stack_type")  # pragma: no cover

        with BuildSketch() as profile:
            with BuildLine():
                Polyline(
                    (0, 0),
                    (
                        gridfinity_standard.stacking_lip.height_1,
                        gridfinity_standard.stacking_lip.height_1,
                    ),
                    (
                        gridfinity_standard.stacking_lip.height_1,
                        gridfinity_standard.stacking_lip.height_1
                        + gridfinity_standard.stacking_lip.height_2,
                    ),
                    (
                        gridfinity_standard.stacking_lip.height_1 + height_3,
                        gridfinity_standard.stacking_lip.height_1
                        + gridfinity_standard.stacking_lip.height_2
                        + height_3,
                    ),
                    (
                        gridfinity_standard.stacking_lip.height_1 + height_3,
                        0,
                    ),
                    close=True,
                )
            make_face()
        super().__init__(profile.face(), rotation, align, mode)
