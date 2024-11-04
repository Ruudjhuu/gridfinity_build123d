import testutils

from gridfinity_build123d.connectors import GridfinityRefinedConnector


class GridfinityRefinedConnectorTest(testutils.UtilTestCase):
    def test_gridfinityrefinedconnector(self) -> None:
        part = GridfinityRefinedConnector()

        bbox = part.bounding_box()

        self.assertVectorAlmostEqual((13.6, 17.4, 2.8), bbox.size)
        self.assertAlmostEqual(445.86058561576374, part.volume)
