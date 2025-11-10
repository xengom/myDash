import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""

    # Projecvt root
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # Dtabase
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/mydash.db')

    # OpenWeather API
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    OPENWEATHER_CITY = os.getenv('OPENWEATHER_CITY', 'Seoul')
    OPENWEATHER_UNITS = os.getenv('OPENWEATHER_UNITS', 'metric')
    WEATHER_CITY = os.getenv('WEATHER_CITY', 'Seoul')  # Alias for easier access

    # Update intervals (seconds)
    REFRESH_INTERVAL_SYSTEM = int(os.getenv('REFRESH_INTERVAL_SYSTEM', 5))
    REFRESH_INTERVAL_WEATHER = int(os.getenv('REFRESH_INTERVAL_WEATHER', 1800))
    REFRESH_INTERVAL_CALENDAR = int(os.getenv('REFRESH_INTERVAL_CALENDAR', 900))
    REFRESH_INTERVAL_GMAIL = int(os.getenv('REFRESH_INTERVAL_GMAIL', 300))
    REFRESH_INTERVAL_TASKS = int(os.getenv('REFRESH_INTERVAL_TASKS', 600))
    REFRESH_INTERVAL_STOCKS = int(os.getenv('REFRESH_INTERVAL_STOCKS', 60))

    # Google OAuth
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', '.credential.json')
    GOOGLE_TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json')
    GOOGLE_SCOPES = os.getenv('GOOGLE_SCOPES', '').split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './data/mydash.log')

    # Cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL',3600))

settings = Settings()
