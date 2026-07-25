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

1. Write `FIND_CUSTOMERS_SQL` using the course `customers` and `orders` tables.
   Return customer ID, full name, and total order value for one country at or
   above a minimum. Choose deterministic ordering.
2. Implement `find_customers()` with two bound parameters. Convert each row to
   `Customer`, preserving monetary values as `Decimal`.
3. Create a recording cursor that stores `(query, params)` and returns fixed
   rows. Use an input such as `"US' OR true --"` to prove it never appears in
   the SQL text.
4. Implement `build_count_query()`. Allow only `customers`, `orders`, and
   `order_items`; then compose `training.<table>` with `psycopg.sql.Identifier`.
5. Explain why an allowlist is valuable even though `Identifier` already quotes
   safely.

### Progressive hints

1. Aggregate order amounts after a left join so customers without orders have
   zero.
2. Group before applying the minimum-total condition.
3. The driver may return `Decimal` already, but an explicit conversion makes
   the application boundary testable.
4. Import Psycopg inside the identifier-composition function so fake-backed
   tests can import the rest of the module without it.

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
