"""Rate limiting utility for API clients."""

import time
from threading import Lock
from typing import Dict, Optional, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Thread-safe in-memory rate limiter using token bucket algorithm.
    """

    def __init__(self):
        """Initialize rate limiter."""
        self._limits: Dict[
            str, Tuple[int, int]
        ] = {}  # service -> (calls, period_seconds)
        self._state: Dict[
            str, Tuple[int, float]
        ] = {}  # service -> (tokens, last_update)
        self._lock = Lock()

    def set_limit(
        self, service_name: str, max_calls: int, period_seconds: int = 60
    ) -> None:
        """
        Set rate limit for a service.

        Args:
            service_name: Name of the service (e.g., "newsapi")
            max_calls: Maximum number of calls allowed in the period
            period_seconds: Time period in seconds (default: 60)
        """
        with self._lock:
            self._limits[service_name] = (max_calls, period_seconds)
            # Initialize state with full tokens
            if service_name not in self._state:
                self._state[service_name] = (max_calls, time.time())

    def check_limit(self, service_name: str) -> bool:
        """
        Check if a request is allowed. Consumes a token if allowed.

        Args:
            service_name: Service to check

        Returns:
            True if allowed, False if limit exceeded
        """
        if service_name not in self._limits:
            return True  # No limit set

        max_calls, period = self._limits[service_name]

        with self._lock:
            current_tokens, last_update = self._state.get(
                service_name, (max_calls, time.time())
            )
            now = time.time()

            # Refill tokens based on elapsed time
            elapsed = now - last_update
            refill_rate = max_calls / period
            new_tokens = elapsed * refill_rate

            # Update token count, capped at max_calls
            current_tokens = min(max_calls, current_tokens + new_tokens)

            if current_tokens >= 1.0:
                self._state[service_name] = (current_tokens - 1.0, now)
                return True
            else:
                # Update time but keep tokens same (don't consume)
                self._state[service_name] = (current_tokens, now)
                return False

    def wait_for_token(self, service_name: str, timeout: float = 30.0) -> bool:
        """
        Block until a token is available or timeout reached.

        Args:
            service_name: Service to wait for
            timeout: Max time to wait in seconds

        Returns:
            True if token acquired, False if timed out
        """
        if service_name not in self._limits:
            return True

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_limit(service_name):
                return True
            time.sleep(0.5)

        logger.warning(
            f"Rate limit exceeded for {service_name} (timeout waiting for token)"
        )
        return False
