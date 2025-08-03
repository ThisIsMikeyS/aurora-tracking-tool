# -*- coding: utf-8 -*-
"""
Fetches live solar wind conditions and sun imagery for aurora tracking insights.
"""

import requests
import matplotlib.pyplot as plt
import csv
from io import StringIO
from pathlib import Path
from datetime import datetime, timedelta, timezone
from config import PLASMA_URL, MAGNETIC_URL, SUN_IMAGE_URLS

# Directory to store the latest image locally
IMAGE_DIR = Path("assets/images")

def get_solar_wind_data():
    """
    Retrieves solar wind plasma and magnetic field data.

    Returns:
        tuple: 
            - plasma_times: list of timestamps for plasma data
            - speeds: list of solar wind speeds (km/s)
            - densities: list of proton densities (p/cc)
            - mag_times: list of timestamps for magnetic field data
            - bz_values: list of Bz values (nT)
            - bt_values: list of Bt values (nT)
    """
    try:
        # --- Define Data Period ---
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=2)

        # --- Fetch Plasma Data ---
        r_plasma = requests.get(PLASMA_URL, timeout=10)
        r_plasma.raise_for_status()
        plasma_json = r_plasma.json()

        # Skip header row
        plasma_data = plasma_json[1:]

        plasma_times, speeds, densities = [], [], []
        for row in plasma_data:
            time_str, density, speed = row[0], row[1], row[2]

            if None in (time_str, speed, density):
                continue

            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            except ValueError:
                dt = datetime.strptime(time_str.split('.')[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

            if dt >= cutoff:
                plasma_times.append(f"{dt.strftime('%H:%M')}")
                speeds.append(float(speed))
                densities.append(float(density))

        # --- Fetch Magnetic Field Data ---
        r_mag = requests.get(MAGNETIC_URL, timeout=10)
        r_mag.raise_for_status()
        mag_json = r_mag.json()

        mag_data = mag_json[1:]

        mag_times, bz_values, bt_values = [], [], []
        for row in mag_data:
            time_str, bt, bz = row[0], row[6], row[3]  # Confirmed structure

            if None in (time_str, bz, bt):
                continue

            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            except ValueError:
                dt = datetime.strptime(time_str.split('.')[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

            if dt >= cutoff:
                mag_times.append(f"{dt.strftime('%H:%M')}")
                bz_values.append(float(bz))
                bt_values.append(float(bt))

        # Debug log
        print(f"[DEBUG] Plasma: {len(plasma_times)} entries, Speeds: {len(speeds)}, Densities: {len(densities)}")
        print(f"[DEBUG] Magnetic: {len(mag_times)} entries, Bz: {len(bz_values)}, Bt: {len(bt_values)}")

        return plasma_times, speeds, densities, mag_times, bz_values, bt_values

    except Exception as e:
        print(f"[ERROR] Failed to fetch solar wind data: {e}")
        return [], [], [], [], [], []


def download_sun_image(name: str, url: str, save_dir: Path = IMAGE_DIR) -> Path:
    """
    Downloads a solar image by name and URL.
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
    return SUN_IMAGE_URLS

