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

### Practice contract

- **Focus:** Separate deterministic domain tests, recording database adapters, and explicitly opt-in rollback-only PostgreSQL integration tests.
- **Assumptions:** Money remains `Decimal`; fake-backed tests do not import Psycopg; live tests require both an opt-in flag and the disposable database URL.
- **Primary failure mode:** A fake that asserts internally or a fixture that skips cleanup on failure hides ownership and can leave persistent learner data.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Implementation:** Implement `customer_order_total()` against `OrderRepository`, reject
   non-positive IDs, and return exact zero for no amounts.
   - **Progressive hint:** Use a Decimal start value so the empty case keeps the money type.
2. **Test double:** Implement `FakeOrderRepository` with configured values and public call
   history but no internal assertions.
   - **Progressive hint:** A fake supplies behavior and observations; the test owns
     expectations.
3. **Testing:** Test totals, exact zero, invalid IDs, Decimal preservation, and the precise
   repository call sequence.
   - **Progressive hint:** Verify behavior and collaboration separately.
4. **Adapter:** Create a cursor-backed repository and test its SQL text and bound customer
   parameter with a recording cursor.
   - **Progressive hint:** Keep SQL structure static and adapt returned rows to Decimal values.
5. **Fixture:** Implement `rollback_only()` so rollback occurs after a passing or failing body
   without suppressing the body failure.
   - **Progressive hint:** Fixture cleanup belongs in `finally`.
6. **Live-test gate:** Require both `DS60_RUN_LIVE_DB_TESTS=1` and `DS60_DATABASE_URL`; skip
   with a clear reason when either is absent.
   - **Progressive hint:** Opt-in state and connection location are independent requirements.
7. **Integration:** Write one optional test that inserts, queries, and observes a temporary
   order inside a transaction that the fixture rolls back.
   - **Progressive hint:** Use a unique fixture key and verify disappearance after rollback when
     practical.
8. **Design:** Compare a fake, a recording stub, and a mock for the repository boundary; choose
   one for each test purpose.
   - **Progressive hint:** Prefer the simplest double that expresses the evidence needed.
9. **Failure analysis:** Test what happens when rollback itself fails while the test body is
   already failing and document exception chaining.
   - **Progressive hint:** Cleanup failures can mask the primary assertion.
10. **Database semantics:** Explain why SQLite is not a PostgreSQL substitute for `ON CONFLICT`,
   numeric, isolation, or driver behavior tests.
   - **Progressive hint:** A fast substitute is useful only when it shares the semantics under
     test.
11. **Security testing:** Pass an injection-shaped value through the cursor adapter and prove it
   appears only in the parameter tuple.
   - **Progressive hint:** Recording fakes should keep query and parameters in separate fields.
12. **Property reasoning:** Define invariants for order totals over empty, single, and multiple
   non-negative Decimal sequences.
   - **Progressive hint:** Useful invariants complement example cases without changing domain
     policy.
13. **Sensitive fixtures:** Design fixture credentials and failure assertions so secret-scan
   markers remain explicit and secrets never enter test IDs or assertion messages.
   - **Progressive hint:** Parameterized test IDs and reprs are output channels.
14. **Isolation:** Run the optional integration case twice and prove rollback makes repetition
   independent.
   - **Progressive hint:** A passing test that leaves data behind is not isolated.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


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
