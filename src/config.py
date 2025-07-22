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

SWPC_KP_INDEX_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
SWPC_OVATION_IMAGE_URL = "https://services.swpc.noaa.gov/images/animations/ovation/north/latest.jpg"
NASA_SOLAR_WIND_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
NASA_SUN_IMAGE_URL = "https://services.swpc.noaa.gov/images/sdo/hmi_color.jpg"

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
# AURORA WEBCAMS (Live streams)
# --------------------------------------------

AURORA_WEBCAMS = [
    {
        "name": "Abisko, Sweden",
        "url": "https://lightsoverlapland.com/live"
    },
    {
        "name": "Fairbanks, Alaska",
        "url": "https://auroraviewer.com/"
    },
    {
        "name": "Tromsø, Norway",
        "url": "https://polarlights.live/"
    },
    {
        "name": "Yellowknife, Canada",
        "url": "https://astronomynorth.com/live/"
    }
]

# --------------------------------------------
# EXPORT SETTINGS
# --------------------------------------------

EXPORT_DIRECTORY = os.path.join(os.path.expanduser("~"), "Downloads")
EXPORT_FILENAME_FORMAT = "aurora_report_%Y-%m-%d_%H-%M-%S.json"

# --------------------------------------------
# UI SETTINGS
# --------------------------------------------

WINDOW_TITLE = "Aurora Tracker"
WINDOW_SIZE = "1000x700"
THEME_COLOR = "#1f1f2e"  # Dark background for aurora theme
TEXT_COLOR = "#e0f7fa"
FONT_FAMILY = "Segoe UI"
