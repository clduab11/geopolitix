"""World Bank API integration for governance indicators."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd

from config.api_endpoints import APIEndpoints
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WorldBankClient(BaseAPIClient):
    """Client for World Bank API - Governance and economic indicators."""

    # World Governance Indicators
    WGI_INDICATORS = {
        "VA.EST": "Voice and Accountability",
        "PV.EST": "Political Stability",
        "GE.EST": "Government Effectiveness",
        "RQ.EST": "Regulatory Quality",
        "RL.EST": "Rule of Law",
        "CC.EST": "Control of Corruption",
    }

    def __init__(self):
        """Initialize World Bank client."""
        super().__init__(APIEndpoints.WORLDBANK_BASE_URL)

    @cache_response()
    def get_indicator(
        self,
        indicator: str,
        country: str = "all",
        date_range: str = "2015:2023",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get World Bank indicator data.

        Args:
            indicator: Indicator code (e.g., "PV.EST")
            country: Country code or "all"
            date_range: Date range (e.g., "2015:2023")

        Returns:
            List of indicator data points
        """
        endpoint = f"country/{country}/indicator/{indicator}"

        params = {
            "format": "json",
            "date": date_range,
            "per_page": 500,
        }

        response = self.get(endpoint, params=params)

        # World Bank API returns [metadata, data]
        if response and isinstance(response, list) and len(response) > 1:
            return response[1]

        return None

    @cache_response()
    def get_political_stability(
        self,
        country_code: str,
    ) -> Dict[str, Any]:
        """
        Get political stability indicator for a country.

        Args:
            country_code: ISO 3166-1 alpha-3 country code

        Returns:
            Political stability data
        """
        data = self.get_indicator(
            APIEndpoints.WGI_POLITICAL_STABILITY,
            country_code,
        )

        if data:
            # Get most recent non-null value
            for entry in data:
                if entry.get("value") is not None:
                    return {
                        "country": entry.get("country", {}).get("value", ""),
                        "country_code": country_code,
                        "indicator": "Political Stability",
                        "value": entry.get("value"),
                        "year": entry.get("date"),
                        "query_time": datetime.utcnow().isoformat(),
                    }

        return {
            "country_code": country_code,
            "indicator": "Political Stability",
            "value": None,
            "year": None,
            "query_time": datetime.utcnow().isoformat(),
        }

    @cache_response()
    def get_governance_indicators(
        self,
        country_code: str,
    ) -> Dict[str, Any]:
        """
        Get all governance indicators for a country.

        Args:
            country_code: ISO 3166-1 alpha-3 country code

        Returns:
            Dictionary with all WGI indicators
        """
        results = {
            "country_code": country_code,
            "indicators": {},
            "query_time": datetime.utcnow().isoformat(),
        }

        for code, name in self.WGI_INDICATORS.items():
            data = self.get_indicator(code, country_code)

            if data:
                # Get most recent value
                for entry in data:
                    if entry.get("value") is not None:
                        results["indicators"][name] = {
                            "value": round(entry.get("value", 0), 3),
                            "year": entry.get("date"),
                        }
                        results["country"] = entry.get("country", {}).get("value", "")
                        break

        return results

    def calculate_governance_risk_score(
        self,
        country_code: str,
    ) -> float:
        """
        Calculate risk score based on governance indicators.

        WGI scores range from -2.5 (weak) to 2.5 (strong)
        Convert to 0-100 risk score (higher = more risk)

        Args:
            country_code: ISO 3166-1 alpha-3 country code

        Returns:
            Risk score from 0-100
        """
        indicators = self.get_governance_indicators(country_code)

        if not indicators or not indicators.get("indicators"):
            return 50.0  # Default moderate risk

        values = [
            ind["value"]
            for ind in indicators["indicators"].values()
            if ind.get("value") is not None
        ]

        if not values:
            return 50.0

        # Average of all indicators
        avg_value = sum(values) / len(values)

        # Convert from [-2.5, 2.5] to [0, 100] risk score
        # Lower WGI = higher risk
        risk_score = ((2.5 - avg_value) / 5) * 100

        return round(min(max(risk_score, 0), 100), 1)

    @cache_response()
    def get_country_list(self) -> List[Dict[str, str]]:
        """
        Get list of all countries from World Bank.

        Returns:
            List of country dictionaries with id and name
        """
        params = {
            "format": "json",
            "per_page": 300,
        }

        response = self.get("country", params=params)

        if response and isinstance(response, list) and len(response) > 1:
            countries = []
            for entry in response[1]:
                if entry.get("region", {}).get("value") != "Aggregates":
                    countries.append({
                        "id": entry.get("id"),
                        "iso3": entry.get("iso2Code"),
                        "name": entry.get("name"),
                        "region": entry.get("region", {}).get("value"),
                        "income_level": entry.get("incomeLevel", {}).get("value"),
                    })
            return countries

        return []

    def get_historical_trend(
        self,
        country_code: str,
        indicator: str = "PV.EST",
        years: int = 10,
    ) -> pd.DataFrame:
        """
        Get historical trend for an indicator.

        Args:
            country_code: ISO 3166-1 alpha-3 country code
            indicator: Indicator code
            years: Number of years of history

        Returns:
            DataFrame with year and value columns
        """
        end_year = datetime.now().year
        start_year = end_year - years
        date_range = f"{start_year}:{end_year}"

        data = self.get_indicator(indicator, country_code, date_range)

        if not data:
            return pd.DataFrame(columns=["year", "value"])

        records = []
        for entry in data:
            if entry.get("value") is not None:
                records.append({
                    "year": int(entry.get("date")),
                    "value": float(entry.get("value")),
                })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("year")

        return df
