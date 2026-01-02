"""
HTTP Client with resilience patterns (retries, backoff, rate limiting).
"""

import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    A wrapper around requests.Session with built-in retry logic and basic rate limiting.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        rate_limit_delay: float = 0.0,  # Min seconds between requests
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0.0

        # Configure Retry Strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
        )

        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _rate_limit(self):
        """Ensure minimum delay between requests."""
        if self.rate_limit_delay > 0:
            elapsed = time.time() - self.last_request_time
            wait = self.rate_limit_delay - elapsed
            if wait > 0:
                time.sleep(wait)
            self.last_request_time = time.time()

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """
        Execute an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: URL path (appended to base_url)
            params: Query parameters
            json_data: JSON body
            headers: Custom headers
            timeout: Request specific timeout

        Returns:
            parsed JSON response or raw response if parse fails/not JSON

        Raises:
            requests.exceptions.RequestException
        """
        self._rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=timeout or self.timeout,
            )
            response.raise_for_status()

            try:
                return response.json()
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {method} {url} - {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> Any:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Any:
        return self.request("POST", endpoint, **kwargs)
