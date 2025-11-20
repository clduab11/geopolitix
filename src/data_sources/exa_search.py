"""Exa AI integration for neural search and semantic discovery."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Constants for result limits and scoring
EXPERT_SEARCH_RESULTS = 15  # Number of expert analysis results
NARRATIVE_SEARCH_RESULTS = 20  # Number of emerging narrative results
POLICY_SEARCH_RESULTS = 15  # Number of policy document results
SIMILARITY_CLUSTER_RESULTS = 5  # Number of similar events per cluster
MAX_SIMILARITY_SCORE = 1.0  # Maximum similarity score
SIMILARITY_DECAY_RATE = 0.1  # Decay rate for similarity ranking
RECENT_CUTOFF_DAYS = 7  # Days cutoff for "recent" events


class ExaSearchClient(BaseAPIClient):
    """Client for Exa AI - Neural search for high-quality content."""

    def __init__(self):
        """Initialize Exa Search client."""
        super().__init__(
            base_url="https://api.exa.ai",
            api_key=Settings.EXA_API_KEY,
        )
        self.num_results = Settings.EXA_NUM_RESULTS
        self.use_autoprompt = Settings.EXA_USE_AUTOPROMPT

    def _get_headers(self) -> Dict[str, str]:
        """Override headers for Exa authentication."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

    @cache_response(ttl_minutes=30)
    def neural_search(
        self,
        query: str,
        num_results: Optional[int] = None,
        use_autoprompt: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform neural search for geopolitical content.

        Args:
            query: Search query
            num_results: Number of results to return
            use_autoprompt: Use Exa's autoprompt for better results
            category: Content category filter

        Returns:
            Neural search results
        """
        num = num_results or self.num_results
        autoprompt = use_autoprompt if use_autoprompt is not None else self.use_autoprompt

        payload = {
            "query": query,
            "numResults": num,
            "useAutoprompt": autoprompt,
            "type": "neural",
        }

        if category:
            payload["category"] = category

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            return {
                "query": query,
                "results": response["results"],
                "autoprompt_string": response.get("autopromptString"),
                "total_results": len(response["results"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_search_response(query)

    @cache_response(ttl_minutes=60)
    def find_similar_events(
        self,
        event_description: str,
        num_results: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find similar geopolitical events across history.

        Args:
            event_description: Description of the event
            num_results: Number of similar events to find
            start_date: Start date for historical search
            end_date: End date for historical search

        Returns:
            Similar events with relevance scores
        """
        payload = {
            "query": f"Similar geopolitical events to: {event_description}",
            "numResults": num_results,
            "useAutoprompt": True,
            "type": "neural",
        }

        # Add date filters if provided
        if start_date or end_date:
            payload["startPublishedDate"] = start_date
            payload["endPublishedDate"] = end_date

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            # Calculate similarity scores
            results_with_scores = self._add_similarity_scores(
                response["results"],
                event_description,
            )

            return {
                "event": event_description,
                "similar_events": results_with_scores,
                "count": len(results_with_scores),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"event": event_description, "similar_events": [], "count": 0}

    @cache_response(ttl_minutes=120)
    def discover_expert_analysis(
        self,
        topic: str,
        domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Discover expert analysis and think tank reports.

        Args:
            topic: Topic to search for
            domains: Specific domains to search (think tanks, research orgs)

        Returns:
            Expert analysis and reports
        """
        expert_domains = domains or [
            "cfr.org",  # Council on Foreign Relations
            "csis.org",  # Center for Strategic and International Studies
            "chathamhouse.org",  # Chatham House
            "brookings.edu",  # Brookings Institution
            "rand.org",  # RAND Corporation
            "carnegieendowment.org",  # Carnegie Endowment
            "crisisgroup.org",  # International Crisis Group
        ]

        payload = {
            "query": f"Expert analysis on {topic}",
            "numResults": EXPERT_SEARCH_RESULTS,
            "useAutoprompt": True,
            "type": "neural",
            "includeDomains": expert_domains,
        }

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            return {
                "topic": topic,
                "expert_content": response["results"],
                "sources": self._extract_unique_sources(response["results"]),
                "count": len(response["results"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"topic": topic, "expert_content": [], "count": 0}

    @cache_response(ttl_minutes=180)
    def identify_emerging_narratives(
        self,
        region: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Identify emerging narratives before they trend.

        Args:
            region: Region to analyze
            days: Number of days to look back

        Returns:
            Emerging narratives and trends
        """
        end_date = datetime.utcnow().isoformat()
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        payload = {
            "query": f"Emerging geopolitical narratives and trends in {region}",
            "numResults": NARRATIVE_SEARCH_RESULTS,
            "useAutoprompt": True,
            "type": "neural",
            "startPublishedDate": start_date,
            "endPublishedDate": end_date,
        }

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            # Cluster results by narrative themes
            narratives = self._cluster_by_narrative(response["results"])

            return {
                "region": region,
                "time_period": f"{days} days",
                "narratives": narratives,
                "total_sources": len(response["results"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"region": region, "narratives": [], "total_sources": 0}

    @cache_response(ttl_minutes=60)
    def content_recommendations(
        self,
        current_content: str,
        num_recommendations: int = 5,
    ) -> Dict[str, Any]:
        """
        Get content recommendations based on current analysis.

        Args:
            current_content: Current content being viewed
            num_recommendations: Number of recommendations

        Returns:
            Recommended related content
        """
        payload = {
            "query": f"Content related to: {current_content[:500]}",
            "numResults": num_recommendations,
            "useAutoprompt": True,
            "type": "neural",
        }

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            return {
                "recommendations": response["results"],
                "count": len(response["results"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"recommendations": [], "count": 0}

    @cache_response(ttl_minutes=240)
    def search_academic_research(
        self,
        topic: str,
        num_results: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for academic research and scholarly articles.

        Args:
            topic: Research topic
            num_results: Number of results

        Returns:
            Academic research results
        """
        academic_domains = [
            "scholar.google.com",
            "jstor.org",
            "academia.edu",
            "researchgate.net",
            "ssrn.com",
        ]

        payload = {
            "query": f"Academic research on {topic}",
            "numResults": num_results,
            "useAutoprompt": True,
            "type": "neural",
            "category": "research paper",
            "includeDomains": academic_domains,
        }

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            return {
                "topic": topic,
                "research_papers": response["results"],
                "count": len(response["results"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"topic": topic, "research_papers": [], "count": 0}

    @cache_response(ttl_minutes=120)
    def policy_document_search(
        self,
        query: str,
        governments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for policy documents and government publications.

        Args:
            query: Search query
            governments: Specific government domains to search

        Returns:
            Policy documents
        """
        gov_domains = governments or [
            "state.gov",
            "whitehouse.gov",
            "europa.eu",
            "un.org",
            "imf.org",
            "worldbank.org",
        ]

        payload = {
            "query": f"Policy documents on {query}",
            "numResults": POLICY_SEARCH_RESULTS,
            "useAutoprompt": True,
            "type": "neural",
            "includeDomains": gov_domains,
        }

        response = self.post("search", json_data=payload)

        if response and "results" in response:
            return {
                "query": query,
                "policy_documents": response["results"],
                "count": len(response["results"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"query": query, "policy_documents": [], "count": 0}

    @cache_response(ttl_minutes=90)
    def similarity_clustering(
        self,
        events: List[str],
    ) -> Dict[str, Any]:
        """
        Cluster geopolitical events by similarity.

        Args:
            events: List of event descriptions

        Returns:
            Clustered events with similarity scores
        """
        clusters = {}

        # Search for each event and find similar ones
        for event in events:
            similar = self.find_similar_events(event, num_results=SIMILARITY_CLUSTER_RESULTS)
            clusters[event] = similar.get("similar_events", [])

        return {
            "original_events": events,
            "clusters": clusters,
            "total_clusters": len(clusters),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _add_similarity_scores(
        self,
        results: List[Dict[str, Any]],
        reference_event: str,
    ) -> List[Dict[str, Any]]:
        """Add similarity scores to results (placeholder for actual scoring)."""
        # In production, this would use embeddings or other similarity metrics
        for i, result in enumerate(results):
            # Simple scoring based on position (Exa returns most relevant first)
            result["similarity_score"] = round(
                MAX_SIMILARITY_SCORE - (i * SIMILARITY_DECAY_RATE), 2
            )

        return results

    def _extract_unique_sources(
        self,
        results: List[Dict[str, Any]],
    ) -> List[str]:
        """Extract unique source domains from results."""
        sources = set()
        for result in results:
            url = result.get("url", "")
            if url:
                # Extract domain
                domain = url.split("//")[-1].split("/")[0]
                sources.add(domain)

        return sorted(list(sources))

    def _cluster_by_narrative(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Cluster results by narrative themes (simplified implementation)."""
        # In production, this would use NLP clustering
        # For now, return results grouped by timeframe
        narratives = []

        # Simple grouping by recent vs older content
        recent = []
        older = []

        cutoff = datetime.utcnow() - timedelta(days=RECENT_CUTOFF_DAYS)

        for result in results:
            pub_date = result.get("publishedDate")
            if pub_date:
                try:
                    pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    if pub_dt >= cutoff:
                        recent.append(result)
                    else:
                        older.append(result)
                except (ValueError, AttributeError):
                    recent.append(result)
            else:
                recent.append(result)

        if recent:
            narratives.append(
                {
                    "theme": "Recent Developments",
                    "content": recent,
                    "count": len(recent),
                }
            )

        if older:
            narratives.append(
                {
                    "theme": "Established Trends",
                    "content": older,
                    "count": len(older),
                }
            )

        return narratives

    def _empty_search_response(self, query: str) -> Dict[str, Any]:
        """Return empty search response structure."""
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }
