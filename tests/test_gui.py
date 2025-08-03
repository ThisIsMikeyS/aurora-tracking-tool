# -*- coding: utf-8 -*-
"""
Unit tests for gui.py (AuroraTrackerApp).

Covers:
- KP index retrieval success/failure
- Aurora overlay image success/failure
- Short-term (hourly) forecast success/failure
- Long-term forecast success/failure
- Solar wind graphs success/failure

Tkinter GUI elements and message boxes are mocked to prevent actual windows/dialogs.
"""

import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import src.gui as gui


@patch("src.gui.messagebox.showerror", MagicMock())
@patch("src.gui.messagebox.showinfo", MagicMock())
class TestAuroraTrackerApp(unittest.TestCase):
    """Unit tests for AuroraTrackerApp GUI methods."""

    # ----------------------------------------------------------------------
    # Class Setup / Teardown
    # ----------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        """Create Tk root once (withdrawn to avoid popups)."""
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        """Destroy root after all tests complete."""
        cls.root.destroy()

    def setUp(self):
        """Initialize the app for each test."""
        self.app = gui.AuroraTrackerApp(self.root)

    # ----------------------------------------------------------------------
    # KP Index Tests
    # ----------------------------------------------------------------------

    @patch("src.gui.get_current_kp_index", side_effect=Exception("fail"))
    def test_update_kp_index_failure(self, _):
        """Should show error dialog if KP index retrieval fails."""
        self.app.update_kp_index()
        gui.messagebox.showerror.assert_called()

    @patch("src.gui.get_current_kp_index", return_value=4.5)
    def test_update_kp_index_success(self, _):
        """Label should update correctly on successful KP index retrieval."""
        self.app.update_kp_index()
        self.assertIn("4.5", self.app.kp_label.cget("text"))

    # ----------------------------------------------------------------------
    # Aurora Overlay Tests
    # ----------------------------------------------------------------------

    @patch("src.gui.ImageTk.PhotoImage", return_value="mock_img")
    @patch("src.gui.Image.open", return_value=MagicMock())
    @patch("src.gui.generate_aurora_map", return_value="aurora_map.png")
    def test_show_aurora_overlay_success(self, mock_map, mock_open, mock_photo):
        """Aurora overlay should display image when map generation succeeds."""
        self.app.show_aurora_overlay()

        mock_map.assert_called_once()
        mock_open.assert_called_once_with("aurora_map.png")
        mock_photo.assert_called_once()
        self.assertTrue(hasattr(self.app.map_canvas, "image") or mock_photo.called)

    @patch("src.gui.generate_aurora_map", return_value=None)
    def test_show_aurora_overlay_failure(self, _):
        """Error dialog should appear if aurora map generation fails."""
        self.app.show_aurora_overlay()
        gui.messagebox.showerror.assert_called()

    # ----------------------------------------------------------------------
    # Short-Term Forecast Tests
    # ----------------------------------------------------------------------

    @patch("src.gui.get_hourly_forecast", return_value=([], []))
    def test_show_hourly_forecast_no_data(self, _):
        """Error dialog should appear if short-term forecast returns no data."""
        self.app.show_hourly_forecast()
        gui.messagebox.showerror.assert_called()

    @patch("src.gui.plot_3_day_forecast_chart")
    @patch("src.gui.get_hourly_forecast", return_value=(["2025-07-28"], [4]))
    def test_show_hourly_forecast_success(self, mock_forecast, mock_plot):
        """Chart should be plotted when short-term forecast returns valid data."""
        self.app.show_hourly_forecast()
        mock_plot.assert_called_once()

    # ----------------------------------------------------------------------
    # Long-Term Forecast Tests
    # ----------------------------------------------------------------------

    @patch("src.gui.get_long_term_forecast", return_value=([], []))
    def test_show_long_forecast_no_data(self, _):
        """Error dialog should appear if long-term forecast returns no data."""
        self.app.show_long_forecast()
        gui.messagebox.showerror.assert_called()

    @patch("src.gui.plot_long_term_forecast_chart")
    @patch("src.gui.get_long_term_forecast", return_value=(["Day1"], [5]))
    def test_show_long_forecast_success(self, mock_forecast, mock_plot):
        """Chart should be plotted when long-term forecast returns valid data."""
        self.app.show_long_forecast()
        mock_plot.assert_called_once()

    # ----------------------------------------------------------------------
    # Solar Wind Data Tests
    # ----------------------------------------------------------------------

    @patch("src.gui.get_solar_wind_data", return_value=([], [], [], [], [], []))
    def test_show_solar_wind_graphs_no_data(self, _):
        """Error dialog should appear if solar wind data retrieval fails."""
        self.app.show_solar_wind_graphs()
        gui.messagebox.showerror.assert_called()

    @patch.object(gui.AuroraTrackerApp, "_draw_solar_charts")
    @patch("src.gui.get_solar_wind_data", return_value=(
        ["t1", "t2"], [300, 320], [5, 6], ["t1", "t2"], [1, -1], [2, 3]
    ))
    def test_show_solar_wind_graphs_success(self, mock_data, mock_draw):
        """Charts should be drawn when solar wind data retrieval succeeds."""
        self.app.show_solar_wind_graphs()
        mock_draw.assert_called_once()


if __name__ == "__main__":
    unittest.main()
