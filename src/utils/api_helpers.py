# -*- coding: utf-8 -*-
"""
API data formatting and utility logic for KP index and forecasts.
"""

from datetime import datetime


def format_timestamp(timestamp_str):
    """
    Convert ISO 8601 timestamp to readable format.

    Args:
        timestamp_str (str): ISO timestamp string (e.g. '2023-07-18T00:00:00Z')

    Returns:
        str: Human-readable string (e.g. '2023-07-18 00:00 UTC')
    """
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return timestamp_str


def interpret_kp_index(kp_value: float) -> str:
    """
    Provide a rough visibility area description based on KP index.

    Args:
        kp_value (float): KP index

    Returns:
        str: Description of visibility reach
    """
    if kp_value < 3:
        return "Visible in High Arctic only"
    elif kp_value < 5:
        return "Visible above 60°N"
    elif kp_value < 7:
        return "Visible in Scandinavia, Canada, Alaska"
    elif kp_value < 8:
        return "Visible in UK, Germany, USA"
    else:
        return "May be visible as far south as Northern Spain or Southern USA"


def generate_filename(prefix: str, extension: str = "json") -> str:
    """
    Generate a standardized timestamped filename.

    Args:
        prefix (str): Prefix for the filename
        extension (str): File extension (default is 'json')

    Returns:
        str: Filename string
    """
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{now}.{extension}"
