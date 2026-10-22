# Local PostgreSQL, step by step

PostgreSQL runs as a server. `psql`, the course SQL runner, and a notebook are
clients connecting to that server. Installing a Python driver does not install
the server, and installing a server does not guarantee that `psql` is on PATH.

Use PostgreSQL 16 or newer; the canonical course container and SQL CI use
PostgreSQL 17. These commands operate only on the disposable
`advanced_sql_training` database. The setup file drops and recreates its
`training` schema. Preserve any personal tables or work before rerunning it.

## Choose one route

| Route | Good fit | What you need |
| --- | --- | --- |
| Native server | You want the normal local database workflow | Your [OS setup guide](first-success.md#1-choose-the-matching-operating-system-guide), PostgreSQL server, `psql`, and local authentication |
| Course container | You already use Docker or want consistent server defaults | Docker Desktop on Windows/macOS, or Docker Engine plus Compose on Linux; host `psql` only for Python-launched SQL |

Choose one for your first session. If both servers run, they need different
ports. A container-only SQL workflow does not require a host PostgreSQL server
or host `psql`; the `sql-runner` container supplies its own client.

## Route A: the course container

Start Docker first. Confirm both tools respond:

```text
docker --version
docker compose version
```

From the repository root, use the same commands in PowerShell and Bash:

```text
docker compose up -d postgres
docker compose ps
docker compose run --rm sql-runner -c "SELECT current_database(), 2 + 3 AS first_result;"
```

Expect `advanced_sql_training` and `5`. The `sql-runner` waits for the server's
health check. A running container alone is not proof the database is ready;
this distinction follows [Compose's startup-order documentation](https://docs.docker.com/compose/how-tos/startup-order/).
If a command fails, inspect `docker compose logs postgres` before rerunning it.

Initialize the disposable seed and run the invariant checks:

```text
docker compose run --rm sql-runner -f sql/postgres-60day/00_setup.sql
docker compose run --rm sql-runner -f sql/postgres-60day/00_verify.sql
docker compose run --rm sql-runner -f sql/postgres-60day/day01_select_where_orderby.sql
```

Each command must exit successfully. The verifier checks more than whether a
table exists. You should see Day 1's result tables after it succeeds.
`sql-runner` already supplies `-X -v ON_ERROR_STOP=1` and the fixed course target.

To use **guided SQL notebooks**, also install the PostgreSQL client tools on
the host and confirm `psql --version`. The notebook launches host `psql`; it
does not automatically execute a container. The standalone Docker commands
above remain available if you do not install that host client.

The runner defaults to the course container's disposable local `ds60`
connection. When switching from a native server, explicitly choose that URL
in the terminal that starts the portal:

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = "postgresql://ds60:ds60@localhost:5432/advanced_sql_training"
```

```bash
# macOS/Linux
export DS60_DATABASE_URL="postgresql://ds60:ds60@localhost:5432/advanced_sql_training"
```

For a port conflict, choose a new host port before starting the container:

```powershell
# Windows PowerShell
$env:DS60_POSTGRES_PORT = "55432"
docker compose up -d postgres
$env:DS60_DATABASE_URL = "postgresql://ds60:ds60@localhost:55432/advanced_sql_training"
```

```bash
# macOS/Linux
export DS60_POSTGRES_PORT=55432
docker compose up -d postgres
export DS60_DATABASE_URL="postgresql://ds60:ds60@localhost:55432/advanced_sql_training"
```

Container-to-container `sql-runner` commands still use port 5432 internally.
For normal shutdown run `docker compose down`. It preserves the database
volume. Volume deletion is a separate destructive operation and is not needed
to stop or resume study.

On Windows with no native `psql`, use
`& .\scripts\bootstrap_windows.ps1 -SkipPostgreSql` to prepare Python, then the
Docker commands above for SQL. The regular Windows launcher expects a host
client unless `-SkipPostgreSql` is explicitly supplied.

## Route B: the native server

Complete your [Windows](windows.md#5-set-up-postgresql),
[macOS](macos.md#4-set-up-postgresql), or [Linux](linux.md#4-set-up-postgresql)
instructions first. They explain installing, starting, creating the local
role, and creating `advanced_sql_training`.

### macOS and Linux with the normal username/socket connection

The OS guides use the local operating-system username and a Unix socket, a
local connection that does not use the TCP network. Check that exact route:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -c "SELECT current_database(), current_user, 2 + 3 AS first_result;"
```

Expect the course database, your local username, and `5`. Initialize and
verify if this is a fresh disposable database:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_verify.sql
```

The course tools otherwise default to the container connection. Give them the
same native target and start the portal in this terminal:

```bash
export DS60_DATABASE_URL=advanced_sql_training
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/learning_portal.py
```

The literal database name is supported by doctor and the guided `psql`
notebooks; it deliberately uses local defaults without inheriting routing
overrides such as `PGHOST` or `PGSERVICE`. It is not a SQLAlchemy URL. For the
separate [JupySQL lesson](jupyter-postgresql.md), use
`postgresql:///advanced_sql_training` for a matching local default socket, or
an explicit local TCP URL and the authentication described below.

### Windows, or a native server requiring a password

Use the local role from the installer, commonly `postgres` on Windows. Verify
the target interactively:

```text
psql -X -v ON_ERROR_STOP=1 -h localhost -U postgres -d advanced_sql_training -c "SELECT current_database(), 2 + 3 AS first_result;"
```

Follow the [Windows password-file instructions](windows.md#let-the-guided-notebook-authenticate-without-a-hidden-prompt)
before launching a notebook. Guided execution intentionally disables password
prompts; an interactive terminal login alone does not prove it will work.

On macOS/Linux a local password file is `~/.pgpass` with permissions `0600`.
On Windows it is `%APPDATA%\postgresql\pgpass.conf`. The entry must match host,
port, database, and role. Escape `:` and `\` in passwords with a preceding
backslash. Keep the file private and outside this repository. See the
[PostgreSQL password-file reference](https://www.postgresql.org/docs/17/libpq-pgpass.html).

Set a password-free URL in the launching terminal, using your actual role:

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = "postgresql://postgres@localhost:5432/advanced_sql_training"
```

```bash
# macOS/Linux, only when using the postgres role over local TCP
export DS60_DATABASE_URL="postgresql://postgres@localhost:5432/advanced_sql_training"
```

On Linux, a socket login using peer authentication and a TCP login using a
password are different authentication routes. Avoid changing server-wide
authentication to `trust` as a troubleshooting shortcut. If a Python driver
uses a different default socket location from distro `psql`, the explicit
local TCP route and a matching password file avoid that ambiguity.

## Confirm the whole path

1. Run doctor using the repository interpreter in the terminal with your
   chosen connection. Expect the course database to be reachable.
2. Start the learning portal in that same terminal.
3. Open `sql-01` and choose **Create/open guided SQL notebook**.
4. Run the notebook's read-only readiness step, read the reset notice before
   initializing the disposable seed, and run Day 1.
5. Check the output against the lesson guide. Keep personal SQL in the ignored
   working copy under `.learning/sql/sql-01/`.

The `DS60_DATABASE_URL` setting lasts for the terminal and its child processes.
Repeat it in a new terminal. A `.env` file is not automatically loaded.
Doctor proves bounded connectivity. Seed verification proves the fixture
invariants. Successful Day 1 execution proves that lesson path. None of those
checks proves that every later lesson or native OS configuration has run.
