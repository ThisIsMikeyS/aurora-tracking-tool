# -*- coding: utf-8 -*-
"""
Unit tests for webcams.py

Covers:
- Darkness detection (`is_dark`) for normal, polar day, and polar night cases.
- Webcam sorting by visibility, location, and country.
- Handling of errors and edge cases.

Mocks:
- `get_current_kp_index` for Kp values.
- `is_dark` and `datetime` for consistent time checks.
- Astral dawn/dusk calculations for predictable results.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.aurora import webcams


class TestWebcams(unittest.TestCase):
    """Unit tests for webcams module."""

    # -------------------------------
    # Sorting: Location & Country
    # -------------------------------
    def test_location_sorted_order(self):
        """Webcams should be sorted alphabetically by location name."""
        sorted_cams = webcams.get_live_webcams_location_sorted()
        locations = [cam["location"] for cam in sorted_cams]
        self.assertEqual(locations, sorted(locations))

    def test_country_sorted_order(self):
        """Webcams should be sorted by country, then location within each country."""
        sorted_cams = webcams.get_live_webcams_country_sorted()
        country_location_pairs = [(cam["country"], cam["location"]) for cam in sorted_cams]
        self.assertEqual(country_location_pairs, sorted(country_location_pairs))

    # -------------------------------
    # Sorting: Best Visibility
    # -------------------------------
    @patch("src.aurora.webcams.is_dark", return_value=True)
    @patch("src.aurora.webcams.get_current_kp_index", return_value=5)
    def test_best_sorted_dark_high_kp(self, mock_kp, mock_dark):
        """Dark locations with high Kp should be prioritized."""
        sorted_cams = webcams.get_live_webcams_best_sorted()
        self.assertIsInstance(sorted_cams, list)
        self.assertIn("score", sorted_cams[0])

    @patch("src.aurora.webcams.is_dark", return_value=False)
    @patch("src.aurora.webcams.get_current_kp_index", return_value=0)
    def test_best_sorted_bright_low_kp(self, mock_kp, mock_dark):
        """Bright locations with low Kp should still return a sorted list."""
        sorted_cams = webcams.get_live_webcams_best_sorted()
        self.assertTrue(all("score" in cam for cam in sorted_cams))

    @patch("src.aurora.webcams.is_dark", side_effect=Exception("Astral error"))
    @patch("src.aurora.webcams.get_current_kp_index", return_value=4)
    def test_best_sorted_handles_darkness_error(self, mock_kp, mock_dark):
        """Sorting should still complete if is_dark() raises an error."""
        sorted_cams = webcams.get_live_webcams_best_sorted()
        self.assertIsInstance(sorted_cams, list)

    # -------------------------------
    # Darkness Detection
    # -------------------------------
    @patch("src.aurora.webcams.sun")
    @patch("src.aurora.webcams.LocationInfo")
    def test_is_dark_true_case(self, mock_loc, mock_sun):
        """Time after dusk or before dawn should return True (dark)."""
        mock_sun.return_value = {
            "dawn": datetime(2025, 7, 28, 2),
            "dusk": datetime(2025, 7, 28, 5)
        }
        test_time = datetime(2025, 7, 28, 6)  # After dusk

        with patch("src.aurora.webcams.datetime", wraps=datetime) as mock_datetime:
            mock_datetime.now.return_value = test_time
            result = webcams.is_dark(60, 20, "Troms\u00F8")
        self.assertTrue(result)

    @patch("src.aurora.webcams.sun")
    @patch("src.aurora.webcams.LocationInfo")
    def test_is_dark_false_case(self, mock_loc, mock_sun):
        """Time between dawn and dusk should return False (bright)."""
        mock_sun.return_value = {
            "dawn": datetime(2025, 7, 28, 2),
            "dusk": datetime(2025, 7, 28, 5)
        }
        test_time = datetime(2025, 7, 28, 3)  # Between dawn & dusk

        with patch("src.aurora.webcams.datetime", wraps=datetime) as mock_datetime:
            mock_datetime.now.return_value = test_time
            result = webcams.is_dark(60, 20, "Troms\u00F8")
        self.assertFalse(result)

    @patch("src.aurora.webcams.sun", side_effect=ValueError("degrees above horizon"))
    def test_is_dark_sun_never_rises(self, mock_sun):
        """If sun never rises, location should be considered dark."""
        result = webcams.is_dark(70, 20, "Troms\u00F8")
        self.assertTrue(result)

    @patch("src.aurora.webcams.sun", side_effect=ValueError("degrees below horizon"))
    def test_is_dark_sun_never_sets(self, mock_sun):
        """If sun never sets, location should be considered bright."""
        result = webcams.is_dark(70, 20, "Troms\u00F8")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
