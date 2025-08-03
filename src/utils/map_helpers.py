# -*- coding: utf-8 -*-
"""
map_helpers.py
==============
Helper functions for generating maps that visualize aurora visibility probability.

Responsibilities:
- Filtering and normalizing aurora probability coordinate data.
- Creating a configured Basemap instance for plotting.
- Mapping probability values to colors for display.

Dependencies:
    - numpy
    - mpl_toolkits.basemap
"""

import numpy as np
from mpl_toolkits.basemap import Basemap


# -------------------------------------------------------------------
# Coordinate Processing
# -------------------------------------------------------------------

def normalize_coordinates(coords):
    """
    Filter and normalize aurora coordinates for plotting.

    Processing steps:
        - Keep only points where probability ≥ 1%.
        - Keep only points where latitude is within auroral zone (≥ ±45°).
        - Convert longitudes from [0, 360] to [-180, 180].

    Args:
        coords (list): List of [longitude, latitude, probability].

    Returns:
        list: Filtered and normalized coordinates as tuples (lon, lat, prob).
    """
    normalized = []
    for lon, lat, prob in coords:
        if prob >= 1.0 and abs(lat) >= 45.0:
            # Adjust longitude range for Basemap compatibility
            if lon > 180:
                lon -= 360
            normalized.append((lon, lat, prob))
    return normalized


# -------------------------------------------------------------------
# Basemap Setup
# -------------------------------------------------------------------

def create_basemap():
    """
    Configure and return a Basemap instance with standard map features.

    Returns:
        Basemap: Configured Basemap object ready for plotting.
    """
    m = Basemap(projection='mill', lon_0=0, resolution='c')

    # Draw geographical features
    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary(fill_color='midnightblue')
    m.fillcontinents(color='lightgray', lake_color='midnightblue')
    m.drawparallels(np.arange(-90, 91, 30), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(-180, 181, 60), labels=[0, 0, 0, 1])

    return m


# -------------------------------------------------------------------
# Probability-to-Color Mapping
# -------------------------------------------------------------------

def probability_to_color(prob):
    """
    Map aurora probability percentage to a corresponding color for plotting.

    Args:
        prob (float): Aurora visibility probability percentage.

    Returns:
        str: Color name representing probability level.
    """
    if prob >= 50:
        return "red"
    elif prob >= 30:
        return "orange"
    elif prob >= 10:
        return "green"
    elif prob >= 1:
        return "dimgray"
    return "black"
