"""Weather information service using OpenWeatherMap API."""

from datetime import datetime, timedelta
from typing import Optional
import requests

from src.config.settings import settings


class WeatherService:
    """Fetches weather data from OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize weather service.

        Args:
            api_key: OpenWeatherMap API key (default: from settings)
        """
        self.api_key = api_key or settings.OPENWEATHER_API_KEY
        self._cache = {}
        self._cache_duration = timedelta(minutes=10)

    def get_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        units: str = "metric"
    ) -> Optional[dict]:
        """Get current weather data.

        Args:
            city: City name (e.g., "Seoul", "New York")
            lat: Latitude (if using coordinates)
            lon: Longitude (if using coordinates)
            units: Units system ("metric", "imperial", "standard")

        Returns:
            Weather data dictionary or None if fetch fails
        """
        if not self.api_key:
            return None

        # Build cache key
        if city:
            cache_key = f"city_{city}_{units}"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units
            }
        elif lat is not None and lon is not None:
            cache_key = f"coords_{lat}_{lon}_{units}"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': units
            }
        else:
            return None

        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_duration:
                return cached_data

        # Fetch from API
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Parse weather data
            weather_data = {
                'city': data.get('name', 'Unknown'),
                'country': data.get('sys', {}).get('country', ''),
                'temperature': data.get('main', {}).get('temp'),
                'feels_like': data.get('main', {}).get('feels_like'),
                'temp_min': data.get('main', {}).get('temp_min'),
                'temp_max': data.get('main', {}).get('temp_max'),
                'humidity': data.get('main', {}).get('humidity'),
                'pressure': data.get('main', {}).get('pressure'),
                'weather': data.get('weather', [{}])[0].get('main', 'Unknown'),
                'description': data.get('weather', [{}])[0].get('description', ''),
                'icon': data.get('weather', [{}])[0].get('icon', '01d'),
                'wind_speed': data.get('wind', {}).get('speed'),
                'wind_deg': data.get('wind', {}).get('deg'),
                'clouds': data.get('clouds', {}).get('all'),
                'visibility': data.get('visibility'),
                'sunrise': datetime.fromtimestamp(data.get('sys', {}).get('sunrise', 0)),
                'sunset': datetime.fromtimestamp(data.get('sys', {}).get('sunset', 0)),
                'timestamp': datetime.fromtimestamp(data.get('dt', 0)),
                'units': units
            }

            # Cache the result
            self._cache[cache_key] = (datetime.now(), weather_data)

            return weather_data

        except requests.RequestException as e:
            print(f"Weather API error: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Weather data parsing error: {e}")
            return None

    def get_weather_icon_emoji(self, icon_code: str) -> str:
        """Get emoji for weather icon code.

        Args:
            icon_code: OpenWeatherMap icon code

        Returns:
            Weather emoji
        """
        icon_map = {
            '01d': '☀️',   # clear sky day
            '01n': '🌙',   # clear sky night
            '02d': '⛅',   # few clouds day
            '02n': '☁️',   # few clouds night
            '03d': '☁️',   # scattered clouds
            '03n': '☁️',
            '04d': '☁️',   # broken clouds
            '04n': '☁️',
            '09d': '🌧️',   # shower rain
            '09n': '🌧️',
            '10d': '🌦️',   # rain day
            '10n': '🌧️',   # rain night
            '11d': '⛈️',   # thunderstorm
            '11n': '⛈️',
            '13d': '❄️',   # snow
            '13n': '❄️',
            '50d': '🌫️',   # mist
            '50n': '🌫️',
        }
        return icon_map.get(icon_code, '🌤️')

    def format_weather_short(self, weather_data: Optional[dict] = None, city: str = "Seoul") -> str:
        """Format weather for compact display.

        Args:
            weather_data: Weather data (fetches if None)
            city: City name if fetching

        Returns:
            Formatted weather string
        """
        if weather_data is None:
            weather_data = self.get_weather(city=city)

        if not weather_data:
            return "🌡️ --°C"

        temp = weather_data.get('temperature')
        icon = self.get_weather_icon_emoji(weather_data.get('icon', '01d'))
        weather = weather_data.get('weather', 'Unknown')

        if temp is not None:
            return f"{icon} {temp:.1f}°C"
        else:
            return f"{icon} --°C"

    def clear_cache(self):
        """Clear weather cache."""
        self._cache.clear()
