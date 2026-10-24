# Troubleshooting

> For the supported Docker classroom, begin with `./classroom doctor`,
> `./classroom status` and `./classroom logs` from Linux, macOS or WSL 2. See
> [the one-command guide](one-command-classroom.md). Native host diagnostics
> below are retained compatibility references, outside product support.

Start from the repository root and run:

```text
python scripts/course.py doctor
```

If `python` points elsewhere, use the repository interpreter directly. On
Windows PowerShell, resolve the standard-`venv` or conda-prefix layout once per
window:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
```

On macOS/Linux, run `.venv/bin/python scripts/course.py doctor`.

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

- Windows: do not reinstall merely because an existing Python or Anaconda
  installation is missing from `PATH`. From the repository root, run the
  read-only discovery preview first:

  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  & .\scripts\bootstrap_windows.ps1 -SkipPostgreSql -WhatIf
  ```

  If it finds a supported Python, Anaconda, or Miniconda installation, rerun
  without `-WhatIf` to prepare the repository environment. Only if discovery
  reports that no supported interpreter exists should you install Python 3.12
  manually or explicitly preview the optional winget path with
  `& .\scripts\bootstrap_windows.ps1 -SkipPostgreSql -InstallMissingWithWinget -WhatIf`.
- macOS/Linux: run `python3.12 --version`; do not replace the operating system’s Python.
- In VS Code: select the repository `.venv` from **Python: Select Interpreter**.

## Virtual environment creation fails

Windows:

```powershell
& .\scripts\bootstrap_windows.ps1 -SkipPostgreSql -WhatIf
& .\scripts\bootstrap_windows.ps1 -SkipPostgreSql
```

The preview discovers Python.org and Anaconda/Miniconda installations before
the real run chooses either the standard `venv` layout or the conda-prefix
fallback. It does not delete a partial environment.

Linux may need the venv package:

```bash
sudo apt-get install python3.12-venv
```

Remove a partially created `.venv` only after confirming it is the repository environment and contains no work you need.

## PowerShell refuses to activate the environment

Activation is not required:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
```

For a temporary activated session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

The activation script exists only in the standard `venv` layout. The
conda-prefix fallback continues to use `& $CoursePython ...`. Do not change
machine-wide execution policy for this course.

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

Multiple clones share the per-user `ds60sqlpy` kernel name. Check the complete
`sys.executable` path. A stale registration can point to a moved or deleted
folder. Repair only the registration from the intended environment:

```powershell
# Windows, after resolving $CoursePython above
& $CoursePython -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
```

```bash
# macOS/Linux
.venv/bin/python -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
```

Restart the kernel and verify its path again. Virtual environments should be
recreated after moving them rather than copied between operating systems or
folders. See [Python venv](https://docs.python.org/3.12/library/venv.html).

## `jupyter` is not found

Use the environment’s Python:

Windows:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython -m jupyterlab
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

If locked setup reports a stale lock, use the matching source checkout and
`uv.lock`, or ask a maintainer to update the lock. Do not silently remove
`--locked` during a reproducibility check. On a restrictive network, use your
organization's approved proxy/certificate setup or a prepared
[offline wheelhouse](setup/offline.md#optional-package-only-offline-bundle).
Do not disable TLS verification or include credentials in support commands.
A source build instead of a binary wheel can indicate an unsupported Python,
CPU architecture, or OS for that package.

On macOS, missing `libomp.dylib` during advanced imports calls for the
documented `brew install libomp` runtime. On Debian/Ubuntu, a missing
`libgomp.so.1` calls for `libgomp1`. Those native runtimes are separate from
Python package installation.

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

- Windows: first run
  `& .\scripts\bootstrap_windows.ps1 -WhatIf`; it searches `PATH`, the
  registry, and versioned PostgreSQL installation directories before any
  install advice. Use the discovered executable in the current session, or
  rerun with `-PersistUserPath` only if you want the narrowly scoped user
  `PATH` change.
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

## Native `psql` works, but doctor or a guided notebook cannot connect

Native OS setup uses your local role, while course tools default to the
Compose `ds60` connection. Select the same target as the successful native
command in the terminal that starts the portal. For macOS/Linux's normal
username-and-socket route:

```bash
export DS60_DATABASE_URL=advanced_sql_training
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/learning_portal.py
```

For native Windows, follow the [password-file handoff](setup/windows.md#let-the-guided-notebook-authenticate-without-a-hidden-prompt)
and set its password-free local URL in the launching PowerShell window.
Guided notebooks disable password prompts. An interactive login that asked
for a password does not prove unattended authentication. See
[Local PostgreSQL](setup/postgresql.md).

## Docker SQL works, but the guided notebook says `psql` is missing

`docker compose run --rm sql-runner` has a client inside its container. Python
guided notebooks run host `psql`, so install that client or continue using
container SQL commands. The PostgreSQL server can remain only in Docker. A
Docker daemon, a host client, and a Python driver are separate requirements
for different workflows.

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
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   & .\scripts\bootstrap_windows.ps1 -Profile Advanced
   ```

   macOS/Linux:

   ```bash
   bash scripts/setup.sh --advanced
   ```

5. Distinguish a fake-backed unit-test pass from server authentication,
   permissions, lock behavior, or network evidence.

## `%sql` or `%%sql` is unavailable in a notebook

The SQL magics come from JupySQL and run only in an IPython-based kernel.

1. Select the repository `ds60sqlpy` kernel.
2. Install the `sql-notebooks` profile while connected.
3. Restart the kernel.
4. Run `%load_ext sql` before `%sql`.
5. Confirm no learner file named `sql.py` is shadowing the extension.

If the extension loads but PostgreSQL does not connect, verify
`DS60_DATABASE_URL` in the terminal that launched Jupyter. Do not print the
value when it contains a password. Use `postgresql+psycopg://` through the
lesson's SQLAlchemy engine rather than accidentally requesting the older
`psycopg2` driver. See [PostgreSQL in Jupyter](setup/jupyter-postgresql.md).

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

Then ask the AI tutor using [Learning with an AI tutor](learning-with-an-ai-tutor.md) or open an issue with those details and no secrets.
