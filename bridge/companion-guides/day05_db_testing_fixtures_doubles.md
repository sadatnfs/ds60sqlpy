# Bridge Day 5 — Database tests, fixtures, and test doubles

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 4](day04_transactions_idempotency_retries.md)

## Why this matters

Most application behavior can be tested without opening a database connection.
Those tests should be fast, deterministic, and precise. A smaller integration
layer still needs PostgreSQL tests because a fake cannot prove SQL syntax,
constraints, transaction isolation, or driver conversions. A useful test
strategy knows which question belongs at each layer.

## Objectives

By the end, you can:

- hide cursor details behind a domain-facing repository Protocol;
- build a configurable fake that records interactions;
- distinguish a stub, fake, spy, and mock by purpose;
- make optional live tests require two explicit environment settings;
- use rollback-only fixtures so test writes do not persist.

## Vocabulary

| Term | Meaning |
|---|---|
| unit test | A focused test of application behavior with external effects replaced |
| integration test | A test of real components working together, here Python, Psycopg, and PostgreSQL |
| test double | A controlled replacement for a dependency |
| fake | A lightweight working implementation, often in memory |
| spy | A double that records how it was called |
| fixture | Setup and cleanup shared by tests |
| contract | The behavior an implementation promises to its callers |

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day05_db_testing_fixtures_doubles.py
```

```bash
.venv/bin/python bridge/lessons/day05_db_testing_fixtures_doubles.py
```

## Worked example: test the business rule at the domain seam

Suppose the rule is “sum all stored order amounts for this customer.” The
business function needs only this behavior:

```python
class AmountSource(Protocol):
    def for_customer(self, customer_id: int) -> Sequence[Decimal]: ...
```

A fake can return two `Decimal` values and record the requested ID. That proves
the summing rule and collaboration without requiring SQL. A separate adapter
test proves that the repository sends a parameterized query and maps returned
rows. One optional PostgreSQL test proves the actual query against the course
schema.

| Question | Best test |
|---|---|
| Does the total use `Decimal` and handle no orders? | Unit test with fake repository |
| Is customer ID bound separately? | Recording-cursor adapter test |
| Does the query match the real schema? | PostgreSQL integration test |
| Does rollback clean up a test insert? | PostgreSQL fixture test |

## Exercises

1. Implement `customer_order_total()` against `OrderRepository`. Validate a
   positive ID and return `Decimal("0.00")` when no amounts exist.
2. Implement `FakeOrderRepository` with configured per-customer values and a
   public call history. Do not make assertions inside the fake.
3. Test totals, the empty case, invalid IDs, and the exact repository call.
4. Create a cursor-backed repository adapter. Test its SQL and parameters with a
   recording cursor.
5. Implement `rollback_only()`. It must roll back after a passing body and after
   a failing body without suppressing the body failure.
6. Gate live tests on both `DS60_RUN_LIVE_DB_TESTS=1` and
   `DS60_DATABASE_URL`. Skip with a clear reason otherwise.
7. Write one optional integration test that inserts an order inside a
   transaction, queries it, and lets the fixture roll it back.

### Progressive hints

1. Accept abstract `Sequence[Decimal]`; do not require a list.
2. `sum(values, start=Decimal("0.00"))` preserves the money type for an empty
   sequence.
3. A fixture's cleanup belongs in `finally`.
4. `pytest.skip()` is appropriate when an explicitly optional dependency is not
   enabled; silent pass logic is not.

## Optional live-DB fixture

Use the disposable course database only. A fixture can connect, start normal
test work, and always roll back before closing. Do not use SQLite as a faster
substitute: it cannot validate PostgreSQL SQL, types, or transaction behavior.

```powershell
$env:DS60_RUN_LIVE_DB_TESTS = "1"
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.\.venv\Scripts\python.exe -m pytest path\to\your_live_test.py -q
```

```bash
export DS60_RUN_LIVE_DB_TESTS=1
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.venv/bin/python -m pytest path/to/your_live_test.py -q
```

The opt-in flag prevents an ordinary offline test run from contacting whatever
database happens to be named in a developer's shell.

## Self-check

- Can all unit tests run with no network, driver, or database?
- Does the fake expose behavior rather than reproduce SQL internals?
- Does the adapter test inspect both query and parameters?
- Does the live test skip unless both settings are present?
- Are test writes absent after fixture cleanup?

## Common pitfalls

- **Mocking every cursor method:** tests become coupled to an implementation
  sequence instead of application behavior.
- **Making the fake smarter than production:** duplicated business rules can
  make the same bug pass twice.
- **Treating a fake as SQL proof:** only PostgreSQL validates PostgreSQL.
- **Committing test fixtures:** cleanup becomes fragile and data accumulates.
- **Pointing tests at a shared database:** rollback does not protect other users
  from locks, sequences, or accidental non-transactional operations.

## Next step

[Day 6](day06_bulk_etl_validation.md) uses these seams to validate and load
batches. See [the Day 5 solution notes](../solutions/day05_solutions.md) after
your attempt.
