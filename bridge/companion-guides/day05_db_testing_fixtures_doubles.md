# Bridge Day 5 — Database tests, fixtures, and test doubles

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 4](day04_transactions_idempotency_retries.md)

## Why this matters

Most application behavior can be tested without opening a database connection.
Those tests should be fast, deterministic, and precise. A smaller integration
layer still needs PostgreSQL tests because a fake cannot prove SQL syntax,
constraints, transaction isolation, or driver conversions. A useful test
strategy knows which question belongs at each layer.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day05_db_testing_fixtures_doubles.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day05_db_testing_fixtures_doubles.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day05_db_testing_fixtures_doubles.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

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


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: test the smallest truthful boundary

A database application needs several kinds of tests because no single double
can prove every property. Pure domain tests prove calculations and validation.
Recording adapter tests prove SQL text stays separate from parameter values and
that rows are mapped correctly. A small opt-in PostgreSQL test proves the
server-specific behavior that a fake cannot reproduce. The useful shape is
many fast tests, fewer adapter tests, and the smallest necessary live layer.

The `OrderRepository` Protocol keeps the business rule independent of a
cursor. Its fake should be deliberately small:

```python
from decimal import Decimal


class OrderAmountsFake:
    def __init__(self) -> None:
        self.requested_ids: list[int] = []

    def amounts_for_customer(self, customer_id: int) -> tuple[Decimal, ...]:
        self.requested_ids.append(customer_id)
        return (Decimal("2.50"), Decimal("7.50"))


fake = OrderAmountsFake()
assert sum(fake.amounts_for_customer(7), Decimal("0.00")) == Decimal("10.00")
assert fake.requested_ids == [7]
```

Notice the division of responsibility: the fake records and returns; the test
asserts. A mock can verify one interaction, but a readable recording fake often
shows order and parameters more clearly. A test double must not imitate SQL
joins, transactions, and constraints so thoroughly that it becomes a second
database implementation.

Fixtures are resource owners. A rollback-only fixture must roll back whether
the body passes or raises, and it must not swallow the body exception. The live
gate requires both explicit authorization and a URL so an ordinary test run
cannot contact a database merely because a credential exists in the shell.
SQLite is not a substitute for PostgreSQL semantics such as `ON CONFLICT`,
array operators, isolation behavior, or Psycopg adaptation.

Finally, rollback does not erase every observable effect: sequences may
advance, locks existed, and external calls cannot be rolled back. Use only the
disposable course database, choose isolated course-owned objects, and verify
postconditions. A live test is incomplete until it proves cleanup and can run
twice without leaving learner data behind.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

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
   - **Verify:** Assert IDs `0` and `-1` raise `ValueError`; an empty repository returns `Decimal('0.00')`; and two configured Decimal amounts sum exactly without float conversion.
2. **Test double:** Implement `FakeOrderRepository` with configured values and public call
   history but no internal assertions.
   - **Progressive hint:** A fake supplies behavior and observations; the test owns
     expectations.
   - **Verify:** Call the fake for configured and missing customer IDs; assert returned sequences and public call history match exactly, with no assertion performed inside the fake.
3. **Testing:** Test totals, exact zero, invalid IDs, Decimal preservation, and the precise
   repository call sequence.
   - **Progressive hint:** Verify behavior and collaboration separately.
   - **Verify:** Compare exact totals for empty/single/multiple sequences, exact zero type, invalid-ID exceptions, unchanged Decimal values, and one repository call per valid request.
4. **Adapter:** Create a cursor-backed repository and test its SQL text and bound customer
   parameter with a recording cursor.
   - **Progressive hint:** Keep SQL structure static and adapt returned rows to Decimal values.
   - **Verify:** Use a recording cursor; assert the SQL remains static with one `%s`, the parameter tuple is `(customer_id,)`, one fetch occurs, and rows become `Decimal` values.
5. **Fixture:** Implement `rollback_only()` so rollback occurs after a passing or failing body
   without suppressing the body failure.
   - **Progressive hint:** Fixture cleanup belongs in `finally`.
   - **Verify:** Assert rollback occurs after a passing body and after a body that raises; in the latter case the original exception identity remains visible and no commit occurs.
6. **Live-test gate:** Require both `DS60_RUN_LIVE_DB_TESTS=1` and `DS60_DATABASE_URL`; skip
   with a clear reason when either is absent.
   - **Progressive hint:** Opt-in state and connection location are independent requirements.
   - **Verify:** Parameterize missing flag, missing URL, and both present; assert only `DS60_RUN_LIVE_DB_TESTS=1` plus a URL enables the fixture and every other case skips.
7. **Integration:** Write one optional test that inserts, queries, and observes a temporary
   order inside a transaction that the fixture rolls back.
   - **Progressive hint:** Use a unique fixture key and verify disappearance after rollback when
     practical.
   - **Verify:** In the opt-in database, insert and read one course-owned temporary order, then assert rollback removes it and a second run starts from the same clean state.
8. **Design:** Compare a fake, a recording stub, and a mock for the repository boundary; choose
   one for each test purpose.
   - **Progressive hint:** Prefer the simplest double that expresses the evidence needed.
   - **Verify:** Provide a table mapping pure totals to the configured fake, SQL/parameter assertions to the recording stub, and one collaboration-count check to a mock, with one reason each.
9. **Failure analysis:** Test what happens when rollback itself fails while the test body is
   already failing and document exception chaining.
   - **Progressive hint:** Cleanup failures can mask the primary assertion.
   - **Verify:** Raise distinct body and rollback exceptions; inspect chaining/grouping and assert the test report contains evidence of both failures rather than silently replacing one.
10. **Database semantics:** Explain why SQLite is not a PostgreSQL substitute for `ON CONFLICT`,
   numeric, isolation, or driver behavior tests.
   - **Progressive hint:** A fast substitute is useful only when it shares the semantics under
     test.
   - **Verify:** List the PostgreSQL behavior under test—conflict handling, exact numeric adaptation, transaction/isolation, and Psycopg calls—and mark each as unproved by SQLite.
11. **Security testing:** Pass an injection-shaped value through the cursor adapter and prove it
   appears only in the parameter tuple.
   - **Progressive hint:** Recording fakes should keep query and parameters in separate fields.
   - **Verify:** Send an injection-shaped customer value through the adapter; assert it is absent from SQL text and present unchanged only in the recorded parameter tuple.
12. **Property reasoning:** Define invariants for order totals over empty, single, and multiple
   non-negative Decimal sequences.
   - **Progressive hint:** Useful invariants complement example cases without changing domain
     policy.
   - **Verify:** For non-negative Decimal sequences, assert totals are non-negative, empty is exact zero, single returns itself, concatenation totals add, and input order does not change the sum.
13. **Sensitive fixtures:** Design fixture credentials and failure assertions so secret-scan
   markers remain explicit and secrets never enter test IDs or assertion messages.
   - **Progressive hint:** Parameterized test IDs and reprs are output channels.
   - **Verify:** Scan test IDs, exception messages, logs, and snapshots with a sentinel credential; assert the secret never appears while explicit safe markers remain detectable.
14. **Isolation:** Run the optional integration case twice and prove rollback makes repetition
   independent.
   - **Progressive hint:** A passing test that leaves data behind is not isolated.
   - **Verify:** Run the opt-in case twice; assert each run sees only its own temporary row and post-test queries find no persisted course record.

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


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-04`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-05: DB Testing Fixtures Doubles.
Direct catalog prerequisites: bridge-04. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day05_db_testing_fixtures_doubles.md
Learner artifact: bridge/lessons/day05_db_testing_fixtures_doubles.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

[Day 6](day06_bulk_etl_validation.md) uses these seams to validate and load
batches. See [the Day 5 solution notes](../solutions/day05_solutions.md) after
your attempt.
