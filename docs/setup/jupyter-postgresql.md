# PostgreSQL in Jupyter

The professional bridge includes a notebook that runs PostgreSQL queries from
the normal Python kernel with JupySQL. JupySQL supplies IPython line and cell
magics such as `%sql` and `%%sql`; PostgreSQL still runs in the local
`advanced_sql_training` database.

For a normal SQL course lesson or solution, open its
[generated guided notebook](../guided-sql-notebooks.md) from the learning
portal. Those notebooks run the complete cataloged script through `psql`
because many course files use `psql` meta-commands that are not valid JupySQL
cells. Use this page for the dedicated lesson about interactive SQL magics.

This is an interactive learning workflow. Application code should continue to
use explicit Psycopg or SQLAlchemy boundaries, tests, and transaction
ownership.

## 1. Install the notebook database profile

The Windows discovery bootstrap's default `Core` profile installs the required
packages. On macOS/Linux, use the aggregate advanced setup.

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1

$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
```

The resolver supports both a standard `venv` and the Anaconda conda-prefix
fallback. Reuse `$CoursePython` for the remaining Windows commands in this
PowerShell window.

macOS/Linux:

```bash
bash scripts/setup.sh --advanced
```

For a smaller targeted installation after normal setup:

```powershell
# Windows PowerShell
& $CoursePython -m pip install -e ".[sql-notebooks]"
```

```bash
# macOS/Linux
.venv/bin/python -m pip install -e ".[sql-notebooks]"
```

The profile installs JupySQL, pandas for `.DataFrame()` result conversion,
SQLAlchemy, and Psycopg 3. Do not put `%pip` installation cells into a lesson
notebook: they hide which interpreter was modified and cannot work during
offline study.

## 2. Prepare only the disposable database

Start or verify PostgreSQL, then reset the course-owned `training` schema with
the commands in the operating-system setup guide.

If you use the repository Compose service:

```text
docker compose up -d postgres
docker compose run --rm sql-runner -f sql/postgres-60day/00_setup.sql
docker compose run --rm sql-runner -f sql/postgres-60day/00_verify.sql
```

Never point the reset or professional notebook at a workplace, shared,
production, or personally valuable database.

## 3. Set the connection for this terminal

The notebook reads `DS60_DATABASE_URL`. Keep it in the terminal environment;
do not paste a real password into the notebook, commit it, or print it.

For the repository's disposable Compose database:

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = "postgresql://ds60:ds60@localhost:5432/advanced_sql_training"
```

```bash
# macOS/Linux
export DS60_DATABASE_URL="postgresql://ds60:ds60@localhost:5432/advanced_sql_training"
```

Those `ds60` credentials belong only to the disposable local Compose service.
For native PostgreSQL, use the local role and authentication method from the
OS setup guide. If a password must appear in a URL, percent-encode reserved
characters and keep the value out of shell history and repository files; a
local password file or operating-system credential store is preferable.

Closing the terminal clears these process-scoped settings. A personal `.env`
file is ignored by Git, but the notebook deliberately does not load one
silently.

## 4. Start the course kernel

Windows PowerShell:

```powershell
& $CoursePython -m jupyter lab .\bridge\professional\notebooks
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab bridge/professional/notebooks
```

In VS Code, open
`bridge/professional/notebooks/bridge_jupyter_01_postgresql_magics.ipynb`
and select **Python (ds60sqlpy)** (internal kernel name `ds60sqlpy`).

The notebook parses the environment value, refuses any target except the
disposable course database, and selects the explicit Psycopg 3 driver:

```python
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

course_url = make_url(os.environ["DS60_DATABASE_URL"])
if course_url.get_backend_name() not in {"postgres", "postgresql"}:
    raise RuntimeError("DS60_DATABASE_URL must select PostgreSQL.")
if course_url.database != "advanced_sql_training":
    raise RuntimeError("This notebook is restricted to the disposable course database.")

psycopg_url = course_url.set(drivername="postgresql+psycopg")
engine = create_engine(psycopg_url, pool_pre_ping=True)
```

It then loads the extension and passes the engine object—not a password-bearing
string—to the magic:

```text
%load_ext sql
%config SqlMagic.displaycon = False
%sql engine --alias ds60-course
```

JupySQL's current connection documentation recommends avoiding hard-coded
passwords, and SQLAlchemy documents `postgresql+psycopg://` as the Psycopg 3
dialect. See the
[JupySQL connection guide](https://jupysql.readthedocs.io/en/latest/connecting.html)
and
[SQLAlchemy PostgreSQL dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html).

## 5. Know what the magics do

- `%sql SELECT ...` runs a short, one-line query.
- `%%sql` makes the rest of a cell SQL.
- `%sql --connections` lists the notebook's active database connections.
- `%sql --close <alias>` closes one connection.
- `%config SqlMagic.displaycon = False` avoids displaying a connection URL.
- `%config SqlMagic.autolimit = 100` bounds exploratory result retrieval.
- `%config SqlMagic.named_parameters = "enabled"` enables bound `:value`
  parameters for SQLAlchemy connections.

Jinja `{{variable}}` syntax renders SQL text and can change identifiers or
whole clauses. It is code generation, not safe value binding. Use named
parameters for values and fixed or allowlisted identifiers. JupySQL documents
both modes in its
[parameterization guide](https://jupysql.readthedocs.io/en/latest/user-guide/template.html).

JupySQL defaults to autocommit. The lesson therefore uses bounded read queries
and explains transaction ownership before any write. Do not assume that
running several notebook cells creates one atomic transaction.

## 6. Verify and go offline

Run the notebook checks while connected:

```powershell
# Windows PowerShell
& $CoursePython scripts\validate_notebooks.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/validate_notebooks.py
```

After packages and PostgreSQL are installed, the notebook needs no internet
connection. The database server must still be running locally. Structural
validation does not prove live authentication; execute the solution notebook
top to bottom against the disposable database for that evidence.

## Common failures

- **`No module named sql`** — install the `sql-notebooks` extra in the selected
  kernel and restart it.
- **`Line magic function %sql not found`** — run `%load_ext sql`; also check
  that no local file named `sql.py` shadows the extension.
- **`No module named psycopg2`** — use the explicit
  `postgresql+psycopg://` URL for the course's Psycopg 3 dependency.
- **Connection refused** — start PostgreSQL and check host and port.
- **Authentication failed** — verify the local role without displaying the
  password.
- **Queries affect more rows than expected** — stop, confirm the database is
  `advanced_sql_training`, and restore the lesson's bounded/read-only setup.

See [Troubleshooting](../troubleshooting.md) for the general environment and
PostgreSQL checks.
