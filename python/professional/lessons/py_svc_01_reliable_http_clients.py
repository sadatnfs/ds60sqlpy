"""python-svc-01 learner lab: reliable HTTP client boundaries.

This artifact makes no network calls. The worked example feeds local response
objects through a classifier. Complete the TODO policy functions before
opening the reference implementation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

Method = Literal["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
Outcome = Literal["success", "retryable", "permanent"]


@dataclass(frozen=True)
class Response:
    """Minimal local response used to practise policy."""

    status: int
    headers: Mapping[str, str]


def classify_status(status: int) -> Outcome:
    """Classify an HTTP status without sending a request.

    TODO:
    - 2xx is success
    - 408, 425, 429, 500, 502, 503, and 504 are retryable
    - every other valid status is permanent
    Reject values outside 100..599.
    """

    raise NotImplementedError("complete classify_status")


def method_can_retry(method: Method, idempotency_key: str | None) -> bool:
    """Return whether replaying this logical operation is permitted.

    TODO: safe/idempotent methods may retry. Require a non-empty idempotency key
    before replaying POST or PATCH.
    """

    raise NotImplementedError("complete method_can_retry")


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return log-safe headers without changing the caller's mapping.

    TODO: replace Authorization, Cookie, Set-Cookie, and X-API-Key values with
    ``<redacted>`` using case-insensitive header-name matching.
    """

    raise NotImplementedError("complete redact_headers")


def worked_example() -> None:
    """Show a local response sequence and activate completed exercises."""

    script = [
        Response(503, {"Retry-After": "1"}),
        Response(200, {"Content-Type": "application/json"}),
    ]
    print("Local scripted statuses:", [response.status for response in script])
    for response in script:
        try:
            outcome = classify_status(response.status)
        except NotImplementedError:
            print("TODO: status classification")
            break
        else:
            print(f"{response.status} -> {outcome}")

    for label, call in (
        ("POST replay policy", lambda: method_can_retry("POST", "order-1001")),
        (
            "header redaction",
            lambda: redact_headers(
                {"Authorization": "Bearer local-example", "Accept": "application/json"}
            ),
        ),
    ):
        try:
            value = call()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {value!r}")


if __name__ == "__main__":
    worked_example()
