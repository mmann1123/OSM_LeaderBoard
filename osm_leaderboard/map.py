import folium
from shapely.geometry import mapping


def explore_shapely_object(geom, color="blue", popup_attr=None, tooltip_attr=None):
    """
    Create an interactive map for any shapely object (Point, LineString, Polygon)
    that dynamically adjusts the zoom level to fit the geometry bounds.

    Parameters:
        geom (shapely.geometry): The shapely geometry to plot.
        color (str): Color for the geometry. Default is 'blue'.
        popup_attr (str): A string to show in a popup on click.
        tooltip_attr (str): A string to show in a tooltip on hover.

    Returns:
        folium.Map: A folium Map object with the given geometry displayed.
    """
    # Create a map centered around the geometry's centroid
    centroid = geom.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=13)

    # Generate geojson data from the shapely geometry
    geojson_data = mapping(geom)

    # Create a GeoJson object and add it to the map
    gj = folium.GeoJson(
        geojson_data, style_function=lambda x: {"color": color, "weight": 2}
    )
    m.add_child(gj)

    # Fit the map's bounds to the geometry's bounds
    bounds = geom.bounds
    m.fit_bounds([(bounds[1], bounds[0]), (bounds[3], bounds[2])])

    # Add popup and tooltip if specified
    if popup_attr:
        gj.add_child(folium.Popup(popup_attr))
    if tooltip_attr:
        gj.add_child(folium.Tooltip(tooltip_attr))

    return m
