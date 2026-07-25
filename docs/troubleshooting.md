# Troubleshooting

Start from the repository root and run:

```text
python scripts/course.py doctor
```

On Windows, use `.\.venv\Scripts\python.exe`; on macOS/Linux, use `.venv/bin/python` if `python` points elsewhere.

For the difference between `.venv`, disposable caches, offline model data,
learner progress, and Docker state, see
[Local environments and caches](local-files-and-caches.md).

## “File not found” for requirements, scripts, notebooks, or SQL

You are probably in the wrong directory.

Windows PowerShell:

```powershell
Test-Path .\README.md
Get-Location
```

macOS/Linux:

```bash
test -f README.md
pwd
```

Change to the directory containing the root README and retry.

## `python` or `py` is not found

- Windows: reinstall Python 3.12 with the Python launcher, then open a new terminal and run `py -3.12 --version`.
- macOS/Linux: run `python3.12 --version`; do not replace the operating system’s Python.
- In VS Code: select the repository `.venv` from **Python: Select Interpreter**.

## Virtual environment creation fails

Windows:

```powershell
py -3.12 -m venv .venv
```

Linux may need the venv package:

```bash
sudo apt-get install python3.12-venv
```

Remove a partially created `.venv` only after confirming it is the repository environment and contains no work you need.

## PowerShell refuses to activate the environment

Activation is not required:

```powershell
.\.venv\Scripts\python.exe scripts\course.py doctor
```

For a temporary activated session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Do not change machine-wide execution policy for this course.

## A package installs but the notebook cannot import it

The terminal interpreter and notebook kernel differ.

1. Run:

   ```text
   python -c "import sys; print(sys.executable)"
   ```

2. In the notebook, run:

   ```python
   import sys
   print(sys.executable)
   ```

3. Select the repository `.venv` kernel and restart it.

## `jupyter` is not found

Use the environment’s Python:

Windows:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyterlab
```

If the module is missing, rerun the setup script and doctor.

## Package installation fails

- Confirm Python 3.12 is active.
- Upgrade installer tooling through the setup script.
- Read the first package error, not only the final summary.
- Optional heavy packages may need more disk, memory, or a platform-specific wheel.
- CPU is the supported default; do not install a CUDA build unless a lesson explicitly asks for it.
- Do not work around a failed install by putting packages into the system Python.

## A Seaborn dataset fails offline

Seaborn sample data downloads on first use.

1. Reconnect temporarily.
2. Run the affected `sns.load_dataset(...)` once.
3. Confirm the local cache exists.
4. Retry offline.

See [Offline use](setup/offline.md).

## Hugging Face, spaCy, or torchvision tries to download

The model or weights are not yet cached.

- Run the disclosed preparation step while connected.
- Or use the lesson’s local/no-pretrained fallback.
- Do not claim the lesson is offline-ready merely because the Python package is installed.

## `psql` is not found

- Windows: add the PostgreSQL `bin` directory to `PATH`, or use SQL Shell.
- macOS Homebrew: add `$(brew --prefix postgresql@17)/bin` to `PATH`.
- Linux: install the PostgreSQL client package.

Then verify:

```text
psql --version
```

The supported major version is 16 or newer.

## PostgreSQL connection is refused

Confirm the server is running:

- Windows: check the PostgreSQL service in **Services**
- macOS Homebrew: `brew services list`
- Linux: `systemctl status postgresql`
- Container: `docker compose ps` and `docker compose logs postgres`

Also check host, port, database, and role. The default port is 5432.

## Docker is installed but Compose cannot start PostgreSQL

1. Start Docker Desktop or your container daemon.
2. Check the exact state:

   ```text
   docker compose ps
   docker compose logs postgres
   ```

3. If host port 5432 is already in use, choose another host port before starting the service.

   Windows PowerShell:

   ```powershell
   $env:DS60_POSTGRES_PORT = "55432"
   docker compose up -d postgres
   ```

   macOS/Linux:

   ```bash
   export DS60_POSTGRES_PORT=55432
   docker compose up -d postgres
   ```

The `sql-runner` service connects over the internal Compose network, so its course commands remain unchanged.

## `role "postgres" does not exist` on macOS

Homebrew commonly creates a role matching the macOS username. Omit `-U postgres` and use:

```bash
psql -d advanced_sql_training
```

Do not create an unnecessary superuser merely to match an old command.

## Peer authentication fails on Linux

Create a PostgreSQL role matching the Linux username:

```bash
sudo -u postgres createuser --createdb "$USER"
createdb advanced_sql_training
```

Then use normal local `psql` commands without `-U postgres`.

## The training database already exists

That is normally fine. Run the setup file to reset only the disposable `training` schema:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
```

This deletes and recreates the training schema. Stop if the target database is not disposable.

Run `sql/postgres-60day/00_verify.sql` immediately afterward to catch an incomplete or incorrect seed.

## A later SQL project says a table or schema does not exist

Most lessons are independent and rollback-safe. Days 52–54 are the declared stateful exception: Day 52 resets and commits the course-owned `dwh` schema, then Days 53 and 54 use it in order. Do not simply remove `ROLLBACK` from other lessons.

1. Inspect the lesson’s generated catalog entry and companion guide.
2. For the warehouse project, run Days 52, 53, and 54 in order.
3. Use `ON_ERROR_STOP=1`.
4. Report a curriculum defect if the earlier lesson rolls back an object the later lesson requires.

## A bridge lesson cannot connect to PostgreSQL

The bridge defaults to fakes; use a live database only when the lesson marks
the step as optional.

1. Run the bridge tests first:

   ```text
   python -m pytest bridge/tests
   ```

2. Confirm `DS60_DATABASE_URL` points to the disposable course database, not a
   workplace, shared, or production database.
3. Run the SQL setup and verification before a live exercise.
4. Check whether the lesson needs Psycopg:

   Windows PowerShell:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
   ```

   macOS/Linux:

   ```bash
   bash scripts/setup.sh --advanced
   ```

5. Distinguish a fake-backed unit-test pass from server authentication,
   permissions, lock behavior, or network evidence.

## A SQL file shows errors but the command exits successfully

Use:

```text
psql -X -v ON_ERROR_STOP=1 ...
```

Without `ON_ERROR_STOP`, `psql` can continue after a statement fails.

## Bash commands fail in PowerShell

PowerShell does not use:

- `source`
- Bash `\` line continuations
- `cat file | ...`
- Bash `|| echo` on Windows PowerShell 5.1

Use the Windows guide and PowerShell examples instead of translating punctuation literally.

## Find the executable solution for a lesson

Inspect:

```text
python scripts/course.py catalog
```

PostgreSQL executable and Markdown solutions cover Days 1–60. Use the
generated availability view for the exact path. The Day 52–54 executable
warehouse solutions are stateful and must run in order.

## Still blocked

Capture:

- Operating system and version
- The exact command
- Full first error
- `python scripts/course.py doctor` output
- `python --version` and `psql --version` when relevant
- The selected VS Code interpreter/kernel

Then ask Codex using [Learning with Codex](learning-with-codex.md) or open an issue with those details and no secrets.
