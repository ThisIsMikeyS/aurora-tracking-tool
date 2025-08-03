"""
Unit tests for viewer_ranker.py

Validates:
- Geographic distance calculations (haversine function)
- Ranked location visibility scoring based on geomagnetic activity indices

Test framework:
- Uses unittest with patching for external dependencies
"""

import unittest
from unittest.mock import patch
import math

# Import module under test
from src.aurora import viewer_ranker


class TestViewerRanker(unittest.TestCase):
    """Unit tests for viewer_ranker module."""

    # ============================================================
    # Tests for haversine() function
    # ============================================================
    
    def test_haversine_zero_distance(self):
        """Distance between identical points should be 0 km."""
        distance = viewer_ranker.haversine(0, 0, 0, 0)
        self.assertAlmostEqual(distance, 0.0, places=5)

    def test_haversine_known_distance(self):
        """Distance between known coordinates should match expected (quarter of Earth)."""
        distance = viewer_ranker.haversine(0, 0, 0, 90)
        expected_distance = math.pi / 2 * 6371  # Quarter circumference of Earth
        self.assertAlmostEqual(distance, expected_distance, delta=10)

    def test_haversine_opposite_points(self):
        """Antipodal points should be approximately half the Earth's circumference."""
        distance = viewer_ranker.haversine(0, 0, 0, 180)
        expected_distance = math.pi * 6371  # Half circumference of Earth
        self.assertAlmostEqual(distance, expected_distance, delta=10)

    # ============================================================
    # Tests for get_top_locations() function
    # ============================================================
    
    @patch("src.aurora.viewer_ranker.get_user_location")
    @patch("src.aurora.viewer_ranker.get_current_kp_index")
    def test_get_top_locations_basic_sorting(self, mock_kp, mock_loc):
        """Locations should be sorted in descending order by score."""
        mock_loc.return_value = {"latitude": 65.0, "longitude": 25.0}
        mock_kp.return_value = 5

        ranked_locations = viewer_ranker.get_top_locations()
        self.assertIsInstance(ranked_locations, list)
        self.assertGreater(len(ranked_locations), 0)

        # Ensure sorting is in descending order
        scores = [loc["score"] for loc in ranked_locations]
        self.assertEqual(scores, sorted(scores, reverse=True))

    @patch("src.aurora.viewer_ranker.get_user_location")
    @patch("src.aurora.viewer_ranker.get_current_kp_index")
    def test_get_top_locations_high_kp_visibility(self, mock_kp, mock_loc):
        """High Kp index should result in 'High' visibility for most locations."""
        mock_loc.return_value = {"latitude": 65.0, "longitude": 25.0}
        mock_kp.return_value = 9  # Very high activity

        ranked_locations = viewer_ranker.get_top_locations()
        visibilities = [loc["visibility"] for loc in ranked_locations]
        self.assertIn("High", visibilities)

    @patch("src.aurora.viewer_ranker.get_user_location")
    @patch("src.aurora.viewer_ranker.get_current_kp_index")
    def test_get_top_locations_low_kp_visibility(self, mock_kp, mock_loc):
        """Low Kp index should mark far-south locations as 'Low' visibility."""
        mock_loc.return_value = {"latitude": 65.0, "longitude": 25.0}
        mock_kp.return_value = 0  # Very low activity

        ranked_locations = viewer_ranker.get_top_locations()
        visibilities = [loc["visibility"] for loc in ranked_locations]
        self.assertIn("Low", visibilities)

    @patch("src.aurora.viewer_ranker.get_user_location", return_value=None)
    @patch("src.aurora.viewer_ranker.get_current_kp_index", return_value=5)
    def test_get_top_locations_no_user_location(self, mock_kp, mock_loc):
        """Should return empty list if user location is unavailable."""
        ranked_locations = viewer_ranker.get_top_locations()
        self.assertEqual(ranked_locations, [])

    @patch("src.aurora.viewer_ranker.get_user_location", return_value={"latitude": 65.0, "longitude": 25.0})
    @patch("src.aurora.viewer_ranker.get_current_kp_index", return_value=None)
    def test_get_top_locations_no_kp_value(self, mock_kp, mock_loc):
        """Should return empty list if Kp index is unavailable."""
        ranked_locations = viewer_ranker.get_top_locations()
        self.assertEqual(ranked_locations, [])


if __name__ == "__main__":
    unittest.main()
