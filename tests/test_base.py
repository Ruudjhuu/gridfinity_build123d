import unittest
import sys
import os
from build123d import *
import gridfinity_build123d

# Not needed for testing but handy for developing
try:
    from ocp_vscode import set_port
    set_port(3939)
except ImportError:
    # ignore if not installed
    pass


class BaseTest(unittest.TestCase):
    def test_base(self) -> None:
        with BuildPart() as part:
            gridfinity_build123d.base.Base()

        bbox = part.part.bounding_box()
        self.assertEqual(Vector(42,42,6.003553390593281), bbox.size)
        self.assertEqual(8901.250776327015,part.part.volume)

class StackProfileTest(unittest.TestCase):
    def test_profile(self)->None:
        with BuildSketch() as sketch:
            gridfinity_build123d.base.StackProfile()

        bbox = sketch.sketch.bounding_box()

        self.assertEqual(Vector(2.5999999999999996,4.4,0), bbox.size)
        self.assertEqual(6.8, sketch.sketch.area)

