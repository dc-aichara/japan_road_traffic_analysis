import asyncio

import logfire
import streamlit as st
from decouple import config

from .get_roads_from_gpx_file import (
    get_road_numbers,
    get_roads_and_prefecture_codes,
)
from .get_traffic_status import get_road_status_by_prefecture_code
from .plot_route import plot_route_with_closed_sections
from .postprocessing import filter_closed_roads, filter_traffic_status_by_road

LOGFIRE_TOKEN = config("LOGFIRE_TOKEN")
logfire.configure(token=LOGFIRE_TOKEN)


async def get_closed_roads(
    gpx_file_path: str, gpx_points_interval: int = 400
) -> tuple:
    """
    Retrieves and processes information about closed roads along a GPX route.

    This function extracts road and prefecture information from a GPX file,
    retrieves road numbers using the Overpass API, fetches traffic data from
    JARTIC, filters the data to identify closed roads, and plots the route with
    closed sections highlighted.

    Args:
        gpx_file_path (str): The file path to the GPX file.
        gpx_points_interval (int, optional): The interval at which to sample
            points from the extracted coordinates. Defaults to 400.

    Returns:
        tuple: A tuple containing:
            - all_affected_roads (pandas.DataFrame): A DataFrame containing
              processed closed roads' data.
            - fig (plotly.graph_objs._figure.Figure): A Plotly figure object
              with the route and closed sections plotted.
    """
    message_placeholder = st.empty()
    message_placeholder.info(
        "Getting roads information using OpenStreetMap Data!!", icon="ℹ️"
    )
    logfire.info("Getting roads information using OpenStreetMap Data!!")
    roads, prefs = await get_roads_and_prefecture_codes(
        gpx_file_path, gpx_points_interval
    )
    logfire.info(f"List of roads: {str(roads)}")
    logfire.info(f"List of prefectures: {str(prefs)}")
    message_placeholder.info(
        "Getting roads numbers using Overpass API!!", icon="ℹ️"
    )
    logfire.info("Getting roads numbers using Overpass API!!")
    road_numbers = get_road_numbers(road_names=roads)
    message_placeholder.info(
        "Getting traffic data from https://www.jartic.or.jp/!", icon="ℹ️"
    )
    logfire.info("Getting traffic data from https://www.jartic.or.jp/!")
    traffic_data = []
    for pref_code in prefs:
        pref_code = pref_code.replace("JP-", "")
        data = get_road_status_by_prefecture_code(pref_code)
        traffic_data.append(data)
    message_placeholder.info("Filtering restricted roads!!", icon="ℹ️")
    logfire.info("Filtering restricted roads!!")
    closed_roads = []
    for _, v in road_numbers.items():
        for data in traffic_data:
            filter_data = filter_traffic_status_by_road(v, data)
            closed_roads.extend(filter_data)
    all_affected_roads, complete_closed_roads = filter_closed_roads(
        closed_roads
    )
    closed_road_points = []
    if not complete_closed_roads.empty:
        closed_road_points = complete_closed_roads["coordinates"].tolist()
    message_placeholder.info(
        "Preparing Map of route and affect roads!", icon="ℹ️"
    )
    logfire.info("Preparing Map of route and affect roads!")
    fig = plot_route_with_closed_sections(gpx_file_path, closed_road_points)
    message_placeholder.empty()
    return all_affected_roads, fig


def run_gpx_route_pipeline(
    gpx_file_path: str, gpx_points_interval: int = 400
) -> tuple:
    """
    Run pipeline to get traffic restricted roads` information and a figure
    highlighting closed roads on the GPX route.

    Args:
        gpx_file_path (str): The file path to the GPX file.
        gpx_points_interval (int, optional): The interval at which to sample
            points from the extracted coordinates. Defaults to 400.

    Returns:
        tuple: A tuple containing:
            - all_affected_roads (pandas.DataFrame): A DataFrame containing
              processed closed roads' data.
            - fig (plotly.graph_objs._figure.Figure): A Plotly figure object
              with the route and closed sections plotted.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    closed_roads, fig = loop.run_until_complete(
        (
            get_closed_roads(
                gpx_file_path=gpx_file_path,
                gpx_points_interval=gpx_points_interval,
            )
        )
    )

    return closed_roads, fig
