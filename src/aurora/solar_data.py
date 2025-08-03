# -*- coding: utf-8 -*-
"""
solar_data.py
=============
Fetches live solar wind conditions (plasma and magnetic field data) and downloads 
sun imagery for aurora tracking insights.

Data Sources:
- NOAA/SWPC Solar Wind Data (Plasma & Magnetic Field)
- SDO/NASA Sun Imagery
"""

import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from config import PLASMA_URL, MAGNETIC_URL, SUN_IMAGE_URLS

# Directory to store the latest sun images locally
IMAGE_DIR = Path("assets/images")


# -------------------------------------------------------------------
# Solar Wind Data Retrieval
# -------------------------------------------------------------------

def get_solar_wind_data():
    """
    Retrieve recent solar wind plasma and magnetic field data.

    Data covers approximately the last 2 hours.

    Returns:
        tuple:
            (
                plasma_times (list[str]),  # Timestamps for plasma data
                speeds (list[float]),      # Solar wind speeds (km/s)
                densities (list[float]),   # Proton densities (p/cc)
                mag_times (list[str]),     # Timestamps for magnetic field data
                bz_values (list[float]),   # Bz component values (nT)
                bt_values (list[float])    # Bt total field values (nT)
            )
    """
    try:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=2)

        # ------------------------------
        # Fetch Plasma (Density, Speed)
        # ------------------------------
        r_plasma = requests.get(PLASMA_URL, timeout=10)
        r_plasma.raise_for_status()
        plasma_json = r_plasma.json()[1:]  # Skip header

        plasma_times, speeds, densities = [], [], []
        for row in plasma_json:
            time_str, density, speed = row[0], row[1], row[2]

            if None in (time_str, speed, density):
                continue  # Skip incomplete data rows

            # Parse timestamp (strip microseconds if present)
            dt = _parse_time(time_str)
            if dt and dt >= cutoff:
                plasma_times.append(dt.strftime('%H:%M'))
                speeds.append(float(speed))
                densities.append(float(density))

        # ------------------------------
        # Fetch Magnetic Field (Bz, Bt)
        # ------------------------------
        r_mag = requests.get(MAGNETIC_URL, timeout=10)
        r_mag.raise_for_status()
        mag_json = r_mag.json()[1:]  # Skip header

        mag_times, bz_values, bt_values = [], [], []
        for row in mag_json:
            time_str, bt, bz = row[0], row[6], row[3]  # Confirmed column indices

            if None in (time_str, bz, bt):
                continue

            dt = _parse_time(time_str)
            if dt and dt >= cutoff:
                mag_times.append(dt.strftime('%H:%M'))
                bz_values.append(float(bz))
                bt_values.append(float(bt))

        # Debug info
        print(f"[DEBUG] Plasma: {len(plasma_times)} timestamps, {len(speeds)} speeds, {len(densities)} densities")
        print(f"[DEBUG] Magnetic: {len(mag_times)} timestamps, {len(bz_values)} Bz, {len(bt_values)} Bt")

        return plasma_times, speeds, densities, mag_times, bz_values, bt_values

    except Exception as e:
        print(f"[ERROR] Failed to fetch solar wind data: {e}")
        return [], [], [], [], [], []


def _parse_time(time_str):
    """
    Safely parse a timestamp string into a timezone-aware datetime object.
    Handles both standard and microsecond timestamps.

    Args:
        time_str (str): Timestamp string from API.

    Returns:
        datetime or None
    """
    try:
        # Handle microseconds if present
        if '.' in time_str:
            time_str = time_str.split('.')[0]
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


# -------------------------------------------------------------------
# Sun Image Retrieval
# -------------------------------------------------------------------

def download_sun_image(name: str, url: str, save_dir: Path = IMAGE_DIR) -> Path:
    """
    Download a solar image and save it locally.

    Args:
        name (str): Image name (used as filename without extension).
        url (str): Image URL.
        save_dir (Path): Directory to save images.

    Returns:
        Path or None: Path to the saved image, or None if download failed.
    """
    try:
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"{name}.jpg"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(save_path, "wb") as file:
            file.write(response.content)

        return save_path

    except Exception as e:
        print(f"[ERROR] Failed to download {name}: {e}")
        return None


def get_sun_image_urls():
    """
    Retrieve the configured list of sun image URLs.

    Returns:
        list[tuple]: List of (name, url) tuples for sun images.
    """
    return SUN_IMAGE_URLS
