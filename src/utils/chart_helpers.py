# -*- coding: utf-8 -*-
"""
chart_helpers.py
================
Utility functions for color mapping and chart generation used across Aurora Tracker.

Functions:
- get_kp_color: Assigns a color based on the Kp index value.
- plot_line_chart: Creates a formatted time-series line chart.
"""

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


# -------------------------------------------------------------------
# KP Index Color Mapping
# -------------------------------------------------------------------

def get_kp_color(kp) -> str:
    """
    Return a color name corresponding to the Kp index value.

    Args:
        kp (float or str): Kp index value.

    Returns:
        str: Matplotlib-compatible color name.
    """
    try:
        kp_value = float(kp)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Kp value: {kp}")

    if kp_value < 3.0:
        return 'green'
    elif 3.0 <= kp_value < 4.0:
        return 'yellow'
    elif 4.0 <= kp_value < 6.0:
        return 'orange'
    elif 6.0 <= kp_value < 8.0:
        return 'red'
    else:
        return 'darkred'


# -------------------------------------------------------------------
# Line Chart Plotting
# -------------------------------------------------------------------

def plot_line_chart(title: str, x_data, y_data, y_label: str):
    """
    Generate a matplotlib figure for a time series line chart.

    Args:
        title (str): Title of the chart.
        x_data (list): X-axis values (datetime or time values).
        y_data (list): Y-axis values (numeric).
        y_label (str): Label for the Y-axis.

    Returns:
        matplotlib.figure.Figure: Configured figure object.
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot the line
    ax.plot(x_data, y_data, linestyle='-', marker='', color='red')

    # Set labels and formatting
    ax.set_title(title)
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel(y_label)
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax.tick_params(axis='x', rotation=45)

    return fig
