"""GDELT Project API integration for global event data."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.api_endpoints import APIEndpoints
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GDELTClient(BaseAPIClient):
    """Client for GDELT Project API - Global Database of Events, Language, and Tone."""

    def __init__(self):
        """Initialize GDELT client."""
        super().__init__(
            APIEndpoints.GDELT_BASE_URL,
            service_name="gdelt",
        )

    @cache_response()
    def get_country_mentions(
        self,
        country: str,
        days: int = 7,
        max_records: int = 250,
    ) -> Optional[Dict[str, Any]]:
        """
        Get news article mentions for a country.

        Args:
            country: Country name to search
            days: Number of days to look back
            max_records: Maximum records to return

        Returns:
            Dictionary with articles and metadata
        """
        # Build GDELT query
        query = f'"{country}" sourcelang:eng'

        # Convert days to hours for timespan parameter
        timespan_hours = days * 24

        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_records,
            "format": "json",
            "sort": "datedesc",
            "timespan": f"{timespan_hours}h",
        }

        response = self.get("doc/doc", params=params)

        if response and "articles" in response:
            return {
                "country": country,
                "article_count": len(response["articles"]),
                "articles": response["articles"],
                "query_time": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "country": country,
            "article_count": 0,
            "articles": [],
            "query_time": datetime.now(timezone.utc).isoformat(),
        }

    @cache_response()
    def get_conflict_events(
        self,
        country: str,
        days: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        Get conflict-related events for a country.

        Args:
            country: Country name
            days: Number of days to look back

        Returns:
            Dictionary with conflict events and metrics
        """
        # Search for conflict-related terms
        conflict_terms = [
            "military",
            "conflict",
            "attack",
            "protest",
            "violence",
            "war",
            "tension",
        ]

        query = f'"{country}" ({" OR ".join(conflict_terms)}) sourcelang:eng'

        # Convert days to hours for timespan parameter
        timespan_hours = days * 24

        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": 100,
            "format": "json",
            "sort": "datedesc",
            "timespan": f"{timespan_hours}h",
        }

        response = self.get("doc/doc", params=params)

        if response and "articles" in response:
            articles = response["articles"]

            # Calculate average tone (negative = more conflict)
            tones = [float(a.get("tone", 0)) for a in articles if "tone" in a]
            avg_tone = sum(tones) / len(tones) if tones else 0

            return {
                "country": country,
                "conflict_articles": len(articles),
                "average_tone": round(avg_tone, 2),
                "articles": articles[:20],  # Return top 20
                "query_time": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "country": country,
            "conflict_articles": 0,
            "average_tone": 0,
            "articles": [],
            "query_time": datetime.now(timezone.utc).isoformat(),
        }

    @cache_response()
    def get_sentiment_analysis(
        self,
        country: str,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get sentiment analysis for a country and optional topic.

        Args:
            country: Country name
            topic: Optional specific topic (e.g., "trade", "security")

        Returns:
            Sentiment metrics dictionary
        """
        query = f'"{country}"'
        if topic:
            query += f' "{topic}"'
        query += " sourcelang:eng"

        params = {
            "query": query,
            "mode": "tonechart",
            "format": "json",
        }

        response = self.get("doc/doc", params=params)

        if response and "tonechart" in response:
            tone_data = response["tonechart"]

            # Process tone chart data
            positive_count = sum(1 for t in tone_data if float(t.get("tone", 0)) > 0)
            negative_count = sum(1 for t in tone_data if float(t.get("tone", 0)) < 0)

            return {
                "country": country,
                "topic": topic,
                "total_articles": len(tone_data),
                "positive_articles": positive_count,
                "negative_articles": negative_count,
                "sentiment_ratio": positive_count / max(negative_count, 1),
                "query_time": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "country": country,
            "topic": topic,
            "total_articles": 0,
            "positive_articles": 0,
            "negative_articles": 0,
            "sentiment_ratio": 1.0,
            "query_time": datetime.now(timezone.utc).isoformat(),
        }

    def calculate_news_risk_score(self, country: str) -> float:
        """
        Calculate risk score based on news sentiment and volume.

        Args:
            country: Country name

        Returns:
            Risk score from 0-100
        """
        # Get recent mentions
        mentions = self.get_country_mentions(country, days=7)
        conflicts = self.get_conflict_events(country, days=30)

        if not mentions or not conflicts:
            return 50.0  # Default moderate risk

        # Factors for risk calculation
        article_volume = mentions.get("article_count", 0)
        conflict_volume = conflicts.get("conflict_articles", 0)
        tone = conflicts.get("average_tone", 0)

        # Higher volume with negative tone = higher risk
        volume_score = min(article_volume / 100, 1) * 30
        conflict_score = min(conflict_volume / 50, 1) * 40
        tone_score = max(0, -tone) * 3  # Negative tone increases risk

        risk_score = volume_score + conflict_score + tone_score

        return min(max(risk_score, 0), 100)

    def get_trending_topics(
        self,
        country: str,
        max_topics: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get trending geopolitical topics for a country.

        Args:
            country: Country name
            max_topics: Maximum topics to return

        Returns:
            List of trending topics with metrics
        """
        topics = [
            "trade",
            "military",
            "economy",
            "sanctions",
            "diplomacy",
            "election",
            "protest",
            "security",
        ]

        results = []
        for topic in topics:
            sentiment = self.get_sentiment_analysis(country, topic)
            if sentiment and sentiment.get("total_articles", 0) > 0:
                results.append(
                    {
                        "topic": topic,
                        "article_count": sentiment["total_articles"],
                        "sentiment_ratio": sentiment["sentiment_ratio"],
                    }
                )

        # Sort by article count
        results.sort(key=lambda x: x["article_count"], reverse=True)

        return results[:max_topics]
