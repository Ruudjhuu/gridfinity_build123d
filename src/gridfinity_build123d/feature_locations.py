"""Feature Locations.

Module containing classes responsible for the location of features.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator

from build123d import (
    BoundBox,
    GridLocations,
    Location,
    Locations,
    Part,
)

from .constants import gridfinity_standard


class FeatureLocation(ABC):
    """Feature location.

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


class TopMiddle(FeatureLocation):
    """Top Middle feature location.

    Locate a feature top center of the boundingbox of an object
    """

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        bbox = part.bounding_box()
        center = bbox.center()
        center.Z = bbox.max.Z
        with Locations(center):
            yield


class BottomMiddle(FeatureLocation):
    """Bottom Middle feature location.

    Locate a feature bottom center of the boundingbox of an object
    """

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        bbox = part.bounding_box()
        center = bbox.center()
        center.Z = bbox.min.Z
        with Locations(Location(center, (180, 0, 0))):
            yield


class Corners(FeatureLocation):
    """Abstract corners class.

    Contains helper function to locate objects in the corners of a face from a boundingbox.
    """

    def __init__(self, offset: float = 0) -> None:
        """Only callable by a child object.

        Args:
            offset (float, optional): The ofset from corner to final location. Defaults to 0.
        """
        self._offset = offset

    @contextmanager
    def _apply_on_corners(self, center: Location, bbox: BoundBox) -> Iterator[None]:
        self._corner_distance_x = bbox.size.X - 2 * self._offset
        self._corner_distance_y = bbox.size.Y - 2 * self._offset

        with Locations(center), GridLocations(
            self._corner_distance_x,
            self._corner_distance_y,
            2,
            2,
        ):
            yield


class BottomCorners(Corners):
    """Bottom Corners.

    Locate a feature at the corners of the bottom plane of a objects boundingbox.
    """

    def __init__(
        self,
        offset: float = gridfinity_standard.bottom.hole_from_side,
    ) -> None:
        """Create Bottom corners object.

        Args:
            offset (float, optional): The ofset from corner to final location. Defaults to
                gridfinity_standard.bottom.hole_from_side.
        """
        super().__init__(offset)

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        bbox = part.bounding_box()
        center = bbox.center()
        center.Z = bbox.min.Z
        with self._apply_on_corners(Location(center, (180, 0, 0)), bbox):
            yield


class TopCorners(Corners):
    """Top Corners.

    Locate a feature at the conrers of the top plane of a boundingbox.
    """

    def __init__(
        self,
        offset: float = gridfinity_standard.bottom.hole_from_side,
    ) -> None:
        """Create Top corners object.

        Args:
            offset (float, optional): The ofset from corner to final location. Defaults to
                gridfinity_standard.bottom.hole_from_side.
        """
        super().__init__(offset)

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        bbox = part.bounding_box()
        center = bbox.center()
        center.Z = bbox.max.Z
        with self._apply_on_corners(Location(center), bbox):
            yield
