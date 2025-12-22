"""
Shared response cache for API calls with batched saves and graceful shutdown.
"""

import json
import os
import asyncio
import hashlib
import atexit
import signal

# Global registry of cache instances for cleanup
_cache_instances = []


class ResponseCache:
    """Cache for API responses to avoid duplicate calls."""

    def __init__(self, cache_file, save_every=100):
        self.cache_file = cache_file
        self.cache = {}
        self.lock = asyncio.Lock()
        self.save_every = save_every
        self.unsaved_count = 0
        self.load_cache()
        _cache_instances.append(self)

    def load_cache(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
            print(f"Loaded {len(self.cache)} cached responses from {self.cache_file}")
        else:
            self.cache = {}

    async def save_cache(self, force=False):
        """Save cache to disk if enough writes have accumulated or force=True."""
        if not force and self.unsaved_count < self.save_every:
            return
        async with self.lock:
            # Re-check under lock in case another task just saved
            if not force and self.unsaved_count < self.save_every:
                return
            self._save_cache_sync()

    def _save_cache_sync(self):
        """Synchronous cache save (for use in signal handlers and atexit)."""
        if self.unsaved_count == 0:
            return
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False)
            self.unsaved_count = 0
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def make_cache_key(self, key_dict):
        """Create a cache key from a dictionary of parameters."""
        key_str = json.dumps(key_dict, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get(self, key_dict):
        """Get cached response if it exists."""
        cache_key = self.make_cache_key(key_dict)
        return self.cache.get(cache_key)

    async def set(self, key_dict, response_data):
        """Store response in cache and periodically save to disk."""
        cache_key = self.make_cache_key(key_dict)
        async with self.lock:
            self.cache[cache_key] = response_data
            self.unsaved_count += 1
        # Save cache to disk if threshold reached
        await self.save_cache()


def _save_all_caches_sync():
    """Save all registered caches (for use in signal handlers and atexit)."""
    for cache in _cache_instances:
        cache._save_cache_sync()


def _save_caches_on_exit():
    """Save caches when program exits."""
    print("\nSaving cache before exit...")
    _save_all_caches_sync()


def _signal_handler(signum, frame):
    """Handle interrupt signals by saving cache and exiting."""
    print(f"\nReceived signal {signum}, saving cache...")
    _save_all_caches_sync()
    exit(1)


# Register cleanup handlers
atexit.register(_save_caches_on_exit)
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)
