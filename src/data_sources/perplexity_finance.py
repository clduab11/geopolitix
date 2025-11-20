"""Perplexity Finance API integration for financial market intelligence."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PerplexityFinanceClient(BaseAPIClient):
    """Client for Perplexity Finance - Financial market intelligence."""

    def __init__(self):
        """Initialize Perplexity Finance client."""
        super().__init__(
            base_url="https://api.perplexity.ai",
            api_key=Settings.PERPLEXITY_API_KEY,
        )
        self.finance_enabled = Settings.PERPLEXITY_FINANCE_ENABLED

    @cache_response(ttl_minutes=5)
    def get_market_impact(
        self,
        country: str,
        event_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get financial market impact for a country or geopolitical event.

        Args:
            country: Country name or code
            event_description: Optional description of specific event

        Returns:
            Dictionary with market impact data
        """
        if not self.finance_enabled:
            logger.warning("Perplexity Finance is disabled")
            return self._empty_market_response(country)

        # Build query for market impact
        query = f"Financial market impact {country}"
        if event_description:
            query += f" {event_description}"

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial analyst. Provide structured "
                    "analysis of market impacts including stock indices, "
                    "currencies, commodities, and bonds.",
                },
                {
                    "role": "user",
                    "content": f"{query}. Provide current market data and trends.",
                },
            ],
            "return_citations": True,
            "search_domain_filter": ["finance"],
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            citations = response.get("citations", [])

            return {
                "country": country,
                "event": event_description,
                "analysis": content,
                "citations": citations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_market_response(country)

    @cache_response(ttl_minutes=10)
    def get_stock_market_impact(
        self,
        country: str,
        sector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get stock market reaction to geopolitical events.

        Args:
            country: Country name
            sector: Specific sector (defense, energy, tech, etc.)

        Returns:
            Stock market impact data
        """
        if not self.finance_enabled:
            return self._empty_market_response(country)

        sector_filter = f"in {sector} sector" if sector else ""
        query = (
            f"Stock market performance and indices for {country} "
            f"{sector_filter} affected by recent geopolitical events"
        )

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a stock market analyst. Provide specific "
                    "index values, percentage changes, and affected stocks.",
                },
                {"role": "user", "content": query},
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "country": country,
                "sector": sector,
                "market_data": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_market_response(country)

    @cache_response(ttl_minutes=5)
    def get_currency_impact(
        self,
        country: str,
        currency_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get currency fluctuations and forex impacts.

        Args:
            country: Country name
            currency_code: Currency code (USD, EUR, etc.)

        Returns:
            Currency impact data
        """
        if not self.finance_enabled:
            return self._empty_market_response(country)

        currency_part = f"({currency_code})" if currency_code else ""
        query = (
            f"Currency exchange rate changes and forex impact for "
            f"{country} {currency_part} due to geopolitical events"
        )

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a forex analyst. Provide exchange rates, "
                    "percentage changes, and currency strength indicators.",
                },
                {"role": "user", "content": query},
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "country": country,
                "currency_code": currency_code,
                "forex_data": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_market_response(country)

    @cache_response(ttl_minutes=10)
    def get_commodity_prices(
        self,
        commodity_type: str,
        countries: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get commodity price movements (oil, gas, metals, agricultural).

        Args:
            commodity_type: Type of commodity (oil, gas, metals, agricultural)
            countries: List of countries affecting prices

        Returns:
            Commodity price data
        """
        if not self.finance_enabled:
            return {"commodity": commodity_type, "data": {}}

        country_filter = (
            f"related to {', '.join(countries)}" if countries else "globally"
        )
        query = (
            f"Current {commodity_type} prices and recent changes "
            f"{country_filter} due to geopolitical events"
        )

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a commodities analyst. Provide current "
                    "prices, percentage changes, and supply/demand factors.",
                },
                {"role": "user", "content": query},
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "commodity_type": commodity_type,
                "countries": countries,
                "price_data": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"commodity": commodity_type, "data": {}}

    @cache_response(ttl_minutes=15)
    def get_bond_yields(
        self,
        country: str,
    ) -> Dict[str, Any]:
        """
        Get bond yields and sovereign debt indicators.

        Args:
            country: Country name

        Returns:
            Bond yield data
        """
        if not self.finance_enabled:
            return self._empty_market_response(country)

        query = (
            f"Government bond yields and sovereign debt indicators "
            f"for {country} affected by geopolitical risk"
        )

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a fixed income analyst. Provide bond "
                    "yields, credit ratings, and debt sustainability metrics.",
                },
                {"role": "user", "content": query},
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "country": country,
                "bond_data": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_market_response(country)

    @cache_response(ttl_minutes=5)
    def get_crypto_sentiment(
        self,
        geopolitical_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get cryptocurrency market sentiment related to geopolitical events.

        Args:
            geopolitical_context: Optional context about geopolitical events

        Returns:
            Crypto market sentiment data
        """
        if not self.finance_enabled:
            return {"sentiment": "neutral", "data": {}}

        context_part = (
            f"given {geopolitical_context}" if geopolitical_context else ""
        )
        query = (
            f"Cryptocurrency market sentiment and major coin performance "
            f"{context_part} in current geopolitical environment"
        )

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cryptocurrency analyst. Provide BTC, "
                    "ETH and other major coin trends and geopolitical impacts.",
                },
                {"role": "user", "content": query},
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "context": geopolitical_context,
                "crypto_data": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"sentiment": "neutral", "data": {}}

    def calculate_financial_risk_correlation(
        self,
        country: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        """
        Calculate correlation between geopolitical risk score and financial metrics.

        Args:
            country: Country name
            risk_score: Current geopolitical risk score (0-100)

        Returns:
            Correlation analysis
        """
        if not self.finance_enabled:
            return {"country": country, "correlation": 0.0}

        # Get various financial metrics
        market_impact = self.get_market_impact(country)
        currency_impact = self.get_currency_impact(country)

        # Simple correlation estimation based on risk score
        # Higher risk typically correlates with:
        # - Lower stock prices
        # - Currency depreciation (for emerging markets)
        # - Higher bond yields
        correlation_factor = risk_score / 100.0

        return {
            "country": country,
            "risk_score": risk_score,
            "market_impact": market_impact,
            "currency_impact": currency_impact,
            "correlation_factor": round(correlation_factor, 3),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _empty_market_response(self, country: str) -> Dict[str, Any]:
        """Return empty market response structure."""
        return {
            "country": country,
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
        }
