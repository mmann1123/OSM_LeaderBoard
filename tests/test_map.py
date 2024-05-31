import unittest
from shapely.geometry import Polygon, LineString, Point
import folium
from osm_leaderboard.map import explore_shapely_object


class TestExploreShapelyObject(unittest.TestCase):
    def test_polygon(self):
        polygon = Polygon(
            [
                (-77.119759, 38.791645),
                (-77.119759, 38.995548),
                (-76.909393, 38.995548),
                (-76.909393, 38.791645),
                (-77.119759, 38.791645),
            ]
        )
        map_obj = explore_shapely_object(polygon, color="red")
        self.assertIsInstance(map_obj, folium.Map)

    def test_line(self):
        line = LineString([(-77.119759, 38.791645), (-76.909393, 38.995548)])
        map_obj = explore_shapely_object(line, color="green")
        self.assertIsInstance(map_obj, folium.Map)

    def test_point(self):
        point = Point(-77.0369, 38.9072)
        map_obj = explore_shapely_object(point, color="blue")
        self.assertIsInstance(map_obj, folium.Map)
