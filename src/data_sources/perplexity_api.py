"""Perplexity Sonar API client for financial analysis with model selection."""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from openai import OpenAI

from config.settings import Settings
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Model configuration for Perplexity Sonar API
MODEL_CONFIG = {
    "sonar-pro": {
        "use_case": "Complex financial analysis, multi-step queries",
        "context_window": "large",
        "cost": "moderate",
        "features": ["citations", "real-time_search", "structured_output"],
    },
    "sonar": {
        "use_case": "Quick company lookups, factual queries",
        "context_window": "standard",
        "cost": "low",
        "features": ["citations", "basic_search"],
    },
    "sonar-deep-research": {
        "use_case": "In-depth market research, comprehensive reports",
        "context_window": "very_large",
        "cost": "high",
        "processing_time": "30+ minutes",
    },
}

# Domain filters for high-quality financial sources
FINANCE_DOMAINS = [
    "sec.gov",
    "bloomberg.com",
    "reuters.com",
    "wsj.com",
    "seekingalpha.com",
    "ft.com",
    "cnbc.com",
    "marketwatch.com",
]


class PerplexityClient:
    """Client for Perplexity Sonar API with model selection and citation support."""

    def __init__(self):
        """Initialize Perplexity client using OpenAI-compatible interface."""
        self.api_key = Settings.PERPLEXITY_API_KEY
        self.default_model = Settings.PERPLEXITY_FINANCE_MODEL

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai",
            )
        else:
            self.client = None
            logger.warning("Perplexity API key not configured")

    def _is_available(self) -> bool:
        """Check if the client is available."""
        return self.client is not None and bool(self.api_key)

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get available model configurations."""
        return MODEL_CONFIG.copy()

    def select_model(self, use_case: str = "default") -> str:
        """
        Select appropriate model based on use case.

        Args:
            use_case: Type of query - 'quick', 'detailed', 'research', or 'default'

        Returns:
            Model name string
        """
        model_map = {
            "quick": "sonar",
            "detailed": "sonar-pro",
            "research": "sonar-deep-research",
            "default": self.default_model,
        }
        return model_map.get(use_case, self.default_model)

    def query(
        self,
        prompt: str,
        model: Optional[str] = None,
        search_domain_filter: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute Perplexity Sonar API query with citations.

        Args:
            prompt: User query
            model: Model to use (sonar, sonar-pro, sonar-deep-research)
            search_domain_filter: List of domains to filter search
            system_prompt: Custom system prompt
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Dictionary with content, citations, usage, and model info
        """
        if not self._is_available():
            logger.warning("Perplexity API not available")
            return self._empty_response("API not configured")

        model = model or self.default_model
        if model not in MODEL_CONFIG:
            logger.warning(f"Unknown model {model}, falling back to {self.default_model}")
            model = self.default_model

        default_system = (
            "You are a financial analysis assistant specializing in "
            "geopolitical risk assessment. Provide accurate, well-sourced "
            "analysis with specific data and citations."
        )

        messages = [
            {"role": "system", "content": system_prompt or default_system},
            {"role": "user", "content": prompt},
        ]

        params: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            params["max_tokens"] = max_tokens

        if search_domain_filter:
            params["search_domain_filter"] = search_domain_filter

        try:
            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content
            citations = self._extract_citations(response)

            return {
                "content": content,
                "citations": citations,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "model": model,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            return self._empty_response(str(e))

    def _extract_citations(self, response: Any) -> List[Dict[str, str]]:
        """
        Extract and format citations from response.

        Args:
            response: API response object

        Returns:
            List of citation dictionaries with url and title
        """
        citations = []

        # Check for citations in response metadata
        if hasattr(response, "citations"):
            for i, url in enumerate(response.citations):
                citations.append({
                    "index": i + 1,
                    "url": url,
                    "title": f"Source {i + 1}",
                })

        return citations

    def _empty_response(self, error: str = "") -> Dict[str, Any]:
        """Return empty response structure."""
        return {
            "content": "",
            "citations": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": None,
            "error": error,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @cache_response(ttl_minutes=10)
    def analyze_stock(
        self,
        ticker: str,
        analysis_type: str = "overview",
    ) -> Dict[str, Any]:
        """
        Analyze a stock with AI-enhanced insights.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            analysis_type: Type of analysis ('overview', 'earnings', 'risk', 'technical')

        Returns:
            AI analysis with citations
        """
        analysis_prompts = {
            "overview": f"Provide a comprehensive overview of {ticker} stock including current price movement, key metrics, recent news, and market sentiment. Include specific data points.",
            "earnings": f"Analyze the latest earnings report for {ticker}. Focus on revenue growth, profit margins, forward guidance, and key risks. Include specific numbers and comparisons.",
            "risk": f"Evaluate major risks facing {ticker} including regulatory, competitive, geopolitical, and operational risks. Reference recent news and SEC filings.",
            "technical": f"Provide technical analysis for {ticker} including support/resistance levels, moving averages, volume patterns, and momentum indicators.",
        }

        prompt = analysis_prompts.get(analysis_type, analysis_prompts["overview"])

        return self.query(
            prompt=prompt,
            model=self.select_model("detailed"),
            search_domain_filter=FINANCE_DOMAINS,
        )

    @cache_response(ttl_minutes=10)
    def compare_stocks(
        self,
        ticker1: str,
        ticker2: str,
    ) -> Dict[str, Any]:
        """
        Compare two stocks across key metrics.

        Args:
            ticker1: First stock ticker
            ticker2: Second stock ticker

        Returns:
            Comparative analysis with citations
        """
        prompt = (
            f"Compare {ticker1} vs {ticker2} across: revenue growth, profitability, "
            f"valuation metrics (P/E, P/S, EV/EBITDA), and market positioning. "
            f"Use latest financial data with specific numbers and citations."
        )

        return self.query(
            prompt=prompt,
            model=self.select_model("detailed"),
            search_domain_filter=FINANCE_DOMAINS,
        )

    @cache_response(ttl_minutes=5)
    def get_geopolitical_impact(
        self,
        company: str,
        region: str,
    ) -> Dict[str, Any]:
        """
        Assess geopolitical impact on a company.

        Args:
            company: Company name or ticker
            region: Geographic region of concern

        Returns:
            Geopolitical impact analysis with citations
        """
        prompt = (
            f"Assess how recent geopolitical events in {region} affect {company}'s "
            f"operations, supply chain, and revenue. Provide specific examples, "
            f"revenue exposure percentages, and risk assessment with citations."
        )

        return self.query(
            prompt=prompt,
            model=self.select_model("detailed"),
            search_domain_filter=FINANCE_DOMAINS,
        )

    @cache_response(ttl_minutes=15)
    def get_market_sentiment(
        self,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Get market sentiment on a topic.

        Args:
            topic: Topic to analyze (e.g., 'tech sector', 'oil prices', 'inflation')

        Returns:
            Sentiment analysis with citations
        """
        prompt = (
            f"Analyze current market sentiment regarding {topic}. "
            f"Include investor positioning, recent price movements, "
            f"analyst opinions, and key sentiment indicators with citations."
        )

        return self.query(
            prompt=prompt,
            model=self.select_model("quick"),
            search_domain_filter=FINANCE_DOMAINS,
        )

    def ask_followup(
        self,
        original_query: str,
        original_response: str,
        followup_question: str,
    ) -> Dict[str, Any]:
        """
        Ask a follow-up question based on previous context.

        Args:
            original_query: The initial query
            original_response: The response to the initial query
            followup_question: The follow-up question

        Returns:
            Follow-up response with citations
        """
        prompt = (
            f"Based on this previous analysis:\n\n"
            f"Question: {original_query}\n"
            f"Analysis: {original_response[:2000]}\n\n"
            f"Please answer this follow-up question: {followup_question}"
        )

        return self.query(
            prompt=prompt,
            model=self.select_model("detailed"),
            search_domain_filter=FINANCE_DOMAINS,
        )
