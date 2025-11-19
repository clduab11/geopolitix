"""Data source API integrations."""

from src.data_sources.base import BaseAPIClient
from src.data_sources.gdelt import GDELTClient
from src.data_sources.newsapi import NewsAPIClient
from src.data_sources.worldbank import WorldBankClient
from src.data_sources.acled import ACLEDClient

__all__ = [
    "ACLEDClient",
    "BaseAPIClient",
    "GDELTClient",
    "NewsAPIClient",
    "WorldBankClient",
]
