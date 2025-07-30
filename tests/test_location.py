# -*- coding: utf-8 -*-
"""
Unit tests for location.py
Covers success, missing data, invalid JSON, HTTP error, and network failures.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests
from src.aurora import location  # Adjust path if needed


class TestLocation(unittest.TestCase):

    @patch("src.aurora.location.requests.get")
    def test_get_user_location_success(self, mock_get):
        """Test normal successful API response with full data."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "city": "Troms\u00F8",
            "regionName": "Troms",
            "country": "Norway",
            "lat": 69.6496,
            "lon": 18.9560
        }
        mock_get.return_value = mock_response

        result = location.get_user_location()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["city"], "Troms\u00F8")
        self.assertEqual(result["country"], "Norway")
        self.assertAlmostEqual(result["latitude"], 69.6496)

    @patch("src.aurora.location.requests.get")
    def test_get_user_location_missing_fields(self, mock_get):
        """Test API returns missing fields. Should still return dict with None values."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}  # Missing everything
        mock_get.return_value = mock_response

        result = location.get_user_location()
        self.assertIsInstance(result, dict)
        self.assertIsNone(result["city"])
        self.assertIsNone(result["latitude"])

    @patch("src.aurora.location.requests.get")
    def test_get_user_location_invalid_json(self, mock_get):
        """Test API returns invalid JSON. Should return None gracefully."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = location.get_user_location()
        self.assertIsNone(result)

    @patch("src.aurora.location.requests.get")
    def test_get_user_location_http_error(self, mock_get):
        """Test HTTP error during request."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_get.return_value = mock_response

        result = location.get_user_location()
        self.assertIsNone(result)

    @patch("src.aurora.location.requests.get")
    def test_get_user_location_network_error(self, mock_get):
        """Test network error (timeout, connection error, etc.)."""
        mock_get.side_effect = requests.RequestException("Network failure")

        result = location.get_user_location()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
