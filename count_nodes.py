# %%

import requests

# Define the Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Define the bounding box for Brooklyn, NY
brooklyn_bbox = "40.551042, -74.05663, 40.739446, -73.833365"

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
]

# Initialize a dictionary to store the count of nodes added by each user
user_node_counts = {}

for username in usernames:
    # Define the Overpass QL query for the current username
    query = f"""
    [out:json];
    (
      node(user:"{username}")({brooklyn_bbox});
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

pd.DataFrame(user_node_counts.items(), columns=["Username", "Node_Count"]).to_csv(
    "user_node_counts.csv", index=False
)

# %%
# %%
import geopandas as gpd
from shapely.geometry import box

# Define the bounding box for Brooklyn, NY
# Format: south latitude, west longitude, north latitude, east longitude
brooklyn_bbox = "40.551042, -74.05663, 40.739446, -73.833365"
south, west, north, east = map(float, brooklyn_bbox.split(", "))

# Create a Polygon from the bounding box using `box`
bbox_polygon = box(west, south, east, north)

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(geometry=[bbox_polygon], crs="EPSG:4326")
gdf.explore()
