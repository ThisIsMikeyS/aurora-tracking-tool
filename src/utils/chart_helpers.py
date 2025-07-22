"""
Image downloading and formatting utilities for Aurora Tracker.
"""

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def get_kp_color(kp):
    """Return color based on Kp index value."""
    if not isinstance(kp, float):
        kp = float(kp)

    if kp < 3.0:
        return 'green'
    elif 3.0 <= kp < 4.0:
        return 'yellow'
    elif 4.0 <= kp < 6.0:
        return 'orange'
    elif 6.0 <= kp < 8.0:
        return 'red'
    else:
        return 'darkred'


def plot_line_chart(title, x_data, y_data, y_label):
    """Generate a single matplotlib figure for a time series line chart."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x_data, y_data, linestyle='-', marker='', color='red')

    ax.set_title(title)
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel(y_label)
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax.tick_params(axis='x', rotation=45)

    return fig


