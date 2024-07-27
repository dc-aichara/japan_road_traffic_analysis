import numpy as np
import plotly.graph_objects as go
from decouple import config
from geopy.distance import geodesic

from .utils import extract_coordinates_from_gpx

MAPBOX_SECRET = config("MAPBOX_SECRET")
MAPBOX_STYLE = config("MAPBOX_STYLE")


def plot_route_with_closed_sections(
    gpx_file_path: str, closed_sections: list
) -> go.Figure:
    """
    Plots a GPX route with closed sections highlighted.

    This function reads a GPX file to extract the route coordinates and plots
    the route on a map using Plotly. It also highlights the closed sections of
    the route in red.

    Args:
        gpx_file_path (str): The file path to the GPX file.
        closed_sections (list): A list of tuples, where each tuple contains the
            start and end coordinates (latitude, longitude) of a closed section.

    Returns:
        go.Figure: A Plotly figure object with the route and closed sections
            plotted.
    """
    coords = extract_coordinates_from_gpx(gpx_file_path)
    latitudes, longitudes = zip(*coords)

    # Create the main route plot
    fig = go.Figure(
        go.Scattermapbox(
            lat=latitudes,
            lon=longitudes,
            mode="lines",
            line=dict(color="blue", width=3),
            name="Route",
        )
    )

    # Highlight closed sections
    for start, end in closed_sections:
        closed_latitudes = []
        closed_longitudes = []
        start_found = False
        end_found = False
        for lat, lon in coords:
            if not start_found:
                if (
                    geodesic(start[::-1], (lat, lon)).meters < 50
                ):  # Correct order: (latitude, longitude)
                    start_found = True
                if geodesic(end[::-1], (lat, lon)).meters < 50:
                    start_found = True
                    end = start
            if start_found:
                closed_latitudes.append(lat)
                closed_longitudes.append(lon)
                if (
                    geodesic(end[::-1], (lat, lon)).meters < 50
                ):  # Correct order: (latitude, longitude)
                    end_found = True
                    break
        # Only add closed road data is start and end both found.
        if start_found is True and end_found is True:
            fig.add_trace(
                go.Scattermapbox(
                    lat=closed_latitudes,
                    lon=closed_longitudes,
                    mode="lines",
                    line=dict(color="red", width=5),
                    name="Closed Road",
                )
            )

    fig.update_layout(
        mapbox_style=MAPBOX_STYLE,
        mapbox_zoom=10,
        mapbox_center={"lat": np.mean(latitudes), "lon": np.mean(longitudes)},
        height=800,
        # title={
        #     'text': "GPX Route with Closed Sections Highlighted",
        #     'y': 0.9,
        #     'x': 0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top',
        #     'font': {
        #         'color': 'blue',
        #         'size': 24
        #     }
        # },
        legend={
            "x": 0.01,
            "y": 0.99,
            "traceorder": "normal",
            "bgcolor": "rgba(255, 255, 255, 0.5)",
            "bordercolor": "Black",
            "borderwidth": 1,
            "font": {
                "family": "Arial",
                "size": 14,
                "color": "green",  # Change legend font color here
            },
        },
        mapbox_accesstoken=MAPBOX_SECRET,
    )

    return fig
