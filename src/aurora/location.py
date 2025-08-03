# -*- coding: utf-8 -*-
"""
location.py
===========
Handles IP-based geolocation to determine the user's approximate location.

Uses `ip-api.com` to retrieve the city, region, country, and coordinates.
"""

import requests


def get_user_location():
    """
    Retrieve user's approximate latitude, longitude, and region using IP-based geolocation.

    Makes a request to `http://ip-api.com/json` and returns the location details
    if successful.

    Returns:
        dict or None: Dictionary containing:
            {
                "city": str,
                "region": str,
                "country": str,
                "latitude": float,
                "longitude": float
            }
            Returns None if location could not be determined.
    """
    try:
        # API endpoint for free IP geolocation lookup
        GEO_API_URL = "http://ip-api.com/json"

        response = requests.get(GEO_API_URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Build location dictionary from API response
        return {
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon")
        }

    except requests.RequestException as e:
        # Network or HTTP error
        print(f"[ERROR] Network issue while retrieving user location: {e}")
        return None

    except ValueError as e:
        # JSON decoding error
        print(f"[ERROR] Invalid JSON from location API: {e}")
        return None

    except Exception as e:
        # Any other unexpected error
        print(f"[ERROR] Failed to retrieve user location: {e}")
        return None
