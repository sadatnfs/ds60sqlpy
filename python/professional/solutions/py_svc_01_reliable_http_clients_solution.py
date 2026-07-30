"""Reference implementation for python-svc-01.

The client depends on a Transport protocol. Tests and the demo inject a
ScriptedTransport, so the entire module runs offline without a socket, API
account, credential, or public service.
"""

from __future__ import annotations

import os
import re
import time
from collections import deque
from collections.abc import Callable, Mapping, MutableSequence, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, TypeAlias
from urllib.parse import urlencode

Method = Literal["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
Outcome = Literal["success", "retryable", "permanent"]
JsonObject: TypeAlias = dict[str, Any]
LogSink: TypeAlias = Callable[[str, Mapping[str, object]], None]
Sleep: TypeAlias = Callable[[float], None]
Jitter: TypeAlias = Callable[[], float]
IdFactory: TypeAlias = Callable[[], str]

RETRYABLE_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})
REPLAYABLE_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS"})
SENSITIVE_HEADERS = frozenset(
    {"authorization", "cookie", "set-cookie", "x-api-key", "proxy-authorization"}
)
SENSITIVE_QUERY = re.compile(r"(?i)(access_token|api_key|password|secret|token)=([^&\s]+)")


class TransportTimeout(TimeoutError):
    """Raised by a transport when its configured deadline expires."""


class ClientError(RuntimeError):
    """Base class for failures at the HTTP client boundary."""


class PermanentHttpError(ClientError):
    """A response should reach the caller without automatic replay."""

    def __init__(self, status: int, correlation_id: str) -> None:
        super().__init__(f"HTTP {status} for correlation_id={correlation_id}; request not retried")
        self.status = status
        self.correlation_id = correlation_id


class RetryExhausted(ClientError):
    """All policy-permitted attempts failed."""

    def __init__(self, attempts: int, correlation_id: str, reason: str) -> None:
        super().__init__(
            f"request failed after {attempts} attempts "
            f"for correlation_id={correlation_id}: {reason}"
        )
        self.attempts = attempts
        self.correlation_id = correlation_id


class ResponseProtocolError(ClientError):
    """A successful response violates the declared pagination contract."""


@dataclass(frozen=True)
class Request:
    """Transport-neutral prepared request."""

    method: Method
    url: str
    headers: Mapping[str, str]
    timeout_seconds: float
    json_body: JsonObject | None = None


@dataclass(frozen=True)
class Response:
    """Transport-neutral response with already-decoded local JSON."""

    status: int
    headers: Mapping[str, str] = field(default_factory=dict)
    json_body: JsonObject | None = None


class Transport(Protocol):
    """Structural boundary implemented by a real adapter or local fake."""

    def send(self, request: Request) -> Response:
        """Send one prepared attempt or raise ``TransportTimeout``."""


@dataclass(frozen=True)
class ClientConfig:
    """Validated runtime configuration; token is hidden from ``repr``."""

    base_url: str
    auth_token: str = field(repr=False)
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if not self.auth_token.strip():
            raise ValueError("auth_token must not be blank")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> ClientConfig:
        """Read authentication at runtime rather than from source control."""

        values = os.environ if environ is None else environ
        token = values.get("DS60_API_TOKEN", "")
        base_url = values.get("DS60_API_BASE_URL", "https://local.invalid")
        timeout_text = values.get("DS60_API_TIMEOUT_SECONDS", "5")
        if not token.strip():
            raise ValueError("DS60_API_TOKEN is required")
        try:
            timeout_seconds = float(timeout_text)
        except ValueError as exc:
            raise ValueError("DS60_API_TIMEOUT_SECONDS must be numeric") from exc
        return cls(
            base_url=base_url.rstrip("/"),
            auth_token=token,
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class RetryPolicy:
    """Bounded exponential backoff policy."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.1
    maximum_delay_seconds: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be non-negative")
        if self.maximum_delay_seconds < self.base_delay_seconds:
            raise ValueError("maximum delay must be at least the base delay")

    def delay_before_retry(
        self,
        completed_attempt: int,
        *,
        retry_after: str | None,
        jitter_fraction: float,
    ) -> float:
        """Return a capped delay after a one-based failed attempt."""

        if not 0 <= jitter_fraction <= 1:
            raise ValueError("jitter_fraction must be between 0 and 1")
        exponential: float = self.base_delay_seconds * float(2 ** (completed_attempt - 1))
        jitter: float = self.base_delay_seconds * jitter_fraction
        delay: float = exponential + jitter
        if retry_after is not None:
            try:
                server_delay = max(0.0, float(retry_after))
            except ValueError:
                server_delay = 0.0
            delay = max(delay, server_delay)
        return float(min(delay, self.maximum_delay_seconds))


def classify_status(status: int) -> Outcome:
    """Classify valid HTTP status codes for retry policy."""

    if not 100 <= status <= 599:
        raise ValueError(f"invalid HTTP status: {status}")
    if 200 <= status <= 299:
        return "success"
    if status in RETRYABLE_STATUSES:
        return "retryable"
    return "permanent"


def method_can_retry(method: Method, idempotency_key: str | None) -> bool:
    """Decide whether replaying the logical operation is safe enough."""

    if method in REPLAYABLE_METHODS:
        return True
    return method in {"POST", "PATCH"} and bool(idempotency_key and idempotency_key.strip())


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return a case-insensitively redacted copy for logging."""

    return {
        name: "<redacted>" if name.lower() in SENSITIVE_HEADERS else value
        for name, value in headers.items()
    }


def redact_url(url: str) -> str:
    """Redact common sensitive query parameters in a display URL."""

    return SENSITIVE_QUERY.sub(lambda match: f"{match.group(1)}=<redacted>", url)


def _header(headers: Mapping[str, str], name: str) -> str | None:
    """Look up one HTTP header case-insensitively."""

    wanted = name.lower()
    return next(
        (value for key, value in headers.items() if key.lower() == wanted),
        None,
    )


@dataclass
class MemoryLog:
    """Simple log sink that lets tests inspect structured events."""

    events: MutableSequence[tuple[str, dict[str, object]]] = field(default_factory=list)

    def __call__(self, event: str, fields: Mapping[str, object]) -> None:
        self.events.append((event, dict(fields)))


ScriptStep: TypeAlias = Response | BaseException | Callable[[Request], Response]


@dataclass
class ScriptedTransport:
    """Deterministic injected transport for tests and offline practice."""

    steps: Sequence[ScriptStep]
    requests: list[Request] = field(default_factory=list, init=False)
    _remaining: deque[ScriptStep] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._remaining = deque(self.steps)

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        if not self._remaining:
            raise AssertionError("scripted transport received an unexpected request")
        step = self._remaining.popleft()
        if isinstance(step, BaseException):
            raise step
        if callable(step):
            return step(request)
        return step


@dataclass
class ReliableClient:
    """Policy layer independent from a concrete network library."""

    config: ClientConfig
    transport: Transport
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    sleep: Sleep = time.sleep
    jitter: Jitter = lambda: 0.0
    id_factory: IdFactory = lambda: "correlation-local"
    log: LogSink = lambda _event, _fields: None

    def _url(self, path: str, query: Mapping[str, str] | None = None) -> str:
        if not path.startswith("/"):
            raise ValueError("path must start with /")
        url = f"{self.config.base_url.rstrip('/')}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        return url

    def request(
        self,
        method: Method,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: JsonObject | None = None,
        idempotency_key: str | None = None,
    ) -> Response:
        """Execute one logical request with bounded, policy-safe retries."""

        correlation_id = self.id_factory()
        if not correlation_id.strip():
            raise ValueError("id_factory returned a blank correlation ID")
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.auth_token}",
            "X-Correlation-ID": correlation_id,
        }
        if idempotency_key is not None:
            if not idempotency_key.strip():
                raise ValueError("idempotency_key must not be blank")
            headers["Idempotency-Key"] = idempotency_key

        prepared = Request(
            method=method,
            url=self._url(path, query),
            headers=headers,
            timeout_seconds=self.config.timeout_seconds,
            json_body=json_body,
        )
        replay_allowed = method_can_retry(method, idempotency_key)

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            self.log(
                "http_attempt",
                {
                    "method": method,
                    "url": redact_url(prepared.url),
                    "headers": redact_headers(prepared.headers),
                    "attempt": attempt,
                    "correlation_id": correlation_id,
                    "timeout_seconds": prepared.timeout_seconds,
                },
            )
            try:
                response = self.transport.send(prepared)
            except TransportTimeout as exc:
                if not replay_allowed or attempt == self.retry_policy.max_attempts:
                    raise RetryExhausted(
                        attempt,
                        correlation_id,
                        "transport timeout",
                    ) from exc
                delay = self.retry_policy.delay_before_retry(
                    attempt,
                    retry_after=None,
                    jitter_fraction=self.jitter(),
                )
                self.log(
                    "http_retry",
                    {
                        "reason": "timeout",
                        "delay_seconds": delay,
                        "attempt": attempt,
                        "correlation_id": correlation_id,
                    },
                )
                self.sleep(delay)
                continue

            outcome = classify_status(response.status)
            if outcome == "success":
                return response
            if outcome == "permanent" or not replay_allowed:
                raise PermanentHttpError(response.status, correlation_id)
            if attempt == self.retry_policy.max_attempts:
                raise RetryExhausted(
                    attempt,
                    correlation_id,
                    f"last HTTP status {response.status}",
                )

            retry_after = (
                _header(response.headers, "Retry-After") if response.status == 429 else None
            )
            delay = self.retry_policy.delay_before_retry(
                attempt,
                retry_after=retry_after,
                jitter_fraction=self.jitter(),
            )
            self.log(
                "http_retry",
                {
                    "reason": f"status_{response.status}",
                    "delay_seconds": delay,
                    "attempt": attempt,
                    "correlation_id": correlation_id,
                },
            )
            self.sleep(delay)

        raise AssertionError("retry loop exhausted without returning or raising")

    def get_all_pages(
        self,
        path: str,
        *,
        items_key: str = "items",
        cursor_key: str = "next_cursor",
        maximum_pages: int = 100,
    ) -> list[JsonObject]:
        """Collect cursor pages while detecting loops and malformed payloads."""

        if maximum_pages < 1:
            raise ValueError("maximum_pages must be at least 1")
        items: list[JsonObject] = []
        cursor: str | None = None
        seen_cursors: set[str] = set()

        for _page_number in range(1, maximum_pages + 1):
            query = {"cursor": cursor} if cursor is not None else None
            response = self.request("GET", path, query=query)
            body = response.json_body
            if not isinstance(body, dict):
                raise ResponseProtocolError("page body must be a JSON object")
            raw_items = body.get(items_key)
            if not isinstance(raw_items, list) or not all(
                isinstance(item, dict) for item in raw_items
            ):
                raise ResponseProtocolError(f"{items_key!r} must be a list of objects")
            items.extend(raw_items)

            next_cursor = body.get(cursor_key)
            if next_cursor is None:
                return items
            if not isinstance(next_cursor, str) or not next_cursor:
                raise ResponseProtocolError(f"{cursor_key!r} must be a non-empty string or null")
            if next_cursor in seen_cursors:
                raise ResponseProtocolError(f"pagination repeated cursor {next_cursor!r}")
            seen_cursors.add(next_cursor)
            cursor = next_cursor

        raise ResponseProtocolError(f"pagination exceeded maximum_pages={maximum_pages}")


def main() -> int:
    """Run retry and pagination examples through local scripted transports."""

    retry_log = MemoryLog()
    retry_delays: list[float] = []
    retry_transport = ScriptedTransport(
        [
            Response(503),
            Response(200, json_body={"message": "local success"}),
        ]
    )
    client = ReliableClient(
        config=ClientConfig(
            base_url="https://local.invalid",
            auth_token="local-example-credential",
            timeout_seconds=0.25,
        ),
        transport=retry_transport,
        sleep=retry_delays.append,
        jitter=lambda: 0.0,
        id_factory=lambda: "correlation-demo-1",
        log=retry_log,
    )
    response = client.request("GET", "/health")
    print("retry demo:", response.status, "delays:", retry_delays)
    print("safe first log:", retry_log.events[0])

    page_transport = ScriptedTransport(
        [
            Response(200, json_body={"items": [{"id": 1}], "next_cursor": "p2"}),
            Response(200, json_body={"items": [{"id": 2}], "next_cursor": None}),
        ]
    )
    page_client = ReliableClient(
        config=client.config,
        transport=page_transport,
        sleep=lambda _seconds: None,
        id_factory=lambda: "correlation-page",
    )
    print("pagination demo:", page_client.get_all_pages("/items"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
