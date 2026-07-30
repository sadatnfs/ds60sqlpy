"""python-svc-02 learner lab: service hardening and observability."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

Role = Literal["reader", "operator"]


def is_authorized(role: Role, action: str) -> bool:
    """TODO: readers may predict; operators may predict and reload."""

    raise NotImplementedError("complete is_authorized")


def readiness(
    dependency_checks: Sequence[bool],
    *,
    artifact_verified: bool,
    draining: bool,
) -> bool:
    """TODO: ready only when all dependencies and the artifact are safe."""

    raise NotImplementedError("complete readiness")


def redact_fields(fields: Mapping[str, str]) -> dict[str, str]:
    """TODO: redact token, authorization, password, and secret keys."""

    raise NotImplementedError("complete redact_fields")


def self_check() -> None:
    print("Worked health rule: a running process may be healthy but not ready.")
    for label, call in (
        ("authorization", lambda: is_authorized("reader", "predict")),
        (
            "readiness",
            lambda: readiness([True, True], artifact_verified=True, draining=False),
        ),
        (
            "redaction",
            lambda: redact_fields({"request_id": "r1", "token": "local-value"}),
        ),
    ):
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


if __name__ == "__main__":
    self_check()
