"""Utiity module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

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
    Sketch,
    add,  # pyright: ignore[reportUnknownVariableType]
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
        match direction:
            case Direction.TOP:
                return (0, 0, 1)
            case Direction.BOT:
                return (0, 0, -1)
            case Direction.RIGHT:
                return (1, 0, 0)
            case Direction.LEFT:
                return (-1, 0, 0)
            case Direction.BACK:
                return (0, 1, 0)
            case Direction.FRONT:
                return (0, -1, 0)


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

        match attach:
            case Attach.TOP:
                location = (
                    0,
                    0,
                    context_part.bounding_box().max.Z
                    + -1 * part.bounding_box().min.Z
                    + offset_value,
                )
            case Attach.BOTTOM:
                location = (
                    0,
                    0,
                    context_part.bounding_box().min.Z
                    + -1 * part.bounding_box().max.Z
                    - offset_value,
                )
            case Attach.LEFT:
                location = (
                    context_part.bounding_box().min.X
                    + -1 * part.bounding_box().max.X
                    - offset_value,
                    0,
                    0,
                )
            case Attach.RIGHT:
                location = (
                    context_part.bounding_box().max.X
                    + -1 * part.bounding_box().min.X
                    + offset_value,
                    0,
                    0,
                )
            case Attach.FRONT:
                location = (
                    0,
                    context_part.bounding_box().min.Y
                    + -1 * part.bounding_box().max.Y
                    - offset_value,
                    0,
                )
            case Attach.BACK:
                location = (
                    0,
                    context_part.bounding_box().max.Y
                    + -1 * part.bounding_box().min.Y
                    + offset_value,
                    0,
                )

        with Locations(location):
            _ = add(part)

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
    def get_subclasses(class_name: type) -> list[type]:
        """Get subclasses of a base class recursively.

        Args:
            class_name (Any): class type to get subcalsses from

        Returns:
            Any: list of child class types
        """
        classes: list[type] = []

        for subclass in class_name.__subclasses__():
            classes.append(subclass)
            classes += Utils.get_subclasses(subclass)

        return classes

    @staticmethod
    def locate_grid(grid: list[list[bool]], width: float, length: float) -> list[Location]:
        """Generate locations for a grid with given spacing in x and y directions.

        Args:
            grid (list[list[bool]]): grid
            width (float): spacing of the grid in the x-direction.
            length (float): spacing of the grid in the y-direction.

        Returns:
            list[Location]: the locations for the grid.

        """
        locations: list[Location] = []
        for row_nr, row_value in enumerate(grid):
            for column_nr, column_value in enumerate(row_value):
                if column_value:
                    locations.append(
                        Location((width * (column_nr + 1), length * -(row_nr + 1))),
                    )

        return locations

    @staticmethod
    def place_sketch_by_grid(
        obj: Sketch,
        grid: list[list[bool]],
        width: float | None = None,
        length: float | None = None,
        rotation: float = 0,
        align: Align | tuple[Align, Align] = Align.CENTER,
        mode: Mode = Mode.ADD,
    ) -> BaseSketchObject:
        """Place multiple instances of a sketch according to a grid.

        Args:
            obj (BaseSketchObject): sketch to be copied
            grid (list[list[bool]]): grid
            width (float | None): spacing of the grid in the x-direction. Defaults to None.
            length (float | None): spacing of the grid in the y-direction. Defaults to None.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to Align.CENTER.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Returns:
            BaseSketchObject: gridlike sketch

        """
        bbox = obj.bounding_box()
        if width is None:
            width = bbox.size.X
        if length is None:
            length = bbox.size.Y

        locations = Utils.locate_grid(grid, width, length)

        with BuildSketch() as sketch, Locations(locations):
            _ = add(obj)

        return BaseSketchObject(sketch.sketch, rotation, align, mode)

    @staticmethod
    def place_by_grid(
        obj: BasePartObject,
        grid: list[list[bool]],
        width: float | None = None,
        length: float | None = None,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] = Align.CENTER,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Place multiple instances of object according to grid.

        Args:
            obj (BasePartObject): object to be copied
            grid (list[list[bool]]): grid
            width (float | None): spacing of the grid in the x-direction. Defaults to None.
            length (float | None): spacing of the grid in the y-direction. Defaults to None.
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to Align.CENTER.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Raises:
            ValueError: grid does not reasemble locations

        Returns:
            BasePartObject: gridlike object
        """
        if not width or not length:
            bbox = obj.bounding_box()
            if width is None:
                width = bbox.size.X
            if length is None:
                length = bbox.size.Y

        locations = Utils.locate_grid(grid, width, length)

        if not locations:
            msg = f"grid {grid} does not reasemble locations"
            raise ValueError(msg)

        with BuildPart() as part, Locations(locations):
            _ = add(obj)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

        return BasePartObject(part.part, rotation, align, mode)

    @staticmethod
    def create_bin_platform(
        grid: list[list[bool]],
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> BasePartObject:
        """Create the platform for the bin.

        This function considers that the bins have a different dimension than the base elements
        (41.5mm instead of 42mm). This is to allow for certain tolerance for the bins. Therefore the
        size of the grid is set to the gridfinity standard grid size instead of the size of the
        sketch.

        Args:
            grid (list[list[bool]]): grid
            rotation (RotationLike, optional): Angels to rotate around axes. Defaults to (0, 0, 0).
            align (Union[Align, tuple[Align, Align, Align]], optional): Align min center of max of
                object. Defaults to Align.CENTER.
            mode (Mode, optional): Combination mode. Defaults to Mode.ADD.

        Returns:
            BasePartObject: the upper part of the bin.

        """
        width = gridfinity_standard.grid.size
        length = gridfinity_standard.grid.size

        tol = gridfinity_standard.grid.tollerance

        with BuildSketch() as base:
            _ = Rectangle(length, width)

        base_grid = Utils.place_sketch_by_grid(base.sketch, grid, width=width, length=length)

        with BuildPart() as part:
            with BuildSketch() as base:
                _ = add(base_grid)
                _ = offset(amount=-tol / 2, kind=Kind.INTERSECTION)
                _ = fillet(base.vertices(), radius=gridfinity_standard.grid.radius - tol / 2)

            _ = extrude(amount=gridfinity_standard.bottom.platform_height)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

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
            with (
                BuildSketch(Plane.XZ) as profile,
                Locations(
                    (
                        gridfinity_standard.grid.size / 2 - offset_value,
                        0,
                    ),
                ),
            ):
                _ = StackProfile(profile_type, align=(Align.MAX, Align.MIN))
                if offset_value:
                    _ = offset(
                        amount=offset_value,
                        kind=Kind.INTERSECTION,
                    )

            with BuildSketch() as rect:
                if profile_type == StackProfile.ProfileType.BIN:
                    e = gridfinity_standard.grid.tollerance
                else:
                    e = 0.0

                _ = RectangleRounded(
                    gridfinity_standard.grid.size - e,
                    gridfinity_standard.grid.size - e,
                    gridfinity_standard.grid.radius - e * 0.5,
                )
            _ = extrude(to_extrude=rect.face(), amount=profile.sketch.bounding_box().max.Z)

            path = part.wires().sort_by(Axis.Z)[-1]
            _ = sweep(sections=profile.sketch, path=path, mode=Mode.SUBTRACT)

        if not part.part:  # pragma: no cover
            msg = "Part is empty"
            raise RuntimeError(msg)

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
        match stack_type:
            case StackProfile.ProfileType.BIN:
                height_3 = gridfinity_standard.stacking_lip.height_3_bin
            case StackProfile.ProfileType.PLATE:
                height_3 = gridfinity_standard.stacking_lip.height_3_base_plate

        with BuildSketch() as profile:
            with BuildLine():
                _ = Polyline(
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
            _ = make_face()
        super().__init__(profile.face(), rotation, align, mode)
