from datetime import datetime

import httpx

TIME = datetime.now().strftime("%Y%M%d%H%M%S")
URLS = {
    "current_generation": "https://www.jartic.or.jp/d/map/simple/generation-current.json",
    "roads_map_data": "https://www.jartic.or.jp/d/map/simple/12013/simplemap.json",
    "roads_digital_map": "https://www.jartic.or.jp/d/map/degitalmap.json",
    "emergency": f"https://www.jartic.or.jp/d/telop/emergency.json?_={TIME}",
    "disaster": f"https://www.jartic.or.jp/d/disaster/disaster.json?_={TIME}",
    "target2": f"https://www.jartic.or.jp/d/traffic_info/r2/target.json?_={TIME}",
    # {"target":"202404252247"} # previous one
    "target1": f"https://www.jartic.or.jp/d/traffic_info/r1/target.json?_={TIME}",
    # Latest one
    "normal": f"https://www.jartic.or.jp/d/telop/normal.json?_={TIME}",
}


def get_map_data(url: str) -> dict:
    """
    Fetches map data from the given URL.

    Args:
        url (str): The URL to fetch the map data from.

    Returns:
        dict: The map data retrieved from the URL if the request is successful.

    Raises:
        httpx.HTTPStatusError: If the request fails with a status code other
        than 200.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise httpx.HTTPStatusError(f"Request failed with status code: {response.status_code}", request=response.request, response=response)


def get_road_status_by_prefecture_code(pref_code: str = "21") -> dict:
    """
    Retrieves road status data for a given prefecture code.

    Args:
        pref_code (str): The prefecture code to fetch the road status for.
            Defaults to "21".

    Returns:
        dict: The road status data for the specified prefecture code.

    Raises:
        httpx.HTTPStatusError: If the request fails with a status code other
            than 200.
    """
    time = datetime.now().strftime("%Y%M%d%H%M%S")
    target_url = (
        f"https://www.jartic.or.jp/d/traffic_info/r1/target.json?_={time}"
    )
    target = get_map_data(target_url)["target"]
    data = get_map_data(
        f"https://www.jartic.or.jp/d/traffic_info/r1/{target}/d/301/"
        f"R{pref_code}.json"
    )

    return data
