# %%
import base64
import io
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yaml
import requests
import pandas as pd
import geopandas as gpd
import folium
import webbrowser
import os
from multiprocessing import Pool, freeze_support
from flask import Flask
from datetime import datetime
import platform
import socket
import logging
from threading import Timer


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
                ["Drag and Drop or ", html.A("Select a config.yaml file")]
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
        dcc.Interval(
            id="interval-component",
            interval=30 * 1000,  # 30 seconds
            n_intervals=0,
        ),
        dcc.Store(
            id="stored-data"
        ),  # Hidden storage for persisting data across callbacks
        html.Div(
            [
                html.A(
                    html.Img(
                        src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/video/gw.png?raw=true",
                        style={"height": "70px", "margin": "4px"},
                    ),
                    href="https://geography.columbian.gwu.edu/",
                ),
                html.A(
                    html.Img(
                        src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/video/pygis.png?raw=true",
                        style={"height": "70px", "margin": "4px"},
                    ),
                    href="https://pygis.io",
                ),
                html.A(
                    html.Img(
                        src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/video/youthmappers.webp?raw=true",
                        style={"height": "70px", "margin": "4px"},
                    ),
                    href="https://pygis.io",
                ),
                html.Br(),
                html.Br(),
                html.Br(),
                html.A(
                    html.Img(
                        src="https://zenodo.org/badge/DOI/10.5281/zenodo.11387666.svg"
                    ),
                    href="https://doi.org/10.5281/zenodo.11387666",
                ),
            ],
            style={"textAlign": "center", "padding": "20px"},
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


# Function to fetch user edits today
def fetch_user_edits_today(username):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    query = f"""
    [out:json][timeout:25];
    (
      node(user:"{username}")(newer:"{today}T00:00:00Z");
      way(user:"{username}")(newer:"{today}T00:00:00Z");
      relation(user:"{username}")(newer:"{today}T00:00:00Z");
    );
    out body;
    >;
    out skel qt;
    """

    response = requests.post(OVERPASS_URL, data={"data": query})

    if response.status_code == 200:
        data = response.json()
        if "elements" in data and len(data["elements"]) > 0:
            return data["elements"]
        else:
            return []
    else:
        response.raise_for_status()


# Function to create a map with user edits
def create_map(user_edits, map_file):
    if user_edits:
        # Create a base map
        m = folium.Map(location=[0, 0], zoom_start=2)

        for element in user_edits:
            if element["type"] == "node":
                folium.CircleMarker(
                    location=[element["lat"], element["lon"]],
                    radius=2,
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.6,
                    popup=f"Node ID: {element['id']}",
                ).add_to(m)
            elif element["type"] in ["way", "relation"]:
                coords = []
                for member in element["geometry"]:
                    coords.append([member["lat"], member["lon"]])
                folium.PolyLine(
                    locations=coords,
                    color="blue",
                    weight=2,
                    opacity=0.6,
                    popup=f"{element['type'].capitalize()} ID: {element['id']}",
                ).add_to(m)

        # Save map to an HTML file
        m.save(map_file)


# Callback to handle the file upload and initialize data
@app.callback(
    Output("stored-data", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def handle_upload(contents, filename):
    if contents:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            if "yaml" in filename:
                config = yaml.safe_load(io.StringIO(decoded.decode("utf-8")))
                return config  # Store the entire configuration
        except Exception as e:
            return None
    return None


# Callback to update data based on the interval
@app.callback(
    [
        Output("output-data-upload", "children"),
        Output("map", "srcDoc"),
        Output("table", "columns"),
        Output("table", "data"),
    ],
    [Input("interval-component", "n_intervals"), Input("stored-data", "data")],
)
def update_data(n_intervals, stored_data):
    if stored_data:
        bbox = stored_data["bbox"]
        usernames = stored_data["usernames"]
        newer_date = convert_to_iso8601(stored_data.get("newer_than_date"))

        with Pool(processes=len(usernames)) as pool:
            results = pool.starmap(
                fetch_node_count,
                [(username, newer_date, bbox) for username in usernames],
            )

        user_node_counts = {username: count for username, count in results}
        df = pd.DataFrame(user_node_counts.items(), columns=["Username", "Node_Count"])
        df.sort_values(by="Node_Count", ascending=False, inplace=True)

        # Generate a simple GeoDataFrame with a bounding box
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

        map_obj = bbox_gpd.explore(style_kwds={"fillColor": "blue", "color": "black"})
        map_src = map_obj.get_root().render()

        # Update the map with today's edits of the top user
        top_user = df.iloc[0]["Username"]
        user_edits = fetch_user_edits_today(top_user)
        map_file = "user_edits_map.html"
        create_map(user_edits, map_file)

        return (
            f"Data updated at interval {n_intervals}",
            open(map_file).read(),
            [{"name": i, "id": i} for i in df.columns],
            df.to_dict("records"),
        )
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


def open_browser(port):
    webbrowser.open_new(f"http://127.0.0.1:{port}/")


def main():
    print("This app brought to you by https://pygis.io")
    # Ensure compatibility with Windows exe for threading
    if platform.system() == "Windows":
        freeze_support()

    try:
        # Setup a socket to dynamically find a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))  # Bind to a free port provided by the host.
            port = s.getsockname()[1]

        # Open a web browser pointed at the URL
        Timer(1, open_browser, args=[port]).start()

        # Run the Dash app on the dynamically assigned port
        app.run_server(port=port, debug=False)
    except Exception as e:
        print(f"Failed to start the application: {e}")


if __name__ == "__main__":
    main()

# %%
