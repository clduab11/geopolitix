"""Tests for the RateLimiter utility."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from src.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter."""

    def test_init(self):
        """Test initialization."""
        limiter = RateLimiter()
        assert limiter._limits == {}
        assert limiter._state == {}

    def test_set_limit(self):
        """Test setting limits."""
        limiter = RateLimiter()
        limiter.set_limit("test_service", 10, 60)
        assert "test_service" in limiter._limits
        assert limiter._limits["test_service"] == (10, 60)
        assert "test_service" in limiter._state

    def test_check_limit_allowed(self):
        """Test allowed requests."""
        limiter = RateLimiter()
        limiter.set_limit("test_service", 10, 60)

        # Should allow 10 requests
        for _ in range(10):
            assert limiter.check_limit("test_service") is True

    def test_check_limit_exceeded(self):
        """Test exceeded limits."""
        limiter = RateLimiter()
        limiter.set_limit("test_service", 1, 60)

        assert limiter.check_limit("test_service") is True
        assert limiter.check_limit("test_service") is False

    def test_no_limit_set(self):
        """Test checking limit for service with no limit allowed."""
        limiter = RateLimiter()
        assert limiter.check_limit("unknown_service") is True

    def test_token_refill(self):
        """Test that tokens refill over time."""
        limiter = RateLimiter()
        # 1 call per second
        limiter.set_limit("test_service", 1, 1)

        assert limiter.check_limit("test_service") is True
        assert limiter.check_limit("test_service") is False

        # Manually advance time by mocking time.time
        with patch("time.time") as mock_time:
            # Initial time
            start_time = 1000.0
            mock_time.return_value = start_time

            # Reset state with known time
            limiter._state["test_service"] = (0.0, start_time)

            # Advance time by 1.1 seconds
            mock_time.return_value = start_time + 1.1

            # Should be allowed now
            assert limiter.check_limit("test_service") is True

    def test_wait_for_token_success(self):
        """Test waiting for a token successfully."""
        limiter = RateLimiter()
        limiter.set_limit("test_service", 1, 1)

        # Consume the token
        limiter.check_limit("test_service")

        # Mock time and sleep to simulate waiting
        with patch("time.time") as mock_time, patch("time.sleep") as mock_sleep:
            start_time = 1000.0
            # Sequence of times: start, loop1 (still blocked), loop2 (refilled)
            mock_time.side_effect = [
                start_time,  # Initial check
                start_time + 0.1,  # In loop
                start_time + 1.1,  # Refilled
            ]

            # Manually refill in the "thread" (since we mocked time)
            # In real life, check_limit calculates refill based on real time
            # checking logic handles the refill calculation

            # We need to ensure check_limit sees the advanced time
            # The side_effect above handles the calls inside wait_for_token

            # However, since check_limit calls time.time() internally, we need to match that
            # limit.check_limit calls time-time() once

            # Let's just use a simpler approach:
            # We trust manual refill logic test.
            # Here we test the wait loop.

            # Mock check_limit to return False then True
            limiter.check_limit = MagicMock(side_effect=[False, True])

            assert limiter.wait_for_token("test_service", timeout=2.0) is True
            assert limiter.check_limit.call_count == 2
