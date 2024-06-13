# OSM_LeaderBoard
This is a Dash application that creates a leaderboard of OpenStreetMap contributors based on the number of nodes they have contributed for a given bounding box and time period.

## Executables

Executable files for `OSx`, `Windows` and `linux` are available for download:

<a href="https://www.dropbox.com/scl/fo/07gchwqkr5kl2c4julr52/AGoB9nqB9aCRBVJnMg5V4CA?rlkey=x23yu6k6utvb98izvjjyexcub&st=mdh91bij&dl=0"> <img src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/download.png?raw=true" alt="exe" height="45"></a>

**Note:** Make sure to download and update `example_config.yaml`  

## Running the Application
1) Update the contents of `config.yaml` file with the desired bounding box, usernames, and optional date.

2) Run the application using one of the following methods: <br> 

    A) **From the downloaded executable file**: Double click on the downloaded executable file to run the application. 

    B) **From Python**: From the terminal window, navigate to the directory where the `dash_app.py` file is located. To download and run the application, use the following command:

      ```bash
      pip install git+https://github.com/mmann1123/OSM_LeaderBoard.git
      ```

      Once installed simply type:

      ```bash
      leaderboard
      ```

  3) Then in the browser window select or drag your `config.yaml` file to the upload box. The leaderboard will be displayed in the browser window once the api calls are complete. 

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




# Demo

![OSM Leaderboard](https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/leaderboard3.gif?raw=true)

# Credits
[![GWU Geography](https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/gw.png?raw=true)](https://geography.columbian.gwu.edu/)    <a href="https://pygis.io"> <img src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/pygis.png?raw=true" alt="pygis.io" height="70"></a>  <a href="https://www.youthmappers.org/"> <img src="https://github.com/mmann1123/OSM_LeaderBoard/blob/main/static/youthmappers.webp?raw=true" alt="YouthMappers" height="70"></a>
<br><br><br>
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11387666.svg)](https://doi.org/10.5281/zenodo.11387666)

