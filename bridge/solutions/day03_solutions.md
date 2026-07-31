# Bridge Day 3 — Solution notes

Start with the [learner file](../lessons/day03_safe_psycopg_queries.py). The
reference implementation is [day03_solution.py](day03_solution.py).

## Value binding

`FIND_CUSTOMERS_SQL` contains two `%s` placeholders. `find_customers()` supplies
the country and minimum `Decimal` as a separate tuple. A recording fake proves
that injection-shaped input is data in `params`, never text in the query.

The SQL left-joins orders, groups per customer, converts no-order totals to zero,
filters aggregates with `HAVING`, and uses customer ID as a deterministic
tie-breaker. Returned driver rows become immutable `Customer` objects at the
adapter boundary.

## Identifier composition

`build_count_query()` first allowlists three course tables. It then imports
`psycopg.sql` at the live boundary and combines `SQL` with `Identifier`.
Identifiers cannot be parameters, and manually quoting them is brittle.

The allowlist and `Identifier` solve different problems:

- `Identifier` produces valid, injection-safe SQL syntax.
- The allowlist enforces the application's authorization and intent.

## Tradeoffs

- A positional row mapper is lightweight but depends on selected column order.
  Psycopg row factories can return mappings or dataclasses when that improves a
  larger adapter.
- Converting through `Decimal(str(value))` is tolerant of fake values and common
  driver outputs. A strict application may reject unexpected driver types.
- Local Psycopg import keeps fake tests offline and importable. It moves a
  missing dependency error to the optional live function, where the message is
  more actionable.
- One aggregate query is efficient for this lesson. At higher volume, verify
  its plan and indexes against real PostgreSQL data.

Never replace the PostgreSQL integration check with SQLite. The recording fake
proves application composition; PostgreSQL proves PostgreSQL behavior.


<!-- BEGIN BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->
## Small executable check

The statement itself makes the value boundary inspectable before a live run:

```python
from bridge.solutions.day03_solution import FIND_CUSTOMERS_SQL

assert FIND_CUSTOMERS_SQL.count("%s") == 2
assert "ORDER BY lifetime_value DESC, c.customer_id" in FIND_CUSTOMERS_SQL
```

A cursor-double test should additionally show that the country and minimum
total appear only in the parameter tuple.
<!-- END BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day03_solution.py`; use it only after an honest attempt.

**Shared failure rule:** String interpolation, quoted placeholders, and treating identifiers as value parameters all break the security boundary.

### Exercise 1 — SQL implementation

**Prompt:** Write `FIND_CUSTOMERS_SQL` for customer ID, name, and lifetime order value by
country and minimum total with deterministic ordering.

**Approach:** Group customers after a left join, convert missing totals to exact zero, apply the
threshold in `HAVING`, then order by lifetime value descending and customer ID ascending.
Country and threshold remain separate parameters.

**Why this boundary matters:** Left join orders, aggregate at customer grain, and keep two `%s`
placeholders unquoted.

**Verification evidence:** Inspect `FIND_CUSTOMERS_SQL`: it selects customer ID/name, uses `LEFT JOIN`, `COALESCE`, `GROUP BY`, and `HAVING`, contains exactly two `%s` placeholders, and orders by lifetime value descending then customer ID.

### Exercise 2 — Implementation

**Prompt:** Implement `find_customers()` with two bound parameters and map rows to `Customer`
while preserving `Decimal` money.

**Approach:** Call `execute(FIND_CUSTOMERS_SQL, (country, minimum_lifetime_value))`, then
construct one frozen `Customer` per row with explicit `int`, `str`, and `Decimal` conversion.

**Why this boundary matters:** Execute once, fetch once, and make row conversion explicit at the
application boundary.

**Verification evidence:** Configure rows with integer/string/Decimal fields; assert one execute call receives `(country, minimum_lifetime_value)` and the returned tuple contains exact typed `Customer` objects with `Decimal` money.

### Exercise 3 — Security testing

**Prompt:** Use a recording cursor and an injection-shaped country to prove values never enter
SQL text.

**Approach:** Inspect the single recorded call. The query must still contain `%s`, must not
contain the hostile string, and the parameter tuple must contain that string unchanged as data.

**Why this boundary matters:** Assert both halves: placeholder remains in structure and hostile
text appears only in parameters.

**Verification evidence:** Use country `US' OR TRUE --`; assert that sentinel is absent from SQL text, appears unchanged as the first bound parameter, and cannot add rows to the fake result.

### Exercise 4 — Identifier safety

**Prompt:** Implement `build_count_query()` for only `customers`, `orders`, and `order_items`
using `psycopg.sql.Identifier`.

**Approach:** Reject names outside a frozen allowlist before importing/composing. Build `SELECT
count(*) FROM {}.{}` with separate `Identifier('training')` and `Identifier(table_name)` objects
rather than interpolating text.

**Why this boundary matters:** Allowlist first, import Psycopg inside the optional boundary,
then compose schema and table identifiers.

**Verification evidence:** Assert each of `customers`, `orders`, and `order_items` composes through `sql.Identifier`, while `users` and an injection-shaped name raise `ValueError` before cursor execution.

### Exercise 5 — Reasoning

**Prompt:** Explain why an allowlist remains valuable when `Identifier` already quotes safely.

**Approach:** `Identifier` prevents a name from becoming executable SQL, but without an
allowlist a caller could still read another legitimately named table. The two controls address
injection and object authorization separately.

**Why this boundary matters:** Quoting protects syntax; authorization controls which valid
object may be selected.

**Verification evidence:** Show that `Identifier` quotes a syntactically valid but unauthorized name, whereas the allowlist rejects it; record authorization and quoting as separate guarantees.

### Exercise 6 — Prediction

**Prompt:** Predict the result for a customer with no orders and explain the roles of `LEFT
JOIN`, `COALESCE`, `GROUP BY`, and `HAVING`.

**Approach:** The customer survives the left join, its aggregate is NULL until `COALESCE` turns
the documented absence into `Decimal('0')`, and it passes only when the bound minimum is at most
zero.

**Why this boundary matters:** Track row preservation first, then aggregation, then threshold
filtering.

**Verification evidence:** For a customer with no orders and minimum total zero, predict and assert lifetime value `Decimal('0')`; explain that the left join retains the row and `COALESCE` supplies zero before `HAVING` evaluates it.

### Exercise 7 — Boundary testing

**Prompt:** Test rows containing integer, string, and already-Decimal values plus an empty
result; document conversion failures.

**Approach:** The empty fetch maps to `[]`; valid rows become typed objects; a malformed ID or
amount raises at conversion rather than silently changing meaning. Keep that failure outside any
secret-bearing log.

**Why this boundary matters:** Mapping is application validation, not a blind cast after trust.

**Verification evidence:** Assert integer, numeric string, and `Decimal` money rows map predictably, an empty fetch returns `()`, and malformed ID or money data raises the documented conversion exception.

### Exercise 8 — Debugging

**Prompt:** Repair queries that use `f"...{country}..."` or `WHERE country = '%s'` and explain
both failures.

**Approach:** Restore static SQL with bare `%s` and pass `(country,)` separately. The f-string
enables injection; quoted `%s` is a literal string and prevents driver binding.

**Why this boundary matters:** Placeholders are driver syntax and must not be interpolated or
quoted.

**Verification evidence:** Show the f-string version embeds the sentinel and the quoted-placeholder version sends literal `%s`; after repair, SQL stays static and the sentinel exists only in parameters.

### Exercise 9 — Protocol testing

**Prompt:** Verify that `find_customers()` does not depend on the return value of `execute()`
and calls `fetchall()` exactly once.

**Approach:** Have the fake `execute` return an unrelated sentinel and track call counts. The
function should ignore that sentinel, fetch from the cursor, and perform one execute/fetch
cycle.

**Why this boundary matters:** Model only the cursor behavior the consumer uses.

**Verification evidence:** Use an `execute()` method that returns `None`; assert `find_customers()` still succeeds, `execute` is called once, and `fetchall` is called exactly once.

### Exercise 10 — Optional integration

**Prompt:** Design a bounded, read-only PostgreSQL smoke test gated by `DS60_DATABASE_URL`
without importing Psycopg during normal fake tests.

**Approach:** Import Psycopg inside the marked integration test, connect only to the disposable
course URL, run the parameterized function with a high threshold or small result, assert
deterministic shape, and close in a context manager.

**Why this boundary matters:** Skip clearly when the opt-in dependency or variable is absent;
never print the URL.

**Verification evidence:** With the live gate off, assert no Psycopg import or connection occurs; if enabled, run one ordered read-only query against `advanced_sql_training`, cap rows, and close cleanly.
