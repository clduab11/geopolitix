"""Tests for base API client."""

import pytest
from unittest.mock import patch, MagicMock
import requests

from src.data_sources.base import BaseAPIClient


class TestBaseAPIClient:
    """Test cases for BaseAPIClient."""

    def test_init(self):
        """Test client initialization."""
        client = BaseAPIClient("https://api.example.com", "test_key")
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test_key"

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        client = BaseAPIClient("https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_get_headers_with_api_key(self):
        """Test headers include authorization when API key is set."""
        client = BaseAPIClient("https://api.example.com", "test_key")
        headers = client._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_key"

    def test_get_headers_without_api_key(self):
        """Test headers without authorization when no API key."""
        client = BaseAPIClient("https://api.example.com")
        headers = client._get_headers()
        assert "Authorization" not in headers

    @patch("requests.Session.get")
    def test_get_success(self, mock_get):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = BaseAPIClient("https://api.example.com")
        result = client.get("endpoint")

        assert result == {"data": "test"}

    @patch("requests.Session.get")
    def test_get_timeout(self, mock_get):
        """Test GET request timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout()

        client = BaseAPIClient("https://api.example.com")
        result = client.get("endpoint")

        assert result is None

    @patch("requests.Session.get")
    def test_get_http_error(self, mock_get):
        """Test GET request HTTP error handling."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(text="Error")
        )
        mock_get.return_value = mock_response

        client = BaseAPIClient("https://api.example.com")
        result = client.get("endpoint")

        assert result is None

    @patch("requests.Session.post")
    def test_post_success(self, mock_post):
        """Test successful POST request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = BaseAPIClient("https://api.example.com")
        result = client.post("endpoint", json_data={"key": "value"})

        assert result == {"result": "success"}

    @patch("requests.Session.head")
    def test_health_check_success(self, mock_head):
        """Test health check success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        client = BaseAPIClient("https://api.example.com")
        result = client.health_check()

        assert result is True

    @patch("requests.Session.head")
    def test_health_check_failure(self, mock_head):
        """Test health check failure."""
        mock_head.side_effect = Exception("Connection error")

        client = BaseAPIClient("https://api.example.com")
        result = client.health_check()

        assert result is False
