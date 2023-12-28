"""Feature Locations.

Module containing classes responsible for the location of features.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator

from build123d import (
    GridLocations,
    Locations,
    Part,
)

from .constants import gridfinity_standard
from .utils import Direction, Utils


class FeatureLocation(ABC):
    """Feature location type.

    Child classes of this type are responsible for the location of features.
    """

    @abstractmethod
    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:
        """Applies feature to Part.

        Args:
            part (Part): part to add feature to

        Raises:
            NotImplementedError: aplly_to not implemented.

        Yields:
            Iterator[None]: context manager return value.
        """
        raise NotImplementedError  # pragma: no cover


class FaceDirection(FeatureLocation):
    """Face Direction location.

    Locates feature on face by direction.
    """

    def __init__(self, face_direction: Direction | None = None) -> None:
        """Create FaceDirection.

        Args:
            face_direction (Direction | None, optional): Direction of face where feature should be
                located. Defaults to None.
        """
        self._direction = face_direction

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        if self._direction:
            face = Utils.get_face_by_direction(part, self._direction)
            with Locations(face.center()), Locations(
                Direction.to_rotation(self._direction),
            ):
                yield
        else:
            yield


class Middle(FaceDirection):
    """Middle feature location.

    Locates the feature in the middle of a face
    """

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        with super().apply_to(part):
            yield


class Corners(FaceDirection):
    """Corners feature location.

    Locates a feature in the corner.
    """

    def __init__(
        self,
        face_direction: Direction,
        offset: float = gridfinity_standard.bottom.hole_from_side,
    ) -> None:
        """Construct Conrers location object.

        Args:
            face_direction (Direction): Direction of the face where features should be located in the
                corners.
            offset (float, optional): Distance from feature to corner. Defaults to
                gridfinity_standard.bottom.hole_from_side.
        """
        super().__init__(face_direction)
        self._offset = offset

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        if not self._direction:  # pragma: no cover
            msg = "No direction given"
            raise ValueError(msg)
        face = Utils.get_face_by_direction(part, self._direction)
        self._corner_distance_x = face.length - 2 * self._offset
        self._corner_distance_y = face.width - 2 * self._offset

        with super().apply_to(part), GridLocations(
            self._corner_distance_x,
            self._corner_distance_y,
            2,
            2,
        ):
            yield
