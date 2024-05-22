# %%
import requests
import yaml
from datetime import datetime, timezone
import dash
import pandas as pd
import requests
import yaml
import geopandas as gpd
from dash import dash_table
from dash import html
import requests
import yaml
from multiprocessing import Pool

# Load configuration from config.yaml
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

bbox = config["bbox"]
usernames = config["usernames"]
newer_date = config.get("newer_than_date")


# Convert the newer_date to ISO 8601 format if provided
def convert_to_iso8601(date_str):
    if date_str:
        return f"{date_str}T00:00:00Z"
    return None


newer_date = convert_to_iso8601(newer_date)

# Define the Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# Function to fetch node count for a username
def fetch_node_count(username):
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

    # Print the query for debugging
    print("Query for user:", username)
    print(query)

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
        print(
            f"Query for user '{username}' failed with status code {response.status_code}"
        )
        print("Response content:", response.content.decode("utf-8"))
        return username, "N/A"


with Pool(processes=len(usernames)) as pool:
    results = pool.map(fetch_node_count, usernames)

# Initialize a dictionary to store the count of nodes added by each user
user_node_counts = dict(results)


# Print the resulting dictionary
print("Node counts by user:", user_node_counts)


# convert Node_count to integers using dictionary comprehension
user_node_counts = {k: int(v) for k, v in user_node_counts.items()}

out = pd.DataFrame(user_node_counts.items(), columns=["Username", "Node_Count"])
# sort in descending order
df = out.sort_values(by="Node_Count", ascending=False)


########################################################################################
#  create python dashboard

# Initialize the Dash app
app = dash.Dash(__name__)

# Create a simple GeoDataFrame with a bounding box
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

# %%
# build the app with pyinstaller
# pyinstaller --onefile --name leaderboard_linux --add-data "config.yaml:." build_app_script.py
# cd dist
# chmod +x leaderboard_linux
# ./leaderboard_linux
