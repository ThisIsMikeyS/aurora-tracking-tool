"""
Image downloading and formatting utilities for Aurora Tracker.
"""

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
