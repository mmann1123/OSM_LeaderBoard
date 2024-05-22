# OSM_LeaderBoard
This is a Dash application that creates a leaderboard of OpenStreetMap contributors based on the number of nodes they have contributed for a given bounding box and time period.

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/mmann1123/OSM_LeaderBoard.git
    ```
2. Navigate to the project directory:
    ```bash
    cd yourrepository
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application is configured through a `config.yaml` file. Here's what each configuration option does:

- `bbox`: This is the bounding box for the area you're interested in. It should be a string with four comma-separated numbers representing the latitude and longitude of the southwest and northeast corners of the bounding box, respectively. For example: `"40.551042, -74.05663, 40.739446, -73.833365"`.

> Note: You can use [http://bboxfinder.com/](http://bboxfinder.com/)  
switch "coordinate format" to "Lat / Lng"

- `usernames`: This is a list of usernames that the application will use to do XYZ. Each username should be a string. For example:
    ```yaml
    usernames:
      - mmann1123
      - ...
      - ...

    ```

- `newer_than_date`: This is an optional configuration option. If provided, the application will only consider data newer than this date. The date should be a string in the format `"YYYY-MM-DD"`. For example: `"2024-05-01"`.

An example `config.yaml` file might look like this:

```yaml
bbox: "40.551042, -74.05663, 40.739446, -73.833365"
usernames:
  - mmann1123
  - haycam
  - I-Izzo
  - isamah
newer_than_date: "2010-12-01"   
```


## Running the Application

To run the application, use the following command:

```bash
cd OSM_LeaderBoard
python dash_app.py
```

In the browser window select or drag your `config.yaml` file to the upload box. The leaderboard will be displayed in the browser window once the api calls are complete.
