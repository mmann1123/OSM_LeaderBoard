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
from datetime import datetime, timezone
import webbrowser
from threading import Timer

# Define the Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of your Dash app
app.layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select a Config File")]),
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
            # Allow multiple files to be uploaded
            multiple=False,
        ),
        html.Div(id="output-data-upload"),
        html.Iframe(id="map", style={"width": "100%", "height": "500px"}),
        dash_table.DataTable(id="table"),
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
                bbox_gpd.explore(
                    style_kwds={"fillColor": "blue", "color": "black"}
                ).save("inlaymap.html")

                # Update the layout of your Dash app
                map_src = open("inlaymap.html", "r").read()
                table_columns = [{"name": i, "id": i} for i in df.columns]
                table_data = df.to_dict("records")

                return (
                    'File "{}" successfully uploaded.'.format(name),
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


# Run the server
if __name__ == "__main__":
    app.run_server(debug=False)
    # open browser and connect to http://127.0.0.1:8050/
    Timer(1, lambda: webbrowser.open("http://127.0.0.1:8050/")).start()
    app.run_server(debug=False)

# %%
