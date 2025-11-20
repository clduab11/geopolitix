"""Firecrawl integration for deep web scraping and content extraction."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FirecrawlClient(BaseAPIClient):
    """Client for Firecrawl - Deep web scraping and content extraction."""

    def __init__(self):
        """Initialize Firecrawl client."""
        super().__init__(
            base_url="https://api.firecrawl.dev/v0",
            api_key=Settings.FIRECRAWL_API_KEY,
        )
        self.crawl_depth = Settings.FIRECRAWL_CRAWL_DEPTH
        self.enable_javascript = Settings.FIRECRAWL_ENABLE_JAVASCRIPT

    def _get_headers(self) -> Dict[str, str]:
        """Override headers for Firecrawl authentication."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @cache_response(ttl_minutes=60)
    def scrape_url(
        self,
        url: str,
        wait_for_selector: Optional[str] = None,
        include_raw_html: bool = False,
    ) -> Dict[str, Any]:
        """
        Scrape a single URL and extract content.

        Args:
            url: URL to scrape
            wait_for_selector: CSS selector to wait for
            include_raw_html: Include raw HTML in response

        Returns:
            Scraped content
        """
        payload = {
            "url": url,
            "pageOptions": {
                "onlyMainContent": True,
                "includeHtml": include_raw_html,
                "waitFor": self.enable_javascript,
            },
        }

        if wait_for_selector:
            payload["pageOptions"]["waitForSelector"] = wait_for_selector

        response = self.post("scrape", json_data=payload)

        if response and "data" in response:
            data = response["data"]
            return {
                "url": url,
                "title": data.get("title", ""),
                "content": data.get("content", ""),
                "markdown": data.get("markdown", ""),
                "html": data.get("html", "") if include_raw_html else None,
                "metadata": data.get("metadata", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_scrape_response(url)

    @cache_response(ttl_minutes=120)
    def crawl_website(
        self,
        start_url: str,
        max_depth: Optional[int] = None,
        limit: int = 50,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Crawl an entire website starting from a URL.

        Args:
            start_url: Starting URL for crawl
            max_depth: Maximum depth to crawl
            limit: Maximum number of pages
            include_paths: Paths to include (regex patterns)
            exclude_paths: Paths to exclude (regex patterns)

        Returns:
            Crawled pages and metadata
        """
        depth = max_depth or self.crawl_depth

        payload = {
            "url": start_url,
            "crawlerOptions": {
                "maxDepth": depth,
                "limit": limit,
                "allowBackwardCrawling": False,
            },
            "pageOptions": {
                "onlyMainContent": True,
            },
        }

        if include_paths:
            payload["crawlerOptions"]["includePaths"] = include_paths

        if exclude_paths:
            payload["crawlerOptions"]["excludePaths"] = exclude_paths

        response = self.post("crawl", json_data=payload)

        if response and "jobId" in response:
            job_id = response["jobId"]
            # In production, you'd poll for results
            # For now, return job info
            return {
                "job_id": job_id,
                "start_url": start_url,
                "status": "queued",
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"start_url": start_url, "status": "failed"}

    def get_crawl_status(
        self,
        job_id: str,
    ) -> Dict[str, Any]:
        """
        Get status of a crawl job.

        Args:
            job_id: Crawl job ID

        Returns:
            Crawl status and results
        """
        response = self.get(f"crawl/status/{job_id}")

        if response:
            return {
                "job_id": job_id,
                "status": response.get("status", "unknown"),
                "completed": response.get("completed", 0),
                "total": response.get("total", 0),
                "data": response.get("data", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"job_id": job_id, "status": "error"}

    @cache_response(ttl_minutes=360)
    def monitor_government_site(
        self,
        country_code: str,
        government_urls: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Monitor government websites for policy changes.

        Args:
            country_code: Country code (e.g., 'US', 'UK')
            government_urls: Specific government URLs to monitor

        Returns:
            Monitored content and changes
        """
        urls = government_urls or self._get_government_urls(country_code)

        results = []
        for url in urls:
            scraped = self.scrape_url(url)
            if scraped and scraped.get("content"):
                results.append(scraped)

        return {
            "country_code": country_code,
            "monitored_sites": urls,
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @cache_response(ttl_minutes=180)
    def track_international_orgs(
        self,
        organization: str,
    ) -> Dict[str, Any]:
        """
        Track announcements from international organizations.

        Args:
            organization: Organization name (UN, IMF, World Bank, etc.)

        Returns:
            Organization announcements and updates
        """
        org_urls = {
            "UN": "https://www.un.org/press/en",
            "IMF": "https://www.imf.org/en/News",
            "World Bank": "https://www.worldbank.org/en/news",
            "NATO": "https://www.nato.int/cps/en/natohq/news.htm",
            "EU": "https://europa.eu/newsroom/home_en",
            "WTO": "https://www.wto.org/english/news_e/news_e.htm",
        }

        url = org_urls.get(organization)
        if not url:
            return {"organization": organization, "error": "Unknown organization"}

        scraped = self.scrape_url(url)

        return {
            "organization": organization,
            "url": url,
            "content": scraped.get("content", ""),
            "title": scraped.get("title", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @cache_response(ttl_minutes=240)
    def scrape_think_tanks(
        self,
        topic: str,
        think_tanks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape publications from major think tanks.

        Args:
            topic: Topic to search for
            think_tanks: Specific think tanks to scrape

        Returns:
            Think tank publications
        """
        tank_urls = think_tanks or [
            "https://www.cfr.org/",
            "https://www.csis.org/",
            "https://www.chathamhouse.org/",
            "https://www.brookings.edu/",
            "https://www.rand.org/",
        ]

        results = []
        for url in tank_urls:
            # Crawl the think tank site
            crawl_job = self.crawl_website(
                start_url=url,
                max_depth=2,
                limit=10,
                include_paths=[topic.lower()],
            )
            results.append(crawl_job)

        return {
            "topic": topic,
            "think_tanks": tank_urls,
            "crawl_jobs": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @cache_response(ttl_minutes=360)
    def monitor_defense_ministries(
        self,
        countries: List[str],
    ) -> Dict[str, Any]:
        """
        Monitor defense ministry and intelligence agency releases.

        Args:
            countries: List of country codes

        Returns:
            Defense ministry updates
        """
        defense_urls = {}
        for country in countries:
            urls = self._get_defense_ministry_urls(country)
            if urls:
                defense_urls[country] = urls

        results = {}
        for country, urls in defense_urls.items():
            country_results = []
            for url in urls:
                scraped = self.scrape_url(url)
                if scraped and scraped.get("content"):
                    country_results.append(scraped)
            results[country] = country_results

        return {
            "countries": countries,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @cache_response(ttl_minutes=180)
    def track_sanctions(
        self,
        target_country: str,
    ) -> Dict[str, Any]:
        """
        Track sanctions from official sources.

        Args:
            target_country: Country being sanctioned

        Returns:
            Sanctions information
        """
        sanctions_urls = [
            f"https://home.treasury.gov/policy-issues/financial-sanctions/"
            f"sanctions-programs-and-country-information",
            "https://www.sanctionsmap.eu/",
            "https://www.un.org/securitycouncil/sanctions/information",
        ]

        results = []
        for url in sanctions_urls:
            scraped = self.scrape_url(url)
            if scraped and scraped.get("content"):
                # Filter content for target country
                content = scraped.get("content", "")
                if target_country.lower() in content.lower():
                    results.append(scraped)

        return {
            "target_country": target_country,
            "sanctions_sources": sanctions_urls,
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def detect_changes(
        self,
        url: str,
        previous_content: str,
    ) -> Dict[str, Any]:
        """
        Detect changes in website content.

        Args:
            url: URL to check
            previous_content: Previous content for comparison

        Returns:
            Change detection results
        """
        current = self.scrape_url(url)
        current_content = current.get("content", "")

        # Simple diff (in production, use proper diff library)
        has_changed = current_content != previous_content
        change_percentage = self._calculate_change_percentage(
            previous_content,
            current_content,
        )

        return {
            "url": url,
            "has_changed": has_changed,
            "change_percentage": change_percentage,
            "current_content": current_content,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_government_urls(self, country_code: str) -> List[str]:
        """Get government URLs for a country."""
        gov_urls = {
            "US": [
                "https://www.state.gov/",
                "https://www.whitehouse.gov/briefing-room/",
            ],
            "UK": [
                "https://www.gov.uk/government/news",
            ],
            "DE": [
                "https://www.bundesregierung.de/breg-en",
            ],
            "FR": [
                "https://www.gouvernement.fr/en",
            ],
            "CN": [
                "http://english.www.gov.cn/",
            ],
            "RU": [
                "http://en.kremlin.ru/",
            ],
        }

        return gov_urls.get(country_code.upper(), [])

    def _get_defense_ministry_urls(self, country_code: str) -> List[str]:
        """Get defense ministry URLs for a country."""
        defense_urls = {
            "US": [
                "https://www.defense.gov/News/",
            ],
            "UK": [
                "https://www.gov.uk/government/organisations/ministry-of-defence",
            ],
            "FR": [
                "https://www.defense.gouv.fr/",
            ],
            "DE": [
                "https://www.bmvg.de/en",
            ],
        }

        return defense_urls.get(country_code.upper(), [])

    def _calculate_change_percentage(
        self,
        old_content: str,
        new_content: str,
    ) -> float:
        """Calculate percentage of content that changed."""
        if not old_content and not new_content:
            return 0.0

        if not old_content or not new_content:
            return 100.0

        # Simple character-based comparison
        old_len = len(old_content)
        new_len = len(new_content)

        if old_len == 0:
            return 100.0

        diff = abs(old_len - new_len)
        percentage = (diff / old_len) * 100

        return round(min(percentage, 100.0), 2)

    def _empty_scrape_response(self, url: str) -> Dict[str, Any]:
        """Return empty scrape response structure."""
        return {
            "url": url,
            "content": "",
            "error": "Failed to scrape",
            "timestamp": datetime.utcnow().isoformat(),
        }
