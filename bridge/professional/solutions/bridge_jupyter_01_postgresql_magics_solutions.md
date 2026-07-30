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
