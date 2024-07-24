import gpxpy
import streamlit as st


# Function to read GPX file and extract coordinates
def extract_coordinates_from_gpx(file_path: str | st.runtime.uploaded_file_manager.UploadedFile) -> list:
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
