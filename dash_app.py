# %%
import base64
import io
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yaml
import requests
from multiprocessing import Pool
import pandas as pd
import geopandas as gpd
import webbrowser
from threading import Timer, Thread
import subprocess
import os
import signal
from flask import Flask
import platform

# Define the Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Create a Flask server
server = Flask(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, server=server)

# Define the layout of your Dash app
app.layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and Drop or ", html.A("Select \n config.yaml file")]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=False,
        ),
        dcc.Loading(
            id="loading",
            type="circle",
            children=[
                html.Div(id="output-data-upload"),
                html.Iframe(id="map", style={"width": "100%", "height": "50vh"}),
                dash_table.DataTable(id="table"),
            ],
        ),
    ]
)


# Convert the newer_date to ISO 8601 format if provided
def convert_to_iso8601(date_str):
    if date_str:
        return f"{date_str}T00:00:00Z"
    return None


# Function to fetch node count for a username
def fetch_node_count(username, newer_date, bbox):
    date_filter = ""
    if newer_date:
        date_filter = f'(newer:"{newer_date}")'

    query = f"""
    [out:json][timeout:25];
    (
      node(user:"{username}"){date_filter}({bbox});
    );
    out count;
    """

    # Send the request to the Overpass API
    response = requests.post(OVERPASS_URL, data={"data": query})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Assuming the count is directly in the "total" field of the JSON. Adjust if necessary.
        count = data.get("elements", [{}])[0].get("tags", {}).get("nodes", "N/A")
        return username, count
    else:
        return username, "N/A"


# Define a callback to handle the uploaded file
@app.callback(
    [
        Output("output-data-upload", "children"),
        Output("map", "srcDoc"),
        Output("table", "columns"),
        Output("table", "data"),
    ],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(content, name):
    if content is not None:
        content_type, content_string = content.split(",")
        decoded = base64.b64decode(content_string)
        try:
            if "yaml" in name:
                # Assume that the user uploaded a yaml file
                config = yaml.safe_load(io.StringIO(decoded.decode("utf-8")))
                # Use the config data to update your app
                bbox = config["bbox"]
                usernames = config["usernames"]
                newer_date = config.get("newer_than_date")
                newer_date = convert_to_iso8601(newer_date)

                with Pool(processes=len(usernames)) as pool:
                    results = pool.starmap(
                        fetch_node_count,
                        [(username, newer_date, bbox) for username in usernames],
                    )

                # Initialize a dictionary to store the count of nodes added by each user
                user_node_counts = dict(results)

                # convert Node_count to integers using dictionary comprehension
                user_node_counts = {k: int(v) for k, v in user_node_counts.items()}

                out = pd.DataFrame(
                    user_node_counts.items(), columns=["Username", "Node_Count"]
                )
                # sort in descending order
                df = out.sort_values(by="Node_Count", ascending=False)

                # Create a simple GeoDataFrame with a bounding box
                min_lat, min_lon, max_lat, max_lon = map(float, bbox.split(","))
                bbox_gpd = gpd.GeoDataFrame.from_features(
                    [
                        {
                            "type": "Feature",
                            "properties": {},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [min_lon, min_lat],
                                        [min_lon, max_lat],
                                        [max_lon, max_lat],
                                        [max_lon, min_lat],
                                        [min_lon, min_lat],
                                    ]
                                ],
                            },
                        }
                    ],
                    crs="EPSG:4326",
                )

                map_obj = bbox_gpd.explore(
                    style_kwds={"fillColor": "blue", "color": "black"}
                )

                map_src = map_obj.get_root().render()
                table_columns = [{"name": i, "id": i} for i in df.columns]
                table_data = df.to_dict("records")

                return (
                    # 'File "{}" successfully uploaded.'.format(name),
                    "",
                    map_src,
                    table_columns,
                    table_data,
                )
        except Exception as e:
            print(e)
            return (
                "There was an error processing this file.",
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

    return None, dash.no_update, dash.no_update, dash.no_update


# Define a function to stop the server
def stop_server():
    if platform.system() == "Windows":
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        os.kill(os.getpid(), signal.SIGINT)


def open_browser():
    webbrowser.open_new(f"http://127.0.0.1:{port}/")


import socket


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


if __name__ == "__main__":
    # Assign a random port between 8000 and 8999
    port = 8050

    # Try to kill any process using the port
    try:
        if platform.system() == "Windows":
            command = f"netstat -ano | findstr :{port}"
        else:
            command = f"lsof -t -i :{port}"

        result = subprocess.check_output(command, shell=True)
        if platform.system() != "Windows":
            os.kill(int(result), signal.SIGKILL)
            # wait 3 seconds
            subprocess.run(["sleep", "3"])
            print(f"Killed process on port {port}")
        elif platform.system() == "Windows":
            pid = result.decode().split(" ")[-1]
            subprocess.run(["taskkill", "/F", "/PID", pid])
            print(f"Killed process on port {port}")
    except subprocess.CalledProcessError:
        print(f"No process running on port {port}")

        # Start a timer to stop the server after 10 minutes
        # Timer(10 * 60, stop_server).start()

    # Check if port is in use
    Timer(1, open_browser).start()  # Start the browser with a slight delay
    app.run_server(debug=False, port=port)


# %%
# build the app with pyinstaller
# pyinstaller --onefile --name leaderboard_linux dash_app.py
# chmod -R +x ./dist/leaderboard_linux
# ./dist/leaderboard_linux

# build windows app
# pyinstaller --onefile --name leaderboard_win dash_app.py
