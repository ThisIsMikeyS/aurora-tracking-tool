# -*- coding: utf-8 -*-
"""
api_helpers.py
==============
Helper functions for formatting API data, interpreting KP index values, and generating standardized filenames.
"""

from datetime import datetime


# -------------------------------------------------------------------
# Timestamp Formatting
# -------------------------------------------------------------------

def format_timestamp(timestamp_str: str) -> str:
    """
    Convert an ISO 8601 timestamp to a human-readable UTC string.

    Args:
        timestamp_str (str): ISO timestamp string (e.g., '2023-07-18T00:00:00Z').

    Returns:
        str: Human-readable UTC string (e.g., '2023-07-18 00:00 UTC').
             If parsing fails, returns the original string.
    """
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return timestamp_str


# -------------------------------------------------------------------
# KP Index Interpretation
# -------------------------------------------------------------------

def interpret_kp_index(kp_value: float) -> str:
    """
    Interpret KP index value to describe likely aurora visibility range.

    Args:
        kp_value (float): KP index value.

    Returns:
        str: Description of expected visibility reach.
    """
    if kp_value < 3:
        return "Visible in High Arctic only"
    elif kp_value < 5:
        return "Visible above 60\u00B0N"
    elif kp_value < 7:
        return "Visible in Scandinavia, Canada, Alaska"
    elif kp_value < 8:
        return "Visible in UK, Germany, USA"
    else:
        return "May be visible as far south as Northern Spain or Southern USA"


# -------------------------------------------------------------------
# Filename Generation
# -------------------------------------------------------------------

def generate_filename(prefix: str, extension: str = "json") -> str:
    """
    Generate a standardized filename with a timestamp.

    Args:
        prefix (str): Prefix for the filename.
        extension (str, optional): File extension (default is 'json').

    Returns:
        str: Filename in the format '<prefix>_YYYY-MM-DD_HH-MM-SS.<extension>'.
    """
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{now}.{extension}"
