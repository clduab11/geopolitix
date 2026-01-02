"""
Polymarket Connector.
Interacts with:
- Gamma API: Market discovery and metadata.
- CLOB API: Historical timeseries data.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import logging

from .base import BaseConnector
from .http import HTTPClient
from ..types import MarketData

logger = logging.getLogger(__name__)


class PolymarketConnector(BaseConnector):
    """
    Polymarket connector implementation.
    """

    def __init__(self, config: dict = None):
        super().__init__(config)

        # Gamma API (Market Discovery)
        self.gamma_url = self.config.get(
            "POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com"
        )
        self.gamma_client = HTTPClient(
            base_url=self.gamma_url,
            rate_limit_delay=0.2,  # 5 req/s conservative
        )

        # CLOB API (History)
        self.clob_url = self.config.get(
            "POLYMARKET_API_URL", "https://clob.polymarket.com"
        )
        self.clob_client = HTTPClient(base_url=self.clob_url, rate_limit_delay=0.2)

        self.api_key = self.config.get("POLYMARKET_API_KEY")

    def _get_history_headers(self) -> Dict[str, str]:
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}

    def fetch_history(
        self,
        symbol: str,  # Polymarket 'clob_token_id' or 'condition_id' depending on endpoint
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> MarketData:
        """
        Fetch historical prices from CLOB API.
        Endpoint: GET /prices-history
        """
        params = {
            "market": symbol,
            "interval": "1d",
            "fidelity": 60,  # minutes? default 1d usually implies coarse granularity
        }

        # Convert dates to timestamps if provided
        if start_date:
            params["start_ts"] = int(start_date.timestamp())
        if end_date:
            params["end_ts"] = int(end_date.timestamp())

        try:
            data = self.clob_client.get(
                "prices-history", params=params, headers=self._get_history_headers()
            )

            # Response format: {"history": [{"t": 123, "p": 0.5}, ...]}
            history = data.get("history", [])

            if not history:
                logger.warning(f"No history found for {symbol}")
                return MarketData(
                    market_id=symbol,
                    symbol=symbol,
                    source="polymarket",
                    data=pd.DataFrame(),
                    metadata={},
                )

            # Parse to DataFrame
            df = pd.DataFrame(history)

            # Map columns: t -> timestamp, p -> price
            # Sometimes 'v' (volume) or other fields exist
            df = df.rename(columns={"t": "timestamp", "p": "price"})

            # Convert timestamp
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

            # Ensure safe bounding
            df["price"] = pd.to_numeric(df["price"], errors="coerce")

            # Minimal metadata
            metadata = {"provider": "polymarket", "interval": "1d", "count": len(df)}

            return MarketData(
                market_id=symbol,
                symbol=symbol,
                source="polymarket",
                data=df,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Failed to fetch Polymarket history for {symbol}: {e}")
            raise

    def list_markets(
        self, limit: int = 20, active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List markets from Gamma API.
        """
        params = {
            "limit": limit,
            "active": str(active).lower(),
            "closed": str(not active).lower(),
        }

        try:
            # Depending on gamma version, endpoint might be /events or /markets
            # /events gives aggregated view (e.g. Election), /markets gives individual binary contracts
            response = self.gamma_client.get("markets", params=params)

            # Gamma usually returns list directly or scoped in key
            if isinstance(response, list):
                return response
            return response.get("markets", [])  # Fallback

        except Exception as e:
            logger.error(f"Failed to list Polymarket markets: {e}")
            return []
