# -*- coding: utf-8 -*-
"""
Unit tests for swpc_map.py

Covers:
- download_swpc_map: Successful download, network error handling, and directory creation.
- get_latest_map_timestamp: Correct timestamp formatting.

Uses unittest with mocks to avoid real HTTP requests and file writes.
"""

import unittest
import requests
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

import src.aurora.swpc_map as swpc_map


class TestSWPCMap(unittest.TestCase):
    """Unit tests for SWPC map download and timestamp utilities."""

    # -------------------------
    # Tests for download_swpc_map
    # -------------------------
    @patch("src.aurora.swpc_map.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_success(self, mock_file, mock_get):
        """Successful download should save file and return path."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"datachunk"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        path = swpc_map.download_swpc_map()

        # Verify HTTP request
        mock_get.assert_called_once_with(swpc_map.SWPC_IMAGE_URL, stream=True, timeout=10)
        # Verify file writing
        mock_file.assert_called_once()
        self.assertEqual(path, swpc_map.IMAGE_PATH)

    @patch("src.aurora.swpc_map.requests.get", side_effect=requests.RequestException("Network error"))
    def test_download_network_error(self, mock_get):
        """Network error should cause function to return None."""
        result = swpc_map.download_swpc_map()
        self.assertIsNone(result)

    @patch("src.aurora.swpc_map.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.aurora.swpc_map.Path.mkdir")
    def test_directory_creation_if_missing(self, mock_mkdir, mock_file, mock_get):
        """Missing directory should be created before saving file."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        swpc_map.download_swpc_map()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # -------------------------
    # Tests for get_latest_map_timestamp
    # -------------------------
    def test_get_latest_map_timestamp_format(self):
        """Returned timestamp should match expected format."""
        ts = swpc_map.get_latest_map_timestamp()
        try:
            datetime.strptime(ts, "%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            self.fail(f"Timestamp format invalid: {ts}")


if __name__ == "__main__":
    unittest.main()
