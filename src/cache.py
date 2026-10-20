"""
ResponseCache — disk-backed cache for agent responses.

Responses are stored as JSON files inside the `cache/` directory
(relative to the working directory).  The cache key is the SHA-256
digest of ``"{agent_name}:{input_text}"``, so collisions across
different agents or inputs are practically impossible.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional


CACHE_DIR = "cache"


class ResponseCache:
    """Disk-backed cache for agent responses.

    Each entry is stored as ``cache/<sha256>.json`` containing:
    - agent_name   : str   — name of the agent that produced the response
    - input_hash   : str   — the SHA-256 key
    - response     : str   — the cached response text
    - cached_at    : str   — ISO-8601 UTC timestamp of when it was stored
    - hits         : int   — number of times this entry has been read
    """

    def __init__(self, cache_dir: str = CACHE_DIR) -> None:
        self.cache_dir = cache_dir
        self._ensure_dir()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_dir(self) -> None:
        """Create the cache directory if it does not already exist."""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _key(self, agent_name: str, input_text: str) -> str:
        """Return the SHA-256 hex digest for the given agent + input pair."""
        raw = f"{agent_name}:{input_text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _path(self, key: str) -> str:
        """Return the absolute file path for a cache key."""
        return os.path.join(self.cache_dir, f"{key}.json")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, agent_name: str, input_text: str) -> Optional[str]:
        """Return the cached response string, or ``None`` on a miss.

        If the entry exists its ``hits`` counter is incremented and the
        file is rewritten before returning the response.

        Parameters
        ----------
        agent_name:
            The logical name of the agent (e.g. ``"CodegenAgent"``).
        input_text:
            The raw input that was sent to the agent.

        Returns
        -------
        The cached response string, or ``None`` if not found.
        """
        key = self._key(agent_name, input_text)
        path = self._path(key)

        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

        try:
            data["hits"] = int(data.get("hits", 0)) + 1
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError:
            # Non-fatal — still return the response even if we can't persist
            # the updated hit count.
            pass

        return data.get("response")

    def set(self, agent_name: str, input_text: str, response: str) -> None:
        """Persist a response to disk.

        Parameters
        ----------
        agent_name:
            The logical name of the agent (e.g. ``"CodegenAgent"``).
        input_text:
            The raw input that was sent to the agent.
        response:
            The response string to cache.
        """
        self._ensure_dir()
        key = self._key(agent_name, input_text)
        path = self._path(key)

        data = {
            "agent_name": agent_name,
            "input_hash": key,
            "response": response,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "hits": 0,
        }

        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            # Log the problem but don't crash the caller.
            print(f"[ResponseCache] WARNING: could not write cache entry: {exc}")

    def clear(self) -> None:
        """Delete all ``*.json`` files from the cache directory."""
        self._ensure_dir()
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except OSError as exc:
                    print(f"[ResponseCache] WARNING: could not delete {filename}: {exc}")

    def stats(self) -> dict:
        """Return aggregate statistics about the cache.

        Returns
        -------
        dict with keys:
        - ``total_cached``    : number of JSON files in the cache directory
        - ``cache_size_bytes``: total size of those files in bytes
        - ``hits_total``      : sum of the ``hits`` field across all entries
        """
        self._ensure_dir()
        total_cached = 0
        cache_size_bytes = 0
        hits_total = 0

        for filename in os.listdir(self.cache_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(self.cache_dir, filename)
            total_cached += 1
            try:
                cache_size_bytes += os.path.getsize(filepath)
                with open(filepath, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                hits_total += int(data.get("hits", 0))
            except (OSError, json.JSONDecodeError):
                pass

        return {
            "total_cached": total_cached,
            "cache_size_bytes": cache_size_bytes,
            "hits_total": hits_total,
        }
