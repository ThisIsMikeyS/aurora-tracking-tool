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


# -----------------------
# Webcam List with Lat/Lon
# -----------------------
WEBCAM_LIST = [
    {"location": "Tromsø", "country": "Norway", "lat": 69.6496, "lon": 18.9560, "url": "https://weather.cs.uit.no/"},
    {"location": "Abisko", "country": "Sweden", "lat": 68.3518, "lon": 18.8294, "url": "https://lightsoverlapland.com/webcam/"},
    {"location": "Kilpisjärvi", "country": "Finland", "lat": 69.0472, "lon": 20.7972, "url": "https://www.youtube.com/watch?v=ccTVAhJU5lg"},
    {"location": "Fairbanks, AK", "country": "United States", "lat": 64.8378, "lon": -147.7164, "url": "https://www.youtube.com/watch?v=O52zDyxg5QI"},
    {"location": "Yellowknife, NT", "country": "Canada", "lat": 62.4540, "lon": -114.3718, "url": "https://auroramax.com/live"},
    {"location": "Kingston, TAS", "country": "Australia", "lat": -42.9728, "lon": 147.3050, "url": "https://www.allskycam.com/u.php?u=539"},
    {"location": "Casey Station", "country": "Antarctica", "lat": -66.2833, "lon": 110.5333, "url": "https://www.antarctica.gov.au/antarctic-operations/webcams/casey/"},
    {"location": "Shetland Islands", "country": "Scotland", "lat": 59.8541, "lon": -1.2752, "url": "https://www.shetlandwebcams.com/cliff-cam-3/"},
    {"location": "Queenstown", "country": "New Zealand", "lat": -45.0311, "lon": 168.6625, "url": "https://queenstown.roundshot.com/#/"},
    {"location": "Churchill", "country": "Canada", "lat": 58.7808, "lon": -94.1869, "url": "https://www.youtube.com/watch?v=a0i1Kg6fROg"},
    {"location": "Porjus", "country": "Sweden", "lat": 66.9500, "lon": 19.8167, "url": "https://uk.jokkmokk.jp/detail_nr4.shtml"},
    {"location": "Hella", "country": "Iceland", "lat": 63.9777, "lon": -20.2557, "url": "https://landhotel.is/index.php/northernlights-live"},
    {"location": "Sodankylä", "country": "Finland", "lat": 67.4167, "lon": 26.5833, "url": "https://www.youtube.com/watch?v=zSGpRT-xIkQ"},
    {"location": "Kuusamo", "country": "Finland", "lat": 65.9667, "lon": 29.1833, "url": "https://ruka3.panocloud.webcam/"},
    {"location": "Sentermoen", "country": "Norway", "lat": 68.8609, "lon": 18.3483, "url": "https://www.yr.no/en/other-conditions/1-291747/Norway/Troms/Bardu/Setermoen"},
    {"location": "Kangerlussuaq", "country": "Greenland", "lat": 67.0086, "lon": -50.6892, "url": "https://www.youtube.com/watch?v=dG4pb20EqJc"},
    {"location": "Tampere", "country": "Finland", "lat": 61.4981, "lon": 23.7600, "url": "https://www.ursa.fi/yhd/tampereenursa/"},
    {"location": "Ilulissat", "country": "Greenland", "lat": 69.2167, "lon": -51.1000, "url": "https://www.youtube.com/watch?v=EI27YpsNzSQ"},
]

# -----------------------
# Manual Timezone Mapping
# -----------------------
CAMERA_TIMEZONES = {
    "Tromsø": "Europe/Oslo",
    "Abisko": "Europe/Stockholm",
    "Kilpisjärvi": "Europe/Helsinki",
    "Fairbanks, AK": "America/Anchorage",
    "Yellowknife, NT": "America/Yellowknife",
    "Kingston, TAS": "Australia/Hobart",
    "Casey Station": "Antarctica/Casey",
    "Shetland Islands": "Europe/London",
    "Queenstown": "Pacific/Auckland",
    "Churchill": "America/Winnipeg",
    "Porjus": "Europe/Stockholm",
    "Hella": "Atlantic/Reykjavik",
    "Sodankylä": "Europe/Helsinki",
    "Kuusamo": "Europe/Helsinki",
    "Sentermoen": "Europe/Oslo",
    "Kangerlussuaq": "America/Godthab",
    "Tampere": "Europe/Helsinki",
    "Ilulissat": "America/Godthab",
}


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

