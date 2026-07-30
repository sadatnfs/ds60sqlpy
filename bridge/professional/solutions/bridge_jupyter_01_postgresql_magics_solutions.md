# BRIDGE-JUPYTER-01 — Solution reasoning

Try the
[learner notebook](../notebooks/bridge_jupyter_01_postgresql_magics.ipynb)
before opening the
[completed notebook](bridge_jupyter_01_postgresql_magics_solution.ipynb).

## Connection construction

The solution reads `DS60_DATABASE_URL` from the process environment, rejects a
non-PostgreSQL backend and any database name other than
`advanced_sql_training`, and replaces the dialect driver with
`postgresql+psycopg`. SQLAlchemy's URL object preserves encoded connection
fields better than string replacement.

The URL variables and engine are never the final expression in a cell, so
Jupyter does not render them. `SqlMagic.displaycon=False` is configured before
the engine is bound. This is defense in depth; the primary rule is never to
log, print, or save the URL.

## Magic and result choices

The diagnostic uses `%sql` because it is one short statement. The first
training query uses `%%sql` because line breaks expose selected columns,
source, ordering, and limit. An assigned `%sql` call returns a JupySQL
`ResultSet` while `autopandas` is false; `.DataFrame()` makes the conversion
explicit.

The second path temporarily enables `autopandas`, proves that the returned
object has the expected shape, and immediately restores the default. Explicit
SQL limits remain useful in both modes.

## Parameter safety

All changing values use named `:value` markers. The completed aggregate binds
country in `WHERE` and the minimum lifetime total in `HAVING`. Static schema,
table, and column names remain SQL structure.

Jinja `{{...}}` is intentionally shown only in explanatory Markdown. It renders
SQL text before execution and is therefore code generation. The solution does
not execute templated input. It also does not pretend parameters can bind
identifiers; a reusable dynamic identifier belongs behind an allowlist and
`psycopg.sql.Identifier` in application code.

## Aggregate reasoning

The check solution:

1. starts from `training.customers`;
2. left-joins orders so customers with no orders remain representable;
3. groups at customer grain;
4. converts a missing sum to zero with `COALESCE`;
5. filters the aggregate with `HAVING`;
6. orders by lifetime total descending and customer ID ascending;
7. limits the result to 10.

The deterministic tie-breaker matters in notebooks and tests. Without it, rows
with equal totals may appear in any order.

## Transaction and cleanup reasoning

The notebook stays read-only because JupySQL autocommit and out-of-order cell
execution make write ownership easy to misunderstand. A small
`engine.begin()` block shows an explicit transaction context without changing
state. Production writes, retries, COPY, streaming, and observability belong
behind tested Psycopg or SQLAlchemy application functions.

Cleanup has two layers: `%sql --close ds60-course` removes JupySQL's named
connection, and `engine.dispose()` releases the SQLAlchemy pool.

## Tradeoffs

- Passing an engine object avoids placing a URL in magic source, but the Python
  process still holds credentials in memory. Process access and notebook trust
  still matter.
- `autolimit` protects exploration from accidental unbounded results, but it
  may alter query semantics or conceal that a result was truncated. Deliberate
  SQL limits and aggregate checks remain clearer.
- `autopandas` is convenient but changes result type globally for the notebook
  session. A local explicit conversion is easier to reason about in shared
  notebooks.
- Magics make exploration concise but are harder to type-check, unit test, and
  reuse than an ordinary Python function.
- A read-only notebook is safer than an ad hoc write notebook, but database
  permissions should enforce least privilege rather than relying on prose.
- A static identifier is intentionally less flexible. The reduced attack and
  review surface is usually desirable during exploration.

The structural tests verify metadata, clean execution state, tag coverage,
required concepts, named parameters, and prohibited credential/setup patterns.
Only an opt-in live run can prove the local PostgreSQL and JupySQL integration.

## Exercise solutions

These walkthroughs map one-for-one to the answer-free learner artifact and
companion guide. The executable reference is `bridge/professional/solutions/bridge_jupyter_01_postgresql_magics_solution.ipynb`.

**Shared failure rule:** Notebook output, connection displays, Jinja rendering, or unbounded result materialization can leak secrets or turn exploration into unsafe application behavior.

### Exercise 1 — Magic selection

**Prompt:** Run the line diagnostic and multi-line training query; explain why one `%sql` form
is easier to review for each statement.

**Approach:** Use line magic for one compact diagnostic or assignment and cell magic for
formatted multi-line SQL. Both use the same bound engine and require the same value-binding
discipline.

**Why:** Choose from statement shape and reviewability, not from different security semantics.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 2 — Security testing

**Prompt:** Bind an injection-shaped string to a harmless read-only comparison, verify it
behaves as data, then remove the value.

**Approach:** Assign the sentinel in Python, reference it through a named parameter, and query a
bounded comparison. The result should reflect literal data semantics rather than altering the
SQL structure.

**Why:** Use `:name`; never paste the sentinel into SQL or notebook output.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 3 — SQL practice

**Prompt:** Query US customers whose lifetime order total meets a Python threshold; bind country
and threshold, order deterministically, and limit to 10.

**Approach:** Use static schema/table names, `:exercise_country` and `:exercise_minimum_total`,
`COALESCE(sum(...), 0)`, `HAVING`, and final `ORDER BY total DESC, customer_id LIMIT 10`.

**Why:** Aggregate after a left join, apply the threshold after grouping, and add customer ID as
tie-breaker.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 4 — DataFrame boundary

**Prompt:** Convert the assigned result with `.DataFrame()` and assert the expected columns in
order.

**Approach:** Call `.DataFrame()` once, compare the exact column list with the query projection,
and assert the row count is bounded by 10 before using the frame.

**Why:** Treat conversion as an explicit boundary and validate shape before analysis.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 5 — Configuration

**Prompt:** Repeat one small query with `autopandas=True`, identify the changed return type,
then restore it to false.

**Approach:** Enable the option in a live-tagged cell, verify a DataFrame is returned directly,
and reset it in the same teaching section so later cells retain explicit result conversion.

**Why:** Notebook-global magic configuration is hidden state unless restored visibly.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 6 — Memory reasoning

**Prompt:** Explain why `displaylimit=25` does not bound memory and identify the setting/query
clause that does.

**Approach:** `displaylimit` truncates presentation only. Use SQL `LIMIT` and JupySQL
`autolimit` as fetch guards, while recognizing that an aggregate or expensive query can still do
substantial server work.

**Why:** Rendering fewer rows is different from fetching fewer rows.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 7 — Identifier boundary

**Prompt:** Explain why `FROM :table_name` is not identifier binding and how a Psycopg
application handles a validated dynamic identifier.

**Approach:** Keep notebook identifiers static. Application code first allowlists the requested
object, then composes it with `psycopg.sql.Identifier`; it does not pass a table name as `%s` or
`:name`.

**Why:** Bound parameters represent data values, never SQL grammar.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 8 — Architecture decision

**Prompt:** Write a decision note choosing interactive exploration or Psycopg application code
using at least three criteria.

**Approach:** Keep bounded one-off read exploration in the notebook; move reusable,
write-capable, dynamically composed, scheduled, or heavily tested behavior into typed
application code.

**Why:** Consider reuse, transaction ownership, tests, dynamic structure, scale, and operational
observability.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 9 — Cleanup

**Prompt:** List active aliases, close `ds60-course`, dispose the engine, and verify no
connection literal or output remains saved.

**Approach:** Inspect `%sql --connections`, close the named alias, call `engine.dispose()`,
clear all outputs/execution counts, and scan notebook JSON for URL-shaped credential text.

**Why:** Both JupySQL alias state and SQLAlchemy pool state need explicit cleanup.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 10 — Setup review

**Prompt:** Trace how the environment URL becomes a SQLAlchemy engine without ever being
displayed and identify every validation step.

**Approach:** Read the variable with `os.environ`, parse with `make_url`, require PostgreSQL
plus the `psycopg` driver and disposable database, set `displaycon=False`, create the engine,
then bind the object rather than a literal URL.

**Why:** Validate scheme, driver, host/database target, and display settings before connecting.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 11 — Prediction

**Prompt:** Predict the difference between a `%sql` line assignment and a `%%sql` cell when both
return the same rows.

**Approach:** A line magic can assign its result directly in Python on one line; a cell magic
owns the whole cell and emphasizes formatted SQL. Result semantics and parameter safety are
otherwise equivalent.

**Why:** Compare Python assignment syntax, multi-line readability, and result access.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 12 — Capacity

**Prompt:** Design a query/result-size check for a table with millions of rows and explain what
remains unbounded after `LIMIT 25`.

**Approach:** Add selective predicates and partition/date bounds, project only needed columns,
use deterministic `LIMIT`, and inspect a plan if authorized. `LIMIT` alone may still require a
large scan/sort and does not cap aggregate work.

**Why:** Bound output, scan scope, and server work separately.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 13 — Type binding

**Prompt:** Bind a `Decimal`, date, boolean, and list value in small read-only queries and
record their PostgreSQL result types.

**Approach:** Assign typed Python values, reference each with `:name`, and use bounded `SELECT
pg_typeof(...)` diagnostics. The adapter preserves value boundaries and exposes type mismatches
explicitly.

**Why:** Let SQLAlchemy/JupySQL adapt Python values; do not pre-render literals.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 14 — Transaction reasoning

**Prompt:** Use `engine.begin()` for a rollback-safe teaching write in a disposable temporary
scope, then explain why magics are not the transaction owner.

**Approach:** Application-level SQLAlchemy context owns commit/rollback and connection return.
JupySQL exploratory cells should remain read-only; any write lab needs a separate tagged,
opt-in, rollback-protected artifact.

**Why:** The checked-in notebook remains read-only; describe or run writes only in an explicitly
authorized disposable lab.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 15 — Jinja boundary

**Prompt:** Demonstrate conceptually why `{{value}}` is code generation rather than safe value
binding, including a harmless fixed example.

**Approach:** Use `:value` for data. Reserve Jinja for trusted, reviewed structure when
unavoidable; never pass user text through it and never describe rendering as equivalent to
driver binding.

**Why:** Rendered text becomes SQL before the driver sees parameters.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 16 — Notebook hygiene

**Prompt:** Validate nbformat, stable IDs, kernel metadata, live/static tags, empty outputs, and
the absence of package-install magics, shell installs, URLs, and destructive SQL.

**Approach:** Run `nbformat.validate` plus repository validators/tests, require the `ds60sqlpy`
kernel and unique IDs, clear every code output/count, and scan sources for forbidden
installation/credential/write patterns.

**Why:** Inspect the serialized artifact, not only the visible notebook UI.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 17 — Offline review

**Prompt:** Explain how a learner without a running PostgreSQL server can still review this
module and which claims remain unexecuted.

**Approach:** They can read all prose/SQL, validate notebook JSON/tags/security, and run
non-live Python cells where dependencies exist. Query results, adapter behavior, and cleanup
against PostgreSQL remain explicitly unverified until the opt-in live path runs.

**Why:** Separate structural/offline evidence from live query evidence.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 18 — Handoff

**Prompt:** Extract the capstone query into a Psycopg function design with typed inputs, a small
cursor Protocol, and a fake-backed test.

**Approach:** Keep static SQL with `%s` placeholders, type country/threshold inputs, inject a
cursor Protocol, map bounded rows explicitly, and test query/parameter separation before an
optional live integration test.

**Why:** Carry over SQL and value semantics while changing the ownership/testing surface.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.
