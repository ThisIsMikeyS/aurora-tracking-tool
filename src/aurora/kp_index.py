# -*- coding: utf-8 -*-
"""
kp_index.py
===========
Fetches the current Kp index from the GFZ Kp Index service and
provides a rough estimate of aurora visibility zones based on Kp values.

Functions:
    - get_current_kp_index(): Retrieve the latest Kp index value
    - get_visibility_zone(kp): Map Kp value to approximate visible latitude range
"""

import requests
from datetime import datetime, timezone
from .libraries.get_kp_index import getKpindex


# =========================================
# FETCH CURRENT Kp INDEX
# =========================================
def get_current_kp_index():
    """
    Retrieve the most recent available Kp index from GFZ service.

    Returns:
        float: Latest Kp index value if available.
        str: Message if data is unavailable or an error occurs.
    """
    try:
        now = datetime.now(timezone.utc)

        # Build time range: from midnight UTC today to now
        start_time = now.strftime("%Y-%m-%dT00:00:00Z")
        end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Request Kp index values
        times, kp_values, statuses = getKpindex(
            start_time, end_time, index="Kp", status="all"
        )

        # Handle empty response
        if not times or not kp_values:
            return "Unavailable: No Kp index data returned."

        # Find most recent Kp value at or before current time
        latest_index = None
        for t, val in zip(times, kp_values):
            t_obj = datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if t_obj <= now:
                latest_index = val
            else:
                break

        return (
            float(latest_index)
            if latest_index is not None
            else "Unavailable: No valid value found."
        )

    except Exception as e:
        print(f"[ERROR] Failed to get Kp index: {e}")
        return f"Unavailable: {e}"


# =========================================
# DETERMINE VISIBILITY ZONE
# =========================================
def get_visibility_zone(kp):
    """
    Estimate approximate geographic latitude range where aurora is visible,
    based on Kp index level.

    Args:
        kp (float|int|None): Kp index value.

    Returns:
        str: Description of visibility latitude band.
    """
    if kp is None:
        return "Unknown"

    visibility_map = {
        0: "Very High Latitudes (e.g. North Pole)",
        1: "Arctic Circle (~66\u00B0)",
        2: "Iceland, Troms\u00F8",
        3: "Northern Scandinavia",
        4: "Southern Norway, Scotland",
        5: "UK, Germany, Canada border",
        6: "Central Europe, North USA",
        7: "France, New York",
        8: "Spain, California",
        9: "Mexico, North Africa"
    }

    return visibility_map.get(int(kp), "Unavailable")
