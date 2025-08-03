# -*- coding: utf-8 -*-
"""
Handles fetching of aurora forecasts from short-term to long-term windows.
"""

import requests
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from aurora.libraries import get_kp_index
from src.aurora.kp_index import get_current_kp_index
from utils.chart_helpers import get_kp_color
from config import HOURLY_FORECAST_API, LONG_TERM_FORECAST_API


# def get_hourly_forecast():
#     """
#     Fetch NOAA 3-day Kp index forecast in 3-hour intervals.

#     Returns:
#         str: Formatted Kp forecast as a human-readable string.
#     """

#     try:
#         response = requests.get(HOURLY_FORECAST_API, timeout=10)
#         response.raise_for_status()
#         data = response.json()

#         forecast_data = data[1:]

#         now = datetime.now(timezone.utc)
#         lines = []
#         for row in forecast_data:
#             time_utc, kp_str = row[0], row[1]
#             dt = datetime.strptime(time_utc, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

#             if dt > now:
#                 lines.append(f"{dt.strftime('%Y-%m-%d %H:%M')} UTC — Kp Index: {kp_str}")

#         return "\n".join(lines)

#     except Exception as e:
#         print(f"[ERROR] Failed to fetch Kp forecast: {e}")
#         return f"Unavailable: {e}"


def get_hourly_forecast():
    """
    Fetch Kp index forecast in 3-hour intervals for the next 72 hours.

    Returns:
        list of tuples: (timestamp, kp_value) for plotting and display.
    """
    try:
        response = requests.get(HOURLY_FORECAST_API, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecast_data = data[1:]

        now = datetime.now(timezone.utc)

        times = []
        kp_values = []

        for row in forecast_data:

            dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

            if dt > now:
                 times.append(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}")
                 kp_values.append(float(row[1]))

        if not times or not kp_values:
            return [], []

        return times, kp_values

    except Exception as e:
        print(f"[ERROR] Failed to get hourly forecast: {e}")
        return [], []


# def get_long_term_forecast():
#     """
#     Fetches and parses the 27-day NOAA outlook to extract 'Largest Kp Index' values
#     only for today and future dates.

#     Returns:
#         str: A formatted string of dates and corresponding Largest Kp Index values.
#     """

#     try:
#         response = requests.get(LONG_TERM_FORECAST_API, timeout=10)
#         response.raise_for_status()
#         lines = response.text.splitlines()

#         forecast_lines = []
#         today = datetime.now(timezone.utc)

#         # Find lines that begin with a valid date format and extract the 6th value (Largest Kp Index)
#         for line in lines:
#             parts = line.strip().split()
#             if len(parts) >= 6 and parts[0].isdigit() and parts[1].isalpha() and len(parts[1]) == 3:
#                 try:
#                     # parts: [year, month_abbr, day, ...]
#                     date_str = f"{parts[0]} {parts[1]} {parts[2]}"

#                     # parse date with format "YYYY Mon DD"
#                     date_obj = datetime.strptime(date_str, "%Y %b %d").replace(tzinfo=timezone.utc)

#                     if date_obj >= today:
#                         largest_kp = parts[5]  # 6th item: Largest Kp Index
#                         forecast_lines.append(f"{date_obj.strftime('%Y-%m-%d')}: Kp {largest_kp}")
#                 except (IndexError, ValueError):
#                     continue

#         if not forecast_lines:
#             return "Unavailable: No Kp index data found for today or future dates."

#         return "\n".join(forecast_lines)

#     except requests.RequestException as e:
#         print(f"[ERROR] Failed to fetch long-term forecast: {e}")
#         return "Long-term forecast is currently unavailable."


def get_long_term_forecast():
    """
    Fetch 27-day Kp index forecast from NOAA and extract daily max values.

    Returns:
        list of tuples: (date, largest_kp_value) for chart display.
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
                    kp = float(parts[5])  # Largest Kp Index
                    dates.append(date_str)
                    kp_values.append(kp)
                except ValueError:
                    continue  # Skip invalid rows

        return dates, kp_values

    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch long-term forecast: {e}")
        return [], []



def plot_3_day_forecast_chart(self, times, kp_values):
    """Display 3-day forecast as a colored bar chart with value labels."""
    fig, ax = plt.subplots(figsize=(8, 4))

    # Convert Kp values to floats
    kp_values_float = [float(kp) for kp in kp_values]
    times_fmt = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S').strftime('%d %b %H:%M') for t in times]
    colors = [get_kp_color(kp) for kp in kp_values_float]

    # Create bars
    bars = ax.bar(times_fmt, kp_values_float, color=colors)

    # Add value labels above each bar
    ax.bar_label(bars, labels=[f"{kp:.2f}" for kp in kp_values_float], padding=3, fontsize=8)

    # Chart formatting
    ax.set_title("3-Day Kp Forecast")
    ax.set_ylabel("Kp Index")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylim(0, 9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
    ax.set_xticks(times_fmt[::max(1, len(times_fmt)//10)])
    ax.tick_params(axis='x', rotation=45)

    self._draw_forecast_chart(fig)


def plot_long_term_forecast_chart(self, date_labels, kp_values):
    """Display long-term forecast as a colored bar chart."""
    fig, ax = plt.subplots(figsize=(8, 4))

    colors = [get_kp_color(kp) for kp in kp_values]
    bars = ax.bar(date_labels, kp_values, color=colors)

    # Add value labels above each bar
    ax.bar_label(bars, labels=[f"{kp:.2f}" for kp in kp_values], padding=3, fontsize=7)

    ax.set_title("27-Day Largest Kp Forecast")
    ax.set_ylabel("Kp Index")
    ax.set_xlabel("Date")
    ax.set_ylim(0, 9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
    ax.tick_params(axis='x', rotation=45)

    self._draw_forecast_chart(fig)

