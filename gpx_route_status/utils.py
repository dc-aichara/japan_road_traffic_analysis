from __future__ import annotations

import gpxpy
import httpx
import logfire
import streamlit as st
from decouple import config
from geopy.distance import geodesic

LOGFIRE_TOKEN = config("LOGFIRE_TOKEN")
logfire.configure(token=LOGFIRE_TOKEN)


# Function to read GPX file and extract coordinates
def extract_coordinates_from_gpx(
    file_path: str | st.runtime.uploaded_file_manager.UploadedFile,
) -> list:
    """
    Extracts coordinates from a GPX file.

    This function parses a GPX file and extracts the latitude and longitude
    coordinates from it. The input can be either a file path or a Streamlit
    UploadedFile object.

    Args:
        file_path (str or st.runtime.uploaded_file_manager.UploadedFile):
            The path to the GPX file or a Streamlit UploadedFile object.

    Returns:
        list: A list of tuples where each tuple contains the latitude
        and longitude of a point in the GPX file.
    """
    if isinstance(file_path, st.runtime.uploaded_file_manager.UploadedFile):
        gpx = gpxpy.parse(file_path.getvalue())
    else:
        with open(file_path, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)

    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((point.latitude, point.longitude))
    logfire.info(f"Number of points is {len(coordinates)}.")
    return coordinates


# Function to sample points at regular intervals
def sample_points(coordinates: list, interval=400) -> list:
    """
    Samples points from a list of coordinates at a specified interval.

    Args:
        coordinates (list): A list of coordinate points.
        interval (int, optional): The interval at which to sample points.
            Defaults to 400.

    Returns:
        list: A list of sampled coordinate points.
    """
    return coordinates[::interval]


def get_shortest_path_osrm(
    lat1: float, lon1: float, lat2: float, lon2: float, return_geometry=False
) -> tuple | float:
    """
    Retrieves the shortest path between two geographical points using the
    OSRM API.

    Args:
        lat1 (float): Latitude of the starting point.
        lon1 (float): Longitude of the starting point.
        lat2 (float): Latitude of the destination point.
        lon2 (float): Longitude of the destination point.
        return_geometry (bool, optional): If True, returns the route
            geometry in GeoJSON format. Defaults to False.

    Returns:
        tuple | float: If `return_geometry` is True, returns a tuple
            containing the distance in kilometers and the route geometry in
            GeoJSON format.
            If `return_geometry` is False, returns only the distance in
            kilometers.
    """
    client = httpx.Client(base_url="https://router.project-osrm.org")
    # Format the URL for the route request
    url = (
        f"/route/v1/bike/{lon1},{lat1};{lon2},{lat2}?overview=full&"
        f"geometries=geojson"
    )

    # Send the request to OSRM
    response = client.get(url)
    data = response.json()

    # Extract route information
    route = data["routes"][0]
    distance = route["distance"] / 1000  # in kilometers
    geometry = route["geometry"]  # GeoJSON format
    if return_geometry:
        return distance, geometry
    return distance


def calculate_geo_distance(points: list) -> float:
    """
    Calculate geo distance between 2 points.

    Args:
        points (list): A list of start and end points of
            restricted road.

    Returns:
        float: Distance between two points.

    """
    if points and len(points) == 2:
        distance = geodesic(points[0][::-1], points[1][::-1]).km
        return round(distance, 3)
    return 0
