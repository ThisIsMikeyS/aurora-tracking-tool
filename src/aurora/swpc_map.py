# -*- coding: utf-8 -*-
"""
Downloads and updates the latest NOAA SWPC Ovation Aurora Forecast imagery.
Used to visualize global auroral activity within the Aurora Tracker application.
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from config import SWPC_IMAGE_URL, MAP_DIR, SWPC_MAP_NAME

# Directory to store the latest image locally
IMAGE_PATH = MAP_DIR / SWPC_MAP_NAME


def download_swpc_map(save_path: Path = IMAGE_PATH) -> Path:
    """
    Downloads the latest SWPC aurora map and saves it locally.
    
    Args:
        save_path (Path): Destination path to save the image.
    
    Returns:
        Path: Path to the downloaded image file.
    """
    try:
        print(f"[INFO] Downloading SWPC Ovation image from {SWPC_IMAGE_URL}")
        response = requests.get(SWPC_IMAGE_URL, stream=True, timeout=10)
        response.raise_for_status()

        # Ensure the directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the image to the specified path
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"[SUCCESS] Aurora map saved to {save_path}")
        return save_path

    except requests.RequestException as e:
        print(f"[ERROR] Failed to download SWPC image: {e}")
        return None


def get_latest_map_timestamp() -> str:
    """
    Returns the current timestamp to indicate freshness of map updates.

    Returns:
        str: Timestamp string (e.g. "2025-07-18 21:12:00").
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


if __name__ == "__main__":
    # Test the module standalone
    print("[TEST] Attempting to download latest SWPC map...")
    path = download_swpc_map()
    if path:
        print(f"[TEST PASS] File downloaded to {path}")
    else:
        print("[TEST FAIL] Download failed.")
