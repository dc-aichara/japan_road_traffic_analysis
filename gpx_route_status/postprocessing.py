import re
from unicodedata import normalize
from geopy.distance import geodesic

import pandas as pd
import pydash


def clean_road_names(road_name: str) -> str:
    """
    Clean and normalize the road name.

    This function normalizes the input road name using Unicode Normalization
    Form KC (NFKC) and extracts the road number if it matches the pattern of
    digits followed by the character '号'. If no such pattern is found, the
    original road name is returned.

    Args:
        road_name (str): The name of the road to be cleaned.

    Returns:
        str: The cleaned road name, which is either the extracted road number or the original road name.
    """
    road_name = normalize("NFKC", road_name)
    match = re.search("\\d+号", road_name)
    if match:
        return match.group()
    return road_name


def calculate_closed_road_distance(closed_road_points: list) -> float:
    """
    Calculate distance of closed/restricted roads.

    Args:
        closed_road_points (list): A list of start and end points of
            restricted road.

    Returns:
        float: Length of restricted road in kilometers.

    """
    if closed_road_points and len(closed_road_points) == 2:
        distance = geodesic(closed_road_points[0][::-1], closed_road_points[1][::-1]).km
        return round(distance, 3)
    return 0


def filter_traffic_status_by_road(road_number: str, traffic_data: dict) -> list:
    """
    Filter traffic status data by a specific road number.

    Args:
        road_number (str): The road number to filter the traffic data.
        traffic_data (dict): The traffic data containing road features.

    Returns:
        list: Filtered traffic data for the specified road number.
    """
    road_names_traffic = pydash.map_(traffic_data["features"], "properties.r")
    road_names_traffic = [clean_road_names(r) for r in road_names_traffic]
    matched_road_idx = [
        i for i, v in enumerate(road_names_traffic) if road_number == v
    ]
    road_traffic_data = [traffic_data["features"][i] for i in matched_road_idx]

    return road_traffic_data


def filter_closed_roads(closed_roads: list):
    """
    Filters and processes a list of closed roads data.

    Args:
        closed_roads (list): A list of dictionaries containing closed roads
            data.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - The first DataFrame contains the processed closed roads data with
             unnecessary columns removed and remaining columns renamed.
            - The second DataFrame is a subset of the first DataFrame,
            containing only rows where the restriction description indicates a complete road closure.
    """
    df = pd.DataFrame(pydash.map_(closed_roads, "properties"))
    columns = df.columns
    useless_cols = ["cs", "l", "lo", "pd", "rn", "j"]
    remove_cols = [col for col in useless_cols if col in columns]
    df.drop(columns=remove_cols, axis=1, inplace=True)
    column_mapping = {
        "c": "work_type",
        "d": "direction",
        "i": "location_description",
        "p": "coordinates",
        "r": "route_name",
        # 'cs': 'cs',
        # 'l': 'lane_type',
        # 'lo': 'lane_occupancy',
        # 'pd': 'road_type',
        "rd": "restriction_description",
        # 'rn': 'restriction_id',
        # 'j': 'additional_info'
    }
    df.rename(columns=column_mapping, inplace=True)
    df = df[df["restriction_description"].notnull()]
    df["distance_km"] = df["coordinates"].apply(calculate_closed_road_distance)
    complete_closed_roads = df[df["restriction_description"] == "通行止"]
    return df, complete_closed_roads
