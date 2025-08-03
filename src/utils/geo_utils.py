# -*- coding: utf-8 -*-
"""
geo_utils.py
============
Geolocation utility functions for the Aurora Tracker.

Functions:
- haversine_distance: Calculate the great-circle distance between two coordinates.
- is_northern_hemisphere: Check if a given latitude is in the Northern Hemisphere.
"""

from math import radians, cos, sin, asin, sqrt


# -------------------------------------------------------------------
# Distance Calculation
# -------------------------------------------------------------------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth 
    using the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point (degrees).
        lon1 (float): Longitude of the first point (degrees).
        lat2 (float): Latitude of the second point (degrees).
        lon2 (float): Longitude of the second point (degrees).

    Returns:
        float: Distance between the points in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    earth_radius_km = 6371  # Mean Earth radius in kilometers
    return c * earth_radius_km


# -------------------------------------------------------------------
# Hemisphere Check
# -------------------------------------------------------------------

def is_northern_hemisphere(lat: float) -> bool:
    """
    Determine if the given latitude is in the Northern Hemisphere.

    Args:
        lat (float): Latitude (degrees).

    Returns:
        bool: True if north of the equator, False otherwise.
    """
    return lat >= 0
