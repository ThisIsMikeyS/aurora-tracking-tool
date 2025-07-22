# -*- coding: utf-8 -*-
"""
Fetches live solar wind conditions and sun imagery for aurora tracking insights.
"""

import requests
from pathlib import Path

# Directory to store the latest image locally
IMAGE_DIR = Path("assets/images")
IMAGE_NAME = "solar_disk_aia_193.jpg"
IMAGE_PATH = IMAGE_DIR / IMAGE_NAME

# Data URLs
SOLAR_WIND_API = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
SUN_IMAGE_URL = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"


def get_solar_wind_data():
    """
    Fetch the latest solar wind data.

    Returns:
        dict: Dictionary with selected solar wind properties (e.g., speed, density, temperature).
    """
    try:
        response = requests.get(SOLAR_WIND_API, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Grab the most recent reading
        latest = data[-1]
        return {
            "timestamp": latest[0],
            "speed_kms": float(latest[1]),
            "density_ppcm3": float(latest[2]),
            "temperature_K": float(latest[3])
        }

    except Exception as e:
        print(f"[ERROR] Failed to fetch solar wind data: {e}")
        return {
            "timestamp": "N/A",
            "speed_kms": "N/A",
            "density_ppcm3": "N/A",
            "temperature_K": "N/A"
        }


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
