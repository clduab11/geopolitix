"""Application settings and configuration."""

import os
from decouple import config


class Settings:
    """Central configuration for the GEOPOLITIX application."""

    # Application
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    PORT: int = config("PORT", default=8050, cast=int)
    HOST: str = config("HOST", default="127.0.0.1")

    # API Keys
    NEWSAPI_KEY: str = config("NEWSAPI_KEY", default="")
    GDELT_API_KEY: str = config("GDELT_API_KEY", default="")
    ACLED_API_KEY: str = config("ACLED_API_KEY", default="")
    ACLED_EMAIL: str = config("ACLED_EMAIL", default="")

    # Cache Settings
    CACHE_TTL_MINUTES: int = config("CACHE_TTL_MINUTES", default=15, cast=int)
    CACHE_MAX_SIZE: int = config("CACHE_MAX_SIZE", default=1000, cast=int)

    # HTTP Settings
    REQUEST_TIMEOUT: int = 10  # seconds
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 1.0

    # Logging
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    LOG_FILE: str = config("LOG_FILE", default="logs/app.log")

    # Rate Limiting
    API_RATE_LIMIT_PER_MINUTE: int = config(
        "API_RATE_LIMIT_PER_MINUTE", default=60, cast=int
    )

    # Dashboard Update Intervals (milliseconds)
    DATA_REFRESH_INTERVAL: int = 900000  # 15 minutes
    ALERT_REFRESH_INTERVAL: int = 300000  # 5 minutes

    @classmethod
    def get_log_dir(cls) -> str:
        """Ensure log directory exists and return path."""
        log_dir = os.path.dirname(cls.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        return log_dir
