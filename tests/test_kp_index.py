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
import src.aurora.kp_index as kp_index


class TestKpIndex(unittest.TestCase):
    """Unit tests for functions in kp_index.py"""

    # ----------------------------------------------------------------------
    # Tests for get_current_kp_index
    # ----------------------------------------------------------------------

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_success(self, mock_get):
        """Should return latest valid Kp value as float when valid data exists."""
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
        """Should return 'Unavailable' string when no data is returned."""
        mock_get.return_value = ([], [], [])
        result = kp_index.get_current_kp_index()

        self.assertIsInstance(result, str)
        self.assertIn("Unavailable", result)

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_all_future_times(self, mock_get):
        """Should return 'Unavailable' if all returned times are in the future."""
        future_time = (datetime.now(timezone.utc)
                       .replace(hour=23, minute=0)
                       .strftime("%Y-%m-%dT%H:%M:%SZ"))

        mock_get.return_value = ([future_time], [5.0], ["ok"])
        result = kp_index.get_current_kp_index()

        self.assertIn("Unavailable", result)

    @patch("src.aurora.kp_index.getKpindex")
    def test_get_current_kp_index_exception(self, mock_get):
        """Should return 'Unavailable' if an exception occurs."""
        mock_get.side_effect = Exception("Network error")
        result = kp_index.get_current_kp_index()

        self.assertIn("Unavailable", result)

    # ----------------------------------------------------------------------
    # Tests for get_visibility_zone
    # ----------------------------------------------------------------------

    def test_get_visibility_zone_known_values(self):
        """Should return correct description for all Kp values 0-9."""
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
            9: "Mexico, North Africa"
        }

        for kp_value, expected_desc in expected_mapping.items():
            self.assertEqual(kp_index.get_visibility_zone(kp_value), expected_desc)

    def test_get_visibility_zone_none_value(self):
        """Should return 'Unknown' if Kp value is None."""
        self.assertEqual(kp_index.get_visibility_zone(None), "Unknown")

    def test_get_visibility_zone_out_of_range(self):
        """Should return 'Unavailable' if Kp value is outside 0-9."""
        self.assertEqual(kp_index.get_visibility_zone(15), "Unavailable")
        self.assertEqual(kp_index.get_visibility_zone(-1), "Unavailable")


if __name__ == "__main__":
    unittest.main()
