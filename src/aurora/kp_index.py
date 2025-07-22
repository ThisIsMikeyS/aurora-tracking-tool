# -*- coding: utf-8 -*-
"""
Fetches the current Kp index and assesses aurora visibility by latitude.
"""

import requests
from datetime import datetime, timedelta, timezone
from .libraries.get_kp_index import getKpindex

# def get_current_kp_index():
#     """
#     Fetches the current KP index from NOAA SWPC API.
#     Returns the most recent KP index as a float or None if unavailable.
#     """
#     try:
#         response = requests.get("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json", timeout=10)
#         response.raise_for_status()
#         data = response.json()

#         print("[DEBUG] KP Index API response:", data)  # Optional debug line

#         if isinstance(data, list) and data:
#             latest = data[-1]
#             kp = latest.get("kp_index") or latest.get("Kp")  # Try both common key names
#             if kp is None:
#                 raise ValueError("KP index not found in latest response item.")
#             return float(kp)

#         raise ValueError("Unexpected KP index response format.")

#     except Exception as e:
#         print(f"[ERROR] Failed to get Kp index: {e}")
#         return None


def get_current_kp_index():
    """
    Retrieve the most recent available Kp index using the GFZ Kp index service.

    Returns:
        float or str: Most recent Kp index, or a string explaining an error.
    """
    try:
        # Define time window: today from 00:00Z to now
        now = datetime.now(timezone.utc)
        start_time = now.strftime("%Y-%m-%dT00:00:00Z")
        end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        times, kp_values, statuses = getKpindex(start_time, end_time, index="Kp", status="all")

        if not times or not kp_values:
            return "Unavailable: No Kp index data returned."

        # Find the latest available value before now
        latest_index = None
        for t, val in zip(times, kp_values):
            t_obj = datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if t_obj <= now:
                latest_index = val
            else:
                break

        return float(latest_index) if latest_index is not None else "Unavailable: No valid value found."

    except Exception as e:
        print(f"[ERROR] Failed to get Kp index: {e}")
        return f"Unavailable: {e}"


def get_visibility_zone(kp):
    """
    Estimate aurora visibility zone by Kp value.
    Kp values roughly correspond to geographic latitude bands.
    """
    if kp is None:
        return "Unknown"

    visibility = {
        0: "Very High Latitudes (e.g. North Pole)",
        1: "Arctic Circle (approx. 66 degrees)",
        2: "Iceland, Tromso",
        3: "Northern Scandinavia",
        4: "Southern Norway, Scotland",
        5: "UK, Germany, Canada border",
        6: "Central Europe/North USA",
        7: "France, New York",
        8: "Spain, California",
        9: "Mexico, North Africa"
    }
    return visibility.get(int(kp), "Unavailable")
