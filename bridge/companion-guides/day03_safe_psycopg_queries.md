# Bridge Day 3 — Safe parameterized Psycopg queries

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 2](day02_protocols_context_decorators.md)

## Why this matters

SQL text and data values are different things. Psycopg 3 sends them separately
when you use `%s` placeholders and a parameter sequence. String interpolation
blurs that boundary and can turn an ordinary value into executable SQL. Table
and column names are different again: placeholders cannot represent them, so
Psycopg provides composable `SQL` and `Identifier` objects.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day03_safe_psycopg_queries.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day03_safe_psycopg_queries.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day03_safe_psycopg_queries.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Objectives

By the end, you can:

- execute PostgreSQL statements with `%s` placeholders and separate values;
- map driver rows into typed domain records;
- test query shape and bound values with a recording cursor;
- distinguish values from identifiers;
- compose an allowlisted identifier with `psycopg.sql.Identifier`.

## Vocabulary

| Term | Meaning |
|---|---|
| parameter binding | Sending SQL structure and data values separately |
| SQL injection | Untrusted input changing the structure or meaning of a statement |
| placeholder | A marker whose value the driver binds separately; Psycopg uses `%s` |
| identifier | A database object name such as a table or column |
| allowlist | A small explicit set of accepted values |
| row mapping | Converting a driver row into an application type |


## Worked example: structure and values stay separate

```python
statement = """
SELECT order_id, total_amount
FROM training.orders
WHERE status = %s AND total_amount >= %s
ORDER BY order_id
"""
cursor.execute(statement, ("paid", minimum_amount))
```

The placeholder is always `%s`, even for integers and decimals. Do not write
`'%s'`; quoting is the driver's job. A malicious-looking status remains a value
because it never becomes part of `statement`.

This is not valid identifier binding:

```python
# Wrong: a placeholder cannot stand for a table name.
cursor.execute("SELECT count(*) FROM %s", ("orders",))
```

For a genuinely dynamic table, first restrict choices, then use
`sql.Identifier`. Never write your own identifier-quoting function.


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: SQL structure, data values, and row mapping

A database call crosses three boundaries. First, the SQL statement defines
trusted structure: selected columns, joins, predicates, grouping, and ordering.
Second, a parameter sequence carries untrusted data values separately. Third,
returned driver rows are converted into application types. Treating these as
three explicit steps makes both security and correctness testable without a
database server.

Psycopg uses `%s` placeholders for values regardless of the Python value's
type. Do not add quotes around the placeholder. The driver adapts the value and
sends it separately from the statement. A recording cursor can prove the
boundary by storing the SQL object and parameters independently:

```python
class RecordingCursor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(self, query: str, params: tuple[object, ...]) -> None:
        self.calls.append((query, params))


cursor = RecordingCursor()
country = "US' OR TRUE --"
cursor.execute("SELECT 1 WHERE %s = %s", (country, "US"))
assert cursor.calls[0][1][0] == country
assert country not in cursor.calls[0][0]
```

Identifiers are different because a table or column name changes SQL grammar.
A value placeholder cannot stand for `training.customers`. If a reusable
function truly needs a dynamic identifier, validate it against a small
application allowlist and compose it with `psycopg.sql.Identifier`. The
allowlist expresses authorization—what the application permits—while
`Identifier` expresses correct quoting. Both are necessary.

The query result has its own contract. A left join preserves customers without
orders; `COALESCE` gives them exact zero; `HAVING` filters after aggregation;
and a unique tie-breaker makes ordering deterministic. When rows become
`Customer` objects, convert identifiers, text, and money explicitly. Preserve
`Decimal` for money instead of passing through a float. A fake-backed test
should assert one execute call, the exact parameter tuple, one fetch, and the
mapped objects. The optional PostgreSQL smoke test proves server semantics, but
it does not replace these fast boundary tests.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

## Exercises

### Practice contract

- **Focus:** Keep SQL structure trusted, bind data values separately, and compose the rare dynamic identifier through an allowlist plus Psycopg.
- **Assumptions:** The course uses PostgreSQL semantics, `Decimal` money, and fake-backed imports that remain usable without Psycopg installed.
- **Primary failure mode:** String interpolation, quoted placeholders, and treating identifiers as value parameters all break the security boundary.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **SQL implementation:** Write `FIND_CUSTOMERS_SQL` for customer ID, name, and lifetime order
   value by country and minimum total with deterministic ordering.
   - **Progressive hint:** Left join orders, aggregate at customer grain, and keep two `%s`
     placeholders unquoted.
   - **Verify:** Inspect `FIND_CUSTOMERS_SQL`: it selects customer ID/name, uses `LEFT JOIN`, `COALESCE`, `GROUP BY`, and `HAVING`, contains exactly two `%s` placeholders, and orders by lifetime value descending then customer ID.
2. **Implementation:** Implement `find_customers()` with two bound parameters and map rows to
   `Customer` while preserving `Decimal` money.
   - **Progressive hint:** Execute once, fetch once, and make row conversion explicit at the
     application boundary.
   - **Verify:** Configure rows with integer/string/Decimal fields; assert one execute call receives `(country, minimum_lifetime_value)` and the returned tuple contains exact typed `Customer` objects with `Decimal` money.
3. **Security testing:** Use a recording cursor and an injection-shaped country to prove values
   never enter SQL text.
   - **Progressive hint:** Assert both halves: placeholder remains in structure and hostile text
     appears only in parameters.
   - **Verify:** Use country `US' OR TRUE --`; assert that sentinel is absent from SQL text, appears unchanged as the first bound parameter, and cannot add rows to the fake result.
4. **Identifier safety:** Implement `build_count_query()` for only `customers`, `orders`, and
   `order_items` using `psycopg.sql.Identifier`.
   - **Progressive hint:** Allowlist first, import Psycopg inside the optional boundary, then
     compose schema and table identifiers.
   - **Verify:** Assert each of `customers`, `orders`, and `order_items` composes through `sql.Identifier`, while `users` and an injection-shaped name raise `ValueError` before cursor execution.
5. **Reasoning:** Explain why an allowlist remains valuable when `Identifier` already quotes
   safely.
   - **Progressive hint:** Quoting protects syntax; authorization controls which valid object
     may be selected.
   - **Verify:** Show that `Identifier` quotes a syntactically valid but unauthorized name, whereas the allowlist rejects it; record authorization and quoting as separate guarantees.
6. **Prediction:** Predict the result for a customer with no orders and explain the roles of
   `LEFT JOIN`, `COALESCE`, `GROUP BY`, and `HAVING`.
   - **Progressive hint:** Track row preservation first, then aggregation, then threshold
     filtering.
   - **Verify:** For a customer with no orders and minimum total zero, predict and assert lifetime value `Decimal('0')`; explain that the left join retains the row and `COALESCE` supplies zero before `HAVING` evaluates it.
7. **Boundary testing:** Test rows containing integer, string, and already-Decimal values plus
   an empty result; document conversion failures.
   - **Progressive hint:** Mapping is application validation, not a blind cast after trust.
   - **Verify:** Assert integer, numeric string, and `Decimal` money rows map predictably, an empty fetch returns `()`, and malformed ID or money data raises the documented conversion exception.
8. **Debugging:** Repair queries that use `f"...{country}..."` or `WHERE country = '%s'` and
   explain both failures.
   - **Progressive hint:** Placeholders are driver syntax and must not be interpolated or
     quoted.
   - **Verify:** Show the f-string version embeds the sentinel and the quoted-placeholder version sends literal `%s`; after repair, SQL stays static and the sentinel exists only in parameters.
9. **Protocol testing:** Verify that `find_customers()` does not depend on the return value of
   `execute()` and calls `fetchall()` exactly once.
   - **Progressive hint:** Model only the cursor behavior the consumer uses.
   - **Verify:** Use an `execute()` method that returns `None`; assert `find_customers()` still succeeds, `execute` is called once, and `fetchall` is called exactly once.
10. **Optional integration:** Design a bounded, read-only PostgreSQL smoke test gated by
   `DS60_DATABASE_URL` without importing Psycopg during normal fake tests.
   - **Progressive hint:** Skip clearly when the opt-in dependency or variable is absent; never
     print the URL.
   - **Verify:** With the live gate off, assert no Psycopg import or connection occurs; if enabled, run one ordered read-only query against `advanced_sql_training`, cap rows, and close cleanly.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


## Optional live-DB step

Only after fake tests pass, set `DS60_DATABASE_URL` to the disposable course
database and run the read-only function in a Python shell.

```powershell
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.\.venv\Scripts\python.exe
```

```bash
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.venv/bin/python
```

Connect with `psycopg.connect(os.environ["DS60_DATABASE_URL"])`, open a cursor,
and call your function. Do not print the URL. This step reads only; if you add
temporary exploratory writes, call `rollback()` before closing.

## Self-check

- Are there exactly two `%s` placeholders and two separate values?
- Does the injection-shaped country remain absent from the query string?
- Are money values represented with `Decimal`, not binary `float`?
- Is output ordering deterministic when totals tie?
- Does an unsupported identifier fail before `cursor.execute()`?

## Common pitfalls

- **Using f-strings or `.format()` for values:** this creates an injection path.
- **Quoting a placeholder:** `WHERE country = '%s'` binds incorrectly.
- **Using SQLite for tests:** its placeholders, type behavior, concurrency, and
  SQL dialect do not prove PostgreSQL behavior.
- **Calling `str(Identifier(...))` as SQL:** composable objects need a Psycopg
  connection context to render correctly.
- **Assuming row shape forever:** map and validate rows at the adapter boundary.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-02`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-03: Safe Psycopg Queries.
Direct catalog prerequisites: bridge-02. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day03_safe_psycopg_queries.md
Learner artifact: bridge/lessons/day03_safe_psycopg_queries.py

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

[Day 4](day04_transactions_idempotency_retries.md) adds writes, transaction
ownership, and retry classification. See
[the Day 3 solution notes](../solutions/day03_solutions.md) after attempting the
exercises.
