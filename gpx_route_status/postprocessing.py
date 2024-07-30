import re
from unicodedata import normalize

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


def get_closed_road_geometry(closed_roads: dict) -> tuple:
    """
    Get geometry of closed/restricted roads.

    Args:
        closed_roads (dict): Traffic data of restricted/closed roads.

    Returns:
        tuple: Tuple of list of latitudes and longitudes.

    """
    types = pydash.map_(closed_roads, "geometry.type")
    coords = pydash.map_(closed_roads, "geometry.coordinates")
    lat_coordinates = []
    lon_coordinates = []
    for geo_type, coord in zip(types, coords):
        lons, lats = [], []
        if geo_type == "MultiLineString":
            lons, lats = zip(*coord[0])
        elif geo_type == "LineString":
            lons, lats = zip(*coord)
        lat_coordinates.append(lats)
        lon_coordinates.append(lons)
    return lat_coordinates, lon_coordinates


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
            containing only rows where the restriction description indicates a
            complete road closure.
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
    if not df.empty:
        df = df[df["restriction_description"].notnull()]
        complete_closed_roads = df[df["restriction_description"] == "通行止"]
        return df, complete_closed_roads
    return pd.DataFrame(), pd.DataFrame()
