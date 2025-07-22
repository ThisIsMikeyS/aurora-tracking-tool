"""
aurora_map_overlay.py
==========================
Generates a world map overlaid with aurora visibility probabilities using the 
SWPC Ovation Aurora Forecast. The result is saved as an image for display in the GUI.

Dependencies:
- requests
- matplotlib
- (mpl_toolkits).basemap
- numpy
"""

import os
import requests
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timezone

AURORA_VISIBILITY_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"


def fetch_aurora_data():
    """
    Fetch aurora probability data from the SWPC Ovation Aurora Forecast API.

    Returns:
        list: List of [longitude, latitude, probability] records.
    """
    try:
        response = requests.get(AURORA_VISIBILITY_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("coordinates", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch aurora overlay data: {e}")
        return []


def generate_aurora_map(save_path="aurora_map.png"):
    """
    Generates and saves a map with aurora probability overlay.

    Args:
        save_path (str): File path to save the generated image.
    """
    coords = fetch_aurora_data()
    if not coords:
        print("[WARN] No aurora data available to render.")
        return None

    # Normalize longitudes from [0, 360] → [-180, 180] and out only points with probability >= 1 and latitudes within the auroral zones (≥45°).
    normalized_coords = []
    for lon, lat, prob in coords:
        if prob >= 1.0 and abs(lat) >= 45.0:
            if lon > 180:
                lon -= 360
            normalized_coords.append((lon, lat, prob))

    # Extract values for plotting
    lon = np.array([pt[0] for pt in normalized_coords])
    lat = np.array([pt[1] for pt in normalized_coords])
    prob = np.array([pt[2] for pt in normalized_coords])

    # Set up the map
    fig = plt.figure(figsize=(14, 8))
    m = Basemap(projection='mill', lon_0=0, resolution='c')

    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary(fill_color='midnightblue')
    m.fillcontinents(color='lightgray', lake_color='midnightblue')
    m.drawparallels(np.arange(-90, 91, 30), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(-180, 181, 60), labels=[0, 0, 0, 1])

    # Map projection
    x, y = m(lon, lat)

    # Convert probabilities to color
    def prob_to_color(p):
        if p >= 50:
            return "red"
        elif p >= 30:
            return "orange"
        elif p >= 10:
            return "green"
        elif p >= 1:
            return "dimgray"
        return "black"

    colors = [prob_to_color(p) for p in prob]

    # Draw points
    m.scatter(x, y, c=colors, s=3, alpha=0.7)

    plt.title(f"Aurora Visibility Probability\n{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[INFO] Aurora map saved to {save_path}")
    return save_path

