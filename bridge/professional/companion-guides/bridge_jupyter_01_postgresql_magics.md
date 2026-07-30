# BRIDGE-JUPYTER-01 — PostgreSQL magics in Jupyter

## Level and prerequisites

**Level:** Intermediate/advanced  
**Stable lesson ID:** `bridge-jupyter-01`  
**Catalog prerequisites:** `python-18`, `sql-15`, and `bridge-03`  
**Prerequisites:** Python Day 18, SQL Day 15,
[Bridge Day 3](../../companion-guides/day03_safe_psycopg_queries.md), the
repository notebook and bridge dependencies, and a reset disposable course
database.

This module is for interactive analysis. Its learner artifact is the
[answer-free notebook](../notebooks/bridge_jupyter_01_postgresql_magics.ipynb);
the completed notebook remains separate under `solutions/`.

### One-time connected setup

Install the course profiles before going offline:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

```bash
# macOS/Linux
bash scripts/setup.sh --advanced
```

Do not install packages with `%pip` inside the lesson. Central setup keeps the
kernel reproducible and prevents a notebook from silently selecting a different
interpreter.

Reset and verify only the disposable `advanced_sql_training` database using
the canonical PostgreSQL setup guide. The reset drops and recreates the
course-owned `training` schema; never point it at valuable data.

### Start VS Code with the environment value

Close existing course kernels. From the repository root, set the connection
string only for the current shell and launch VS Code from that same process:

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = Read-Host "Paste the disposable course PostgreSQL URL"
code .
```

```bash
# macOS/Linux
read -r -s -p "Disposable course PostgreSQL URL: " DS60_DATABASE_URL
export DS60_DATABASE_URL
printf '\n'
code .
```

Open the learner notebook, choose the `ds60sqlpy` kernel, and run cells in
order. Starting VS Code from the shell matters: a kernel cannot inherit an
environment variable added later to an unrelated terminal.

JupyterLab is also supported:

```powershell
# Windows PowerShell, after setting DS60_DATABASE_URL
.\.venv\Scripts\python.exe -m jupyter lab
```

```bash
# macOS/Linux, after setting DS60_DATABASE_URL
.venv/bin/python -m jupyter lab
```

Do not print the environment value, paste it into a cell, save it in notebook
output, or commit a credential file.

## Learning objectives

By the end, you can:

- distinguish IPython line and cell magics;
- load JupySQL and manage a named connection;
- convert `DS60_DATABASE_URL` into a SQLAlchemy Psycopg 3 URL without rendering
  credentials;
- bind a SQLAlchemy engine with `%sql`;
- configure connection display and result limits safely;
- query the `training` schema with `%sql` and `%%sql`;
- convert a JupySQL result to pandas and use `autopandas` deliberately;
- bind data with named `:value` parameters;
- explain why Jinja `{{...}}` is code generation rather than safe binding;
- explain why values and identifiers need different composition mechanisms;
- recognize JupySQL autocommit and notebook-order hazards;
- choose Psycopg application code when interactive magics are the wrong layer.

## Vocabulary and concepts

| Term | Meaning |
|---|---|
| IPython magic | Command supplied by the IPython kernel rather than ordinary Python syntax |
| line magic | One-line command beginning with `%`, such as `%sql SELECT 1` |
| cell magic | Command beginning with `%%` whose body is the rest of the cell |
| JupySQL | IPython extension providing `%sql`, `%%sql`, and related database magics |
| SQLAlchemy engine | Lazy connection and dialect boundary that JupySQL can use |
| dialect URL | URL selecting both a database and driver, here `postgresql+psycopg` |
| parameter binding | Sending SQL structure and data values separately |
| code generation | Rendering text that becomes SQL structure before execution |
| identifier | Database object name such as a schema, table, or column |
| `autolimit` | JupySQL bound on rows returned by a query |
| `displaylimit` | Display-only truncation; all rows may still be fetched |
| `autopandas` | Configuration that returns pandas DataFrames directly |
| autocommit | Mode in which each issued statement commits without an explicit surrounding unit |

## Worked example / walkthrough

### 1. Load the extension

`%load_ext sql` registers JupySQL's magics in the current IPython kernel.
`%sql?` shows the locally installed command help. The extension is named
`sql`, even though the package installed during setup is JupySQL.

IPython defines one-percent line magics and two-percent cell magics. A line
magic can appear on the right side of an assignment; a cell magic owns the
whole remaining cell. See the
[official IPython magic introduction](https://ipython.readthedocs.io/en/stable/interactive/tutorial.html#magic-functions).

### 2. Build the engine without displaying its URL

Read the URL from `os.environ`, parse it with `sqlalchemy.engine.make_url()`,
validate the PostgreSQL backend and exact disposable database name, then select
the Psycopg 3 driver:

```python
raw_database_url = os.environ["DS60_DATABASE_URL"]
course_url = make_url(raw_database_url)
psycopg_url = course_url.set(drivername="postgresql+psycopg")
engine = create_engine(psycopg_url, pool_pre_ping=True)
```

Do not evaluate `raw_database_url`, `course_url`, `psycopg_url`, or `engine` as
the last expression in a notebook cell. Notebook display can reveal more than
intended. The lesson ends the cell with a safe assertion.

SQLAlchemy documents `postgresql+psycopg` as the synchronous Psycopg 3 dialect.
The unqualified PostgreSQL URL may otherwise select a different default driver.

### 3. Configure safe interactive defaults

Set configuration before connecting:

```ipython
%config SqlMagic.displaycon = False
%config SqlMagic.autolimit = 200
%config SqlMagic.displaylimit = 25
%config SqlMagic.autopandas = False
%config SqlMagic.named_parameters = "enabled"
```

`displaycon=False` suppresses connection-string feedback after queries.
`autolimit` is the memory/performance guard. `displaylimit` only limits visible
rows; it can still fetch the full result. `autopandas=True` bypasses JupySQL's
display limit, so SQL should still use an intentional `LIMIT`.
[JupySQL's configuration reference](https://jupysql.readthedocs.io/en/latest/api/configuration.html)
documents these distinctions.

These settings are notebook ergonomics, not a substitute for statement
timeouts, server permissions, reviewed queries, or production resource limits.

### 4. Bind, inspect, and close an engine

Pass the Python engine object and an alias:

```ipython
%sql engine --alias ds60-course
%sql --connections
```

Switching among several databases by alias is possible, but this course module
uses one disposable target. At the end:

```ipython
%sql --close ds60-course
```

Then call `engine.dispose()` in ordinary Python. The
[JupySQL `%sql` reference](https://jupysql.readthedocs.io/en/latest/api/magic-sql.html)
documents `--connections`, `--close`, aliases, line queries, cell queries, and
DataFrame conversion.

### 5. Query with line and cell magics

A small diagnostic fits on one line:

```ipython
%sql SELECT current_database() AS database_name
```

A reviewed multi-line query is easier to read as a cell:

```sql
%%sql
SELECT customer_id, full_name, country
FROM training.customers
ORDER BY customer_id
LIMIT 5;
```

The notebook deliberately performs no DDL, INSERT, UPDATE, DELETE, COPY, or
stored routine call.

### 6. Bind values, do not render them

JupySQL named parameters refer to Python variables:

```python
order_status = "paid"
minimum_total = 250
```

```ipython
orders_result = %sql SELECT order_id, total_amount FROM training.orders WHERE status = :order_status AND total_amount >= :minimum_total ORDER BY order_id LIMIT 20
```

The SQL keeps `:order_status` and `:minimum_total` as named value parameters.
The driver binds their values separately.

By contrast, `{{value}}` is Jinja expansion. It renders text that becomes SQL
source, so malicious or merely malformed input can change the statement.
JupySQL's own magic reference warns that templated values require sanitization.
Use templating only for reviewed code-generation cases, never ordinary data.

### 7. Keep identifiers static

Parameters bind values, not grammar. A table name cannot replace a value marker:

```sql
-- Not identifier binding:
SELECT count(*) FROM :table_name;
```

For a notebook, prefer a static course table. In reusable Psycopg code, enforce
an application allowlist and use `psycopg.sql.Identifier`. Quoting with a
parameter, f-string, `.format()`, Jinja, or a homemade escape function is not a
safe identifier boundary.

### 8. Convert results to pandas

With `autopandas=False`:

```python
orders_frame = orders_result.DataFrame()
```

With `autopandas=True`, an assigned line magic directly returns a DataFrame:

```ipython
%config SqlMagic.autopandas = True
frame = %sql SELECT customer_id, full_name FROM training.customers ORDER BY customer_id LIMIT 10
%config SqlMagic.autopandas = False
```

Keep the data small enough for notebook memory. For a large query, aggregate in
PostgreSQL, page or stream through application code, or write a bounded
extract—do not rely on a browser display limit.

### 9. Understand transaction ownership

JupySQL documents `SqlMagic.autocommit=True` as its default. Notebook cells are
easy to re-run or execute out of order. The professional lesson therefore uses
read-only statements.

For reviewed multi-step writes, use an explicit SQLAlchemy `engine.begin()` or
Psycopg transaction context and define who commits, rolls back, and retries.
Turning `SqlMagic.autocommit` off is not by itself a complete application
transaction policy, especially after a failed PostgreSQL statement leaves a
transaction aborted.

### 10. Know when Psycopg is the better boundary

Keep JupySQL for interactive, bounded exploration. Use tested Psycopg
application code for:

- typed row/domain mapping;
- reusable query functions;
- multiple statements with one transaction owner;
- retry and SQLSTATE classification;
- idempotency keys;
- COPY, server-side cursors, and streaming;
- pooling, async work, cancellation, and timeouts;
- structured logging and metrics;
- Protocol-based fakes plus small live integration tests.

A notebook can import those functions. It should not become the only location
where critical production behavior exists.

## Exercises

### Practice contract

- **Focus:** Use JupySQL for bounded, reviewable PostgreSQL exploration while keeping credentials out of cells and values separate from SQL structure.
- **Assumptions:** The notebook reads `DS60_DATABASE_URL`, binds an explicit SQLAlchemy `postgresql+psycopg` engine, disables connection display, and keeps live cells tagged.
- **Primary failure mode:** Notebook output, connection displays, Jinja rendering, or unbounded result materialization can leak secrets or turn exploration into unsafe application behavior.
- **Evidence loop:** state the boundary and prediction, implement against
  deterministic local doubles, test success/failure/cleanup, and label any
  optional live-adapter evidence separately from offline proof.

1. **Magic selection:** Run the line diagnostic and multi-line training query; explain why one
   `%sql` form is easier to review for each statement.
   - **Progressive hint:** Choose from statement shape and reviewability, not from different
     security semantics.
2. **Security testing:** Bind an injection-shaped string to a harmless read-only comparison,
   verify it behaves as data, then remove the value.
   - **Progressive hint:** Use `:name`; never paste the sentinel into SQL or notebook output.
3. **SQL practice:** Query US customers whose lifetime order total meets a Python threshold;
   bind country and threshold, order deterministically, and limit to 10.
   - **Progressive hint:** Aggregate after a left join, apply the threshold after grouping, and
     add customer ID as tie-breaker.
4. **DataFrame boundary:** Convert the assigned result with `.DataFrame()` and assert the
   expected columns in order.
   - **Progressive hint:** Treat conversion as an explicit boundary and validate shape before
     analysis.
5. **Configuration:** Repeat one small query with `autopandas=True`, identify the changed return
   type, then restore it to false.
   - **Progressive hint:** Notebook-global magic configuration is hidden state unless restored
     visibly.
6. **Memory reasoning:** Explain why `displaylimit=25` does not bound memory and identify the
   setting/query clause that does.
   - **Progressive hint:** Rendering fewer rows is different from fetching fewer rows.
7. **Identifier boundary:** Explain why `FROM :table_name` is not identifier binding and how a
   Psycopg application handles a validated dynamic identifier.
   - **Progressive hint:** Bound parameters represent data values, never SQL grammar.
8. **Architecture decision:** Write a decision note choosing interactive exploration or Psycopg
   application code using at least three criteria.
   - **Progressive hint:** Consider reuse, transaction ownership, tests, dynamic structure,
     scale, and operational observability.
9. **Cleanup:** List active aliases, close `ds60-course`, dispose the engine, and verify no
   connection literal or output remains saved.
   - **Progressive hint:** Both JupySQL alias state and SQLAlchemy pool state need explicit
     cleanup.
10. **Setup review:** Trace how the environment URL becomes a SQLAlchemy engine without ever
   being displayed and identify every validation step.
   - **Progressive hint:** Validate scheme, driver, host/database target, and display settings
     before connecting.
11. **Prediction:** Predict the difference between a `%sql` line assignment and a `%%sql` cell
   when both return the same rows.
   - **Progressive hint:** Compare Python assignment syntax, multi-line readability, and result
     access.
12. **Capacity:** Design a query/result-size check for a table with millions of rows and explain
   what remains unbounded after `LIMIT 25`.
   - **Progressive hint:** Bound output, scan scope, and server work separately.
13. **Type binding:** Bind a `Decimal`, date, boolean, and list value in small read-only queries
   and record their PostgreSQL result types.
   - **Progressive hint:** Let SQLAlchemy/JupySQL adapt Python values; do not pre-render
     literals.
14. **Transaction reasoning:** Use `engine.begin()` for a rollback-safe teaching write in a
   disposable temporary scope, then explain why magics are not the transaction owner.
   - **Progressive hint:** The checked-in notebook remains read-only; describe or run writes
     only in an explicitly authorized disposable lab.
15. **Jinja boundary:** Demonstrate conceptually why `{{value}}` is code generation rather than
   safe value binding, including a harmless fixed example.
   - **Progressive hint:** Rendered text becomes SQL before the driver sees parameters.
16. **Notebook hygiene:** Validate nbformat, stable IDs, kernel metadata, live/static tags,
   empty outputs, and the absence of package-install magics, shell installs, URLs, and
   destructive SQL.
   - **Progressive hint:** Inspect the serialized artifact, not only the visible notebook UI.
17. **Offline review:** Explain how a learner without a running PostgreSQL server can still
   review this module and which claims remain unexecuted.
   - **Progressive hint:** Separate structural/offline evidence from live query evidence.
18. **Handoff:** Extract the capstone query into a Psycopg function design with typed inputs, a
   small cursor Protocol, and a fake-backed test.
   - **Progressive hint:** Carry over SQL and value semantics while changing the
     ownership/testing surface.

### Before opening the solution

- Record what the offline doubles prove and what they cannot prove.
- Inspect exact call order, parameters, schema, and failure behavior.
- Keep credentials, payloads, and high-cardinality identifiers out of output.
- Require deterministic reruns before considering an exercise complete.


## Self-check

- Did the kernel inherit `DS60_DATABASE_URL` without a notebook literal?
- Does the URL select PostgreSQL, Psycopg 3, and exactly the disposable database?
- Is connection display disabled before the first query?
- Is fetched data bounded with `autolimit` or explicit SQL `LIMIT`, not merely
  hidden with `displaylimit`?
- Can you explain one-percent versus two-percent magic syntax?
- Are data values represented with `:name`, never Jinja or string formatting?
- Are table and column names static?
- Can you convert a result explicitly and with `autopandas`?
- Did every cell remain read-only?
- Can you state who owns transactions and retries outside exploratory magics?
- Did you close the alias and dispose the engine?
- Is the notebook free of saved outputs, credentials, local paths, and setup
  commands?

## Common pitfalls

- **Starting the kernel before setting the environment:** restart VS Code or the
  kernel from the configured shell.
- **Using a different Python interpreter:** select the repository
  `ds60sqlpy` kernel.
- **Letting the engine display itself:** even redacted representations invite
  accidental credential handling. End setup cells with a safe assertion.
- **Relying on `displaylimit`:** it truncates presentation, not necessarily the
  fetched result.
- **Leaving `autopandas` enabled unknowingly:** pandas display settings apply,
  and downstream cells receive a different result type.
- **Using Jinja for values:** it is code generation. Use named binding.
- **Trying to bind identifiers:** value parameters cannot represent SQL
  grammar.
- **Writing through an exploratory notebook:** out-of-order re-execution and
  autocommit make side effects hard to review and recover.
- **Assuming `%sql --close` disposes every resource:** explicitly dispose the
  SQLAlchemy engine as well.
- **Installing from a notebook:** `%pip` mutates the environment and may require
  a kernel restart. Use repository setup while connected.

## Next step

Attempt the [learner notebook](../notebooks/bridge_jupyter_01_postgresql_magics.ipynb)
before reviewing the
[completed notebook](../solutions/bridge_jupyter_01_postgresql_magics_solution.ipynb)
and [solution reasoning](../solutions/bridge_jupyter_01_postgresql_magics_solutions.md).
Then use Bridge Days 3–5 to move a reusable query behind a typed, tested
Psycopg boundary, or continue to BRIDGE-OPS-01 for migration delivery and
operational evidence.
