"""Centralized API-Football (API-SPORTS) client.

Responsibilities: shared async HTTP client, controlled retries/backoff,
rate-limit & daily-budget awareness (from provider response headers), in-memory
response caching, structured logging and error normalization. The free plan is
~100 requests/day, so every call is budgeted and logged.

The API key is read from settings (server-side only) and never logged.
"""
from __future__ import annotations

import time
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("providers.api_football")


class APIFootballError(RuntimeError):
    """Normalized provider error."""


class APIFootballBudgetExceeded(APIFootballError):
    """Raised when the configured daily request budget is exhausted."""


class _QuotaState:
    """Tracks remaining daily quota as reported by provider headers."""

    def __init__(self) -> None:
        self.requests_limit: int | None = None
        self.requests_remaining: int | None = None
        self.minute_remaining: int | None = None
        self.local_count: int = 0

    def update_from_headers(self, headers: httpx.Headers) -> None:
        def _get(name: str) -> int | None:
            v = headers.get(name)
            return int(v) if v is not None and v.isdigit() else None

        self.requests_limit = _get("x-ratelimit-requests-limit") or self.requests_limit
        self.requests_remaining = _get("x-ratelimit-requests-remaining")
        self.minute_remaining = _get("x-ratelimit-remaining")

    def snapshot(self) -> dict[str, int | None]:
        return {
            "requests_limit": self.requests_limit,
            "requests_remaining": self.requests_remaining,
            "minute_remaining": self.minute_remaining,
            "local_count_this_process": self.local_count,
        }


class APIFootballClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.api_football_base_url
        self._budget = settings.api_football_daily_budget
        self._reserve = settings.api_football_safety_reserve
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"x-apisports-key": settings.api_football_key},
            timeout=httpx.Timeout(20.0, connect=10.0),
        )
        self.quota = _QuotaState()
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._cache_ttl = 15 * 60  # seconds

    async def aclose(self) -> None:
        await self._client.aclose()

    def _cache_key(self, path: str, params: dict[str, Any] | None) -> str:
        items = sorted((params or {}).items())
        return path + "?" + "&".join(f"{k}={v}" for k, v in items)

    def _budget_ok(self) -> bool:
        remaining = self.quota.requests_remaining
        if remaining is None:
            # Fall back to local counting against the configured budget.
            return self.quota.local_count < (self._budget - self._reserve)
        return remaining > self._reserve

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
    )
    async def _request(self, path: str, params: dict[str, Any] | None) -> httpx.Response:
        return await self._client.get(path, params=params)

    async def get(
        self, path: str, params: dict[str, Any] | None = None, use_cache: bool = True
    ) -> dict[str, Any]:
        key = self._cache_key(path, params)
        if use_cache and key in self._cache:
            ts, payload = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                logger.debug("cache hit %s", key)
                return payload

        if not self._budget_ok():
            raise APIFootballBudgetExceeded(
                f"Daily API-Football budget reached (reserve={self._reserve}). "
                f"Quota: {self.quota.snapshot()}"
            )

        try:
            resp = await self._request(path, params)
        except httpx.HTTPError as exc:  # pragma: no cover - network dependent
            raise APIFootballError(f"Transport error calling {path}: {exc}") from exc

        self.quota.local_count += 1
        self.quota.update_from_headers(resp.headers)

        if resp.status_code != 200:
            raise APIFootballError(f"{path} returned HTTP {resp.status_code}")

        data = resp.json()
        errors = data.get("errors")
        if errors:
            # API-Football returns 200 with an errors object on quota/auth issues.
            raise APIFootballError(f"{path} provider errors: {errors}")

        if use_cache:
            self._cache[key] = (time.time(), data)
        logger.info(
            "GET %s -> %s results (remaining=%s)",
            path,
            data.get("results"),
            self.quota.requests_remaining,
        )
        return data

    async def get_status(self) -> dict[str, Any]:
        data = await self.get("status", use_cache=False)
        return {"response": data.get("response"), "quota": self.quota.snapshot()}
