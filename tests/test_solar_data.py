# -*- coding: utf-8 -*-
"""
Unit tests for solar_data.py

Tests cover:
- get_solar_wind_data: valid responses, malformed/missing values, and network errors.
- download_sun_image: successful and failed downloads.
- get_sun_image_urls: structure validation of returned data.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from src.aurora import solar_data


class TestSolarData(unittest.TestCase):
    """Unit tests for functions in solar_data.py"""

    # -------------------------------
    # Tests for get_solar_wind_data
    # -------------------------------
    @patch("src.aurora.solar_data.requests.get")
    def test_get_solar_wind_data_success(self, mock_get):
        """Valid plasma & magnetic data should parse correctly."""
        recent_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

        # Plasma: timestamp, density, speed
        mock_plasma_resp = MagicMock()
        mock_plasma_resp.raise_for_status.return_value = None
        mock_plasma_resp.json.return_value = [
            ["time_tag", "density", "speed"],  # Header
            [recent_time, "5.2", "350.1"]
        ]

        # Magnetic: timestamp, ..., bz(index=3), ..., bt(index=6)
        mock_mag_resp = MagicMock()
        mock_mag_resp.raise_for_status.return_value = None
        mock_mag_resp.json.return_value = [
            ["time_tag", "col1", "col2", "bz", "col4", "col5", "bt"],  # Header
            [recent_time, "x", "x", "-2.3", "x", "x", "8.7"]
        ]

        mock_get.side_effect = [mock_plasma_resp, mock_mag_resp]

        plasma_times, speeds, densities, mag_times, bz_values, bt_values = solar_data.get_solar_wind_data()
        self.assertEqual(len(plasma_times), 1)
        self.assertEqual(len(speeds), 1)
        self.assertEqual(len(densities), 1)
        self.assertEqual(len(mag_times), 1)
        self.assertEqual(len(bz_values), 1)
        self.assertEqual(len(bt_values), 1)

    @patch("src.aurora.solar_data.requests.get")
    def test_get_solar_wind_data_handles_invalid_data(self, mock_get):
        """Malformed or old data should be filtered out."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

        # Plasma API returns old or invalid row
        mock_plasma_resp = MagicMock()
        mock_plasma_resp.raise_for_status.return_value = None
        mock_plasma_resp.json.return_value = [
            ["time_tag", "density", "speed"],
            [old_time, None, "400.0"],  # Invalid density
        ]

        # Magnetic API returns invalid row
        mock_mag_resp = MagicMock()
        mock_mag_resp.raise_for_status.return_value = None
        mock_mag_resp.json.return_value = [
            ["time_tag", "bt", "bz"],
            [old_time, None, None],  # Invalid values
        ]

        mock_get.side_effect = [mock_plasma_resp, mock_mag_resp]

        plasma_times, speeds, densities, mag_times, bz_values, bt_values = solar_data.get_solar_wind_data()
        self.assertEqual(plasma_times, [])
        self.assertEqual(speeds, [])
        self.assertEqual(densities, [])
        self.assertEqual(mag_times, [])
        self.assertEqual(bz_values, [])
        self.assertEqual(bt_values, [])

    @patch("src.aurora.solar_data.requests.get")
    def test_get_solar_wind_data_network_failure(self, mock_get):
        """Network failures should return empty lists."""
        mock_get.side_effect = Exception("Network error")
        result = solar_data.get_solar_wind_data()
        self.assertEqual(result, ([], [], [], [], [], []))

    # -------------------------------
    # Tests for download_sun_image
    # -------------------------------
    @patch("src.aurora.solar_data.requests.get")
    def test_download_sun_image_success(self, mock_get):
        """Successful image download should save file."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.content = b"fake_image_data"
        mock_get.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = solar_data.download_sun_image("test_image", "http://fakeurl", save_dir=Path(tmpdir))
            self.assertTrue(save_path.exists())
            self.assertTrue(save_path.name.endswith(".jpg"))

    @patch("src.aurora.solar_data.requests.get")
    def test_download_sun_image_failure(self, mock_get):
        """Download errors should return None."""
        mock_get.side_effect = Exception("Download error")
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = solar_data.download_sun_image("test_image", "http://fakeurl", save_dir=Path(tmpdir))
            self.assertIsNone(save_path)

    # -------------------------------
    # Tests for get_sun_image_urls
    # -------------------------------
    def test_get_sun_image_urls_structure(self):
        """Ensure URLs list has correct format."""
        urls = solar_data.get_sun_image_urls()
        self.assertIsInstance(urls, list)
        self.assertTrue(all(isinstance(item, list) and len(item) == 2 for item in urls))
        self.assertGreater(len(urls), 5)  # Expect several entries


if __name__ == "__main__":
    unittest.main()
