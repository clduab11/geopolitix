"""
Specialized HTTP client for Web Signals.
Extends the base pattern with stricter rate limiting and size capping.
"""

import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SignalsHTTPClient:
    """
    HTTP Client with resilience patterns specifically for provider APIs.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 15,
        max_retries: int = 3,
        backoff_factor: float = 1.0,  # More conservative backoff
        rate_limit_delay: float = 0.0,
        max_response_size_bytes: int = 10 * 1024 * 1024,  # 10MB safety cap
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.max_response_size_bytes = max_response_size_bytes
        self.last_request_time = 0.0

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
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
        stream: bool = False,
    ) -> Any:
        """
        Execute request with size safety and rate limiting.
        """
        self._rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint

        try:
            # We use stream=True to check content-length before downloading everything if needed
            # But for simplicity in this implementation, we can just do a head check or use stream
            # to iterate and count bytes if we are really strict.
            # For most API JSON responses, standard request is fine, but for 'crawl' content it matters.

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
                stream=stream,
            )

            response.raise_for_status()

            # Size check logic
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_response_size_bytes:
                logger.warning(f"Response too large from {url}: {content_length} bytes")
                return None

            # If streaming, we return the response object for the caller to handle
            if stream:
                return response

            # Otherwise parse JSON or Text
            try:
                if len(response.content) > self.max_response_size_bytes:
                    logger.warning(f"Downloaded content exceeded limit from {url}")
                    return None
                return response.json()
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Signals HTTP Request failed: {method} {url} - {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> Any:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Any:
        return self.request("POST", endpoint, **kwargs)
