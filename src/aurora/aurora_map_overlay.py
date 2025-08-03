# -*- coding: utf-8 -*-
"""
aurora_map_overlay.py
=====================
Generates a world map with aurora visibility probabilities
overlaid using the SWPC Ovation Aurora Forecast.

Output is saved as an image for display in the Aurora Tracker GUI.

Dependencies:
    - requests
    - numpy
    - matplotlib
    - mpl_toolkits.basemap
"""

import os
from datetime import datetime, timezone

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import requests

from config import AURORA_VISIBILITY_URL, MAP_DIR, OVERLAY_MAP_NAME
from utils.map_helpers import normalize_coordinates, create_basemap, probability_to_color

# Default output path for generated overlay image
IMAGE_PATH = MAP_DIR / OVERLAY_MAP_NAME


# =========================
#  DATA FETCHING
# =========================
def fetch_aurora_data():
    """
    Fetch aurora probability data from the SWPC Ovation Aurora Forecast API.

    Returns:
        list: List of [longitude, latitude, probability] records.
              Returns empty list if data cannot be fetched.
    """
    try:
        response = requests.get(AURORA_VISIBILITY_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("coordinates", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch aurora overlay data: {e}")
        return []


# =========================
#  MAP GENERATION
# =========================
def generate_aurora_map(save_path=IMAGE_PATH):
    """
    Generates and saves a map image with aurora probability overlay.

    Args:
        save_path (str or Path): File path to save the generated image.

    Returns:
        Path or None: Path to saved image if successful, None if failed.
    """
    coords = fetch_aurora_data()
    if not coords:
        print("[WARN] No aurora data available to render.")
        return None

    # Filter and normalize coordinates
    normalized_coords = normalize_coordinates(coords)

    # Extract longitude, latitude, and probability values
    lon = np.array([pt[0] for pt in normalized_coords])
    lat = np.array([pt[1] for pt in normalized_coords])
    prob = np.array([pt[2] for pt in normalized_coords])

    # Initialize map figure
    fig = plt.figure(figsize=(14, 8))
    m = create_basemap()

    # Map projection of points
    x, y = m(lon, lat)

    # Assign colors based on probability
    colors = [probability_to_color(p) for p in prob]

    # Plot points on map
    m.scatter(x, y, c=colors, s=3, alpha=0.7)

    # Add title with timestamp
    plt.title(f"Aurora Visibility Probability\n{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    plt.tight_layout()

    # Save and close figure
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[INFO] Aurora map saved to {save_path}")
    return save_path

