# -*- coding: utf-8 -*-
"""
Ranks global locations based on current aurora visibility and Kp index.
"""

from .kp_index import get_current_kp_index
from .location import get_user_location
import math

# Predefined locations with their coordinates and names
LOCATIONS = [
    {"name": "Tromsø, Norway", "lat": 69.6496, "lon": 18.9560},
    {"name": "Fairbanks, Alaska", "lat": 64.8378, "lon": -147.7164},
    {"name": "Abisko, Sweden", "lat": 68.3518, "lon": 18.8294},
    {"name": "Yellowknife, Canada", "lat": 62.4540, "lon": -114.3718},
    {"name": "Reykjavik, Iceland", "lat": 64.1355, "lon": -21.8954},
    {"name": "Murmansk, Russia", "lat": 68.9585, "lon": 33.0827},
    {"name": "Rovaniemi, Finland", "lat": 66.5039, "lon": 25.7294}
]

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates great-circle distance between two coordinates using the Haversine formula.
    
    Returns:
        float: Distance in kilometers.
    """
    R = 6371  # Radius of Earth in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_top_locations():
    """
    Ranks predefined aurora viewing locations based on proximity to user and Kp index.
    
    Returns:
        list: Sorted list of locations with visibility scores and distance.
    """
    user = get_user_location()
    kp = get_current_kp_index()

    if not user or kp is None:
        return []

    ranked = []
    for loc in LOCATIONS:
        distance = haversine(user["latitude"], user["longitude"], loc["lat"], loc["lon"])
        visibility_band = 67.0 - kp * 2  # Very rough estimate
        is_visible = loc["lat"] >= visibility_band
        score = (10 - distance / 1000) + (5 if is_visible else 0)

        ranked.append({
            "name": loc["name"],
            "latitude": loc["lat"],
            "longitude": loc["lon"],
            "distance_km": round(distance, 1),
            "visibility": "High" if is_visible else "Low",
            "score": round(score, 2)
        })

    return sorted(ranked, key=lambda x: x["score"], reverse=True)
