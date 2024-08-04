import asyncio

import httpx
import pydash
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from httpx import AsyncHTTPTransport

from .utils import extract_coordinates_from_gpx, sample_points

transport = AsyncHTTPTransport(retries=3)

async_client = httpx.AsyncClient(
    timeout=httpx.Timeout(timeout=180, connect=30, read=30, write=30),
    transport=transport,
)
# Cache results for 24 hour
cache = Cache(Cache.MEMORY, serializer=JsonSerializer(), ttl=3600 * 24)


async def fetch_address(lat: float, lon: float) -> dict:
    """
    Fetches the address information for a given latitude and longitude using
    the Nominatim API.

    Args:
        lat (float): The latitude coordinate.
        lon (float): The longitude coordinate.

    Returns:
        dict: The address information in JSON format.
    """
    url = (
        f"https://nominatim.openstreetmap.org/reverse?format=json&lat"
        f"={lat}&lon={lon}&zoom=18&addressdetails=1"
    )
    response = await async_client.get(url)
    return response.json()


async def get_road_address(lat: float, lon: float) -> dict:
    """
    Retrieves the address information for a given latitude and longitude,
    utilizing a cache to store and retrieve results.

    Args:
        lat (float): The latitude coordinate.
        lon (float): The longitude coordinate.

    Returns:
        dict: The address information in JSON format.
    """
    cache_key = f"{lat},{lon}"
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result

    address_data = await fetch_address(lat, lon)
    address = address_data.get("address", {})
    await cache.set(cache_key, address)
    return address


async def get_multiple_road_addresses(coords: list) -> list:
    """
    Retrieves address information for multiple sets of coordinates.

    Args:
        coords (list of tuple): A list of tuples where each tuple contains
            latitude and longitude as floats.

    Returns:
        list of dict: A list of dictionaries containing address information
            for each set of coordinates.
    """
    tasks = [get_road_address(lat, lon) for lat, lon in coords]
    results = await asyncio.gather(*tasks)
    return results


async def get_roads_and_prefecture_codes(
    gpx_file_path: str, interval=400
) -> tuple:
    """
    Extracts coordinates from a GPX file, samples points at regular intervals,
    and retrieves road names/numbers and prefecture codes for each sampled
    point.

    Args:
        gpx_file_path (str): The file path to the GPX file.
        interval (int, optional): The interval at which to sample points from
            the extracted coordinates. Defaults to 400.

    Returns:
        tuple: A tuple containing two lists:
            - unique_road_numbers (list): A list of unique road names/numbers.
            - prefecture_codes (list): A list of unique prefecture codes.
    """
    # Extract coordinates from the GPX file
    coordinates = extract_coordinates_from_gpx(gpx_file_path)
    # Sample points at regular intervals
    sampled_points = sample_points(coordinates, interval=interval)

    # Get road name/number for each sampled point
    addresses = await get_multiple_road_addresses(sampled_points)

    # Remove duplicates and print the road numbers
    unique_road_numbers = list(set(pydash.map_(addresses, ["road"])))
    prefecture_codes = list(set(pydash.map_(addresses, ["ISO3166-2-lvl4"])))
    return unique_road_numbers, prefecture_codes


def get_osm_road_info(road_name: str) -> dict:
    """
    Retrieves OpenStreetMap (OSM) road information for a given road name.

    Args:
        road_name (str): The name of the road to query.

    Returns:
        dict: A dictionary containing the road name and its corresponding road
            number if available. If the road number is not available, the road
            name is returned as the value.

    Example:
        >>> get_osm_road_info("Chuo Dori")
        {'Chuo Dori': '123号'}
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    way["name"="{road_name}"];
    out tags;
    """
    client = httpx.Client(
        base_url=overpass_url,
        timeout=httpx.Timeout(timeout=180, connect=30, read=30, write=30),
    )
    response = client.get(overpass_url, params={"data": overpass_query})
    data = response.json()
    road_numbers = pydash.map_(data["elements"], "tags.ref")
    if road_numbers:
        road_info = {road_name: f"{road_numbers[0]}号"}
    else:
        road_info = {road_name: road_name}

    return road_info


def get_road_numbers(road_names: list) -> dict:
    """
    Retrieves road numbers for a list of road names using OpenStreetMap (OSM)
    data.

    Args:
        road_names (list): A list of road names as strings.

    Returns:
        dict: A dictionary where the keys are road names and the values are the
        corresponding road numbers. If a road number is not available, the road
        name is returned as the value.

    Example:
        >>> get_road_numbers(["Chuo Dori", "Yasukuni Dori"])
        {'Chuo Dori': '123号', 'Yasukuni Dori': 'Yasukuni Dori'}
    """
    road_numbers = {}
    for road in road_names:
        road_info = get_osm_road_info(road)
        road_numbers[road] = road_info[road]
    return road_numbers
