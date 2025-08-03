# -*- coding: utf-8 -*-
"""
map_helpers.py
=====================
Helper functions for use with generation of maps showing
probability of aurora visibility.

Dependencies:
    - numpy
    - mpl_toolkits.basemap
"""
import numpy as np
from mpl_toolkits.basemap import Basemap

def normalize_coordinates(coords):
    """
    Filters and normalizes aurora coordinates.

    - Keeps only points with probability ≥ 1
    - Keeps latitudes ≥ ±45°
    - Converts longitude from [0, 360] → [-180, 180]

    Args:
        coords (list): List of [lon, lat, prob] entries.

    Returns:
        list: Filtered and normalized coordinates.
    """
    normalized = []
    for lon, lat, prob in coords:
        if prob >= 1.0 and abs(lat) >= 45.0:
            if lon > 180:
                lon -= 360
            normalized.append((lon, lat, prob))
    return normalized


def create_basemap():
    """
    Configures and returns a Basemap instance with coastlines, countries, etc.

    Returns:
        Basemap: Configured Basemap object.
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


def probability_to_color(prob):
    """
    Maps aurora probability to a color.

    Args:
        prob (float): Probability percentage.

    Returns:
        str: Color name.
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