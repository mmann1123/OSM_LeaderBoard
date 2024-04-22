# %%
import dash
from dash import html, dcc
import pandas as pd
import geopandas as gpd
from dash.dependencies import Input, Output
from dash import dash_table
import requests
import os

# Define the Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Define the bounding box
# Format: "min_latitude, min_longitude, max_latitude, max_longitude"
# You can use http://bboxfinder.com/  IMPORTANT: switch "coordinate format" to "Lat / Lng"
bbox = "40.551042, -74.05663, 40.739446, -73.833365"

# List of usernames to query
usernames = [
    "mmann1123",
    "haycam",
    "I-Izzo",
    "isamah",
    "livmakesmaps",
    "kangaroo5445",
    "brikin",
    "caitnahc",
    "KQWilson",
    "o_paq",
    "DuckDuckCat",
    "ryleeloveshot",
    "norabutter",
]

# Initialize a dictionary to store the count of nodes added by each user
user_node_counts = {}

for username in usernames:
    # Define the Overpass QL query for the current username
    query = f"""
    [out:json];
    (
      node(user:"{username}")({bbox});
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
        user_node_counts[username] = count
    else:
        print(
            f"Query for user '{username}' failed with status code {response.status_code}"
        )

# Print the resulting dictionary
print("Node counts by user:", user_node_counts)
import pandas as pd

# if results exist delete file
try:
    os.remove("./user_node_counts.csv")
except:
    pass

# convert Node_count to intergers using dictionary comprehension
user_node_counts = {k: int(v) for k, v in user_node_counts.items()}

out = pd.DataFrame(user_node_counts.items(), columns=["Username", "Node_Count"])
# sort in descending order
out = out.sort_values(by="Node_Count", ascending=False)
out
out.to_csv("./user_node_counts.csv", index=False)

########################################################################################
#  create python dashboard


# Initialize the Dash app
app = dash.Dash(__name__)

# Load your CSV data into DataFrame
df = pd.read_csv(
    "user_node_counts.csv"
)  # Replace 'path_to_your_file.csv' with the actual path to your CSV file

# Create a simple GeoDataFrame with a bounding box
# Replace these coordinates with the ones for your specific bounding box
min_lat, min_lon, max_lat, max_lon = map(float, bbox.split(","))

# Create a simple GeoDataFrame with a bounding box
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
bbox_gpd.explore(style_kwds={"fillColor": "blue", "color": "black"}).save(
    "inlaymap.html"
)

# Define the layout of your Dash app
app.layout = html.Div(
    [
        html.Iframe(
            srcDoc=open("inlaymap.html", "r").read(),
            style={
                "width": "100%",
                "height": "500px",
            },  # Adjust the height and width as needed
        ),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
        ),
    ]
)

# Run the server
if __name__ == "__main__":
    app.run_server(debug=False)

print("Run the server and connect to http://127.0.0.1:8050/")

# %% JS CODE VERSION NOT WORKING WELL
# start the server connect to http://0.0.0.0:8000/ in a web browser

# !python -m http.server

# %%
