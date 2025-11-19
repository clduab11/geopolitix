"""ACLED API integration for armed conflict data."""

from datetime import datetime, timedelta
from typing import Any, Dict, List
import pandas as pd

from config.api_endpoints import APIEndpoints
from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ACLEDClient(BaseAPIClient):
    """Client for ACLED API - Armed Conflict Location & Event Data."""

    # Event types in ACLED
    EVENT_TYPES = [
        "Battles",
        "Explosions/Remote violence",
        "Violence against civilians",
        "Protests",
        "Riots",
        "Strategic developments",
    ]

    def __init__(self):
        """Initialize ACLED client."""
        super().__init__(APIEndpoints.ACLED_BASE_URL)
        self.api_key = Settings.ACLED_API_KEY
        self.email = Settings.ACLED_EMAIL

    @cache_response()
    def get_country_events(
        self,
        country: str,
        days: int = 30,
        limit: int = 500,
    ) -> Dict[str, Any]:
        """
        Get conflict events for a country.

        Args:
            country: Country name
            days: Number of days to look back
            limit: Maximum events to return

        Returns:
            Dictionary with events and metadata
        """
        from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

        params = {
            "key": self.api_key,
            "email": self.email,
            "country": country,
            "event_date": f"{from_date}|{datetime.utcnow().strftime('%Y-%m-%d')}",
            "event_date_where": "BETWEEN",
            "limit": limit,
        }

        # Remove empty params
        params = {k: v for k, v in params.items() if v}

        response = self.get("", params=params)

        if response and "data" in response:
            events = response["data"]

            return {
                "country": country,
                "event_count": len(events),
                "events": events,
                "date_range": (
                    f"{from_date} to {datetime.utcnow().strftime('%Y-%m-%d')}"
                ),
                "query_time": datetime.utcnow().isoformat(),
            }

        return {
            "country": country,
            "event_count": 0,
            "events": [],
            "date_range": f"{from_date} to {datetime.utcnow().strftime('%Y-%m-%d')}",
            "query_time": datetime.utcnow().isoformat(),
        }

    @cache_response()
    def get_fatalities_summary(
        self,
        country: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get fatalities summary for a country.

        Args:
            country: Country name
            days: Number of days

        Returns:
            Fatalities summary dictionary
        """
        events_data = self.get_country_events(country, days)

        if not events_data or not events_data.get("events"):
            return {
                "country": country,
                "total_fatalities": 0,
                "event_count": 0,
                "fatalities_by_type": {},
            }

        events = events_data["events"]

        total_fatalities = 0
        fatalities_by_type: Dict[str, int] = {}

        for event in events:
            fatalities = int(event.get("fatalities", 0))
            event_type = event.get("event_type", "Unknown")

            total_fatalities += fatalities
            fatalities_by_type[event_type] = (
                fatalities_by_type.get(event_type, 0) + fatalities
            )

        return {
            "country": country,
            "total_fatalities": total_fatalities,
            "event_count": len(events),
            "fatalities_by_type": fatalities_by_type,
            "query_time": datetime.utcnow().isoformat(),
        }

    @cache_response()
    def get_event_breakdown(
        self,
        country: str,
        days: int = 30,
    ) -> Dict[str, int]:
        """
        Get breakdown of events by type.

        Args:
            country: Country name
            days: Number of days

        Returns:
            Dictionary mapping event types to counts
        """
        events_data = self.get_country_events(country, days)

        breakdown: Dict[str, int] = {event_type: 0 for event_type in self.EVENT_TYPES}

        if events_data and events_data.get("events"):
            for event in events_data["events"]:
                event_type = event.get("event_type", "Unknown")
                if event_type in breakdown:
                    breakdown[event_type] += 1

        return breakdown

    def calculate_conflict_risk_score(
        self,
        country: str,
        days: int = 30,
    ) -> float:
        """
        Calculate conflict risk score based on ACLED events.

        Args:
            country: Country name
            days: Number of days to analyze

        Returns:
            Risk score from 0-100
        """
        events_data = self.get_country_events(country, days)
        fatalities = self.get_fatalities_summary(country, days)

        if not events_data:
            return 30.0  # Default low-moderate risk

        event_count = events_data.get("event_count", 0)
        total_fatalities = fatalities.get("total_fatalities", 0)

        # Severity weights by event type
        severity_weights = {
            "Battles": 10,
            "Explosions/Remote violence": 8,
            "Violence against civilians": 9,
            "Protests": 3,
            "Riots": 5,
            "Strategic developments": 2,
        }

        # Calculate weighted event score
        weighted_score = 0
        if events_data.get("events"):
            for event in events_data["events"]:
                event_type = event.get("event_type", "Unknown")
                weight = severity_weights.get(event_type, 5)
                weighted_score += weight

        # Normalize scores
        event_score = min(event_count / 10, 1) * 30  # Max 30 points
        fatality_score = min(total_fatalities / 100, 1) * 40  # Max 40 points
        severity_score = min(weighted_score / 100, 1) * 30  # Max 30 points

        risk_score = event_score + fatality_score + severity_score

        return round(min(max(risk_score, 0), 100), 1)

    def get_recent_alerts(
        self,
        countries: List[str],
        days: int = 7,
        min_fatalities: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get alert events across multiple countries.

        Args:
            countries: List of country names
            days: Number of days
            min_fatalities: Minimum fatalities for alert

        Returns:
            List of alert dictionaries
        """
        alerts = []

        for country in countries:
            events_data = self.get_country_events(country, days, limit=100)

            if events_data and events_data.get("events"):
                for event in events_data["events"]:
                    fatalities = int(event.get("fatalities", 0))

                    if fatalities >= min_fatalities:
                        alerts.append(
                            {
                                "country": country,
                                "event_date": event.get("event_date"),
                                "event_type": event.get("event_type"),
                                "fatalities": fatalities,
                                "location": event.get("location"),
                                "notes": event.get("notes", "")[:200],
                            }
                        )

        # Sort by date descending
        alerts.sort(key=lambda x: x.get("event_date", ""), reverse=True)

        return alerts

    def get_trend_data(
        self,
        country: str,
        months: int = 12,
    ) -> pd.DataFrame:
        """
        Get monthly conflict trend data.

        Args:
            country: Country name
            months: Number of months

        Returns:
            DataFrame with monthly aggregates
        """
        events_data = self.get_country_events(country, days=months * 30, limit=5000)

        if not events_data or not events_data.get("events"):
            return pd.DataFrame(columns=["month", "event_count", "fatalities"])

        df = pd.DataFrame(events_data["events"])

        if df.empty:
            return pd.DataFrame(columns=["month", "event_count", "fatalities"])

        # Convert date and aggregate by month
        df["event_date"] = pd.to_datetime(df["event_date"])
        df["month"] = df["event_date"].dt.to_period("M")
        df["fatalities"] = pd.to_numeric(df["fatalities"], errors="coerce").fillna(0)

        monthly = (
            df.groupby("month")
            .agg(
                event_count=("event_id", "count"),
                fatalities=("fatalities", "sum"),
            )
            .reset_index()
        )

        monthly["month"] = monthly["month"].astype(str)

        return monthly
