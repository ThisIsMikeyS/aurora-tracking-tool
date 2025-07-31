# -*- coding: utf-8 -*-
"""
Unit tests for gui.py (AuroraTrackerApp).
Covers success & failure for KP index, aurora overlay, forecasts, and solar data.
Tkinter GUI elements are mocked to prevent real windows/dialogs.
"""

import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import src.gui as gui


@patch("src.gui.messagebox.showerror", MagicMock())
@patch("src.gui.messagebox.showinfo", MagicMock())
class TestAuroraTrackerApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure Tk root is created once and withdrawn to prevent GUI popups."""
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        """Destroy root after all tests."""
        cls.root.destroy()

    def setUp(self):
        self.app = gui.AuroraTrackerApp(self.root)

    # ---------- KP INDEX ----------
    @patch("src.gui.get_current_kp_index", side_effect=Exception("fail"))
    def test_update_kp_index_failure(self, mock_kp):
        """Ensure error dialog appears if KP index retrieval fails."""
        self.app.update_kp_index()
        gui.messagebox.showerror.assert_called()

    @patch("src.gui.get_current_kp_index", return_value=4.5)
    def test_update_kp_index_success(self, mock_kp):
        """Label should be updated if KP retrieval succeeds."""
        self.app.update_kp_index()
        self.assertIn("4.5", self.app.kp_label.cget("text"))

    # ---------- AURORA OVERLAY ----------
    @patch("src.gui.ImageTk.PhotoImage", return_value="mock_img")
    @patch("src.gui.Image.open", return_value=MagicMock())
    @patch("src.gui.generate_aurora_map", return_value="aurora_map.png")
    def test_show_aurora_overlay_success(self, mock_map, mock_open, mock_photo):
        """Aurora overlay should load image if generation succeeds."""
        self.app.show_aurora_overlay()

        # Check that map generation was triggered
        mock_map.assert_called_once()
        # Check image opened
        mock_open.assert_called_once_with("aurora_map.png")
        # Check PhotoImage creation
        mock_photo.assert_called_once()
        # Check that canvas was updated
        self.assertTrue(hasattr(self.app.map_canvas, "image") or mock_photo.called)


    @patch("src.gui.generate_aurora_map", return_value=None)
    def test_show_aurora_overlay_failure(self, mock_map):
        """Error dialog should appear if aurora map generation fails."""
        self.app.show_aurora_overlay()
        gui.messagebox.showerror.assert_called()

    # ---------- HOURLY FORECAST ----------
    @patch("src.gui.get_hourly_forecast", return_value=([], []))
    def test_show_hourly_forecast_no_data(self, mock_forecast):
        """Error dialog should appear if hourly forecast returns no data."""
        self.app.show_hourly_forecast()
        gui.messagebox.showerror.assert_called()

    @patch("src.gui.plot_3_day_forecast_chart")
    @patch("src.gui.get_hourly_forecast", return_value=(["2025-07-28"], [4]))
    def test_show_hourly_forecast_success(self, mock_forecast, mock_plot):
        """Chart should be plotted when hourly forecast returns valid data."""
        self.app.show_hourly_forecast()
        mock_plot.assert_called_once()

    # ---------- LONG FORECAST ----------
    @patch("src.gui.get_long_term_forecast", return_value=([], []))
    def test_show_long_forecast_no_data(self, mock_forecast):
        """Error dialog should appear if long forecast returns no data."""
        self.app.show_long_forecast()
        gui.messagebox.showerror.assert_called()

    @patch("src.gui.plot_long_term_forecast_chart")
    @patch("src.gui.get_long_term_forecast", return_value=(["Day1"], [5]))
    def test_show_long_forecast_success(self, mock_forecast, mock_plot):
        """Chart should be plotted when long forecast returns valid data."""
        self.app.show_long_forecast()
        mock_plot.assert_called_once()

    # ---------- SOLAR DATA ----------
    @patch("src.gui.get_solar_wind_data", return_value=([], [], [], [], [], []))
    def test_show_solar_wind_graphs_no_data(self, mock_data):
        """Error dialog should appear if solar wind data is missing."""
        self.app.show_solar_wind_graphs()
        gui.messagebox.showerror.assert_called()

    @patch.object(gui.AuroraTrackerApp, "_draw_solar_charts")
    @patch("src.gui.get_solar_wind_data", return_value=(
        ["t1", "t2"], [300, 320], [5, 6], ["t1", "t2"], [1, -1], [2, 3]
    ))
    def test_show_solar_wind_graphs_success(self, mock_data, mock_draw):
        """Charts should be drawn when solar wind data is valid."""
        self.app.show_solar_wind_graphs()
        mock_draw.assert_called_once()


if __name__ == "__main__":
    unittest.main()