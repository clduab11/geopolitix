"""Tavily API integration for real-time web search and news aggregation."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TavilySearchClient(BaseAPIClient):
    """Client for Tavily - Real-time web search optimized for AI."""

    def __init__(self):
        """Initialize Tavily Search client."""
        super().__init__(
            base_url="https://api.tavily.com",
            api_key=Settings.TAVILY_API_KEY,
        )
        self.search_depth = Settings.TAVILY_SEARCH_DEPTH
        self.max_results = Settings.TAVILY_MAX_RESULTS

    @cache_response(ttl_minutes=5)
    def search_news(
        self,
        query: str,
        days: int = 7,
        search_depth: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for news articles using Tavily.

        Args:
            query: Search query
            days: Number of days to look back
            search_depth: Search depth (basic or advanced)
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude

        Returns:
            Search results with articles
        """
        depth = search_depth or self.search_depth

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": depth,
            "max_results": self.max_results,
            "include_answer": True,
            "include_raw_content": False,
            "include_domains": include_domains or [],
            "exclude_domains": exclude_domains or [],
            "topic": "news",
        }

        # Add time filter if available
        if days:
            from_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            payload["time_filter"] = from_date

        response = self.post("search", json_data=payload)

        if response:
            return {
                "query": query,
                "results": response.get("results", []),
                "answer": response.get("answer", ""),
                "follow_up_questions": response.get("follow_up_questions", []),
                "search_depth": depth,
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_search_response(query)

    @cache_response(ttl_minutes=10)
    def search_country_events(
        self,
        country: str,
        event_type: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Search for country-specific events.

        Args:
            country: Country name
            event_type: Type of event (conflict, election, policy, etc.)
            days: Number of days to look back

        Returns:
            Country event search results
        """
        event_filter = f" {event_type}" if event_type else ""
        query = f"{country}{event_filter} geopolitical events news"

        return self.search_news(
            query=query,
            days=days,
            search_depth="advanced",
        )

    @cache_response(ttl_minutes=3)
    def breaking_news_search(
        self,
        keywords: List[str],
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Search for breaking news on specific keywords.

        Args:
            keywords: List of keywords to search
            hours: Number of hours to look back

        Returns:
            Breaking news results
        """
        query = " OR ".join(keywords)
        days = max(1, hours // 24)

        results = self.search_news(
            query=query,
            days=days,
            search_depth="basic",  # Use basic for speed
        )

        # Filter results to exact hour range if needed
        if results and results.get("results"):
            filtered_results = self._filter_by_hours(
                results["results"],
                hours,
            )
            results["results"] = filtered_results

        return results

    @cache_response(ttl_minutes=15)
    def research_query(
        self,
        topic: str,
        source_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Deep research query for scenario modeling.

        Args:
            topic: Research topic
            source_types: Types of sources (news, academic, government)

        Returns:
            Research results
        """
        payload = {
            "api_key": self.api_key,
            "query": topic,
            "search_depth": "advanced",
            "max_results": 20,  # More results for research
            "include_answer": True,
            "include_raw_content": True,  # Get full content
            "topic": "general",
        }

        # Filter by source types if specified
        if source_types:
            include_domains = self._get_domains_by_type(source_types)
            if include_domains:
                payload["include_domains"] = include_domains

        response = self.post("search", json_data=payload)

        if response:
            return {
                "topic": topic,
                "results": response.get("results", []),
                "answer": response.get("answer", ""),
                "sources": self._extract_sources(response.get("results", [])),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_search_response(topic)

    @cache_response(ttl_minutes=30)
    def validate_event(
        self,
        event_description: str,
        source_count: int = 3,
    ) -> Dict[str, Any]:
        """
        Validate an event by checking multiple sources.

        Args:
            event_description: Description of the event to validate
            source_count: Number of sources to check

        Returns:
            Validation results with source credibility
        """
        results = self.search_news(
            query=event_description,
            days=7,
            search_depth="advanced",
        )

        if results and results.get("results"):
            sources = results["results"][:source_count]
            credibility_scores = [
                self._assess_source_credibility(source) for source in sources
            ]

            return {
                "event": event_description,
                "validated": len(sources) >= source_count,
                "sources": sources,
                "credibility_scores": credibility_scores,
                "average_credibility": (
                    sum(credibility_scores) / len(credibility_scores)
                    if credibility_scores
                    else 0.0
                ),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {
            "event": event_description,
            "validated": False,
            "sources": [],
            "credibility_scores": [],
        }

    @cache_response(ttl_minutes=10)
    def multi_language_search(
        self,
        query: str,
        languages: List[str],
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Search across multiple languages.

        Args:
            query: Search query
            languages: List of language codes (en, es, fr, etc.)
            days: Number of days to look back

        Returns:
            Multi-language search results
        """
        all_results = []

        for lang in languages:
            lang_query = f"{query} language:{lang}"
            results = self.search_news(
                query=lang_query,
                days=days,
                search_depth="basic",
            )

            if results and results.get("results"):
                for result in results["results"]:
                    result["detected_language"] = lang
                    all_results.append(result)

        return {
            "query": query,
            "languages": languages,
            "results": all_results,
            "total_results": len(all_results),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _filter_by_hours(
        self,
        results: List[Dict[str, Any]],
        hours: int,
    ) -> List[Dict[str, Any]]:
        """Filter results by time in hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        filtered = []

        for result in results:
            published_date = result.get("published_date")
            if published_date:
                try:
                    pub_dt = datetime.fromisoformat(
                        published_date.replace("Z", "+00:00")
                    )
                    if pub_dt >= cutoff_time:
                        filtered.append(result)
                except (ValueError, AttributeError):
                    # Include if we can't parse date
                    filtered.append(result)
            else:
                filtered.append(result)

        return filtered

    def _get_domains_by_type(
        self,
        source_types: List[str],
    ) -> List[str]:
        """Get domain filters based on source types."""
        domain_map = {
            "news": [
                "reuters.com",
                "apnews.com",
                "bbc.com",
                "ft.com",
                "wsj.com",
            ],
            "academic": [
                "scholar.google.com",
                "jstor.org",
                "academia.edu",
            ],
            "government": [
                "gov",
                "state.gov",
                "whitehouse.gov",
                "europa.eu",
            ],
        }

        domains = []
        for source_type in source_types:
            domains.extend(domain_map.get(source_type.lower(), []))

        return domains

    def _extract_sources(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """Extract source information from results."""
        sources = []
        for result in results:
            sources.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "domain": result.get("domain", ""),
                    "published_date": result.get("published_date", ""),
                }
            )
        return sources

    def _assess_source_credibility(
        self,
        source: Dict[str, Any],
    ) -> float:
        """
        Assess source credibility (0-1 scale).

        Args:
            source: Source dictionary

        Returns:
            Credibility score
        """
        # Simple credibility scoring based on domain
        high_credibility_domains = [
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "ft.com",
            "wsj.com",
            "nytimes.com",
            "washingtonpost.com",
            "economist.com",
            "gov",
        ]

        domain = source.get("domain", "").lower()

        # Check if domain is in high credibility list
        for trusted_domain in high_credibility_domains:
            if trusted_domain in domain:
                return 0.9

        # Check for government domains
        if ".gov" in domain or domain.endswith("gov"):
            return 0.85

        # Check for academic domains
        if ".edu" in domain or "academic" in domain or "scholar" in domain:
            return 0.8

        # Default medium credibility
        return 0.6

    def _empty_search_response(self, query: str) -> Dict[str, Any]:
        """Return empty search response structure."""
        return {
            "query": query,
            "results": [],
            "answer": "",
            "timestamp": datetime.utcnow().isoformat(),
        }
