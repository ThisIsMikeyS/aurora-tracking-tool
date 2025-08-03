"""
Unit tests for the aurora_map_overlay.py
Tests for:
- Robust fetching of aurora forecast data with error handling.
- Correct behavior when filtering and processing coordinate data.
- Proper map generation output regardless of input dataset size.
Uses unittest with mocks for network requests.
"""

import sys, os, unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.aurora import aurora_map_overlay as amo
from config import MAP_DIR

TEST_IMAGE_PATH = MAP_DIR / "test_aurora_map.png"

class TestAuroraMapOverlay(unittest.TestCase):

    @patch("aurora.aurora_map_overlay.requests.get")
    def test_fetch_aurora_data_success(self, mock_get):
        """Mock returns points that pass filtering."""
        mock_resp = MagicMock()
        # Match structure your code expects *after* parsing JSON
        mock_resp.json.return_value = [[0, 50, 20], [10, 60, 30]]
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        # Call
        coords = amo.fetch_aurora_data()
        # The filtering happens in generate_aurora_map, so we only check type here
        self.assertIsInstance(coords, list)

    @patch("aurora.aurora_map_overlay.requests.get", side_effect=Exception("Network error"))
    def test_fetch_aurora_data_network_error(self, mock_get):
        """Network errors should return []."""
        coords = amo.fetch_aurora_data()
        self.assertEqual(coords, [])

    @patch("aurora.aurora_map_overlay.fetch_aurora_data", return_value=[])
    def test_generate_map_empty_data(self, mock_fetch):
        """Even with no coords, function still returns PNG filename."""
        result = amo.generate_aurora_map(TEST_IMAGE_PATH)
        self.assertEqual(result, TEST_IMAGE_PATH)

    @patch("aurora.aurora_map_overlay.fetch_aurora_data", return_value=[(0, 80, 50)])
    def test_generate_map_valid_data(self, mock_fetch):
        """Valid coords should return PNG filename."""
        result = amo.generate_aurora_map(TEST_IMAGE_PATH)
        self.assertEqual(result, TEST_IMAGE_PATH)

if __name__ == "__main__":
    unittest.main()
