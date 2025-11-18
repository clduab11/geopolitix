"""Base API client with resilient HTTP handling."""

from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import Settings
from src.utils.logger import get_api_logger

logger = get_api_logger()


class BaseAPIClient:
    """Base class for all API integrations with retry logic and error handling."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        retry_strategy = Retry(
            total=Settings.MAX_RETRIES,
            backoff_factor=Settings.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            JSON response data or None on error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or Settings.REQUEST_TIMEOUT

        try:
            response = self.session.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"API timeout for {url}")
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text[:500]}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None

        except ValueError as e:
            logger.error(f"JSON decode error for {url}: {e}")
            return None

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            timeout: Request timeout in seconds

        Returns:
            JSON response data or None on error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or Settings.REQUEST_TIMEOUT

        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=self._get_headers(),
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"API timeout for POST {url}")
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for POST {url}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for POST {url}: {e}")
            return None

        except ValueError as e:
            logger.error(f"JSON decode error for POST {url}: {e}")
            return None

    def health_check(self) -> bool:
        """
        Check if the API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.session.head(
                self.base_url,
                timeout=5,
            )
            return response.status_code < 500
        except Exception:
            return False
