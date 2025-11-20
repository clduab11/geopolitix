"""Perplexity Sonar Reasoning Pro integration for deep geopolitical analysis."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Constants for content limits and processing
MAX_ARTICLES_FOR_SYNTHESIS = 10  # Maximum articles to process for synthesis
SUMMARY_CONTENT_LIMIT = 200  # Character limit for data source summaries


class SonarReasoningClient(BaseAPIClient):
    """Client for Perplexity Sonar Reasoning Pro - Advanced AI analysis."""

    def __init__(self):
        """Initialize Sonar Reasoning client."""
        super().__init__(
            base_url="https://api.perplexity.ai",
            api_key=Settings.PERPLEXITY_API_KEY,
        )
        self.model = Settings.PERPLEXITY_REASONING_MODEL

    @cache_response(ttl_minutes=60)
    def deep_dive_analysis(
        self,
        country: str,
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive deep dive analysis of country risk.

        Args:
            country: Country name or code
            focus_areas: Specific areas to focus on (political, economic, security)

        Returns:
            Comprehensive analysis with reasoning chain
        """
        focus = (
            f"Focus on: {', '.join(focus_areas)}"
            if focus_areas
            else "Cover all aspects"
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert geopolitical analyst. Provide "
                    "comprehensive risk analysis with detailed reasoning, "
                    "evidence, and citations. Structure your analysis with "
                    "clear sections and actionable insights.",
                },
                {
                    "role": "user",
                    "content": f"Provide a comprehensive geopolitical risk analysis "
                    f"for {country}. {focus}. Include: 1) Current "
                    f"situation, 2) Key risk factors, 3) Historical "
                    f"context, 4) Future outlook, 5) Recommendations.",
                },
            ],
            "return_citations": True,
            "return_images": False,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            choice = response["choices"][0]
            return {
                "country": country,
                "focus_areas": focus_areas,
                "analysis": choice["message"]["content"],
                "reasoning_chain": self._extract_reasoning(choice),
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return self._empty_analysis(country)

    @cache_response(ttl_minutes=30)
    def synthesize_news(
        self,
        articles: List[Dict[str, Any]],
        country: str,
    ) -> Dict[str, Any]:
        """
        Synthesize multiple news sources into executive summary.

        Args:
            articles: List of article dictionaries
            country: Country name

        Returns:
            Executive summary with key insights
        """
        # Prepare article summaries for analysis
        article_texts = []
        for i, article in enumerate(articles[:MAX_ARTICLES_FOR_SYNTHESIS], 1):
            title = article.get("title", "")
            description = article.get("description", "")
            article_texts.append(f"{i}. {title}: {description}")

        articles_str = "\n".join(article_texts)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an intelligence analyst. Synthesize "
                    "multiple news sources into a concise executive "
                    "summary with key themes, trends, and implications.",
                },
                {
                    "role": "user",
                    "content": f"Synthesize these news articles about {country} "
                    f"into an executive summary:\n\n{articles_str}",
                },
            ],
            "return_citations": False,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "country": country,
                "article_count": len(articles),
                "summary": response["choices"][0]["message"]["content"],
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"country": country, "summary": "", "article_count": 0}

    @cache_response(ttl_minutes=120)
    def identify_trends(
        self,
        data_sources: Dict[str, Any],
        time_period: str = "30 days",
    ) -> Dict[str, Any]:
        """
        Identify emerging patterns and trends across data sources.

        Args:
            data_sources: Dictionary of data from various sources
            time_period: Time period for trend analysis

        Returns:
            Identified trends and patterns
        """
        # Summarize data sources for the AI
        data_summary = self._summarize_data_sources(data_sources)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strategic analyst. Identify emerging "
                    "patterns, trends, and weak signals that may indicate "
                    "future geopolitical developments.",
                },
                {
                    "role": "user",
                    "content": f"Analyze this geopolitical data from the past "
                    f"{time_period} and identify key trends:\n\n"
                    f"{data_summary}",
                },
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "time_period": time_period,
                "trends": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"time_period": time_period, "trends": ""}

    @cache_response(ttl_minutes=60)
    def validate_scenario(
        self,
        scenario_description: str,
        historical_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate user-created scenarios against historical data.

        Args:
            scenario_description: Description of the scenario
            historical_context: Optional historical context

        Returns:
            Validation analysis with probability assessment
        """
        context_part = (
            f"\n\nHistorical context: {historical_context}"
            if historical_context
            else ""
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a scenario planning expert. Validate "
                    "geopolitical scenarios against historical precedents "
                    "and assess plausibility.",
                },
                {
                    "role": "user",
                    "content": f"Validate this geopolitical scenario and assess "
                    f"its plausibility:\n\n{scenario_description}"
                    f"{context_part}",
                },
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "scenario": scenario_description,
                "validation": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"scenario": scenario_description, "validation": ""}

    @cache_response(ttl_minutes=90)
    def compare_countries(
        self,
        countries: List[str],
        comparison_factors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate detailed country comparisons with reasoning.

        Args:
            countries: List of countries to compare
            comparison_factors: Specific factors to compare

        Returns:
            Comparative analysis
        """
        countries_str = ", ".join(countries)
        factors_str = (
            f"Focus on: {', '.join(comparison_factors)}"
            if comparison_factors
            else "Compare across all risk dimensions"
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a comparative geopolitical analyst. "
                    "Provide structured comparisons with clear metrics "
                    "and reasoning.",
                },
                {
                    "role": "user",
                    "content": f"Compare these countries: {countries_str}. "
                    f"{factors_str}. Provide a structured comparison.",
                },
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "countries": countries,
                "comparison_factors": comparison_factors,
                "analysis": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"countries": countries, "analysis": ""}

    @cache_response(ttl_minutes=30)
    def prioritize_alerts(
        self,
        alerts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Use reasoning to rank and prioritize risk alerts by actual impact.

        Args:
            alerts: List of alert dictionaries

        Returns:
            Prioritized alerts with reasoning
        """
        # Format alerts for analysis
        alert_summary = self._format_alerts(alerts)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a risk assessment expert. Prioritize "
                    "geopolitical alerts by actual impact potential, "
                    "urgency, and strategic importance.",
                },
                {
                    "role": "user",
                    "content": f"Prioritize these geopolitical alerts and explain "
                    f"your reasoning:\n\n{alert_summary}",
                },
            ],
            "return_citations": False,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "original_count": len(alerts),
                "prioritization": response["choices"][0]["message"]["content"],
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"original_count": len(alerts), "prioritization": ""}

    @cache_response(ttl_minutes=60)
    def causal_inference(
        self,
        event: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Identify causality chains between events and risk factors.

        Args:
            event: Description of the event
            context: Contextual data (economic indicators, political events, etc.)

        Returns:
            Causal analysis with reasoning chain
        """
        context_str = self._format_context(context)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a causal inference expert. Identify "
                    "causality chains, contributing factors, and potential "
                    "cascading effects of geopolitical events.",
                },
                {
                    "role": "user",
                    "content": f"Analyze the causal factors and potential effects "
                    f"of this event:\n\nEvent: {event}\n\n"
                    f"Context: {context_str}",
                },
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "event": event,
                "causal_analysis": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {"event": event, "causal_analysis": ""}

    def generate_executive_brief(
        self,
        timeframe: str = "24h",
        focus_regions: Optional[List[str]] = None,
        data_summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI-powered executive briefing.

        Args:
            timeframe: Time period for the brief (24h, 7d, 30d)
            focus_regions: Optional list of regions to focus on
            data_summary: Summary data from various sources

        Returns:
            Executive briefing
        """
        regions_str = (
            f"Focus regions: {', '.join(focus_regions)}"
            if focus_regions
            else "Global coverage"
        )

        data_str = (
            self._summarize_data_sources(data_summary) if data_summary else ""
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an executive briefing analyst. Create "
                    "concise, actionable briefings for C-level executives. "
                    "Focus on strategic implications and key decisions.",
                },
                {
                    "role": "user",
                    "content": f"Generate an executive briefing for the past "
                    f"{timeframe}. {regions_str}.\n\n{data_str}",
                },
            ],
            "return_citations": True,
        }

        response = self.post("chat/completions", json_data=payload)

        if response and "choices" in response:
            return {
                "timeframe": timeframe,
                "focus_regions": focus_regions,
                "brief": response["choices"][0]["message"]["content"],
                "citations": response.get("citations", []),
                "generated_at": datetime.utcnow().isoformat(),
            }

        return {"timeframe": timeframe, "brief": ""}

    def _extract_reasoning(self, choice: Dict[str, Any]) -> List[str]:
        """
        Extract reasoning steps from response.

        Note: Currently returns empty list as Perplexity API does not
        expose intermediate reasoning steps in the response structure.
        This is a placeholder for future enhancement if the API adds
        this capability.

        Args:
            choice: Response choice object from API

        Returns:
            Empty list (reasoning steps not available from API)
        """
        # Perplexity API does not currently expose reasoning chain
        # in the response structure. If this changes in future API versions,
        # this method can be enhanced to parse and return those steps.
        return []

    def _summarize_data_sources(self, data: Dict[str, Any]) -> str:
        """Summarize data sources for AI consumption."""
        if not data:
            return "No data available"

        summary_parts = []
        for source, content in data.items():
            summary_parts.append(f"{source}: {str(content)[:SUMMARY_CONTENT_LIMIT]}...")

        return "\n".join(summary_parts)

    def _format_alerts(self, alerts: List[Dict[str, Any]]) -> str:
        """Format alerts for AI analysis."""
        formatted = []
        for i, alert in enumerate(alerts, 1):
            country = alert.get("country", "Unknown")
            alert_type = alert.get("alert_type", "Unknown")
            risk_score = alert.get("risk_score", 0)
            formatted.append(f"{i}. {country} - {alert_type} (Risk: {risk_score})")

        return "\n".join(formatted)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data for AI analysis."""
        if not context:
            return "No context provided"

        parts = [f"{k}: {v}" for k, v in context.items()]
        return ", ".join(parts)

    def _empty_analysis(self, country: str) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "country": country,
            "analysis": "",
            "timestamp": datetime.utcnow().isoformat(),
        }
