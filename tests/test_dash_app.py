import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from osm_leaderboard.dash_app import app, fetch_node_count
import requests_mock
from dash.testing.application_runners import ThreadedRunner, import_app
import base64


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

    # # Example test for the Dash app's main functionality
    # def test_main(dash_duo):
    #     with requests_mock.Mocker() as m:
    #         # Mock the Overpass API response
    #         expected_url = "https://overpass-api.de/api/interpreter"
    #         mock_response = {"elements": [{"tags": {"nodes": "100"}}]}
    #         m.post(expected_url, json=mock_response)

    #         # Start the Dash app
    #         app = import_app(
    #             "osm_leaderboard.dash_app",
    #         )
    #         dash_duo.run(app)

    #         # Simulate uploading a YAML file
    #         yaml_content = """
    #         bbox: "40.551042, -74.05663, 40.739446, -73.833365"
    #         usernames:
    #         - mmann1123
    #         - haycam
    #         newer_than_date: "2010-12-01"
    #         """
    #         # Convert YAML content to Base64 to simulate file upload
    #         base64_content = base64.b64encode(yaml_content.encode("utf-8")).decode(
    #             "utf-8"
    #         )
    #         file_content = f"data:application/octet-stream;base64,{base64_content}"

    #         # Find and interact with the upload component
    #         dash_duo.find_element("#upload-data").send_keys(file_content)

    #         # Allow time for the app to process the upload and perform callbacks
    #         dash_duo.wait_for_text_to_equal(
    #             "#output-data-upload", "Upload successful", timeout=15
    #         )

    #         # Check for expected outputs in the app
    #         assert dash_duo.find_element(
    #             "#table"
    #         ).is_displayed(), "Data table should be displayed with results"

    #         # Verify the content of the table or other components as needed


if __name__ == "__main__":
    unittest.main()
