# -*- coding: utf-8 -*-
"""
viewer_ranker.py
================
Ranks predefined aurora viewing locations based on:
- Current Kp index
- Proximity to the user's approximate location

The ranking combines distance and visibility likelihood to suggest the
best locations for aurora viewing.
"""

import math
from .kp_index import get_current_kp_index
from .location import get_user_location


# -------------------------------------------------------------------
# Predefined Aurora Viewing Locations
# -------------------------------------------------------------------
LOCATIONS = [
    {"name": "Tromsø, Norway",       "lat": 69.6496, "lon": 18.9560},
    {"name": "Fairbanks, Alaska",    "lat": 64.8378, "lon": -147.7164},
    {"name": "Abisko, Sweden",       "lat": 68.3518, "lon": 18.8294},
    {"name": "Yellowknife, Canada",  "lat": 62.4540, "lon": -114.3718},
    {"name": "Reykjavik, Iceland",   "lat": 64.1355, "lon": -21.8954},
    {"name": "Murmansk, Russia",     "lat": 68.9585, "lon": 33.0827},
    {"name": "Rovaniemi, Finland",   "lat": 66.5039, "lon": 25.7294},
]


# -------------------------------------------------------------------
# Utility: Haversine Distance Calculation
# -------------------------------------------------------------------

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points on the Earth.

    Uses the Haversine formula to return the distance in kilometers.

    Args:
        lat1 (float): Latitude of point 1.
        lon1 (float): Longitude of point 1.
        lat2 (float): Latitude of point 2.
        lon2 (float): Longitude of point 2.

    Returns:
        float: Distance in kilometers.
    """
    R = 6371  # Radius of Earth (km)

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# -------------------------------------------------------------------
# Rank Locations by Aurora Visibility & Distance
# -------------------------------------------------------------------

def get_top_locations():
    """
    Rank predefined aurora locations based on proximity and visibility.

    The ranking is determined by:
    - Distance from the user's location (closer = higher score).
    - Whether the location is likely within the current auroral visibility band
      based on the Kp index.

    Returns:
        list[dict]: List of ranked locations, each containing:
            - name (str)
            - latitude (float)
            - longitude (float)
            - distance_km (float)
            - visibility ("High" or "Low")
            - score (float)
    """
    user = get_user_location()
    kp = get_current_kp_index()

    if not user or kp is None:
        return []

    ranked = []
    for loc in LOCATIONS:
        # Calculate distance from user
        distance = haversine(user["latitude"], user["longitude"], loc["lat"], loc["lon"])

        # Estimate visibility band (very rough approximation)
        visibility_band = 67.0 - kp * 2
        is_visible = loc["lat"] >= visibility_band

        # Calculate score: distance penalty + visibility bonus
        score = (10 - distance / 1000) + (5 if is_visible else 0)

        ranked.append({
            "name": loc["name"],
            "latitude": loc["lat"],
            "longitude": loc["lon"],
            "distance_km": round(distance, 1),
            "visibility": "High" if is_visible else "Low",
            "score": round(score, 2)
        })

    # Sort by score in descending order
    return sorted(ranked, key=lambda x: x["score"], reverse=True)
