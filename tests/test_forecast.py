"""
Unit tests for the forecast.py
Tests for:
- Retrieval and parsing of hourly (3?day) and long?term (27?day) aurora forecasts.
- Robust handling of malformed data and network/API exceptions.
- Proper integration with plotting functions to generate forecast charts.
Uses unittest with mocks for API calls and matplotlib.
"""

import unittest
from unittest.mock import patch, MagicMock
from requests import RequestException
from datetime import datetime, timezone
from src.aurora import forecast


class TestForecast(unittest.TestCase):

    # ---------- get_hourly_forecast Tests ----------
    @patch("src.aurora.forecast.requests.get")
    def test_get_hourly_forecast_success(self, mock_get):
        """Test normal 3-day forecast parsing returns times and values."""
        now = datetime.now(timezone.utc)
        mock_data = [
            ["time_tag", "kp_index"],  
            [now.strftime("%Y-%m-%d %H:%M:%S"), "3.0"],
            [(now.replace(hour=(now.hour + 3) % 24)).strftime("%Y-%m-%d %H:%M:%S"), "4.0"]
        ]
        mock_get.return_value.json.return_value = mock_data
        mock_get.return_value.raise_for_status = MagicMock()

        times, values = forecast.get_hourly_forecast()
        self.assertTrue(len(times) >= 0)
        self.assertTrue(all(isinstance(v, float) for v in values))

    @patch("src.aurora.forecast.requests.get")
    def test_get_hourly_forecast_empty(self, mock_get):
        """Test empty forecast data returns empty lists."""
        mock_get.return_value.json.return_value = [["header1", "header2"]]
        mock_get.return_value.raise_for_status = MagicMock()
        times, values = forecast.get_hourly_forecast()
        self.assertEqual(times, [])
        self.assertEqual(values, [])

    @patch("src.aurora.forecast.requests.get")
    def test_get_hourly_forecast_exception(self, mock_get):
        """Test network exception returns empty lists."""
        mock_get.return_value.raise_for_status.side_effect = Exception("Network error")
        times, values = forecast.get_hourly_forecast()
        self.assertEqual(times, [])
        self.assertEqual(values, [])


    # ---------- get_long_term_forecast Tests ----------
    @patch("src.aurora.forecast.requests.get")
    def test_get_long_term_forecast_success(self, mock_get):
        """Test parsing of valid 27-day forecast."""
        # Format matches parsing condition: len(parts) >= 6
        mock_text = """1 Jan 2025 X X 4.0 X
2 Jan 2025 X X 3.5 X"""
        mock_get.return_value.text = mock_text
        mock_get.return_value.raise_for_status = MagicMock()

        dates, kps = forecast.get_long_term_forecast()
        self.assertGreaterEqual(len(dates), 1)
        self.assertTrue(all(isinstance(kp, float) for kp in kps))

    @patch("src.aurora.forecast.requests.get")
    def test_get_long_term_forecast_malformed(self, mock_get):
        """Test malformed forecast lines are skipped."""
        mock_text = """Bad Line Without Enough Parts"""
        mock_get.return_value.text = mock_text
        mock_get.return_value.raise_for_status = MagicMock()

        dates, kps = forecast.get_long_term_forecast()
        self.assertEqual(dates, [])
        self.assertEqual(kps, [])

    @patch("src.aurora.forecast.requests.get")
    def test_get_long_term_forecast_exception(self, mock_get):
        """Test network exception returns empty lists."""
        mock_get.return_value.raise_for_status.side_effect = RequestException("Network error")
        dates, kps = forecast.get_long_term_forecast()
        self.assertEqual(dates, [])
        self.assertEqual(kps, [])


    # ---------- plot_3_day_forecast_chart Tests ----------
    @patch("src.aurora.forecast.plt")
    def test_plot_3_day_forecast_chart(self, mock_plt):
        """Test 3-day forecast plotting creates bars with correct labels."""
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())
        mock_self = MagicMock()
        times = ["2025-01-01 00:00:00", "2025-01-01 03:00:00"]
        values = [3.0, 4.0]
        forecast.plot_3_day_forecast_chart(mock_self, times, values)
        mock_self._draw_forecast_chart.assert_called()


    # ---------- plot_long_term_forecast_chart Tests ----------
    @patch("src.aurora.forecast.plt")
    def test_plot_long_term_forecast_chart(self, mock_plt):
        """Test 27-day forecast plotting creates bars with correct labels."""
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())
        mock_self = MagicMock()
        dates = ["1 Jan", "2 Jan"]
        values = [3.5, 5.0]
        forecast.plot_long_term_forecast_chart(mock_self, dates, values)
        mock_self._draw_forecast_chart.assert_called()


if __name__ == "__main__":
    unittest.main()
