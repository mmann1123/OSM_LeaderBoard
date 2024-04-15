# OSM_LeaderBoard

## Install Python and Dependencies

### First Time Setup
1) Install Anaconda Python 3.7 from [https://www.anaconda.com/distribution/](https://www.anaconda.com/distribution/)

2) OSX: Open Terminal
   Windows: Open Anaconda Prompt

3) Create a new environment:
    
    ``` bash
    conda create -n osm_leaderboard python=3.7 dash geopandas -y
    ```
### Every Time To Run   

1) Edit `count_nodes.py` in a text editor:

A) Update the user names list:

    ``` python
    # List of usernames to query
    usernames = [
        "username",
        "anothername",
    ]
    ```

B) Change the bounding box for your query:

    ``` python
    bbox = "40.551042, -74.05663, 40.739446, -73.833365"
    ```

    Format: "min_latitude, min_longitude, max_latitude, max_longitude"
    You can use [http://bboxfinder.com/](http://bboxfinder.com/)  
    **IMPORTANT:** switch "coordinate format" to "Lat / Lng"

2) OSX: Open Terminal
   Windows: Open Anaconda Prompt

3) Activate the environment:

    ``` bash
    conda activate osm_leaderboard
    ```
4) Change to the directory where you cloned the repository:

    ``` bash
    cd path/to/OSM_LeaderBoard
    ```
5) Run the leaderboard:

    ``` bash
    python count_nodes.py
    ```
6) Open a web browser and navigate to  [http://127.0.0.1:8050/](http://127.0.0.1:8050/) 

