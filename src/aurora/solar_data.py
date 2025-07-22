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

# Directory to store the latest image locally
IMAGE_DIR = Path("assets/images")
IMAGE_NAME = "solar_disk_aia_193.jpg"
IMAGE_PATH = IMAGE_DIR / IMAGE_NAME

# Data URLs
SOLAR_WIND_API = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
PLASMA_API = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
MAGNETIC_API = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
SUN_IMAGE_URL = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"

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
        r_plasma = requests.get(PLASMA_API, timeout=10)
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
        r_mag = requests.get(MAGNETIC_API, timeout=10)
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


def download_sun_image(save_path: Path = IMAGE_PATH) -> Path:
    """
    Downloads the latest sun image (AIA 193) and saves it locally.
    
    Args:
        save_path (Path): Destination path to save the image.
    
    Returns:
        Path: Path to the downloaded image file.
    """
    try:
        print(f"[INFO] Downloading SWPC Ovation image from {SUN_IMAGE_URL}")
        response = requests.get(SUN_IMAGE_URL, stream=True, timeout=10)
        response.raise_for_status()

        # Ensure the directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the image to the specified path
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"[SUCCESS] Sun map saved to {save_path}")
        return save_path

    except requests.RequestException as e:
        print(f"[ERROR] Failed to download Sun image: {e}")
        return None

def get_sun_image():
    """
    Fetch the URL of the latest image of the solar disk.

    Returns:
        str: URL to the live solar image.
    """
    return SUN_IMAGE_URL
