# -*- coding: utf-8 -*-
"""
swpc_map.py
===========
Handles downloading and updating of NOAA SWPC Ovation Aurora Forecast imagery.

Purpose:
- Fetch the latest aurora map from NOAA's SWPC service.
- Save the image locally for use in the Aurora Tracker application.
- Provide timestamp for freshness indicator.

Dependencies:
- requests (HTTP requests)
- pathlib (path handling)
"""

import requests
from datetime import datetime
from pathlib import Path
from config import SWPC_IMAGE_URL, MAP_DIR, SWPC_MAP_NAME

# Default local save path for the SWPC map
IMAGE_PATH = MAP_DIR / SWPC_MAP_NAME


# -------------------------------------------------------------------
# Download the SWPC Aurora Map
# -------------------------------------------------------------------

def download_swpc_map(save_path: Path = IMAGE_PATH) -> Path:
    """
    Download the latest SWPC Ovation Aurora Forecast image and save it locally.

    Args:
        save_path (Path, optional):
            Destination path to save the image.
            Defaults to IMAGE_PATH.

    Returns:
        Path | None:
            Path to the saved image file if successful,
            None if download fails.
    """
    try:
        print(f"[INFO] Downloading SWPC Ovation image from {SWPC_IMAGE_URL}")
        response = requests.get(SWPC_IMAGE_URL, stream=True, timeout=10)
        response.raise_for_status()

        # Ensure the directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save image in chunks
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"[SUCCESS] Aurora map saved to {save_path}")
        return save_path

    except requests.RequestException as e:
        print(f"[ERROR] Failed to download SWPC image: {e}")
        return None


# -------------------------------------------------------------------
# Get Map Update Timestamp
# -------------------------------------------------------------------

def get_latest_map_timestamp() -> str:
    """
    Get the current UTC timestamp to mark the map update time.

    Returns:
        str: UTC timestamp string (e.g., "2025-07-18 21:12:00 UTC").
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


# -------------------------------------------------------------------
# Standalone Test
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Test module functionality when run standalone
    print("[TEST] Attempting to download latest SWPC map...")
    path = download_swpc_map()
    if path:
        print(f"[TEST PASS] File downloaded to {path}")
    else:
        print("[TEST FAIL] Download failed.")
