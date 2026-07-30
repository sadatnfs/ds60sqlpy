# Bridge Day 3 — Safe parameterized Psycopg queries

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 2](day02_protocols_context_decorators.md)

## Why this matters

SQL text and data values are different things. Psycopg 3 sends them separately
when you use `%s` placeholders and a parameter sequence. String interpolation
blurs that boundary and can turn an ordinary value into executable SQL. Table
and column names are different again: placeholders cannot represent them, so
Psycopg provides composable `SQL` and `Identifier` objects.

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

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day03_safe_psycopg_queries.py
```

```bash
.venv/bin/python bridge/lessons/day03_safe_psycopg_queries.py
```

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
2. **Implementation:** Implement `find_customers()` with two bound parameters and map rows to
   `Customer` while preserving `Decimal` money.
   - **Progressive hint:** Execute once, fetch once, and make row conversion explicit at the
     application boundary.
3. **Security testing:** Use a recording cursor and an injection-shaped country to prove values
   never enter SQL text.
   - **Progressive hint:** Assert both halves: placeholder remains in structure and hostile text
     appears only in parameters.
4. **Identifier safety:** Implement `build_count_query()` for only `customers`, `orders`, and
   `order_items` using `psycopg.sql.Identifier`.
   - **Progressive hint:** Allowlist first, import Psycopg inside the optional boundary, then
     compose schema and table identifiers.
5. **Reasoning:** Explain why an allowlist remains valuable when `Identifier` already quotes
   safely.
   - **Progressive hint:** Quoting protects syntax; authorization controls which valid object
     may be selected.
6. **Prediction:** Predict the result for a customer with no orders and explain the roles of
   `LEFT JOIN`, `COALESCE`, `GROUP BY`, and `HAVING`.
   - **Progressive hint:** Track row preservation first, then aggregation, then threshold
     filtering.
7. **Boundary testing:** Test rows containing integer, string, and already-Decimal values plus
   an empty result; document conversion failures.
   - **Progressive hint:** Mapping is application validation, not a blind cast after trust.
8. **Debugging:** Repair queries that use `f"...{country}..."` or `WHERE country = '%s'` and
   explain both failures.
   - **Progressive hint:** Placeholders are driver syntax and must not be interpolated or
     quoted.
9. **Protocol testing:** Verify that `find_customers()` does not depend on the return value of
   `execute()` and calls `fetchall()` exactly once.
   - **Progressive hint:** Model only the cursor behavior the consumer uses.
10. **Optional integration:** Design a bounded, read-only PostgreSQL smoke test gated by
   `DS60_DATABASE_URL` without importing Psycopg during normal fake tests.
   - **Progressive hint:** Skip clearly when the opt-in dependency or variable is absent; never
     print the URL.

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

## Next step

[Day 4](day04_transactions_idempotency_retries.md) adds writes, transaction
ownership, and retry classification. See
[the Day 3 solution notes](../solutions/day03_solutions.md) after attempting the
exercises.
