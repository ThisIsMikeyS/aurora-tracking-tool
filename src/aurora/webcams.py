# -*- coding: utf-8 -*-
"""
webcams.py
Returns a curated list of live aurora webcam URLs.
- Dependency: astral
"""

from datetime import datetime, timezone
from astral.sun import sun
from astral import LocationInfo
from .kp_index import get_current_kp_index

WEBCAM_LIST = [
        {"location": "Tromsø", "country": "Norway", "lat": 69.6496, "lon": 18.9560, "url": "https://weather.cs.uit.no/"},
        {"location": "Abisko", "country": "Sweden", "lat": 68.3518, "lon": 18.8294, "url": "https://lightsoverlapland.com/webcam/"},
        {"location": "Kilpisjärvi", "country": "Finland", "lat": 69.0472, "lon": 20.7972, "url": "https://www.youtube.com/watch?v=ccTVAhJU5lg"},
        {"location": "Fairbanks, AK", "country": "United States", "lat": 64.8378, "lon": -147.7164, "url": "https://www.youtube.com/watch?v=O52zDyxg5QI"},
        {"location": "Yellowknife, NT", "country": "Canada", "lat": 62.4540, "lon": -114.3718, "url": "https://auroramax.com/live"},
        {"location": "Kingston, TAS", "country": "Australia", "lat": -42.9728, "lon": 147.3050, "url": "https://www.allskycam.com/u.php?u=539"},
        {"location": "Casey Station", "country": "Antarctica", "lat": -66.2833, "lon": 110.5333, "url": "https://www.antarctica.gov.au/antarctic-operations/webcams/casey/"},
        {"location": "Shetland Islands", "country": "Scotland", "lat": 59.8541, "lon": -1.2752, "url": "https://www.shetlandwebcams.com/cliff-cam-3/"},
    ]

def get_live_webcams():
    """Returns a list of popular aurora webcam streams."""
    return WEBCAM_LIST.copy()


def get_live_webcams_location_sorted():
    """
    Returns the list of webcams sorted alphabetically by location name.
    """
    return sorted(WEBCAM_LIST, key=lambda cam: cam["location"])


def get_live_webcams_country_sorted():
    """
    Returns the list of webcams sorted first by country, then by location within each country.
    """
    return sorted(WEBCAM_LIST, key=lambda cam: (cam["country"], cam["location"]))


def is_dark(lat, lon):
    """Returns True if it is currently dark at the location (sun below horizon)."""
    try:
        location = LocationInfo(latitude=lat, longitude=lon)
        s = sun(location.observer, date=datetime.now(timezone.utc), tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return now < s['dawn'] or now > s['dusk']
    except Exception as e:
        print(f"[WARN] Astral failed for lat={lat}, lon={lon}: {e}")
        return False  # Assume not dark if uncertain


def get_live_webcams_best_sorted():
    """
    Returns a list of aurora webcams, sorted by:
    1. Whether it is currently dark at the webcam location
    2. Proximity to the visible auroral boundary based on current Kp
    """
    webcams = WEBCAM_LIST.copy()

    try:
        kp = get_current_kp_index()
        visible_lat = 90 - (kp * 5)  # Estimate aurora boundary

        for cam in webcams:
            cam_lat = abs(cam["lat"])
            diff = cam_lat - visible_lat
            cam["score"] = diff if diff >= 0 else float("inf")  # Less = better
            cam["is_dark"] = is_dark(cam["lat"], cam["lon"])

        # Sort by: 1) darkness (True first), 2) aurora visibility score (lower = better)
        webcams.sort(key=lambda cam: (not cam["is_dark"], cam["score"]))

    except Exception as e:
        print(f"[ERROR] Webcam sorting failed: {e}")

    return webcams