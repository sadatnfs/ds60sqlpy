# Optional PostgreSQL notebooks

Use the Docker classroom for ordinary Python and SQL study. It includes the
runtime, database, editor and saved results. This page covers a separately
prepared notebook workflow for contributors and learners who specifically want
to study IPython SQL magics. Windows uses Ubuntu in WSL 2.

## Choose the appropriate notebook

- **Ordinary SQL lessons:** run them in the classroom's **Whole SQL lesson
  (psql)** mode. Many files contain `psql` commands that are not SQL magics.
  An optional [guided SQL notebook](../guided-sql-notebooks.md) can also be
  generated with `uv run --no-sync python scripts/course.py sql notebook sql-01`.
  Its runner needs a prepared local `psql` client and the disposable database.
- **Interactive SQL magics:** use
  [bridge-jupyter-01](../../bridge/professional/companion-guides/bridge_jupyter_01_postgresql_magics.md).
  JupySQL runs `%sql` and `%%sql` through the selected Python kernel and
  SQLAlchemy/Psycopg. This is the workflow described below.

Neither route starts an editor through the classroom server. A notebook and a
browser pad have separate files and history; copying source does not merge them.

## 1. Prepare the environment while connected

Follow [contributor setup](../../CONTRIBUTING.md), then run from the repository
root in Bash on Linux, macOS or Windows WSL 2:

```bash
uv sync --frozen --python 3.12 --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks
uv run --no-sync python -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
```

This uses the repository lock and installs the notebook packages in its virtual
environment. Registering the kernel makes that interpreter selectable in
Jupyter or VS Code. Do not add `%pip` install cells: they obscure interpreter
selection and prevent predictable offline execution. Installing packages here
does not change Docker workers.

## 2. Prepare the local disposable database

```bash
./classroom --starter
./classroom status
```

Use the actual PostgreSQL host port shown in status, not a remembered default.
The database is `advanced_sql_training`; fresh local classroom credentials are
`admin` / `admin`. Read [PostgreSQL setup](postgresql.md) before choosing the
explicit training reset. That reset replaces course-owned data and is not an
ordinary startup step. Preserve warehouse and other stateful exercises when
following their own instructions.

The notebook's `validate_course_database_target` guard rejects remote and
multi-host targets and inappropriate database names and URL options. Do not
remove it to connect to a shared database. Database identity checks do not make
arbitrary SQL safe; read the statement and its transaction boundary as well.

## 3. Keep the connection URL password-free

In the same Bash shell that will launch Jupyter, set the local database URL
below. Replace `PORT` with the actual forwarded PostgreSQL port reported by
`./classroom status`. Keep the explicit local host, `admin` learning role and
`advanced_sql_training` database. The URL contains no password.

```bash
export DS60_DATABASE_URL="postgresql://admin@127.0.0.1:PORT/advanced_sql_training"
```

Supply authentication through a private **libpq password file**, outside the
repository. In WSL, keep it in your Ubuntu home so Linux file permissions apply.
These commands create the private path without truncating an existing file:

```bash
mkdir -p "$HOME/.config/ds60"
chmod 700 "$HOME/.config/ds60"
export PGPASSFILE="$HOME/.config/ds60/postgresql.pass"
(
  umask 077
  touch "$PGPASSFILE"
)
chmod 600 "$PGPASSFILE"
```

Open that file in your text editor and add this one-line format, replacing
`PORT` with the same actual port and `YOUR_PASSWORD` with the password for your
local learning role. Do not paste the real line into the notebook or terminal
command history. Retain any unrelated existing entries rather than replacing
the whole file.

```text
127.0.0.1:PORT:advanced_sql_training:admin:YOUR_PASSWORD
```

The file matches host, port, database and role exactly. Escape a colon or
backslash inside a field with a backslash. Do not broaden the entry with
wildcards just to hide a mismatch. The file must have mode `600`; libpq ignores
password files readable by a group or other users. See the
[PostgreSQL password-file documentation](https://www.postgresql.org/docs/17/libpq-pgpass.html).

Clear inherited password or routing overrides, then launch the prepared kernel
from this shell. The password remains in the private file, not the URL or a
process argument:

```bash
unset PGPASSWORD PGHOST PGHOSTADDR PGPORT PGSERVICE PGSERVICEFILE PGOPTIONS
uv run --no-sync python -m jupyter lab bridge/professional/notebooks
```

For VS Code, run `code .` from the same shell instead of JupyterLab, select
**Python (ds60sqlpy)** and open the learner notebook. Restart a kernel if its
process environment or interpreter changed. If the classroom's database port
changes, update both the URL and the matching password-file entry before
starting a new kernel.

The notebook validates the local course target before creating its explicit
SQLAlchemy `postgresql+psycopg` engine. Psycopg uses libpq authentication when
the URL omits its password. The separate full-script notebook runner also
preserves `PGPASSFILE` while replacing inherited routing variables with the
validated local target. Do not add `passfile` or service-routing query parameters
to the URL: the course validator permits only its reviewed `sslmode` option.
Neither workflow displays or stores the password in notebook cells.

Keep the password file private and outside Git, exports and screenshots. The
notebook does not silently load a `.env` file. Closing the terminal clears its
process settings; the private password file remains for later local sessions.
See [SQLAlchemy URL handling](https://docs.sqlalchemy.org/en/20/core/engines.html)
for the distinction between a URL and a separately supplied authentication source.

## 4. Work through the lesson in order

The dedicated notebook introduces `%load_ext sql`, line and cell magics,
connection aliases, display limits and conversion to pandas. It suppresses
connection display. Bind data values using the lesson's named-parameter route;
Jinja template substitution generates SQL text and is not safe value binding.
Use fixed or allowlisted identifiers when the query structure varies.

Treat notebook ordering and transactions as part of the program. An earlier
cell may have changed variables or database state, and separate cells do not
implicitly form one atomic transaction. Prefer bounded read queries while
learning. Application code should use explicit Psycopg or SQLAlchemy transaction
ownership rather than relying on an interactive notebook's ambient settings.

## 5. Validate honestly and prepare offline study

```bash
uv run --no-sync python scripts/validate_notebooks.py
```

Structural notebook validation does not prove a live PostgreSQL connection.
Record successful live cells separately. Once the environment and required
images are prepared, this local exercise does not need internet, but its local
database must still run. Save learner copies outside tracked references and clear
outputs before committing.

If the `sql` extension is missing, check the selected kernel and the installed
`sql-notebooks` extra. If a magic is missing, run the notebook's extension-loading
cell. A request for `psycopg2` usually means a URL or engine selected a different
driver. Connection refusal means checking the running project's host port;
authentication errors require checking the local role privately. See
[troubleshooting](../troubleshooting.md) for the general classroom checks.
