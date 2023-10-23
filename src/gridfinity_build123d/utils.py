"""Utiity module."""
from __future__ import annotations
from enum import Enum, auto
from typing import Tuple

from build123d import Builder, BuildPart, add, Locations, Part


class Attach(Enum):
    """Attach.

    Enum for indicating direction when attaching objects
    """

    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    BACK = auto()
    FRONT = auto()
    CENTER = auto()


class Utils:  # pylint: disable=too-few-public-methods
    """Utils.

    Class wrapping utility functions
    """

    @staticmethod
    def attach(part: Part, attach: Attach, offset: float = 0) -> None:
        """attach.

        attaches other object acording to "attach"

        Args:
            part (Part): the part to be attached
            attach (Attach): Direction to attach

        Raises:
            RuntimeError: Attach must have an active builder context
            RuntimeError: Attach only works for BuildPart (yet)
        """
        context: Builder = Builder._get_context(None)  # pylint: disable=protected-access
        if context is None:
            raise RuntimeError("Attach must have an active builder context")
        if not isinstance(context, BuildPart):
            raise RuntimeError("Attach only works for BuildPart (yet)")
        if not context._obj:  # pylint: disable=protected-access
            raise ValueError("Nothing to attach to")

        location: Tuple[float, float, float] = (0, 0, 0)

        match (attach):
            case (Attach.TOP):
                location = (
                    0,
                    0,
                    context.part.bounding_box().max.Z + -1 * part.bounding_box().min.Z + offset,
                )
            case (Attach.BOTTOM):
                location = (
                    0,
                    0,
                    context.part.bounding_box().min.Z + -1 * part.bounding_box().max.Z - offset,
                )
            case (Attach.LEFT):
                location = (
                    context.part.bounding_box().min.X + -1 * part.bounding_box().max.X - offset,
                    0,
                    0,
                )
            case (Attach.RIGHT):
                location = (
                    context.part.bounding_box().max.X + -1 * part.bounding_box().min.X + offset,
                    0,
                    0,
                )
            case (Attach.FRONT):
                location = (
                    0,
                    context.part.bounding_box().min.Y + -1 * part.bounding_box().max.Y - offset,
                    0,
                )
            case (Attach.BACK):
                location = (
                    0,
                    context.part.bounding_box().max.Y + -1 * part.bounding_box().min.Y + offset,
                    0,
                )
            case (_):  # pragma: nocover
                raise ValueError("Unkown attach type")  # pragma: nocover

        with Locations(location):
            add(part)
