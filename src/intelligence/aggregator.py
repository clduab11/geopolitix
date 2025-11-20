"""Unified Intelligence Aggregator - Orchestrates all AI and search services."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.ai_analysis.sonar_reasoning import SonarReasoningClient
from src.data_sources.exa_search import ExaSearchClient
from src.data_sources.firecrawl import FirecrawlClient
from src.data_sources.newsapi import NewsAPIClient
from src.data_sources.perplexity_finance import PerplexityFinanceClient
from src.data_sources.tavily_search import TavilySearchClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Constants
MAX_ARTICLES_FOR_SYNTHESIS = 10  # Maximum articles to process for AI synthesis
MAX_ALERTS = 20  # Maximum alerts to return
DEFAULT_RISK_SCORE = 50.0  # Default risk score when none is available


class IntelligenceAggregator:
    """
    Orchestrates multiple AI and search services for comprehensive analysis.

    This class integrates:
    - Tavily: Real-time news search
    - Exa: Neural/semantic search
    - Firecrawl: Deep web scraping
    - Perplexity Finance: Financial market intelligence
    - Sonar Reasoning: AI-powered deep analysis
    - NewsAPI: Traditional news aggregation
    """

    def __init__(self):
        """Initialize all intelligence service clients."""
        self.tavily = TavilySearchClient()
        self.exa = ExaSearchClient()
        self.firecrawl = FirecrawlClient()
        self.perplexity_finance = PerplexityFinanceClient()
        self.sonar = SonarReasoningClient()
        self.newsapi = NewsAPIClient()

    @cache_response(ttl_minutes=30)
    def comprehensive_country_analysis(
        self,
        country: str,
        include_financial: bool = True,
        include_historical: bool = True,
    ) -> Dict[str, Any]:
        """
        Multi-source intelligence gathering and AI analysis for a country.

        Args:
            country: Country name or code
            include_financial: Include financial market analysis
            include_historical: Include historical precedents

        Returns:
            Comprehensive country intelligence report
        """
        logger.info(f"Starting comprehensive analysis for {country}")

        results = {}

        # Use ThreadPoolExecutor for parallel API calls
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}

            # 1. Real-time news (Tavily)
            futures["tavily_news"] = executor.submit(
                self.tavily.search_country_events,
                country=country,
                days=7,
            )

            # 2. Historical precedents (Exa)
            if include_historical:
                futures["historical_events"] = executor.submit(
                    self.exa.find_similar_events,
                    event_description=f"Recent geopolitical events in {country}",
                    num_results=5,
                )

            # 3. Government sources (Firecrawl)
            futures["government_data"] = executor.submit(
                self.firecrawl.monitor_government_site,
                country_code=self._get_country_code(country),
            )

            # 4. Financial market impact (Perplexity Finance)
            if include_financial:
                futures["financial_impact"] = executor.submit(
                    self.perplexity_finance.get_market_impact,
                    country=country,
                )

            # 5. Traditional news (NewsAPI)
            futures["newsapi_data"] = executor.submit(
                self.newsapi.get_country_news,
                country=country,
                days=7,
            )

            # Collect results
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=30)
                except Exception as e:
                    logger.error(f"Error in {key}: {e}")
                    results[key] = {"error": str(e)}

        # 6. AI synthesis (Sonar Reasoning) - Run after gathering data
        try:
            articles = results.get("newsapi_data", {}).get("articles", [])
            if articles:
                results["ai_synthesis"] = self.sonar.synthesize_news(
                    articles=articles,
                    country=country,
                )

            # Deep dive analysis
            results["deep_analysis"] = self.sonar.deep_dive_analysis(
                country=country,
                focus_areas=["political", "economic", "security"],
            )
        except Exception as e:
            logger.error(f"Error in AI synthesis: {e}")
            results["ai_synthesis"] = {"error": str(e)}

        return {
            "country": country,
            "analysis_type": "comprehensive",
            "data_sources": results,
            "generated_at": datetime.utcnow().isoformat(),
        }

    @cache_response(ttl_minutes=5)
    def breaking_news_monitor(
        self,
        keywords: Optional[List[str]] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Real-time monitoring across all news sources.

        Args:
            keywords: Keywords to monitor (default: geopolitical terms)
            hours: Number of hours to look back

        Returns:
            Breaking news from multiple sources
        """
        default_keywords = [
            "conflict",
            "crisis",
            "sanctions",
            "military",
            "election",
            "coup",
            "terrorism",
        ]

        search_keywords = keywords or default_keywords

        # Parallel search across sources
        with ThreadPoolExecutor(max_workers=3) as executor:
            tavily_future = executor.submit(
                self.tavily.breaking_news_search,
                keywords=search_keywords,
                hours=hours,
            )

            newsapi_future = executor.submit(
                self.newsapi.get_geopolitical_news,
                keywords=search_keywords,
                days=max(1, hours // 24),
            )

            exa_future = executor.submit(
                self.exa.neural_search,
                query=" OR ".join(search_keywords),
                num_results=10,
            )

            # Collect results
            tavily_results = tavily_future.result(timeout=15)
            newsapi_results = newsapi_future.result(timeout=15)
            exa_results = exa_future.result(timeout=15)

        # Prioritize alerts using AI
        all_articles = []
        all_articles.extend(tavily_results.get("results", []))
        all_articles.extend(newsapi_results.get("articles", []))

        prioritized = self.sonar.prioritize_alerts(
            self._convert_to_alerts(all_articles)
        )

        return {
            "keywords": search_keywords,
            "timeframe": f"{hours} hours",
            "tavily_results": tavily_results,
            "newsapi_results": newsapi_results,
            "exa_results": exa_results,
            "prioritized_alerts": prioritized,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @cache_response(ttl_minutes=60)
    def generate_executive_brief(
        self,
        timeframe: str = "24h",
        focus_regions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        AI-generated executive summary using all sources.

        Args:
            timeframe: Time period (24h, 7d, 30d)
            focus_regions: Regions to focus on

        Returns:
            Executive briefing
        """
        # Convert timeframe to days
        days = self._timeframe_to_days(timeframe)

        # Gather data
        data_summary = {}

        if focus_regions:
            for region in focus_regions:
                region_data = self.tavily.search_country_events(
                    country=region,
                    days=days,
                )
                data_summary[region] = region_data
        else:
            # Global news
            global_news = self.tavily.search_news(
                query="global geopolitical events",
                days=days,
            )
            data_summary["global"] = global_news

        # Generate brief using AI
        brief = self.sonar.generate_executive_brief(
            timeframe=timeframe,
            focus_regions=focus_regions,
            data_summary=data_summary,
        )

        return brief

    def multi_source_search(
        self,
        query: str,
        country: Optional[str] = None,
        include_financial: bool = False,
    ) -> Dict[str, Any]:
        """
        Search across all available sources.

        Args:
            query: Search query
            country: Optional country name for financial analysis.
                If not provided and include_financial=True, financial
                analysis will be skipped.
            include_financial: Include financial analysis (requires country parameter)

        Returns:
            Combined search results
        """
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                "tavily": executor.submit(
                    self.tavily.search_news,
                    query=query,
                ),
                "exa": executor.submit(
                    self.exa.neural_search,
                    query=query,
                ),
                "newsapi": executor.submit(
                    self.newsapi.get_geopolitical_news,
                    keywords=[query],
                ),
            }

            # Only include financial analysis if country is specified
            if include_financial and country:
                futures["finance"] = executor.submit(
                    self.perplexity_finance.get_market_impact,
                    country=country,
                    event_description=query,
                )
            elif include_financial and not country:
                logger.warning(
                    "Financial analysis requested but no country specified. "
                    "Skipping financial integration."
                )

            # Collect results
            results = {}
            for source, future in futures.items():
                try:
                    results[source] = future.result(timeout=20)
                except Exception as e:
                    logger.error(f"Error in {source} search: {e}")
                    results[source] = {"error": str(e)}

        return {
            "query": query,
            "sources": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def validate_event_multi_source(
        self,
        event_description: str,
        min_sources: int = 3,
    ) -> Dict[str, Any]:
        """
        Validate an event using multiple sources.

        Args:
            event_description: Event to validate
            min_sources: Minimum number of sources required

        Returns:
            Validation results
        """
        # Search multiple sources
        tavily_validation = self.tavily.validate_event(
            event_description=event_description,
            source_count=min_sources,
        )

        exa_results = self.exa.find_similar_events(
            event_description=event_description,
            num_results=5,
        )

        # Use AI to assess validity
        validation_analysis = self.sonar.causal_inference(
            event=event_description,
            context={
                "tavily_sources": len(tavily_validation.get("sources", [])),
                "exa_similar_events": len(exa_results.get("similar_events", [])),
            },
        )

        is_validated = tavily_validation.get("validated", False)

        return {
            "event": event_description,
            "validated": is_validated,
            "tavily_validation": tavily_validation,
            "historical_precedents": exa_results,
            "ai_analysis": validation_analysis,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def financial_geopolitical_correlation(
        self,
        country: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        """
        Analyze correlation between geopolitical risk and financial markets.

        Args:
            country: Country name
            risk_score: Current risk score (0-100)

        Returns:
            Correlation analysis
        """
        # Get financial data
        financial_correlation = (
            self.perplexity_finance.get_financial_data_for_risk_score(
                country=country,
                risk_score=risk_score,
            )
        )

        # Get market-specific data
        stock_impact = self.perplexity_finance.get_stock_market_impact(
            country=country
        )

        currency_impact = self.perplexity_finance.get_currency_impact(
            country=country
        )

        # AI analysis of correlation
        ai_correlation = self.sonar.causal_inference(
            event=f"Risk score {risk_score} for {country}",
            context={
                "stock_market": stock_impact,
                "currency": currency_impact,
            },
        )

        return {
            "country": country,
            "risk_score": risk_score,
            "financial_correlation": financial_correlation,
            "stock_impact": stock_impact,
            "currency_impact": currency_impact,
            "ai_analysis": ai_correlation,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def track_official_sources(
        self,
        countries: List[str],
        include_international_orgs: bool = True,
    ) -> Dict[str, Any]:
        """
        Monitor official government and international organization sources.

        Args:
            countries: List of countries to monitor
            include_international_orgs: Include UN, IMF, etc.

        Returns:
            Official source updates
        """
        results = {}

        # Monitor government sites
        for country in countries:
            country_code = self._get_country_code(country)
            gov_data = self.firecrawl.monitor_government_site(
                country_code=country_code
            )
            results[country] = gov_data

        # Monitor international organizations
        if include_international_orgs:
            orgs = ["UN", "IMF", "World Bank", "NATO"]
            org_results = {}

            for org in orgs:
                org_data = self.firecrawl.track_international_orgs(org)
                org_results[org] = org_data

            results["international_orgs"] = org_results

        return {
            "countries": countries,
            "official_sources": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_country_code(self, country: str) -> str:
        """Convert country name to code (simplified)."""
        # In production, use proper country code library
        country_codes = {
            "United States": "US",
            "United Kingdom": "UK",
            "China": "CN",
            "Russia": "RU",
            "Germany": "DE",
            "France": "FR",
            "Japan": "JP",
            "India": "IN",
        }

        return country_codes.get(country, country[:2].upper())

    def _convert_to_alerts(
        self,
        articles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Convert articles to alert format.

        Normalizes different article structures from:
        - Tavily: uses 'domain' field
        - NewsAPI: uses 'source' dictionary with 'name' key
        """
        alerts = []

        for article in articles[:MAX_ALERTS]:
            # Normalize source field - handle both Tavily and NewsAPI formats
            source = article.get("source", {})
            if isinstance(source, dict):
                # NewsAPI format: {'id': ..., 'name': ...}
                source_name = source.get("name", "Unknown")
            elif isinstance(source, str):
                # Already a string
                source_name = source
            else:
                # Tavily format: uses 'domain' field
                source_name = article.get("domain", "Unknown")

            alerts.append(
                {
                    "country": article.get("country", "Unknown"),
                    "alert_type": "news",
                    "risk_score": article.get("risk_score", DEFAULT_RISK_SCORE),
                    "title": article.get("title", ""),
                    "source": source_name,
                    "url": article.get("url", ""),
                    "published_at": article.get("published_at")
                    or article.get("publishedAt", ""),
                }
            )

        return alerts

    def _timeframe_to_days(self, timeframe: str) -> int:
        """Convert timeframe string to days."""
        timeframe_map = {
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "1h": 1,
            "12h": 1,
        }

        return timeframe_map.get(timeframe.lower(), 1)
