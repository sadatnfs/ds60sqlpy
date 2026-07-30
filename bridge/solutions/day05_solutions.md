# Bridge Day 5 — Solution notes

Attempt the [learner file](../lessons/day05_db_testing_fixtures_doubles.py)
before comparing [day05_solution.py](day05_solution.py).

## Test seams

`customer_order_total()` depends on `OrderRepository`, a one-method Protocol
expressed in domain terms. The fake stores configured `Decimal` sequences and
records customer IDs. Tests can prove the rule and the collaboration without
knowing about SQL or cursors.

`CursorOrderRepository` is the adapter. Its separate tests should prove a
positive ID check, `%s` binding, and row conversion. An optional PostgreSQL test
then proves the statement against the real course schema.

## Rollback-only ownership

`rollback_only()` puts rollback in `finally`, so a passing assertion and a
failing assertion both clean up. It does not catch the body exception and
therefore cannot accidentally turn a failure into success.

`live_database_url()` requires the explicit opt-in flag and the URL. Merely
having a connection string in a shell does not authorize a normal test run to
contact it.

## Tradeoffs

- The fake is intentionally less capable than PostgreSQL. Adding joins,
  transactions, or constraints would duplicate the implementation and create
  false confidence.
- An in-memory fake can return impossible states. Adapter and integration tests
  cover the small set of database contracts where that matters.
- Transaction rollback removes row changes but not every side effect:
  sequences advance, locks were visible, and some DDL or external calls may
  behave differently. Use a disposable isolated database.
- A session-scoped live fixture is faster, while a function-scoped transaction
  isolates failures better. Choose based on test cost and contamination risk.

The balanced suite has many pure tests, a few recording-adapter tests, and the
smallest useful number of opt-in PostgreSQL tests.

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day05_solution.py`; use it only after an honest attempt.

**Shared failure rule:** A fake that asserts internally or a fixture that skips cleanup on failure hides ownership and can leave persistent learner data.

### Exercise 1 — Implementation

**Prompt:** Implement `customer_order_total()` against `OrderRepository`, reject non-positive
IDs, and return exact zero for no amounts.

**Approach:** Validate `customer_id > 0`, request the abstract sequence once, and call
`sum(values, start=Decimal('0.00'))`. Do not import a database driver into domain logic.

**Why this boundary matters:** Use a Decimal start value so the empty case keeps the money type.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 2 — Test double

**Prompt:** Implement `FakeOrderRepository` with configured values and public call history but
no internal assertions.

**Approach:** Copy the input mapping defensively, initialize `requested_customer_ids`, append on
every call, and return the configured sequence or an empty tuple.

**Why this boundary matters:** A fake supplies behavior and observations; the test owns
expectations.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 3 — Testing

**Prompt:** Test totals, exact zero, invalid IDs, Decimal preservation, and the precise
repository call sequence.

**Approach:** Assert numeric values and types, then assert the fake history. An invalid ID
should raise before the repository history changes.

**Why this boundary matters:** Verify behavior and collaboration separately.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 4 — Adapter

**Prompt:** Create a cursor-backed repository and test its SQL text and bound customer parameter
with a recording cursor.

**Approach:** Execute one ordered query with `(customer_id,)`, fetch rows, and return their
amount column as Decimals. The hostile test ID/value must never be interpolated into SQL.

**Why this boundary matters:** Keep SQL structure static and adapt returned rows to Decimal
values.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 5 — Fixture

**Prompt:** Implement `rollback_only()` so rollback occurs after a passing or failing body
without suppressing the body failure.

**Approach:** Yield once inside `try` and call `connection.rollback()` in `finally`. Do not
catch the body exception unless adding safe context, and never convert it into success.

**Why this boundary matters:** Fixture cleanup belongs in `finally`.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 6 — Live-test gate

**Prompt:** Require both `DS60_RUN_LIVE_DB_TESTS=1` and `DS60_DATABASE_URL`; skip with a clear
reason when either is absent.

**Approach:** Return or use the URL only when both exact conditions are satisfied. The normal
test suite should skip explicitly without importing Psycopg or printing the URL.

**Why this boundary matters:** Opt-in state and connection location are independent
requirements.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 7 — Integration

**Prompt:** Write one optional test that inserts, queries, and observes a temporary order inside
a transaction that the fixture rolls back.

**Approach:** Connect only to the disposable database, enter the rollback-only fixture, perform
parameterized insert/read assertions, and let the fixture own cleanup. A follow-up read can
prove no row persisted.

**Why this boundary matters:** Use a unique fixture key and verify disappearance after rollback
when practical.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 8 — Design

**Prompt:** Compare a fake, a recording stub, and a mock for the repository boundary; choose one
for each test purpose.

**Approach:** Use a fake for reusable in-memory behavior, a recording stub for exact
SQL/parameter observations, and a mock only for narrow interaction assertions that would
otherwise require excess test code.

**Why this boundary matters:** Prefer the simplest double that expresses the evidence needed.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 9 — Failure analysis

**Prompt:** Test what happens when rollback itself fails while the test body is already failing
and document exception chaining.

**Approach:** Use a fake rollback that raises and inspect `__context__`. Decide whether the
fixture should preserve the body failure while reporting cleanup separately; never silently
swallow either failure.

**Why this boundary matters:** Cleanup failures can mask the primary assertion.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 10 — Database semantics

**Prompt:** Explain why SQLite is not a PostgreSQL substitute for `ON CONFLICT`, numeric,
isolation, or driver behavior tests.

**Approach:** Keep domain tests fake-backed and run database-semantic tests on optional
disposable PostgreSQL. SQLite would produce false confidence around SQL dialect, types, locking,
and Psycopg parameter adaptation.

**Why this boundary matters:** A fast substitute is useful only when it shares the semantics
under test.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 11 — Security testing

**Prompt:** Pass an injection-shaped value through the cursor adapter and prove it appears only
in the parameter tuple.

**Approach:** Assert static SQL still contains `%s`, the hostile string is absent from SQL, and
the exact value is present in the one-element parameter tuple.

**Why this boundary matters:** Recording fakes should keep query and parameters in separate
fields.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 12 — Property reasoning

**Prompt:** Define invariants for order totals over empty, single, and multiple non-negative
Decimal sequences.

**Approach:** The empty total is exact zero, adding a non-negative amount cannot reduce the
total, and concatenating two sequences yields the sum of their separate totals. Generate only
domain-valid Decimals.

**Why this boundary matters:** Useful invariants complement example cases without changing
domain policy.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 13 — Sensitive fixtures

**Prompt:** Design fixture credentials and failure assertions so secret-scan markers remain
explicit and secrets never enter test IDs or assertion messages.

**Approach:** Use synthetic marked fixtures, keep them out of parameter IDs, capture
logs/errors, and assert sentinel fragments are absent. Annotate deliberate fixtures for the
repository scanner.

**Why this boundary matters:** Parameterized test IDs and reprs are output channels.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 14 — Isolation

**Prompt:** Run the optional integration case twice and prove rollback makes repetition
independent.

**Approach:** Use a stable test key inside rollback-only transactions; each run should see its
own inserted row and no pre-existing copy. Confirm the fixture closes/rolls back even when an
assertion is forced to fail.

**Why this boundary matters:** A passing test that leaves data behind is not isolated.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.
