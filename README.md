# OSM_LeaderBoard

To run the leader board locally - in `count_nodes.py`:

1) Update the user names list:

``` python
# List of usernames to query
usernames = [
    "username",
    "anothername",
]
```

2) Change the bounding box for your query:

``` python
bbox = "40.551042, -74.05663, 40.739446, -73.833365"
```

Format: "min_latitude, min_longitude, max_latitude, max_longitude"
You can use [http://bboxfinder.com/](http://bboxfinder.com/)  
**IMPORTANT:** switch "coordinate format" to "Lat / Lng"

3) Start a local server connect and to [http://0.0.0.0:8000/](http://0.0.0.0:8000/) in a web browser by running:

within `count_nodes.py`:

``` python
!python -m http.server
```

or from the terminal

``` bash
cd to/your/folder/holding/script.js
python -m http.server
```
