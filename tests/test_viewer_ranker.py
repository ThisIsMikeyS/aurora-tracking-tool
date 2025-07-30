"""
Unit tests for the viewer_ranker.py
Validates geographic distance calculations and ranked location 
visibility scoring based on geomagnetic activity indices.
Uses unittest framework with mocking for external dependencies.
"""

import unittest
from unittest.mock import patch
import math

# Import module under test
from src.aurora import viewer_ranker


class TestViewerRanker(unittest.TestCase):
    """Unit tests for viewer_ranker module."""

    # ---------- Test haversine() ----------
    def test_haversine_zero_distance(self):
        """Distance between identical points should be 0."""
        d = viewer_ranker.haversine(0, 0, 0, 0)
        self.assertAlmostEqual(d, 0.0, places=5)

    def test_haversine_known_distance(self):
        """Distance between two known coordinates should match expected."""
        d = viewer_ranker.haversine(0, 0, 0, 90)  # quarter of Earth
        expected = math.pi / 2 * 6371
        self.assertAlmostEqual(d, expected, delta=10)

    def test_haversine_opposite_points(self):
        """Antipodal points (opposite sides of Earth) should be ~20037 km apart."""
        d = viewer_ranker.haversine(0, 0, 0, 180)
        expected = math.pi * 6371
        self.assertAlmostEqual(d, expected, delta=10)

    # ---------- Test get_top_locations() ----------
    @patch("src.aurora.viewer_ranker.get_user_location")
    @patch("src.aurora.viewer_ranker.get_current_kp_index")
    def test_get_top_locations_basic_sorting(self, mock_kp, mock_loc):
        """Locations should be sorted by score descending."""
        mock_loc.return_value = {"latitude": 65.0, "longitude": 25.0}
        mock_kp.return_value = 5

        ranked = viewer_ranker.get_top_locations()
        self.assertIsInstance(ranked, list)
        self.assertGreater(len(ranked), 0)
        # Ensure sorted by score descending
        scores = [loc["score"] for loc in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

    @patch("src.aurora.viewer_ranker.get_user_location")
    @patch("src.aurora.viewer_ranker.get_current_kp_index")
    def test_get_top_locations_high_kp_visibility(self, mock_kp, mock_loc):
        """High Kp should mark most locations as visible."""
        mock_loc.return_value = {"latitude": 65.0, "longitude": 25.0}
        mock_kp.return_value = 9  # Very high activity

        ranked = viewer_ranker.get_top_locations()
        visibilities = [loc["visibility"] for loc in ranked]
        self.assertIn("High", visibilities)

    @patch("src.aurora.viewer_ranker.get_user_location")
    @patch("src.aurora.viewer_ranker.get_current_kp_index")
    def test_get_top_locations_low_kp_visibility(self, mock_kp, mock_loc):
        """Low Kp should mark far south locations as Low visibility."""
        mock_loc.return_value = {"latitude": 65.0, "longitude": 25.0}
        mock_kp.return_value = 0  # Very low activity

        ranked = viewer_ranker.get_top_locations()
        visibilities = [loc["visibility"] for loc in ranked]
        self.assertIn("Low", visibilities)

    @patch("src.aurora.viewer_ranker.get_user_location", return_value=None)
    @patch("src.aurora.viewer_ranker.get_current_kp_index", return_value=5)
    def test_get_top_locations_no_user_location(self, mock_kp, mock_loc):
        """Should return empty list if user location is missing."""
        ranked = viewer_ranker.get_top_locations()
        self.assertEqual(ranked, [])

    @patch("src.aurora.viewer_ranker.get_user_location", return_value={"latitude": 65.0, "longitude": 25.0})
    @patch("src.aurora.viewer_ranker.get_current_kp_index", return_value=None)
    def test_get_top_locations_no_kp_value(self, mock_kp, mock_loc):
        """Should return empty list if Kp index is missing."""
        ranked = viewer_ranker.get_top_locations()
        self.assertEqual(ranked, [])


if __name__ == "__main__":
    unittest.main()
