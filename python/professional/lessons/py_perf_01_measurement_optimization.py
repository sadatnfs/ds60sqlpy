"""python-perf-01 learner lab: measurement-first optimization."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

Decision = Literal[
    "fix-correctness",
    "reduce-memory",
    "reduce-transfer",
    "optimize-hotspot",
    "keep-current",
]


def first_duplicate_linear(values: Sequence[int]) -> int | None:
    """Return the first value encountered for a second time.

    TODO: preserve semantics while replacing repeated prefix scans with a set.
    """

    raise NotImplementedError("complete first_duplicate_linear")


def estimated_transfer_bytes(
    payload_bytes: int,
    *,
    workers: int,
    copies_per_worker: int,
) -> int:
    """TODO: validate nonnegative inputs and estimate copied process bytes."""

    raise NotImplementedError("complete estimated_transfer_bytes")


def choose_next_step(
    *,
    equivalent: bool,
    peak_bytes: int,
    memory_budget_bytes: int,
    transfer_fraction: float,
    hotspot_fraction: float,
) -> Decision:
    """TODO: apply the guide's deterministic evidence-priority policy."""

    raise NotImplementedError("complete choose_next_step")


def first_duplicate_quadratic(values: Sequence[int]) -> int | None:
    """Worked baseline whose repeated prefix membership is O(n squared)."""

    for index, value in enumerate(values):
        if value in values[:index]:
            return value
    return None


def self_check() -> None:
    workload = [4, 1, 3, 2, 3, 4]
    print("Worked baseline duplicate:", first_duplicate_quadratic(workload))
    for label, call in (
        ("linear equivalent", lambda: first_duplicate_linear(workload)),
        (
            "process transfer estimate",
            lambda: estimated_transfer_bytes(1_024, workers=4, copies_per_worker=2),
        ),
        (
            "evidence decision",
            lambda: choose_next_step(
                equivalent=True,
                peak_bytes=100,
                memory_budget_bytes=1_000,
                transfer_fraction=0.1,
                hotspot_fraction=0.2,
            ),
        ),
    ):
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


if __name__ == "__main__":
    self_check()
