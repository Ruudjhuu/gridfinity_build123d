"""Feature Locations.

Module containing classes responsible for the location of features.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING

from build123d import (
    Axis,
    BoundBox,
    Box,
    Edge,
    Face,
    GeomType,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Rotation,
    ShapePredicate,
    Vector,
)

from .constants import gridfinity_standard

if TYPE_CHECKING:
    from collections.abc import Iterator


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
    def _apply_on_corners(
        self,
        center: Location,
        bbox: BoundBox,
    ) -> Iterator[None]:
        polar_dist = (bbox.size.X**2 + bbox.size.Y**2) ** 0.5
        polar_offset = (self._offset**2 + self._offset**2) ** 0.5

        with (
            Locations(center),
            PolarLocations(
                polar_dist / 2 - polar_offset,
                4,
                -45,
            ),
            Locations(Rotation(0, 0, -90)),
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


class BottomSides(FeatureLocation):
    """Bottom Sides.

    Locate objects at the sides of the bottom plane
    """

    def __init__(self, nr_x: int = 1, nr_y: int = 1, offset: float = 0) -> None:
        """Creste BottomSides object.

        Args:
            nr_x (int, optional): Number of objects which should be located on edges parallel
                to the x axis. Defaults to 1.
            nr_y (int, optional): Number of objects which should be located on edges parallel
                with the y axis. Defaults to 1.
            offset (float, optional): Distance from the side to the located objects. Defaults to 0.
        """
        self._nr_x = nr_x
        self._nr_y = nr_y
        self._offset = offset

    @contextmanager
    def apply_to(self, part: Part) -> Iterator[None]:  # noqa: D102
        bbox = part.bounding_box()

        box = Box(bbox.size.X, bbox.size.Y, bbox.size.Z, mode=Mode.PRIVATE)
        box.locate(Location(bbox.center()))

        face = box.faces().sort_by(Axis.Z)[0]

        pts: list[Location] = []
        pts += self._get_locations_on_edges(Axis.X, face, self._nr_x)
        pts += self._get_locations_on_edges(Axis.Y, face, self._nr_y)

        with Locations(face), Locations(pts), Locations((0, self._offset, 0)):
            yield

    def _get_locations_on_edges(
        self,
        edge_filter: ShapePredicate | Axis | Plane | GeomType,
        face: Face,
        nr_of_points: int,
    ) -> list[Location]:
        pts_list: list[Location] = []

        for edge in face.edges().filter_by(edge_filter):
            pp_edge = edge.perpendicular_line(0.1, 0.5, Plane(face))

            to_front = Edge.make_line(
                pp_edge.start_point(),
                pp_edge.start_point() + Vector(0, -1, 0),
            )

            angle = pp_edge.tangent_at(0).get_signed_angle(to_front.tangent_at(0))

            for i in range(nr_of_points):
                pos = edge.location_at(1 / (nr_of_points * 2) * (i * 2 + 1)).position
                pts_list.append(
                    Location(
                        pos - face.center_location.position,
                        (0, 0, angle),
                    ),
                )

        return pts_list
