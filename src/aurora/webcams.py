# -*- coding: utf-8 -*-
"""
Returns a curated list of live aurora webcam URLs and sorts them by visibility probability.
"""

import math
import pytz
from pytz import timezone as pytz_timezone
from datetime import datetime, timezone
from astral.sun import sun
from astral import LocationInfo
from .kp_index import get_current_kp_index
from config import WEBCAM_LIST, CAMERA_TIMEZONES

# -----------------------
# Darkness Detection
# -----------------------
def is_dark(lat, lon, location_name=None):
    """Returns True if it is currently dark at the location (sun below horizon)."""
    try:
        # Get local timezone from predefined mapping, fallback to UTC
        if location_name and location_name in CAMERA_TIMEZONES:
            tz = pytz_timezone(CAMERA_TIMEZONES[location_name])
        else:
            tz = timezone.utc  # fallback

        now_local = datetime.now(tz)
        #print(f"lat: {lat}  lon: {lon}  Local Date-time: {now_local}")

        location = LocationInfo(latitude=lat, longitude=lon)
        s = sun(location.observer, date=now_local.date(), tzinfo=tz)

        return now_local < s['dawn'] or now_local > s['dusk']

    except ValueError as e:
        msg = str(e).lower()
        if "degrees below" in msg:
            print(f"[INFO] Sun never sets in {location_name} — assuming bright.")
            return False
        elif "degrees above" in msg:
            print(f"[INFO] Sun never rises in {location_name} — assuming dark.")
            return True
        else:
            print(f"[WARN] Astral raised ValueError for {location}: {e}")
            return False

    except Exception as e:
        print(f"[WARN] Astral failed for {location}: {e}")
        return False


# -----------------------
# Sorting by Visibility
# -----------------------
def get_live_webcams_best_sorted():
    """
    Returns webcams sorted by likelihood of aurora visibility.
    Considers both Kp index range and darkness at location.
    """
    webcams = WEBCAM_LIST.copy()
    try:
        kp = get_current_kp_index()
        visible_lat = 90 - (kp * 5)  # Approximate auroral boundary

        for cam in webcams:
            cam_lat = abs(cam["lat"])
            distance_from_boundary = cam_lat - visible_lat

            # Darkness bonus
            dark_bonus = -10 if is_dark(cam["lat"], cam["lon"], cam["location"]) else 10

            # Score: smaller is better
            cam["score"] = distance_from_boundary + dark_bonus

        webcams.sort(key=lambda cam: cam["score"])

    except Exception as e:
        print(f"[ERROR] Webcam sorting failed: {e}")

    return webcams


# -----------------------------------
# Sorting by Location and Country
# -----------------------------------

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

