# -*- coding: utf-8 -*-
"""
Centralized configuration for the Aurora Tracker application.
Includes API endpoints, default thresholds, update intervals, and alert settings.
"""

import os
from datetime import timedelta

# --------------------------------------------
# API ENDPOINTS
# --------------------------------------------

AURORA_VISIBILITY_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
HOURLY_FORECAST_API = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
LONG_TERM_FORECAST_API = "https://services.swpc.noaa.gov/text/27-day-outlook.txt"
PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
MAGNETIC_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
SUN_IMAGE_URLS = [
        ["solar_disk_aia_0193", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"],
        ["solar_disk_aia_0304", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg"],
        ["solar_disk_aia_0171", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0171.jpg"],
        ["solar_disk_aia_0211", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0211.jpg"],
        ["solar_disk_aia_0131", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0131.jpg"],
        ["solar_disk_aia_0335", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0335.jpg"],
        ["solar_disk_aia_0094", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0094.jpg"],
        ["solar_disk_aia_1600", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_1600.jpg"],
        ["solar_disk_aia_1700", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_1700.jpg"],
        ["solar_disk_aia_211193171", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_211193171.jpg"],
        ["solar_disk_aia_304211171", "https://sdo.gsfc.nasa.gov/assets/img/latest/f_304_211_171_1024.jpg"],
        ["solar_disk_aia_94335193", "https://sdo.gsfc.nasa.gov/assets/img/latest/f_094_335_193_1024.jpg"],
        ["solar_disk_aia_0171_HMIB", "https://sdo.gsfc.nasa.gov/assets/img/latest/f_HMImag_171_1024.jpg"],
        ["solar_disk_HMIB", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIB.jpg"],
        ["solar_disk_HMIBC", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIBC.jpg"],
        ["solar_disk_HMIIC", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg"],
        ["solar_disk_HMIIF", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIF.jpg"],
        ["solar_disk_HMII", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMII.jpg"],
        ["solar_disk_HMID", "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMID.jpg"]
    ]
SWPC_IMAGE_URL = "https://services.swpc.noaa.gov/images/animations/ovation/north/latest.jpg"


# --------------------------------------------
# LOCATION & MAP SETTINGS
# --------------------------------------------

DEFAULT_COORDINATES = {
    "latitude": 69.6496,   # Tromsø, Norway
    "longitude": 18.9560
}

MAP_REFRESH_INTERVAL_MINUTES = 15  # How often to update the OVATION map

# --------------------------------------------
# ALERT & THRESHOLD SETTINGS
# --------------------------------------------

KP_ALERT_THRESHOLD = 5  # Minimum Kp index required to trigger visual alert
CHECK_INTERVAL = timedelta(minutes=10)  # How often to check KP updates

# --------------------------------------------
# AURORA WEBCAMS & TIMEZONES (Live streams)
# --------------------------------------------

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

# --------------------------------------------
# EXPORT SETTINGS
# --------------------------------------------

EXPORT_DIRECTORY = os.path.join(os.path.expanduser("~"), "Downloads")
EXPORT_FILENAME_FORMAT = "aurora_report_%Y-%m-%d_%H-%M-%S.json"

# --------------------------------------------
# UI SETTINGS
# --------------------------------------------

class UISettings: 

    WINDOW_TITLE = "Aurora Tracker"
    WINDOW_SIZE = "900x800"
    DARK_THEME_BG = "#1f1f2e"
    DARK_THEME_FG = "#e0f7fa"
    DARK_THEME_ACCENT = "#2e3b4e"
    FONT_FAMILY = "Segoe UI"

# --------------------------------------------
# UI HELP INFO TEXT
# --------------------------------------------

OVERLAY_MAP_INFO = (
            "🗺️ Aurora Map Overlay Help\n\n"
            "This map shows the probability of seeing the aurora based on NOAA's Ovation model.\n\n"
            "To maximise your changes of seeing the aurora, try to find an area with a red, orange or green colour, and without cloud coverage.\n\n"
            "Colour Legend:\n"
            "  🔴 Red: 50%+ chance of seeing aurora.\n"
            "  🟠 Orange: 30% to 49% chance of seeing aurora.\n"
            "  🟢 Green: 10% to 29% chance of seeing aurora.\n"
            "  ⚫ Dark Grey: 1% to 9%vchance of seeing aurora.\n\n"
            "The map updates dynamically using the latest space weather data."
        )

WEBCAM_TAB_INFO = (
            "Aurora Webcams Tab Help\n\n"
            "This tab shows a list of live webcam streams from locations around the world where the aurora (Northern or Southern Lights) may be visible.\n\n"
            "How it works:\n"
            "- The list is automatically sorted to prioritize webcams where the aurora is most likely visible right now.\n"
            "- This takes into account:\n"
            "   • The current Kp index (a measure of geomagnetic activity).\n"
            "   • The latitude of the location.\n"
            "   • Whether it is currently dark at the location (since aurora cannot be seen in daylight).\n\n"
            "How to use:\n"
            "1. Click on any webcam from the list.\n"
            "2. Click the 'Open Webcam' button to open the live stream in your browser.\n\n"
            "Use the Help button at any time to revisit these instructions."
        )