# -*- coding: utf-8 -*-
"""
Unit tests for solar_data.py
Covers:
- get_solar_wind_data (valid, missing data, invalid formats, exception handling)
- download_sun_image (valid, exception handling)
- get_sun_image_urls (structure correctness)
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import os

from src.aurora import solar_data


class TestSolarData(unittest.TestCase):

    @patch("src.aurora.solar_data.requests.get")
    def test_get_solar_wind_data_success(self, mock_get):
        """Test normal successful retrieval of solar wind data."""
        recent_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

        # Plasma: [timestamp, density, speed]
        mock_plasma_resp = MagicMock()
        mock_plasma_resp.raise_for_status.return_value = None
        mock_plasma_resp.json.return_value = [
            ["time_tag", "density", "speed"],  # header
            [recent_time, "5.2", "350.1"]
        ]

        # Magnetic: [timestamp, ..., bz(index=3), ..., bt(index=6)]
        mock_mag_resp = MagicMock()
        mock_mag_resp.raise_for_status.return_value = None
        mock_mag_resp.json.return_value = [
            ["time_tag", "col1", "col2", "bz", "col4", "col5", "bt"],  # header
            [recent_time, "x", "x", "-2.3", "x", "x", "8.7"]
        ]

        mock_get.side_effect = [mock_plasma_resp, mock_mag_resp]

        plasma_times, speeds, densities, mag_times, bz_values, bt_values = solar_data.get_solar_wind_data()
    
        # Validate output
        self.assertEqual(len(plasma_times), 1)
        self.assertEqual(len(speeds), 1)
        self.assertEqual(len(densities), 1)
        self.assertEqual(len(mag_times), 1)
        self.assertEqual(len(bz_values), 1)
        self.assertEqual(len(bt_values), 1)


    @patch("src.aurora.solar_data.requests.get")
    def test_get_solar_wind_data_handles_invalid_data(self, mock_get):
        """Test handling of malformed or missing rows in solar wind data."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

        # Plasma API with old data (should be filtered)
        mock_plasma_resp = MagicMock()
        mock_plasma_resp.raise_for_status.return_value = None
        mock_plasma_resp.json.return_value = [
            ["time_tag", "density", "speed"],
            [old_time, None, "400.0"],  # invalid density
        ]

        # Magnetic API with missing values
        mock_mag_resp = MagicMock()
        mock_mag_resp.raise_for_status.return_value = None
        mock_mag_resp.json.return_value = [
            ["time_tag", "bt", "bz"],
            [old_time, None, None],  # invalid
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
        """Test that network failure returns empty lists."""
        mock_get.side_effect = Exception("Network error")
        result = solar_data.get_solar_wind_data()
        self.assertEqual(result, ([], [], [], [], [], []))

    @patch("src.aurora.solar_data.requests.get")
    def test_download_sun_image_success(self, mock_get):
        """Test successful download of a sun image."""
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
        """Test download failure returns None."""
        mock_get.side_effect = Exception("Download error")
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = solar_data.download_sun_image("test_image", "http://fakeurl", save_dir=Path(tmpdir))
            self.assertIsNone(save_path)

    def test_get_sun_image_urls_structure(self):
        """Ensure get_sun_image_urls returns expected structure."""
        urls = solar_data.get_sun_image_urls()
        self.assertIsInstance(urls, list)
        self.assertTrue(all(isinstance(item, list) and len(item) == 2 for item in urls))
        self.assertGreater(len(urls), 5)  # At least several URLs


if __name__ == "__main__":
    unittest.main()
