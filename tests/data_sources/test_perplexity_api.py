"""Tests for Perplexity Sonar API client."""

from unittest.mock import MagicMock, patch
import pytest

from src.data_sources.perplexity_api import (
    PerplexityClient,
    MODEL_CONFIG,
    FINANCE_DOMAINS,
)


class TestPerplexityClient:
    """Test cases for PerplexityClient."""

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = ""
            client.client = None
            client.default_model = "sonar-pro"

            assert not client._is_available()

    def test_get_available_models(self):
        """Test that model config is returned."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = "test_key"
            client.default_model = "sonar-pro"

            models = client.get_available_models()

            assert "sonar-pro" in models
            assert "sonar" in models
            assert "sonar-deep-research" in models
            assert models["sonar-pro"]["cost"] == "moderate"

    def test_select_model_quick(self):
        """Test model selection for quick use case."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.default_model = "sonar-pro"

            assert client.select_model("quick") == "sonar"

    def test_select_model_detailed(self):
        """Test model selection for detailed use case."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.default_model = "sonar-pro"

            assert client.select_model("detailed") == "sonar-pro"

    def test_select_model_research(self):
        """Test model selection for research use case."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.default_model = "sonar-pro"

            assert client.select_model("research") == "sonar-deep-research"

    def test_select_model_default(self):
        """Test model selection for default use case."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.default_model = "sonar-pro"

            assert client.select_model("default") == "sonar-pro"

    def test_query_returns_empty_when_not_available(self):
        """Test query returns empty response when API not available."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = ""
            client.client = None
            client.default_model = "sonar-pro"

            result = client.query("Test prompt")

            assert result["content"] == ""
            assert result["error"] == "API not configured"

    @patch("src.data_sources.perplexity_api.OpenAI")
    def test_query_success(self, mock_openai):
        """Test successful query execution."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test analysis"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 300

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = "test_key"
            client.client = mock_client
            client.default_model = "sonar-pro"

            result = client.query("Analyze AAPL stock")

            assert result["content"] == "Test analysis"
            assert result["model"] == "sonar-pro"
            assert result["usage"]["total_tokens"] == 300

    @patch("src.data_sources.perplexity_api.OpenAI")
    def test_query_with_custom_model(self, mock_openai):
        """Test query with custom model selection."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Quick analysis"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = "test_key"
            client.client = mock_client
            client.default_model = "sonar-pro"

            result = client.query("Quick lookup", model="sonar")

            assert result["content"] == "Quick analysis"
            assert result["model"] == "sonar"

    @patch("src.data_sources.perplexity_api.OpenAI")
    def test_query_falls_back_to_default_for_unknown_model(self, mock_openai):
        """Test query falls back to default model for unknown model."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Analysis"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = "test_key"
            client.client = mock_client
            client.default_model = "sonar-pro"

            result = client.query("Test", model="unknown-model")

            assert result["model"] == "sonar-pro"

    def test_extract_citations_with_citations(self):
        """Test citation extraction when citations exist."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = "test_key"

            mock_response = MagicMock()
            mock_response.citations = [
                "https://example.com/source1",
                "https://example.com/source2",
            ]

            citations = client._extract_citations(mock_response)

            assert len(citations) == 2
            assert citations[0]["url"] == "https://example.com/source1"
            assert citations[1]["index"] == 2

    def test_extract_citations_without_citations(self):
        """Test citation extraction when no citations exist."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = "test_key"

            mock_response = MagicMock(spec=[])  # No citations attribute

            citations = client._extract_citations(mock_response)

            assert len(citations) == 0

    def test_empty_response_structure(self):
        """Test empty response structure."""
        with patch.object(
            PerplexityClient, "__init__", lambda self: None
        ):
            client = PerplexityClient()
            client.api_key = ""

            response = client._empty_response("Test error")

            assert response["content"] == ""
            assert response["citations"] == []
            assert response["error"] == "Test error"
            assert "timestamp" in response


class TestModelConfig:
    """Test cases for model configuration."""

    def test_model_config_has_required_models(self):
        """Test that all required models are configured."""
        required_models = ["sonar-pro", "sonar", "sonar-deep-research"]
        for model in required_models:
            assert model in MODEL_CONFIG

    def test_sonar_pro_config(self):
        """Test sonar-pro configuration."""
        config = MODEL_CONFIG["sonar-pro"]
        assert "use_case" in config
        assert "features" in config
        assert "citations" in config["features"]

    def test_sonar_config(self):
        """Test sonar configuration."""
        config = MODEL_CONFIG["sonar"]
        assert config["cost"] == "low"

    def test_deep_research_config(self):
        """Test sonar-deep-research configuration."""
        config = MODEL_CONFIG["sonar-deep-research"]
        assert "processing_time" in config


class TestFinanceDomains:
    """Test cases for finance domain filters."""

    def test_finance_domains_not_empty(self):
        """Test that finance domains list is not empty."""
        assert len(FINANCE_DOMAINS) > 0

    def test_finance_domains_contains_sec(self):
        """Test that SEC is in finance domains."""
        assert "sec.gov" in FINANCE_DOMAINS

    def test_finance_domains_contains_financial_news(self):
        """Test that major financial news sites are included."""
        assert "bloomberg.com" in FINANCE_DOMAINS
        assert "reuters.com" in FINANCE_DOMAINS
