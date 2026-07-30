"""python-test-01 learner lab: test architecture and generative testing."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class Clock(Protocol):
    """Small seam that avoids sleeping in tests."""

    def now(self) -> float:
        """Return monotonic-style seconds."""


def ttl_is_valid(created_at: float, ttl_seconds: float, clock: Clock) -> bool:
    """Worked example: test time through an injected clock."""

    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")
    return clock.now() < created_at + ttl_seconds


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Normalize and merge closed integer intervals.

    TODO: normalize reversed endpoints, sort them, and merge overlapping or
    touching intervals. This pure function will become the Hypothesis target.
    """

    raise NotImplementedError("complete merge_intervals")


def choose_double(boundary: str) -> str:
    """Choose ``fake``, ``mock``, or ``real-local`` for a test boundary.

    TODO: return a fake for stateful collaboration, a mock for one interaction,
    and a real local implementation for a file-format contract. Reject unknown
    boundary labels.
    """

    raise NotImplementedError("complete choose_double")


class FixedClock:
    def __init__(self, value: float) -> None:
        self.value = value

    def now(self) -> float:
        return self.value


def self_check() -> None:
    clock = FixedClock(12.0)
    print("Worked clock seam:", ttl_is_valid(10.0, 3.0, clock))
    for label, call in (
        ("interval property target", lambda: merge_intervals([(5, 2), (3, 8)])),
        ("double choice", lambda: choose_double("stateful-collaborator")),
    ):
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


if __name__ == "__main__":
    self_check()
