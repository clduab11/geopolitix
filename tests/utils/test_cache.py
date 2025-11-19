"""Tests for caching utilities."""

from src.utils.cache import (
    cache_response,
    clear_cache,
    get_cache_stats,
    remove_from_cache,
)


class TestCacheResponse:
    """Test cache_response decorator."""

    def test_caches_result(self):
        """Test that results are cached."""
        call_count = 0

        @cache_response()
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1  # Still 1

    def test_different_args_not_cached(self):
        """Test that different arguments don't share cache."""
        call_count = 0

        @cache_response()
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        test_func(5)
        test_func(10)

        assert call_count == 2


class TestClearCache:
    """Test cache clearing."""

    def test_clear_cache(self):
        """Test that clear_cache clears all cached items."""

        @cache_response()
        def test_func(x):
            return x * 2

        # Cache some values
        test_func(1)
        test_func(2)

        # Clear cache
        clear_cache()

        # Check stats
        stats = get_cache_stats()
        assert stats["size"] == 0


class TestGetCacheStats:
    """Test cache statistics."""

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        clear_cache()

        stats = get_cache_stats()
        assert "size" in stats
        assert "maxsize" in stats
        assert "ttl" in stats


class TestRemoveFromCache:
    """Test removing specific cache entries."""

    def test_remove_from_cache(self):
        """Test removing a key from cache."""
        clear_cache()

        # This tests the function exists and works
        result = remove_from_cache("nonexistent_key")
        assert result is False
