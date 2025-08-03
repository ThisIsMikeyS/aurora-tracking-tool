# -*- coding: utf-8 -*-
"""
webcams.py
===========
Provides curated live aurora webcam URLs and sorting utilities.

Features:
- Darkness detection at each webcam location using Astral.
- Sorting webcams by likely aurora visibility (Kp index + local darkness).
- Alphabetical sorting by location and by country.

Dependencies:
- astral (for sunrise/sunset calculations)
- pytz (timezone handling)
"""

import pytz
from pytz import timezone as pytz_timezone
from datetime import datetime, timezone
from astral.sun import sun
from astral import LocationInfo
from .kp_index import get_current_kp_index
from config import WEBCAM_LIST, CAMERA_TIMEZONES


# -------------------------------------------------------------------
# Darkness Detection
# -------------------------------------------------------------------

def is_dark(lat: float, lon: float, location_name: str = None) -> bool:
    """
    Determine whether it is currently dark at the given location.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        location_name (str, optional): Name of the location (used to lookup timezone).

    Returns:
        bool: True if the sun is below the horizon (dark), False if above (light).
    """
    try:
        # Determine timezone (fallback to UTC if not in mapping)
        tz = pytz_timezone(CAMERA_TIMEZONES.get(location_name, "UTC"))

        now_local = datetime.now(tz)

        # Astral location for sunrise/sunset calculation
        location = LocationInfo(latitude=lat, longitude=lon)
        sun_times = sun(location.observer, date=now_local.date(), tzinfo=tz)

        # Dark if current time is before dawn or after dusk
        return now_local < sun_times['dawn'] or now_local > sun_times['dusk']

    except ValueError as e:
        # Handle polar day/night edge cases from Astral
        msg = str(e).lower()
        if "degrees below" in msg:
            print(f"[INFO] Sun never sets in {location_name} — assuming bright.")
            return False
        elif "degrees above" in msg:
            print(f"[INFO] Sun never rises in {location_name} — assuming dark.")
            return True
        else:
            print(f"[WARN] Astral raised ValueError for {location_name}: {e}")
            return False

    except Exception as e:
        print(f"[WARN] Astral calculation failed for {location_name}: {e}")
        return False


# -------------------------------------------------------------------
# Sorting by Visibility Probability
# -------------------------------------------------------------------

def get_live_webcams_best_sorted():
    """
    Sort webcams by likelihood of aurora visibility.

    Sorting is based on:
        - Kp index (geomagnetic activity).
        - Darkness at the location (aurora visible only in dark conditions).
        - Proximity to the auroral oval (estimated from latitude & Kp).

    Returns:
        list[dict]: List of webcam dictionaries sorted by aurora visibility score.
    """
    webcams = WEBCAM_LIST.copy()
    try:
        kp = get_current_kp_index()
        visible_lat = 90 - (kp * 5)  # Rough auroral boundary approximation

        for cam in webcams:
            cam_lat = abs(cam["lat"])
            distance_from_boundary = cam_lat - visible_lat

            # Darkness bonus: negative value improves score (more likely visible)
            dark_bonus = -10 if is_dark(cam["lat"], cam["lon"], cam["location"]) else 10

            # Score: smaller score indicates higher chance of visibility
            cam["score"] = distance_from_boundary + dark_bonus

        # Sort by computed score
        webcams.sort(key=lambda cam: cam["score"])

    except Exception as e:
        print(f"[ERROR] Webcam sorting failed: {e}")

    return webcams


# -------------------------------------------------------------------
# Sorting by Name & Country
# -------------------------------------------------------------------

def get_live_webcams_location_sorted():
    """
    Return webcams sorted alphabetically by location name.

    Returns:
        list[dict]: Sorted list of webcam dictionaries.
    """
    return sorted(WEBCAM_LIST, key=lambda cam: cam["location"])


def get_live_webcams_country_sorted():
    """
    Return webcams sorted by country, then location.

    Returns:
        list[dict]: Sorted list of webcam dictionaries.
    """
    return sorted(WEBCAM_LIST, key=lambda cam: (cam["country"], cam["location"]))
