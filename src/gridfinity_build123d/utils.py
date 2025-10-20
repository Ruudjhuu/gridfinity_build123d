"""Utiity module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BaseSketchObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Face,
    Kind,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Polyline,
    Rectangle,
    RectangleRounded,
    RotationLike,
    add,
    extrude,
    fillet,
    make_face,
    offset,
    sweep,
)

from .constants import gridfinity_standard


class UnsuportedEnumValueError(Exception):
    """Raised when a unsuported enum value is handled."""

    def __init__(self, enum_var: Enum) -> None:
        """Construct Enum exception.

        Args:
            enum_var (Enum): Enum value
        """
        super().__init__(f"Unsuported enum value: {enum_var}")


class ObjectCreate(ABC):
    """Interface for object forcing to implement create_obj."""

    @abstractmethod
    def create_obj(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create the build123d 3d object.

        Args:
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Raises:
            NotImplementedError: Child class does not have an implementation

        Returns:
            BasePartObject: The build123d 3d object
        """
        raise NotImplementedError  # pragma: no cover


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
    def to_tuple(direction: Direction) -> tuple[int, int, int]:
        """Convert Direction to tuple.

        Args:
            direction (Direction): Direction to convert.

        Raises:
            ValueError: Unkonw Direction.

        Returns:
            Tuple[int, int, int]: Output tupple.
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

        raise UnsuportedEnumValueError(direction)  # pragma: no cover


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
    def attach(
        context: BuildPart,
        part: Part,
        attach: Attach,
        offset_value: float = 0,
    ) -> None:
        """Attach.

        Attaches other object acording to "attach".

        Args:
            context (BuildPart): context were attach should be executed.
            part (Part): the part to be attached
            attach (Attach): Direction to attach
            offset_value (float, optional): offset. Defaults to 0.

        Raises:
            UnsuportedEnumValueError: Unsuported Enum value
        """
        context_part = context.part
        if not isinstance(context_part, Part):  # pragma: no cover
            msg = "Context has no part"
            raise TypeError(msg)

        location: tuple[float, float, float] = (0, 0, 0)

        if attach == Attach.TOP:
            location = (
                0,
                0,
                context_part.bounding_box().max.Z + -1 * part.bounding_box().min.Z + offset_value,
            )
        elif attach == Attach.BOTTOM:
            location = (
                0,
                0,
                context_part.bounding_box().min.Z + -1 * part.bounding_box().max.Z - offset_value,
            )
        elif attach == Attach.LEFT:
            location = (
                context_part.bounding_box().min.X + -1 * part.bounding_box().max.X - offset_value,
                0,
                0,
            )
        elif attach == Attach.RIGHT:
            location = (
                context_part.bounding_box().max.X + -1 * part.bounding_box().min.X + offset_value,
                0,
                0,
            )
        elif attach == Attach.FRONT:
            location = (
                0,
                context_part.bounding_box().min.Y + -1 * part.bounding_box().max.Y - offset_value,
                0,
            )
        elif attach == Attach.BACK:
            location = (
                0,
                context_part.bounding_box().max.Y + -1 * part.bounding_box().min.Y + offset_value,
                0,
            )
        else:  # pragma: no cover
            raise UnsuportedEnumValueError(attach)

        with Locations(location):
            add(part)

    @staticmethod
    def get_face_by_direction(context: BuildPart, direction: Direction) -> Face:
        """Get face by direction.

        Args:
            context (BuildPart): context were attach should be executed.
            direction (Direction): Direction of face

        Returns:
            Face: face
        """
        return context.faces().sort_by(Axis((0, 0, 0), Direction.to_tuple(direction)))[-1]

    @staticmethod
    def get_subclasses(class_name: type) -> list[Any]:
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
        grid: list[list[bool]],
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] = Align.CENTER,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Place multiple instances of object according to grid.

        Args:
            obj (BasePartObject): object to be copied
            grid (list[list[bool]]): grid
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to Align.CENTER.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Raises:
            ValueError: grid does not reasemble locations

        Returns:
            BasePartObject: gridlike object
        """
        bbox = obj.bounding_box()
        width = bbox.size.X
        length = bbox.size.Y

        locations: list[Location] = []
        for row_nr, row_value in enumerate(grid):
            for column_nr, column_value in enumerate(row_value):
                if column_value:
                    locations.append(
                        Location((width * (column_nr + 1), length * -(row_nr + 1))),
                    )

        if not locations:
            msg = f"grid {grid} does not reasemble locations"
            raise ValueError(msg)

        with BuildPart() as part, Locations(locations):
            add(obj)

        return BasePartObject(part.part, rotation, align, mode)

    @staticmethod
    def create_upper_bin_block(
        grid: list[list[bool]],
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        width = gridfinity_standard.grid.size
        length = gridfinity_standard.grid.size

        locations: list[Location] = []
        for row_nr, row_value in enumerate(grid):
            for column_nr, column_value in enumerate(row_value):
                if column_value:
                    locations.append(
                        Location((width * (column_nr + 1), length * -(row_nr + 1))),
                    )

        with BuildPart() as part:
            with BuildSketch() as base:
                with Locations(locations):
                    Rectangle(length, width)
                offset(amount=-0.25)
                tol = gridfinity_standard.grid.tollerance
                fillet(base.vertices(), radius=gridfinity_standard.grid.radius - tol * 0.5)

            extrude(amount=gridfinity_standard.bottom.platform_height)

        return BasePartObject(part.part, rotation, align, mode)

    @staticmethod
    def create_profile_block(
        profile_type: StackProfile.ProfileType,
        offset_value: float = 0,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create block with stacing profile.

        Args:
            profile_type (StackProfile.ProfileType): Profile type
            offset_value (float, optional): Offset of profile sweep. Defaults to 0.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: _description_
        """
        with BuildPart() as part:
            with BuildSketch(Plane.XZ) as profile, Locations(
                (
                    gridfinity_standard.grid.size / 2 - offset_value,
                    0,
                ),
            ):
                StackProfile(profile_type, align=(Align.MAX, Align.MIN))
                if offset_value:
                    offset(
                        amount=offset_value,
                        kind=Kind.INTERSECTION,
                    )

            with BuildSketch() as rect:
                if profile_type == StackProfile.ProfileType.BIN:
                    e = gridfinity_standard.grid.tollerance
                else:
                    e = 0.0

                RectangleRounded(
                    gridfinity_standard.grid.size - e,
                    gridfinity_standard.grid.size - e,
                    gridfinity_standard.grid.radius - e * 0.5,
                )
            extrude(to_extrude=rect.face(), amount=profile.sketch.bounding_box().max.Z)

            path = part.wires().sort_by(Axis.Z)[-1]
            sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)
        return BasePartObject(part.part, rotation, align, mode)


class StackProfile(BaseSketchObject):
    """Gridfinity stacking profile."""

    class ProfileType(Enum):
        """Profile Type."""

        BIN = auto()
        PLATE = auto()

    def __init__(
        self,
        stack_type: ProfileType,
        rotation: float = 0,
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        """StackProfile.

        Create a profile of the gridfinity stacking system. Usualy used in the sweep function.

        Args:
            stack_type (ProfileType): Type of stacking lip (Bin vs Plate).
            rotation (float, optional): angles to rotate objects. Defaults to 0.
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to None.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.
        """
        if stack_type == StackProfile.ProfileType.BIN:
            height_3 = gridfinity_standard.stacking_lip.height_3_bin
        elif stack_type == StackProfile.ProfileType.PLATE:
            height_3 = gridfinity_standard.stacking_lip.height_3_base_plate
        else:  # pragma: no cover
            msg = "Unkown stack_type"
            raise ValueError(msg)

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
