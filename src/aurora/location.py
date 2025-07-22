# -*- coding: utf-8 -*-
"""
Handles IP-based geolocation to determine the user's approximate location.
"""

import requests

def get_user_location():
    """
    Returns user's current latitude and longitude using IP geolocation.
    
    Returns:
        dict: Dictionary containing 'city', 'region', 'country', 'latitude', and 'longitude'.
    """
    try:
        response = requests.get("http://ip-api.com/json", timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon")
        }
    except Exception as e:
        print(f"[ERROR] Failed to retrieve user location: {e}")
        return None
