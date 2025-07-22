# -*- coding: utf-8 -*-
"""
webcams.py
Returns a curated list of live aurora webcam URLs.
"""

def get_live_webcams():
    """Returns a list of popular Northern Lights webcam streams."""
    return [
        {"location": "Tromsø, Norway", "url": "https://weather.cs.uit.no/"},
        {"location": "Abisko, Sweden", "url": "https://lightsoverlapland.com/webcam/"},
        {"location": "Kilpisjärvi, Finland", "url": "https://www.youtube.com/watch?v=ccTVAhJU5lg"},
        {"location": "Fairbanks, Alaska", "url": "https://www.youtube.com/watch?v=O52zDyxg5QI"},
        {"location": "Yellowknife, Canada", "url": "https://auroramax.com/live"},
    ]
