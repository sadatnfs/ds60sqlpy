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
#    Verify: Assert IDs `0` and `-1` raise `ValueError`; an empty repository returns
#    `Decimal('0.00')`; and two configured Decimal amounts sum exactly without float conversion.
# 2. [Test double] Implement `FakeOrderRepository` with configured values and public call
#    history but no internal assertions.
#    Hint: A fake supplies behavior and observations; the test owns expectations.
#    Verify: Call the fake for configured and missing customer IDs; assert returned sequences
#    and public call history match exactly, with no assertion performed inside the fake.
# 3. [Testing] Test totals, exact zero, invalid IDs, Decimal preservation, and the precise
#    repository call sequence.
#    Hint: Verify behavior and collaboration separately.
#    Verify: Compare exact totals for empty/single/multiple sequences, exact zero type,
#    invalid-ID exceptions, unchanged Decimal values, and one repository call per valid request.
# 4. [Adapter] Create a cursor-backed repository and test its SQL text and bound customer
#    parameter with a recording cursor.
#    Hint: Keep SQL structure static and adapt returned rows to Decimal values.
#    Verify: Use a recording cursor; assert the SQL remains static with one `%s`, the parameter
#    tuple is `(customer_id,)`, one fetch occurs, and rows become `Decimal` values.
# 5. [Fixture] Implement `rollback_only()` so rollback occurs after a passing or failing body
#    without suppressing the body failure.
#    Hint: Fixture cleanup belongs in `finally`.
#    Verify: Assert rollback occurs after a passing body and after a body that raises; in the
#    latter case the original exception identity remains visible and no commit occurs.
# 6. [Live-test gate] Require both `DS60_RUN_LIVE_DB_TESTS=1` and `DS60_DATABASE_URL`; skip with
#    a clear reason when either is absent.
#    Hint: Opt-in state and connection location are independent requirements.
#    Verify: Parameterize missing flag, missing URL, and both present; assert only
#    `DS60_RUN_LIVE_DB_TESTS=1` plus a URL enables the fixture and every other case skips.
# 7. [Integration] Write one optional test that inserts, queries, and observes a temporary order
#    inside a transaction that the fixture rolls back.
#    Hint: Use a unique fixture key and verify disappearance after rollback when practical.
#    Verify: In the opt-in database, insert and read one course-owned temporary order, then
#    assert rollback removes it and a second run starts from the same clean state.
# 8. [Design] Compare a fake, a recording stub, and a mock for the repository boundary; choose
#    one for each test purpose.
#    Hint: Prefer the simplest double that expresses the evidence needed.
#    Verify: Provide a table mapping pure totals to the configured fake, SQL/parameter
#    assertions to the recording stub, and one collaboration-count check to a mock, with one
#    reason each.
# 9. [Failure analysis] Test what happens when rollback itself fails while the test body is
#    already failing and document exception chaining.
#    Hint: Cleanup failures can mask the primary assertion.
#    Verify: Raise distinct body and rollback exceptions; inspect chaining/grouping and assert
#    the test report contains evidence of both failures rather than silently replacing one.
# 10. [Database semantics] Explain why SQLite is not a PostgreSQL substitute for `ON CONFLICT`,
#    numeric, isolation, or driver behavior tests.
#    Hint: A fast substitute is useful only when it shares the semantics under test.
#    Verify: List the PostgreSQL behavior under test—conflict handling, exact numeric
#    adaptation, transaction/isolation, and Psycopg calls—and mark each as unproved by SQLite.
# 11. [Security testing] Pass an injection-shaped value through the cursor adapter and prove it
#    appears only in the parameter tuple.
#    Hint: Recording fakes should keep query and parameters in separate fields.
#    Verify: Send an injection-shaped customer value through the adapter; assert it is absent
#    from SQL text and present unchanged only in the recorded parameter tuple.
# 12. [Property reasoning] Define invariants for order totals over empty, single, and multiple
#    non-negative Decimal sequences.
#    Hint: Useful invariants complement example cases without changing domain policy.
#    Verify: For non-negative Decimal sequences, assert totals are non-negative, empty is exact
#    zero, single returns itself, concatenation totals add, and input order does not change the
#    sum.
# 13. [Sensitive fixtures] Design fixture credentials and failure assertions so secret-scan
#    markers remain explicit and secrets never enter test IDs or assertion messages.
#    Hint: Parameterized test IDs and reprs are output channels.
#    Verify: Scan test IDs, exception messages, logs, and snapshots with a sentinel credential;
#    assert the secret never appears while explicit safe markers remain detectable.
# 14. [Isolation] Run the optional integration case twice and prove rollback makes repetition
#    independent.
#    Hint: A passing test that leaves data behind is not isolated.
#    Verify: Run the opt-in case twice; assert each run sees only its own temporary row and
#    post-test queries find no persisted course record.


def main() -> int:
    print("Bridge Day 5 starter loaded.")
    print("Build fast fake-backed tests first, then one opt-in PostgreSQL integration test.")
    print("The integration fixture must roll back even when the assertion fails.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
