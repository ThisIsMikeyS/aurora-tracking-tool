# -*- coding: utf-8 -*-
"""
image_utils.py
==============
Image downloading and saving utilities for the Aurora Tracker.

Functions:
- download_image: Download an image from a URL and save it locally.
"""

import requests
from pathlib import Path


# -------------------------------------------------------------------
# Image Download Function
# -------------------------------------------------------------------

def download_image(url: str, save_path: Path) -> bool:
    """
    Download an image from a given URL and save it to a specified local path.

    Args:
        url (str): The full URL of the image to download.
        save_path (Path): The local file path (including filename) where the image will be saved.

    Returns:
        bool: True if download succeeds, False otherwise.
    """
    try:
        # Make HTTP request to fetch the image
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Ensure the directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the image file to disk
        with open(save_path, 'wb') as file:
            file.write(response.content)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to download image from {url}: {e}")
        return False
