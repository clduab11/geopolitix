"""NewsAPI integration for news aggregation and sentiment analysis."""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from textblob import TextBlob

from config.api_endpoints import APIEndpoints
from config.risk_thresholds import RiskThresholds
from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsAPIClient(BaseAPIClient):
    """Client for NewsAPI - News aggregation and search."""

    def __init__(self):
        """Initialize NewsAPI client."""
        super().__init__(
            APIEndpoints.NEWSAPI_BASE_URL,
            api_key=Settings.NEWSAPI_KEY,
        )

    def _get_headers(self) -> Dict[str, str]:
        """Override headers for NewsAPI authentication."""
        headers = super()._get_headers()
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
            # Remove Bearer auth as NewsAPI uses X-Api-Key
            headers.pop("Authorization", None)
        return headers

    @cache_response()
    def get_country_news(
        self,
        country: str,
        days: int = 7,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get news articles about a country.

        Args:
            country: Country name to search
            days: Number of days to look back
            page_size: Number of articles per page

        Returns:
            Dictionary with articles and metadata
        """
        from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

        params = {
            "q": country,
            "from": from_date,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": page_size,
        }

        response = self.get("everything", params=params)

        if response and response.get("status") == "ok":
            articles = response.get("articles", [])

            # Add sentiment analysis to each article
            analyzed_articles = []
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                text = f"{title} {description}"

                sentiment = self._analyze_sentiment(text)
                article["sentiment"] = sentiment
                analyzed_articles.append(article)

            return {
                "country": country,
                "total_results": response.get("totalResults", 0),
                "articles": analyzed_articles,
                "query_time": datetime.utcnow().isoformat(),
            }

        return {
            "country": country,
            "total_results": 0,
            "articles": [],
            "query_time": datetime.utcnow().isoformat(),
        }

    @cache_response()
    def get_geopolitical_news(
        self,
        keywords: List[str],
        days: int = 7,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get news for specific geopolitical keywords.

        Args:
            keywords: List of keywords to search
            days: Number of days to look back
            page_size: Number of articles

        Returns:
            Dictionary with articles and metadata
        """
        from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        query = " OR ".join(keywords)

        params = {
            "q": query,
            "from": from_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
        }

        response = self.get("everything", params=params)

        if response and response.get("status") == "ok":
            return {
                "keywords": keywords,
                "total_results": response.get("totalResults", 0),
                "articles": response.get("articles", []),
                "query_time": datetime.utcnow().isoformat(),
            }

        return {
            "keywords": keywords,
            "total_results": 0,
            "articles": [],
            "query_time": datetime.utcnow().isoformat(),
        }

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using TextBlob.

        Args:
            text: Text to analyze

        Returns:
            Sentiment scores dictionary
        """
        if not text:
            return {"polarity": 0.0, "subjectivity": 0.0}

        try:
            blob = TextBlob(text)
            return {
                "polarity": round(blob.sentiment.polarity, 3),
                "subjectivity": round(blob.sentiment.subjectivity, 3),
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {"polarity": 0.0, "subjectivity": 0.0}

    def calculate_news_sentiment_score(
        self,
        country: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Calculate aggregate sentiment score for a country.

        Args:
            country: Country name
            days: Number of days to analyze

        Returns:
            Aggregate sentiment metrics
        """
        news_data = self.get_country_news(country, days)

        if not news_data or not news_data.get("articles"):
            return {
                "country": country,
                "average_polarity": 0.0,
                "average_subjectivity": 0.0,
                "article_count": 0,
                "risk_score": 50.0,
            }

        articles = news_data["articles"]

        polarities = [a["sentiment"]["polarity"] for a in articles if "sentiment" in a]
        subjectivities = [
            a["sentiment"]["subjectivity"] for a in articles if "sentiment" in a
        ]

        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        avg_subjectivity = (
            sum(subjectivities) / len(subjectivities) if subjectivities else 0
        )

        # Convert sentiment to risk score (negative sentiment = higher risk)
        # Polarity ranges from -1 to 1, convert to 0-100 risk
        risk_score = (1 - avg_polarity) * 50

        return {
            "country": country,
            "average_polarity": round(avg_polarity, 3),
            "average_subjectivity": round(avg_subjectivity, 3),
            "article_count": len(articles),
            "risk_score": round(risk_score, 1),
        }

    def get_risk_alerts(
        self,
        countries: List[str],
        threshold: float = None,
    ) -> List[Dict[str, Any]]:
        """
        Get alerts for countries with negative news sentiment.

        Args:
            countries: List of countries to check
            threshold: Polarity threshold for alerts

        Returns:
            List of alert dictionaries
        """
        if threshold is None:
            threshold = RiskThresholds.SENTIMENT_NEGATIVE_THRESHOLD

        alerts = []

        for country in countries:
            sentiment = self.calculate_news_sentiment_score(country)

            if sentiment["average_polarity"] < threshold:
                alerts.append(
                    {
                        "country": country,
                        "polarity": sentiment["average_polarity"],
                        "article_count": sentiment["article_count"],
                        "risk_score": sentiment["risk_score"],
                        "alert_type": "negative_sentiment",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        # Sort by risk score descending
        alerts.sort(key=lambda x: x["risk_score"], reverse=True)

        return alerts
