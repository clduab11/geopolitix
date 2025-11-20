#!/usr/bin/env python3
"""
Manual data update script for GEOPOLITIX.

This script fetches fresh data from all API sources and updates the cache.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_sources.gdelt import GDELTClient
from src.data_sources.newsapi import NewsAPIClient
from src.data_sources.worldbank import WorldBankClient
from src.data_sources.acled import ACLEDClient
from src.risk_engine.scoring import RiskScorer, get_default_countries
from src.utils.cache import clear_cache
from src.utils.logger import get_logger
from src.utils.transformers import country_to_iso

logger = get_logger(__name__)


def update_all_data():
    """Fetch and cache data from all sources."""
    logger.info("Starting data update...")

    # Clear existing cache
    clear_cache()
    logger.info("Cache cleared")

    # Initialize clients
    gdelt = GDELTClient()
    newsapi = NewsAPIClient()
    worldbank = WorldBankClient()
    acled = ACLEDClient()
    scorer = RiskScorer()

    # Get countries to update
    countries = get_default_countries()
    logger.info(f"Updating data for {len(countries)} countries")

    # Update data for each country
    success_count = 0
    error_count = 0

    for country in countries:
        try:
            logger.info(f"Updating {country}...")

            # Fetch from each source
            gdelt.get_country_mentions(country)
            newsapi.get_country_news(country)

            # World Bank uses ISO codes
            iso = country_to_iso(country)
            worldbank.get_governance_indicators(iso)

            # ACLED
            acled.get_country_events(country)

            # Calculate composite score (caches result)
            scorer.calculate_composite_score(country)

            success_count += 1
            logger.info(f"  {country}: OK")

        except Exception as e:
            error_count += 1
            logger.error(f"  {country}: ERROR - {e}")

    logger.info(f"Data update complete: {success_count} success, {error_count} errors")

    return success_count, error_count


if __name__ == "__main__":
    success, errors = update_all_data()
    sys.exit(0 if errors == 0 else 1)
