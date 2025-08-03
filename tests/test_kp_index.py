# -*- coding: utf-8 -*-
"""
Unit tests for kp_index.py.
Covers:
- get_current_kp_index: normal operation, no data, invalid data, exception.
- get_visibility_zone: correct mapping for all Kp values, unknown Kp, and None.
"""

import unittest
from unittest.mock import patch
from datetime import datetime, timezone

# Import the module under test
import src.aurora.kp_index as kp_index


class TestKpIndex(unittest.TestCase):
    """Unit tests for kp_index.py"""

    # -------------------------
    # Tests for get_current_kp_index
    # -------------------------

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_success(self, mock_get):
        """Test normal case where valid times and Kp values are returned."""
        now = datetime.now(timezone.utc)
        times = [
            now.strftime("%Y-%m-%dT00:00:00Z"),
            now.strftime("%Y-%m-%dT03:00:00Z")
        ]
        kp_values = [2.0, 3.0]
        statuses = ["ok", "ok"]

        mock_get.return_value = (times, kp_values, statuses)
        result = kp_index.get_current_kp_index()
        self.assertIsInstance(result, float)
        self.assertEqual(result, 3.0)

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_no_data(self, mock_get):
        """Test case where getKpindex returns empty data."""
        mock_get.return_value = ([], [], [])
        result = kp_index.get_current_kp_index()
        self.assertIsInstance(result, str)
        self.assertIn("Unavailable", result)

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_all_future_times(self, mock_get):
        """Test case where all returned times are in the future."""
        future_time = (datetime.now(timezone.utc) + 
                       timezone.utc.utcoffset(datetime.now(timezone.utc))).strftime("%Y-%m-%dT23:00:00Z")
        mock_get.return_value = ([future_time], [5.0], ["ok"])
        result = kp_index.get_current_kp_index()
        self.assertIn("Unavailable", result)

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_exception(self, mock_get):
        """Test exception raised inside getKpindex is caught."""
        mock_get.side_effect = Exception("Network error")
        result = kp_index.get_current_kp_index()
        self.assertIn("Unavailable", result)

    # -------------------------
    # Tests for get_visibility_zone
    # -------------------------

    def test_get_visibility_zone_all_known_values(self):
        """Test mapping for all Kp values 0 to 9."""  # ASCII dash now
        expected_mapping = {
            0: "Very High Latitudes (e.g. North Pole)",
            1: "Arctic Circle (~66\u00B0)",
            2: "Iceland, Troms\u00F8",
            3: "Northern Scandinavia",
            4: "Southern Norway, Scotland",
            5: "UK, Germany, Canada border",
            6: "Central Europe, North USA",
            7: "France, New York",
            8: "Spain, California",
            9: "Mexico, North Africa",
        }
        for kp, desc in expected_mapping.items():
            self.assertEqual(kp_index.get_visibility_zone(kp), desc)


    def test_get_visibility_zone_none_value(self):
        """Test that None returns 'Unknown'."""
        self.assertEqual(kp_index.get_visibility_zone(None), "Unknown")

    def test_get_visibility_zone_unknown_kp(self):
        """Test that Kp outside 0 to 9 returns 'Unavailable'."""
        self.assertEqual(kp_index.get_visibility_zone(15), "Unavailable")
        self.assertEqual(kp_index.get_visibility_zone(-1), "Unavailable")


if __name__ == "__main__":
    unittest.main()
