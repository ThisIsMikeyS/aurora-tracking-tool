"""
Unit tests for swpc_map.py
Covers download_swpc_map() and get_latest_map_timestamp().
Ensures correct behavior for successful downloads, network errors, 
directory creation, and timestamp formatting.
"""

import unittest
import io
import requests
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from pathlib import Path

# Import the module under test
import src.aurora.swpc_map as swpc_map


class TestSWPCMap(unittest.TestCase):

    @patch("src.aurora.swpc_map.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_success(self, mock_file, mock_get):
        """Test successful download of SWPC map."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"datachunk"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        path = swpc_map.download_swpc_map()

        # Check requests.get called with correct URL
        mock_get.assert_called_once_with(swpc_map.SWPC_IMAGE_URL, stream=True, timeout=10)
        # Ensure file write was attempted
        mock_file.assert_called_once()
        self.assertEqual(path, swpc_map.IMAGE_PATH)

    @patch("src.aurora.swpc_map.requests.get", side_effect=requests.RequestException("Network error"))
    def test_download_network_error(self, mock_get):
        """Test download returns None when network fails."""
        result = swpc_map.download_swpc_map()
        self.assertIsNone(result)


    @patch("src.aurora.swpc_map.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.aurora.swpc_map.Path.mkdir")
    def test_directory_creation(self, mock_mkdir, mock_file, mock_get):
        """Test that directory is created if missing."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        swpc_map.download_swpc_map()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_latest_map_timestamp_format(self):
        """Test timestamp format correctness."""
        ts = swpc_map.get_latest_map_timestamp()
        # Validate format: 'YYYY-MM-DD HH:MM:SS UTC'
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            self.fail(f"Timestamp format invalid: {ts}")


if __name__ == "__main__":
    unittest.main()
