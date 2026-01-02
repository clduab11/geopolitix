"""
Local file-based cache for signal providers.
"""

import os
import json
import hashlib
import time
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CACHE_DIR = "artifacts/cache"
DEFAULT_TTL_MINUTES = 15


class SignalsCache:
    """
    Simple filesystem cache keyed by (provider, operation, inputs_hash).
    """

    def __init__(self, ttl_minutes: int = DEFAULT_TTL_MINUTES):
        self.ttl_minutes = ttl_minutes
        self.cache_dir = CACHE_DIR
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, provider: str, operation: str, **kwargs) -> str:
        """Generate a stable cache key."""
        # Sort kwargs to ensure stability
        stable_inputs = json.dumps(kwargs, sort_keys=True, default=str)
        input_hash = hashlib.sha256(stable_inputs.encode()).hexdigest()
        return f"{provider}_{operation}_{input_hash}.json"

    def get(self, provider: str, operation: str, **kwargs) -> Optional[Any]:
        """Retrieve from cache if exists and not expired."""
        key = self._get_cache_key(provider, operation, **kwargs)
        path = os.path.join(self.cache_dir, key)

        if not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)

            cached_ts = cached_data.get("_cached_at")
            if not cached_ts:
                return None

            # Check expiry
            cached_dt = datetime.fromisoformat(cached_ts)
            if datetime.utcnow() - cached_dt > timedelta(minutes=self.ttl_minutes):
                # Expired
                return None

            return cached_data.get("data")

        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None

    def set(self, data: Any, provider: str, operation: str, **kwargs):
        """Save data to cache."""
        key = self._get_cache_key(provider, operation, **kwargs)
        path = os.path.join(self.cache_dir, key)

        cache_packet = {
            "_cached_at": datetime.utcnow().isoformat(),
            "_key_params": kwargs,  # Store metadata for debugging
            "data": data,
        }

        try:
            # Atomic write pattern to avoid partial reads
            tmp_path = path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(cache_packet, f, default=str)
            os.rename(tmp_path, path)
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")
