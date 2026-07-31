# Windows setup

This guide assumes a new Windows 10 or Windows 11 machine and PowerShell. The recommended course baseline is Python 3.12, PostgreSQL 16 or newer, and Visual Studio Code.

Run course commands from the repository root—the directory containing `README.md`.

## Fastest route: double-click the guided launcher

After downloading or cloning the repository, open its folder in File Explorer
and double-click:

```text
START_DS60.cmd
```

The launcher finds the repository from its own location, so the folder may
contain spaces and you do not need to type a path. It:

1. Reuses either `.venv\Scripts\python.exe` or the Anaconda conda-prefix
   `.venv\python.exe` layout.
2. If the environment is missing or incomplete, clearly announces the
   **connected first setup**, asks you to type `SETUP`, and delegates to the
   safe discovery bootstrap.
3. Finds VS Code even when its launcher is not on `PATH`, and verifies Python
   3.11-3.12, Jupyter/IPython/JupySQL/Psycopg/SQLAlchemy, and the
   `Python (ds60sqlpy)` kernel.
4. Runs `course.py doctor`.
5. Opens the private learning portal and keeps its terminal window visible.

Keep the launcher window open while studying; press `Ctrl+C` there to stop the
portal. The launcher does not ask for, store, or print a database password and
does not create, drop, or reset data. Course doctor may make its documented
no-prompt, read-only reachability check against only the disposable course
database; configuration and initialization remain separate guided steps in
section 5.

For read-only troubleshooting without installing anything or opening a
browser:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_ds60.ps1 `
    -DiagnosticsOnly -NonInteractive
```

Preview a needed setup without changing the machine:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_ds60.ps1 -WhatIf
```

The rest of this document explains every step that the launcher coordinates
and provides manual alternatives.

## 1. Install the base tools

Install:

1. [Git for Windows](https://git-scm.com/download/win)
2. [Python 3.12](https://www.python.org/downloads/windows/) or a current
   Anaconda/Miniconda distribution. If its base Python is outside 3.11-3.12,
   bootstrap creates a supported repository-local conda prefix.
3. [Visual Studio Code](https://code.visualstudio.com/download)
4. [PostgreSQL 16+](https://www.postgresql.org/download/windows/) or
   [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
   for the SQL track

If Anaconda3 and PostgreSQL are already installed, do not reinstall them just
because `python`, `conda`, or `psql` is missing from `PATH`. The course
bootstrap searches the registry and common installation directories first.
During a new Python.org installation, installing the Python launcher (`py`) is
still useful.

If you choose Docker Desktop, use its WSL 2 backend when your machine supports
it and complete Docker's documented virtualization/WSL prerequisites before
running the Compose commands below.

Open a new PowerShell window and verify:

```powershell
git --version
code --version
```

`py -3.12 --version`, `python --version`, and `psql --version` may fail at this
point; that is exactly what the discovery bootstrap handles. If `code` is not
found, open VS Code from the Start menu and use **File → Open Folder** instead.

## 2. Clone and open the repository

Choose a normal user-owned folder. Paths containing spaces are supported.

```powershell
git clone https://github.com/sadatnfs/ds60sqlpy.git ds60sqlpy
Set-Location .\ds60sqlpy
code .
```

If the repository is already cloned:

```powershell
Set-Location <path-to-ds60sqlpy>
code .
```

Confirm that PowerShell is at the root:

```powershell
Test-Path .\README.md
```

The result should be `True`.

## 3. Create the Python environment

Run the discovery bootstrap. This is the recommended path for a new Windows
machine and for existing Anaconda/PostgreSQL installations that are not on
`PATH`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1
```

Using `&` keeps the script's process-local `PATH` discoveries available in this
PowerShell window. The execution-policy change also applies only to the current
window. The script creates `.venv`, installs IPython, JupyterLab, Notebook,
ipykernel, JupySQL, SQLAlchemy, and Psycopg 3, registers
`Python (ds60sqlpy)`, and runs verification. It never connects to PostgreSQL or
asks for its password.

Verify with the virtual environment’s interpreter:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}

& $CoursePython --version
& $CoursePython scripts\course.py doctor
& $CoursePython scripts\course.py catalog
```

Activation is optional. A normal `venv` uses
`.venv\Scripts\python.exe`; the Anaconda fallback creates a conda prefix and
uses `.venv\python.exe`. Resolve `$CoursePython` once in each new PowerShell
window. Invoking it directly avoids activation-policy issues and guarantees
that commands use the intended environment.

Core setup installs notebook, data, quality, engineering-bridge, professional,
and PostgreSQL-in-Jupyter tooling. Before lessons labeled for the larger
machine-learning, production, deep-learning, natural-language-processing, or
geospatial profiles, install the advanced profile while connected:

```powershell
& .\scripts\bootstrap_windows.ps1 -Profile Advanced
```

This can take substantially longer and some packages use platform-specific
wheels. You can defer it until the catalog shows that a lesson needs an
optional dependency. Use the
[catalog-label mapping](../dependency-profiles.md): labels such as `core`,
`postgres`, and `advanced` are not literal package extras.

See the [one-command bootstrap reference](windows-bootstrap.md) for
`-WhatIf`, locked dependency installation, optional user-level `PATH`
persistence, and the explicit `-InstallMissingWithWinget` opt-in. Use the
smaller historical `scripts\setup.ps1` only when a supported Python is already
discoverable and you do not need PostgreSQL or Jupyter discovery. That legacy
script always creates a standard `venv` at
`.venv\Scripts\python.exe`; do not run it over a conda-prefix `.venv`.

If you used the legacy setup or the bootstrap created a standard `venv`, you
may activate it:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python scripts\course.py doctor
```

The conda-prefix fallback does not contain that activation script. Keep using
`& $CoursePython ...`; activation is not required.

## 4. Configure VS Code

1. Open the repository root.
2. Accept the recommended extensions, or install them from [the VS Code guide](../vscode.md).
3. Open the Command Palette with `Ctrl+Shift+P`.
4. Run **Python: Select Interpreter**.
5. Select the interpreter path printed by bootstrap:
   `.venv\Scripts\python.exe` for a standard `venv`, or
   `.venv\python.exe` for the conda-prefix fallback.
6. Open a notebook and select the same `.venv` interpreter as its kernel.

The checked-in tasks under **Terminal → Run Task** can run setup, the private
learning portal, doctor, catalog, validation, and JupyterLab. Choose
**Course: Guided start (Windows)** for the same readiness-and-launch sequence
as `START_DS60.cmd`.

## 5. Set up PostgreSQL

### Option A: Native PostgreSQL

Install PostgreSQL 16 or newer from the [official Windows installer page](https://www.postgresql.org/download/windows/). Remember the password chosen for the `postgres` role.

The installer normally provides **SQL Shell (psql)** and pgAdmin. To use `psql` from PowerShell, add the PostgreSQL `bin` directory to `PATH` during installation or for the current session. Adjust the version in this example:

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"
psql --version
```

Create the disposable training database:

```powershell
psql -X -v ON_ERROR_STOP=1 -h localhost -U postgres -d postgres
```

At the `postgres=#` prompt:

```sql
CREATE DATABASE advanced_sql_training;
\q
```

If PostgreSQL reports that the database already exists, leave it in place and continue.

Load the course schema from the repository root:

```powershell
psql -X -v ON_ERROR_STOP=1 -h localhost -U postgres -d advanced_sql_training -f .\sql\postgres-60day\00_setup.sql
psql -X -v ON_ERROR_STOP=1 -h localhost -U postgres -d advanced_sql_training -f .\sql\postgres-60day\00_verify.sql
```

The setup file drops and recreates the disposable `training` schema. Do not point it at a database containing valuable data. The verification file raises an error if expected counts, coverage, chronology, totals, or foreign keys are wrong.

### Option B: Canonical container environment

Docker-based automation uses PostgreSQL 17 and gives every operating system the same database behavior. Docker Desktop requires virtualization support and a one-time image download.

From PowerShell at the repository root:

```powershell
docker compose up -d postgres
docker compose run --rm sql-runner -f sql/postgres-60day/00_setup.sql
docker compose run --rm sql-runner -f sql/postgres-60day/00_verify.sql
docker compose run --rm sql-runner -f sql/postgres-60day/day01_select_where_orderby.sql
docker compose down
```

The setup command drops and recreates the course-owned `training` schema in the disposable Compose database. `docker compose down` stops the services but preserves the database volume; deleting the volume is a separate destructive reset and is not needed for normal study.

Use this option when:

- You already use Docker Desktop
- Native PostgreSQL authentication is getting in the way
- You are validating repository-wide SQL behavior

See [Validation](../validation.md) for repository-wide checks and the distinction between structural and executed validation.

## 6. Verify a lesson

Start the private course dashboard. It saves completion in ignored
`.learning\progress.json` and can open allowlisted VS Code/Jupyter targets:

```powershell
& $CoursePython scripts\learning_portal.py
```

Python:

```powershell
& $CoursePython -m jupyter lab .\python\ds-60day\notebooks
```

SQL:

```powershell
psql -X -v ON_ERROR_STOP=1 -h localhost -U postgres -d advanced_sql_training -f .\sql\postgres-60day\day01_select_where_orderby.sql
```

The SQL lesson ends with `ROLLBACK`, so normal lesson examples should not persist changes.

To run PostgreSQL from the course's Python notebook kernel with `%sql` and
`%%sql`, follow [PostgreSQL in Jupyter](jupyter-postgresql.md). Its connection
is limited to the same disposable training database.

## 7. PowerShell equivalents used in later lessons

Use `Invoke-RestMethod` instead of Bash-style multiline `curl`:

```powershell
$body = @{ features = @(5.1, 3.5, 1.4, 0.2) } | ConvertTo-Json
Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/predict" `
    -ContentType "application/json" `
    -Body $body
```

PowerShell uses the backtick for line continuation—not a trailing backslash.

## 8. Continue offline

Run each lesson that has a disclosed first-use download while connected, then follow [Offline use](offline.md). Seaborn data is cached after the first successful load. Pretrained model lessons require separate caches or an offline fallback.

For common failures, see [Troubleshooting](../troubleshooting.md).
