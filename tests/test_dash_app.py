import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from dash_app import app, fetch_node_count
import requests_mock
from dash.testing.application_runners import ThreadedRunner


class TestDashApp(unittest.TestCase):

    def setUp(self):
        # Initialize the Dash test client and the ThreadedRunner with the app
        self.app = app.server.test_client()
        self.runner = ThreadedRunner()

    def test_page_loads(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_fetch_node_count(self, mock):
        mock.post(
            "https://overpass-api.de/api/interpreter",
            json={"elements": [{"tags": {"nodes": "5"}}]},  # Mock the response
        )
        result = fetch_node_count(
            "mmann1123",
            "2020-01-01T00:00:00Z",
            "40.551042, -74.05663, 40.739446, -73.833365",
        )
        self.assertEqual(result, ("mmann1123", "5"))


if __name__ == "__main__":
    unittest.main()
