"""
Unit tests for aurora_map_overlay.py

Covers:
- Robust fetching of aurora forecast data (with error handling).
- Behavior when coordinate data is missing or valid.
- Ensures map generation completes regardless of dataset size.
Uses unittest with mocks for network requests to avoid real API calls.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src to Python path for direct imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.aurora import aurora_map_overlay as amo
from config import MAP_DIR

# Path for test-generated image
TEST_IMAGE_PATH = MAP_DIR / "test_aurora_map.png"


class TestAuroraMapOverlay(unittest.TestCase):
    """Unit tests for aurora_map_overlay functions."""

    # ----------------------------------------------------------------------
    # fetch_aurora_data() Tests
    # ----------------------------------------------------------------------

    @patch("aurora.aurora_map_overlay.requests.get")
    def test_fetch_aurora_data_success(self, mock_get):
        """
        Test successful data retrieval.
        Mock returns coordinates in expected structure.
        """
        mock_resp = MagicMock()
        mock_resp.json.return_value = [[0, 50, 20], [10, 60, 30]]  # Matches expected structure
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        coords = amo.fetch_aurora_data()
        self.assertIsInstance(coords, list)

    @patch("aurora.aurora_map_overlay.requests.get", side_effect=Exception("Network error"))
    def test_fetch_aurora_data_network_error(self, mock_get):
        """
        Test network failure handling.
        Expected: Empty list returned.
        """
        coords = amo.fetch_aurora_data()
        self.assertEqual(coords, [])

    # ----------------------------------------------------------------------
    # generate_aurora_map() Tests
    # ----------------------------------------------------------------------

    @patch("aurora.aurora_map_overlay.fetch_aurora_data", return_value=[])
    def test_generate_map_empty_data(self, mock_fetch):
        """
        Test map generation with empty data.
        Expected: Function still returns the output image path.
        """
        result = amo.generate_aurora_map(TEST_IMAGE_PATH)
        self.assertEqual(result, TEST_IMAGE_PATH)

    @patch("aurora.aurora_map_overlay.fetch_aurora_data", return_value=[(0, 80, 50)])
    def test_generate_map_valid_data(self, mock_fetch):
        """
        Test map generation with valid data.
        Expected: Function returns the output image path.
        """
        result = amo.generate_aurora_map(TEST_IMAGE_PATH)
        self.assertEqual(result, TEST_IMAGE_PATH)


if __name__ == "__main__":
    unittest.main()
