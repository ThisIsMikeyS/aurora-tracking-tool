# -*- coding: utf-8 -*-
"""
forecast.py
===========
Handles fetching and plotting of aurora Kp index forecasts
from short-term (3-day) to long-term (27-day) sources.

Functionality:
- Fetch 3-day forecast (hourly data)
- Fetch 27-day forecast (daily max values)
- Generate matplotlib charts for GUI embedding

Dependencies:
    - requests
    - matplotlib
    - datetime
"""

import requests
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from utils.chart_helpers import get_kp_color
from config import HOURLY_FORECAST_API, LONG_TERM_FORECAST_API


# ====================================
# FETCHING FORECAST DATA
# ====================================
def get_hourly_forecast():
    """
    Fetch Kp index forecast in 3-hour intervals for the next 72 hours.

    Returns:
        tuple: (times, kp_values)
            - times (list of str): UTC timestamps in string format
            - kp_values (list of float): Kp index values
    """
    try:
        response = requests.get(HOURLY_FORECAST_API, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecast_data = data[1:]  # Skip header row if present
        now = datetime.now(timezone.utc)

        times = []
        kp_values = []

        for row in forecast_data:
            dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if dt > now:
                times.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                kp_values.append(float(row[1]))

        return (times, kp_values) if times and kp_values else ([], [])

    except Exception as e:
        print(f"[ERROR] Failed to get hourly forecast: {e}")
        return [], []


def get_long_term_forecast():
    """
    Fetch 27-day Kp index forecast from NOAA and extract daily max values.

    Returns:
        tuple: (dates, kp_values)
            - dates (list of str): Day & month labels
            - kp_values (list of float): Largest daily Kp values
    """
    try:
        response = requests.get(LONG_TERM_FORECAST_API, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()

        dates = []
        kp_values = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 6 and parts[0].isdigit():
                try:
                    date_str = f"{parts[2]} {parts[1]}"
                    kp = float(parts[5])
                    dates.append(date_str)
                    kp_values.append(kp)
                except ValueError:
                    # Skip malformed numeric values
                    continue

        return dates, kp_values

    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch long-term forecast: {e}")
        return [], []


# ====================================
# PLOTTING FORECAST CHARTS
# ====================================
def plot_3_day_forecast_chart(self, times, kp_values):
    """
    Plot 3-day hourly Kp index forecast as color-coded bar chart.

    Args:
        self: AuroraTrackerApp instance (for calling _draw_forecast_chart)
        times (list of str): Timestamps in UTC
        kp_values (list of float): Kp values for each timestamp
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    # Prepare data
    kp_values_float = [float(kp) for kp in kp_values]
    times_fmt = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S').strftime('%d %b %H:%M') for t in times]
    colors = [get_kp_color(kp) for kp in kp_values_float]

    # Plot bars
    bars = ax.bar(times_fmt, kp_values_float, color=colors)

    # Annotate bars
    ax.bar_label(bars, labels=[f"{kp:.2f}" for kp in kp_values_float], padding=3, fontsize=8)

    # Formatting
    ax.set_title("3-Day Kp Forecast")
    ax.set_ylabel("Kp Index")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylim(0, 9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
    ax.set_xticks(times_fmt[::max(1, len(times_fmt)//10)])
    ax.tick_params(axis='x', rotation=45)

    # Embed chart into GUI
    self._draw_forecast_chart(fig)
    plt.close(fig)


def plot_long_term_forecast_chart(self, date_labels, kp_values):
    """
    Plot 27-day daily max Kp index forecast as color-coded bar chart.

    Args:
        self: AuroraTrackerApp instance (for calling _draw_forecast_chart)
        date_labels (list of str): Date labels for x-axis
        kp_values (list of float): Max Kp values for each date
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    colors = [get_kp_color(kp) for kp in kp_values]
    bars = ax.bar(date_labels, kp_values, color=colors)

    # Annotate bars
    ax.bar_label(bars, labels=[f"{kp:.2f}" for kp in kp_values], padding=3, fontsize=7)

    # Formatting
    ax.set_title("27-Day Largest Kp Forecast")
    ax.set_ylabel("Kp Index")
    ax.set_xlabel("Date")
    ax.set_ylim(0, 9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
    ax.tick_params(axis='x', rotation=45)

    # Embed chart into GUI
    self._draw_forecast_chart(fig)
    plt.close(fig)
