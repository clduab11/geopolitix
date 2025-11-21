"""Application settings and configuration."""

import os
from decouple import config


class Settings:
    """Central configuration for the GEOPOLITIX application."""

    # Application
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    PORT: int = config("PORT", default=8050, cast=int)
    HOST: str = config("HOST", default="127.0.0.1")

    # API Keys - Original
    NEWSAPI_KEY: str = config("NEWSAPI_KEY", default="")
    GDELT_API_KEY: str = config("GDELT_API_KEY", default="")
    ACLED_API_KEY: str = config("ACLED_API_KEY", default="")
    ACLED_EMAIL: str = config("ACLED_EMAIL", default="")

    # API Keys - AI & Advanced Search
    PERPLEXITY_API_KEY: str = config("PERPLEXITY_API_KEY", default="")
    PERPLEXITY_FINANCE_ENABLED: bool = config(
        "PERPLEXITY_FINANCE_ENABLED", default=True, cast=bool
    )
    PERPLEXITY_FINANCE_MODEL: str = config(
        "PERPLEXITY_FINANCE_MODEL", default="sonar-pro"
    )
    PERPLEXITY_REASONING_MODEL: str = config(
        "PERPLEXITY_REASONING_MODEL", default="sonar-reasoning-pro"
    )

    TAVILY_API_KEY: str = config("TAVILY_API_KEY", default="")
    TAVILY_SEARCH_DEPTH: str = config("TAVILY_SEARCH_DEPTH", default="advanced")
    TAVILY_MAX_RESULTS: int = config("TAVILY_MAX_RESULTS", default=10, cast=int)
    TAVILY_INCLUDE_DOMAINS: str = config("TAVILY_INCLUDE_DOMAINS", default="")
    TAVILY_EXCLUDE_DOMAINS: str = config("TAVILY_EXCLUDE_DOMAINS", default="")

    EXA_API_KEY: str = config("EXA_API_KEY", default="")
    EXA_NUM_RESULTS: int = config("EXA_NUM_RESULTS", default=10, cast=int)
    EXA_USE_AUTOPROMPT: bool = config("EXA_USE_AUTOPROMPT", default=True, cast=bool)

    FIRECRAWL_API_KEY: str = config("FIRECRAWL_API_KEY", default="")
    FIRECRAWL_CRAWL_DEPTH: int = config("FIRECRAWL_CRAWL_DEPTH", default=2, cast=int)
    FIRECRAWL_ENABLE_JAVASCRIPT: bool = config(
        "FIRECRAWL_ENABLE_JAVASCRIPT", default=True, cast=bool
    )
    FIRECRAWL_WAIT_FOR_SELECTOR: str = config(
        "FIRECRAWL_WAIT_FOR_SELECTOR", default=""
    )

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
