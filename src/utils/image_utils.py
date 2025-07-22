# -*- coding: utf-8 -*-
"""
Image downloading and formatting utilities for Aurora Tracker.
"""

import requests
from pathlib import Path


def download_image(url: str, save_path: Path) -> bool:
    """
    Download an image from a URL to a local file.

    Args:
        url (str): Image URL
        save_path (Path): Local path to save the image

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False
