"""python-test-01 learner lab: test architecture and generative testing."""

from __future__ import annotations

from collections.abc import Callable, Iterable
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
    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        ("interval property target", lambda: merge_intervals([(5, 2), (3, 8)])),
        ("double choice", lambda: choose_double("stateful-collaborator")),
    )
    for label, call in checks:
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_test_01_architecture_generative.md
#
# Exercise 1 — Choose fixture lifetime
# Prompt: For each resource—immutable input rows, mutable in-memory store, temporary JSON
# file, and database connection—choose function, class, module, or session scope. Prefer
# the narrowest lifetime that is fast enough and keeps tests independent.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 2 — Complete interval merging
# Prompt: Implement `merge_intervals`. Add examples for empty input, reversed endpoints,
# adjacent intervals, duplicates, and nesting. Then express properties: - output is
# sorted, - output intervals no longer touch, - every original integer point remains
# covered, and - no new point is created.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 3 — Use Hypothesis meaningfully
# Prompt: Generate lists of bounded integer endpoint pairs with 100 deterministic examples,
# no example database, and no deadline. Introduce an adjacency bug briefly, inspect the
# smallest counterexample, restore the implementation, and keep a useful regression case.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 4 — Compare test doubles
# Prompt: Complete `choose_double`. Use a fake for the stateful store, a mock only for one
# audit interaction, and a real temporary file for serialization behavior. Explain why
# mocking every store method couples tests to implementation steps.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 5 — Patch and restore process state
# Prompt: Use `patch.dict(os.environ, ..., clear=False)` or pytest's `monkeypatch` fixture
# to change cache settings for one test. Assert the original environment is restored
# afterward. Prefer passing a mapping directly when the API permits it.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 6 — Add a contract failure
# Prompt: Create a deliberately broken store that never overwrites values. Run the shared
# contract and locate the exact violated behavior. Contract tests complement, rather than
# replace, implementation-specific failure tests.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 7 — model a state machine
# Prompt: Create a deterministic rule-based state machine for `ExpiringCache`: put, get,
# delete, advance time, and overwrite. Compare every action with a simple in-memory model.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 8 — add metamorphic tests
# Prompt: Write metamorphic relations for interval merging when the exact output is
# inconvenient: input permutation, duplicate insertion, endpoint translation, and applying
# merge twice.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 9 — evaluate mutation-test survivors
# Prompt: Make three deliberate mutations: change expiry `<` to `<=`, stop merging
# adjacent intervals, and skip store overwrite. Predict which test should fail and add a
# focused test for any survivor.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 10 — test concurrency without timing races
# Prompt: Design a two-worker cache/store test using barriers/events to force a specific
# interleaving. State whether the contract promises thread safety; if it does not, test
# the synchronization wrapper instead.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 11 — triage a flaky test
# Prompt: Take a test that depends on wall-clock sleep, random data, shared files, or
# unordered output. Classify the cause, collect repeat evidence, and replace the unstable
# boundary rather than adding retries.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 12 — design a layered verification portfolio
# Prompt: Map one feature across pure unit/property tests, shared store contract, real
# temporary-file integration, CLI/process smoke, and optional external system test. Define
# what each layer proves and does not prove.
# Evidence: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
