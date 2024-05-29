# OSM_LeaderBoard
This is a Dash application that creates a leaderboard of OpenStreetMap contributors based on the number of nodes they have contributed for a given bounding box and time period.

## Executables

Executable files for windows and linux are currently available for download:

[Download Executables](https://www.dropbox.com/scl/fo/07gchwqkr5kl2c4julr52/AGoB9nqB9aCRBVJnMg5V4CA?rlkey=x23yu6k6utvb98izvjjyexcub&st=mdh91bij&dl=0)

Double-click to execute the leaderboard. 

## Python Installation & Execution

Install directly from GitHub using a terminal window:

```bash
pip install git+https://github.com/mmann1123/OSM_LeaderBoard.git
```

Once installed simply type:

```bash
leaderboard
```

## Configuration

The application is configured through a file `config.yaml` file. Here's what each configuration option does:

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


# Demo

![OSM Leaderboard](https://github.com/mmann1123/OSM_LeaderBoard/blob/main/video/leaderboard3.gif?raw=true)

# Credits
This app brought to you by [![GWU Geography](https://github.com/mmann1123/OSM_LeaderBoard/blob/mmann1123-credits/video/gw.png?raw=true)](https://geography.columbian.gwu.edu/)  and  <a href="https://pygis.io"> <img src="https://github.com/mmann1123/OSM_LeaderBoard/blob/mmann1123-credits/video/pygis.png?raw=true" alt="pygis.io" height="70"></a>


