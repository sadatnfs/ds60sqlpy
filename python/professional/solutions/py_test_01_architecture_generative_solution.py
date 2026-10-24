"""Reference implementation for python-test-01."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol


class Clock(Protocol):
    def now(self) -> float:
        """Return monotonic-style seconds."""


class KeyValueStore(Protocol):
    def get(self, key: str) -> str | None:
        """Return a value or ``None``."""

    def put(self, key: str, value: str) -> None:
        """Create or replace a value."""

    def delete(self, key: str) -> bool:
        """Delete a value and report whether it existed."""


class AuditSink(Protocol):
    def record(self, event: str, subject: str) -> None:
        """Record one domain event."""


@dataclass(frozen=True)
class CacheSettings:
    ttl_seconds: float
    namespace: str


@dataclass
class FixedClock:
    value: float

    def now(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("cannot move a monotonic clock backward")
        self.value += seconds


@dataclass
class MemoryStore:
    values: dict[str, str]

    @classmethod
    def empty(cls) -> MemoryStore:
        return cls({})

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def put(self, key: str, value: str) -> None:
        self.values[key] = value

    def delete(self, key: str) -> bool:
        return self.values.pop(key, None) is not None


@dataclass
class JsonFileStore:
    """Small real-local boundary used by the same contract tests as the fake."""

    path: Path

    def _read(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in payload.items()
        ):
            raise ValueError("store file must contain a string-to-string object")
        return payload

    def _write(self, values: Mapping[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(dict(sorted(values.items())), separators=(",", ":")),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def get(self, key: str) -> str | None:
        return self._read().get(key)

    def put(self, key: str, value: str) -> None:
        values = self._read()
        values[key] = value
        self._write(values)

    def delete(self, key: str) -> bool:
        values = self._read()
        existed = values.pop(key, None) is not None
        if existed:
            self._write(values)
        return existed


@dataclass
class ExpiringCache:
    store: KeyValueStore
    clock: Clock
    settings: CacheSettings

    def _key(self, key: str) -> str:
        return f"{self.settings.namespace}:{key}"

    def put(self, key: str, value: str) -> None:
        payload = {
            "expires_at": self.clock.now() + self.settings.ttl_seconds,
            "value": value,
        }
        self.store.put(
            self._key(key),
            json.dumps(payload, separators=(",", ":"), sort_keys=True),
        )

    def get(self, key: str) -> str | None:
        storage_key = self._key(key)
        raw = self.store.get(storage_key)
        if raw is None:
            return None
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("cache payload must be an object")
        expires_at = payload.get("expires_at")
        value = payload.get("value")
        if not isinstance(expires_at, int | float) or not isinstance(value, str):
            raise ValueError("cache payload has the wrong schema")
        if self.clock.now() >= float(expires_at):
            self.store.delete(storage_key)
            return None
        return value


@dataclass
class SessionService:
    cache: ExpiringCache
    audit: AuditSink

    def issue(self, user_id: str, session_id: str) -> None:
        if not user_id or not session_id:
            raise ValueError("identifiers must not be blank")
        self.cache.put(user_id, session_id)
        self.audit.record("session_issued", user_id)


def load_cache_settings(
    environ: Mapping[str, str] | None = None,
) -> CacheSettings:
    values = os.environ if environ is None else environ
    namespace = values.get("DS60_CACHE_NAMESPACE", "sessions").strip()
    if not namespace:
        raise ValueError("DS60_CACHE_NAMESPACE must not be blank")
    try:
        ttl_seconds = float(values.get("DS60_CACHE_TTL_SECONDS", "60"))
    except ValueError as exc:
        raise ValueError("DS60_CACHE_TTL_SECONDS must be numeric") from exc
    if ttl_seconds <= 0:
        raise ValueError("DS60_CACHE_TTL_SECONDS must be positive")
    return CacheSettings(ttl_seconds=ttl_seconds, namespace=namespace)


def verify_store_contract(factory: Callable[[], KeyValueStore]) -> None:
    """Run reusable behavior checks against a fresh store implementation."""

    store = factory()
    assert store.get("missing") is None
    assert store.delete("missing") is False
    store.put("key", "first")
    assert store.get("key") == "first"
    store.put("key", "second")
    assert store.get("key") == "second"
    assert store.delete("key") is True
    assert store.get("key") is None


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Normalize and merge overlapping or touching closed intervals."""

    normalized = sorted((min(left, right), max(left, right)) for left, right in intervals)
    merged: list[tuple[int, int]] = []
    for left, right in normalized:
        if not merged or left > merged[-1][1] + 1:
            merged.append((left, right))
            continue
        previous_left, previous_right = merged[-1]
        merged[-1] = (previous_left, max(previous_right, right))
    return merged


DoubleChoice = Literal["fake", "mock", "real-local"]


def choose_double(boundary: str) -> DoubleChoice:
    choices: dict[str, DoubleChoice] = {
        "stateful-collaborator": "fake",
        "single-interaction": "mock",
        "file-format-contract": "real-local",
    }
    try:
        return choices[boundary]
    except KeyError as exc:
        raise ValueError(f"unknown boundary: {boundary}") from exc


def main() -> int:
    clock = FixedClock(100.0)
    cache = ExpiringCache(
        MemoryStore.empty(),
        clock,
        CacheSettings(ttl_seconds=5.0, namespace="demo"),
    )
    cache.put("learner", "session-local")
    print("before expiry:", cache.get("learner"))
    clock.advance(5.0)
    print("at expiry:", cache.get("learner"))
    print("merged intervals:", merge_intervals([(5, 2), (3, 8), (20, 20)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
