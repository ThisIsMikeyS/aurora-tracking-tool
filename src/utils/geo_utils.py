# -*- coding: utf-8 -*-
"""
Geolocation utility functions for the Aurora Tracker.
"""

from math import radians, cos, sin, asin, sqrt


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance (km) between two lat/lon points using the Haversine formula.

    Args:
        lat1 (float): Latitude of first point
        lon1 (float): Longitude of first point
        lat2 (float): Latitude of second point
        lon2 (float): Longitude of second point

    Returns:
        float: Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    
    earth_radius_km = 6371
    return c * earth_radius_km


def is_northern_hemisphere(lat):
    """
    Determine if a coordinate is in the Northern Hemisphere.

    Args:
        lat (float): Latitude

    Returns:
        bool: True if north of equator, else False
    """
    return lat >= 0
