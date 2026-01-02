"""
Base Connector Interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..types import MarketData


class BaseConnector(ABC):
    """Abstract base class for data connectors."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def fetch_history(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> MarketData:
        """Fetch historical data for a symbol."""
        pass
