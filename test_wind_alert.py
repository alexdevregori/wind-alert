import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

with patch.dict(os.environ, {
    "WEATHER_API_KEY": "sample-weather-key",
    "LOCATION": "San Luis Obispo, CA",
    "THRESHOLD_MPH": "20",
}):
    import wind_alert


class GetWindTests(unittest.TestCase):
    def test_fetches_weather_without_logging_api_key(self):
        output = io.StringIO()
        payload = {
            "current": {"wind_mph": 25, "wind_dir": "NW", "gust_mph": 30},
            "location": {"name": "San Luis Obispo", "region": "California"},
        }
        with (
            patch.object(wind_alert, "WEATHER_API_KEY", "sample-weather-key"),
            patch.object(wind_alert, "LOCATION", "San Luis Obispo, CA"),
            patch("wind_alert.urllib.request.urlopen") as urlopen,
            redirect_stdout(output),
        ):
            urlopen.return_value.__enter__.return_value.read.return_value = (
                json.dumps(payload).encode("utf-8")
            )
            wind = wind_alert.get_wind()

        urlopen.assert_called_once_with(
            "https://api.weatherapi.com/v1/current.json"
            "?key=sample-weather-key&q=San%20Luis%20Obispo%2C%20CA&aqi=no",
            timeout=10,
        )
        self.assertEqual(wind, {
            "mph": 25,
            "direction": "NW",
            "gust_mph": 30,
            "city": "San Luis Obispo, California",
        })
        self.assertNotIn("sample-weather-key", output.getvalue())


if __name__ == "__main__":
    unittest.main()
