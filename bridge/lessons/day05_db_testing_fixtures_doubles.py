"""Bridge Day 5: database tests, fixtures, and test doubles.

Prerequisite: Bridge Day 4.
Read ``bridge/companion-guides/day05_db_testing_fixtures_doubles.md`` first.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from decimal import Decimal
from typing import Protocol

LESSON_ID = "bridge-05"
PREREQUISITES = ("bridge-04",)
LEVEL = "intermediate"


class OrderRepository(Protocol):
    def amounts_for_customer(self, customer_id: int) -> Sequence[Decimal]: ...


class RollbackConnection(Protocol):
    def rollback(self) -> None: ...


def customer_order_total(repository: OrderRepository, customer_id: int) -> Decimal:
    """Core implementation: implement domain logic against a small Protocol."""

    raise NotImplementedError("sum customer order amounts without importing Psycopg")


class FakeOrderRepository:
    """Core implementation: create a configurable fake that also records calls."""

    def __init__(self) -> None:
        raise NotImplementedError("accept deterministic customer amounts")

    def amounts_for_customer(self, customer_id: int) -> Sequence[Decimal]:
        raise NotImplementedError("record the request and return configured amounts")


@contextmanager
def rollback_only(connection: RollbackConnection) -> Iterator[None]:
    """Core implementation: always roll back changes made by an optional live test."""

    raise NotImplementedError("implement rollback-only fixture behavior")
    yield  # pragma: no cover - keeps this function a generator while unfinished


# Exercises (answer-free)
# Focus: Separate deterministic domain tests, recording database adapters, and explicitly opt-in
#    rollback-only PostgreSQL integration tests.
# Assumptions: Money remains `Decimal`; fake-backed tests do not import Psycopg; live tests
#    require both an opt-in flag and the disposable database URL.
# Failure to watch for: A fake that asserts internally or a fixture that skips cleanup on
#    failure hides ownership and can leave persistent learner data.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Implementation] Implement `customer_order_total()` against `OrderRepository`, reject
#    non-positive IDs, and return exact zero for no amounts.
#    Hint: Use a Decimal start value so the empty case keeps the money type.
# 2. [Test double] Implement `FakeOrderRepository` with configured values and public call
#    history but no internal assertions.
#    Hint: A fake supplies behavior and observations; the test owns expectations.
# 3. [Testing] Test totals, exact zero, invalid IDs, Decimal preservation, and the precise
#    repository call sequence.
#    Hint: Verify behavior and collaboration separately.
# 4. [Adapter] Create a cursor-backed repository and test its SQL text and bound customer
#    parameter with a recording cursor.
#    Hint: Keep SQL structure static and adapt returned rows to Decimal values.
# 5. [Fixture] Implement `rollback_only()` so rollback occurs after a passing or failing body
#    without suppressing the body failure.
#    Hint: Fixture cleanup belongs in `finally`.
# 6. [Live-test gate] Require both `DS60_RUN_LIVE_DB_TESTS=1` and `DS60_DATABASE_URL`; skip with
#    a clear reason when either is absent.
#    Hint: Opt-in state and connection location are independent requirements.
# 7. [Integration] Write one optional test that inserts, queries, and observes a temporary order
#    inside a transaction that the fixture rolls back.
#    Hint: Use a unique fixture key and verify disappearance after rollback when practical.
# 8. [Design] Compare a fake, a recording stub, and a mock for the repository boundary; choose
#    one for each test purpose.
#    Hint: Prefer the simplest double that expresses the evidence needed.
# 9. [Failure analysis] Test what happens when rollback itself fails while the test body is
#    already failing and document exception chaining.
#    Hint: Cleanup failures can mask the primary assertion.
# 10. [Database semantics] Explain why SQLite is not a PostgreSQL substitute for `ON CONFLICT`,
#    numeric, isolation, or driver behavior tests.
#    Hint: A fast substitute is useful only when it shares the semantics under test.
# 11. [Security testing] Pass an injection-shaped value through the cursor adapter and prove it
#    appears only in the parameter tuple.
#    Hint: Recording fakes should keep query and parameters in separate fields.
# 12. [Property reasoning] Define invariants for order totals over empty, single, and multiple
#    non-negative Decimal sequences.
#    Hint: Useful invariants complement example cases without changing domain policy.
# 13. [Sensitive fixtures] Design fixture credentials and failure assertions so secret-scan
#    markers remain explicit and secrets never enter test IDs or assertion messages.
#    Hint: Parameterized test IDs and reprs are output channels.
# 14. [Isolation] Run the optional integration case twice and prove rollback makes repetition
#    independent.
#    Hint: A passing test that leaves data behind is not isolated.


def main() -> int:
    print("Bridge Day 5 starter loaded.")
    print("Build fast fake-backed tests first, then one opt-in PostgreSQL integration test.")
    print("The integration fixture must roll back even when the assertion fails.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
