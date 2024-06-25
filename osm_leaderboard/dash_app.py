# %%
import base64
import io
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yaml
import requests
from multiprocessing import Pool, freeze_support
import webbrowser
from threading import Timer
from flask import Flask
import platform
import socket
import logging
from shapely.geometry import Polygon
from osm_leaderboard.map import explore_shapely_object

# Setup logging
logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

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
            interval=60 * 1000,  # 30 seconds
            n_intervals=0,
            max_intervals=60,
        ),
        dcc.Store(
            id="stored-data"
        ),  # Hidden storage for persisting data across callbacks
        html.Div(
            [
                html.A(
                    html.Img(
                        src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/gw.png?raw=true",
                        style={"height": "70px", "margin-right": "10px"},
                    ),
                    href="https://geography.columbian.gwu.edu/",
                ),
                html.A(
                    html.Img(
                        src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/pygis.png?raw=true",
                        style={"height": "70px", "margin-right": "10px"},
                    ),
                    href="https://pygis.io",
                ),
                html.A(
                    html.Img(
                        src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/youthmappers.webp?raw=true",
                        style={"height": "70px"},
                    ),
                    href="https://www.youthmappers.org/",
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
def fetch_node_count(username, newer_date, area):
    logging.debug(
        f"Fetching node count for {username} with filter date {newer_date} and area {area}"
    )
    date_filter = ""
    if newer_date:
        date_filter = f'(newer:"{newer_date}")'

    if ":" in area:  # is OSM id
        if "way" in area:
            area_fix = f"way({area.split(':')[1]});map_to_area"
        elif "rel" in area:
            area_fix = f"rel({area.split(':')[1]});map_to_area"
        else:
            logging.error(
                f"Area not understood"
            )
            return username, "N/A"

        query = f"""
            [out:json][timeout:25];
            {area_fix}->.searchArea;
            (
              node(user:"{username}"){date_filter}(area.searchArea);
            );
            out count;
            """

    elif "," in area:  # is bbox
        query = f"""
            [out:json][timeout:25];
            (
              node(user:"{username}"){date_filter}({area});
            );
            out count;
            """
    else:
        logging.error(
            f"Area not understood"
        )
        return username, "N/A"

    # Send the request to the Overpass API
    response = requests.post(OVERPASS_URL, data={"data": query})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Assuming the count is directly in the "total" field of the JSON. Adjust if necessary.
        count = data.get("elements", [{}])[0].get("tags", {}).get("nodes", "N/A")
        logging.info(f"Node count for {username}: {count}")

        return username, count
    else:
        logging.error(
            f"Failed to fetch node count for {username}: HTTP {response.status_code}"
        )
        return username, "N/A"


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
            logging.error("Failed to process uploaded file:", exc_info=True)
            return None
    return None


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
        area = stored_data["area"]
        usernames = stored_data["usernames"]
        newer_date = convert_to_iso8601(stored_data.get("newer_than_date"))

        with Pool(processes=len(usernames)) as pool:
            results = pool.starmap(
                fetch_node_count,
                [(username, newer_date, area) for username in usernames],
            )

        user_node_counts = {username: count for username, count in results}
        sorted_user_node_counts = sorted(
            user_node_counts.items(), key=lambda item: item[1], reverse=True
        )
        data_for_datatable = [
            {"Username": user, "Node_Count": count}
            for user, count in sorted_user_node_counts
        ]

        # Draw Polygon
        if ":" in area:  # is OSM id
            if "way" in area:
                query = f"""
                        [out:json][timeout:25];
                        way({area.split(':')[1]});
                        out geom;
                        """

                response = requests.post(OVERPASS_URL, data={"data": query})

                if response.status_code == 200:
                    polygon_in_json = response.json()
                    coord_list = []
                    for node in polygon_in_json["elements"][0]["geometry"]:
                        coord_list.append((node["lon"], node["lat"]))
                    polygon = Polygon(coord_list)

            elif "rel" in area:
                polygon = Polygon([[0, 0], [0, 0], [0, 0], [0, 0]])  # TODO: Visualize OSM Multipolygons
            else:
                logging.error(
                    f"Area not understood"
                )
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        elif "," in area:  # is bbox
            min_lat, min_lon, max_lat, max_lon = map(float, area.split(","))
            polygon = Polygon(
                [
                    [min_lon, min_lat],
                    [min_lon, max_lat],
                    [max_lon, max_lat],
                    [max_lon, min_lat],
                    [min_lon, min_lat],
                ]
            )
        else:
            logging.error(
                f"Area not understood"
            )
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        map_obj = explore_shapely_object(polygon, color="blue")
        map_src = map_obj.get_root().render()

        return (
            f"Remaining updates: {60 - n_intervals}",
            map_src,
            [{"name": i, "id": i} for i in data_for_datatable[0].keys()],
            data_for_datatable,
        )
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


def open_browser(port):
    webbrowser.open_new(f"http://127.0.0.1:{port}/")


def main():
    logging.info("Executing main block.")
    # Ensure compatibility with Windows exe for threading
    if platform.system() in ["Windows", "Darwin"]:
        freeze_support()

    try:
        # Setup a socket to dynamically find a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))  # Bind to a free port provided by the host.
            port = s.getsockname()[1]
            logging.info(f"Assigned port {port} for the app.")

        # Open a web browser pointed at the URL
        Timer(1, open_browser, args=[port]).start()
        logging.info(f"Browser will open at http://127.0.0.1:{port}/")

        # Run the Dash app on the dynamically assigned port
        app.run_server(port=port, debug=True)
        logging.info("Application has started.")
    except Exception as e:
        logging.error("Failed to start the application:", exc_info=True)


if __name__ == "__main__":
    main()
# %%
# build the app with pyinstaller
# pyinstaller --onefile --name leaderboard_linux dash_app.py
# chmod -R +x ./dist/leaderboard_linux
# ./dist/leaderboard_linux

# build windows app
# pyinstaller --onefile --name leaderboard_win dash_app.py

# not working
# ncxfreeze --script dash_app.py
