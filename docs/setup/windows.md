# Windows setup

This guide assumes a new Windows 10 or Windows 11 machine and PowerShell. The recommended course baseline is Python 3.12, PostgreSQL 16 or newer, and Visual Studio Code.

Run course commands from the repository root, the directory containing `README.md`.

If terminals, packages, or notebooks are new to you, follow
[Your first successful session](first-success.md) alongside this guide. Use
**Windows PowerShell** from the Start menu for PowerShell blocks. Keep native
Windows and WSL environments separate; this guide uses native Windows Python,
not a Python interpreter inside WSL.

## Browser lab: download, extract, and double-click

For a new supported Windows 11 x64 machine, use the course's first-run
Docker wizard. Existing compatible engines are reused without reinstalling:

1. Download the supplied **`DS60LearningLab-0.3.0-Windows-Starter.zip`**, or
   use **Code**, then **Download ZIP** on a
   [repository version](https://github.com/sadatnfs/ds60sqlpy) containing the
   Windows first-run wizard. No Git installation is needed.
2. In File Explorer, use **Extract All** and open the extracted course folder.
   Do not launch from the compressed ZIP preview.
3. Double-click **`START_DOCKER_LAB.cmd`**. No host Python, native PostgreSQL,
   or VS Code installation is needed for the browser route.
4. The wizard reuses a compatible local engine when ready. If prerequisites
   are missing, follow its offered installation choices and consent prompts.
   A fresh Windows setup recommends Rancher Desktop with Moby; Docker Desktop
   with its WSL 2 backend is another choice.
5. Windows may need administrator approval for installation or WSL 2 and may
   require a restart. Save other work, restart yourself when asked, and rerun
   the **same launcher** afterward. It re-detects the current setup rather
   than deleting state or starting the course over.

The wizard uses WSL 2 without requiring a user Ubuntu distribution, so no Linux
account or terminal is necessary for this Windows-folder route. If WinGet is
missing or installation is managed by your organization, follow the official
installer/IT route shown in the setup guidance, then run the launcher again.
See the [complete Windows Docker walkthrough](../docker-beginners.md#windows-start-with-the-first-run-wizard)
for the exact requirements, manual alternative, and first visible results.

Once ready, the launcher opens `http://127.0.0.1:8765/learn`. Saved pads,
history, evidence, and progress live in the host `.learning` folder; the
PostgreSQL database uses a separate persistent volume. The fresh Docker course
login is the limited `admin` account with password `admin`. The browser supplies
that connection internally.

Existing engine settings, saved files, and database volumes are preserved.
Updating the image or rerunning setup does not reset lesson progress. If you
already work in an Ubuntu/WSL terminal, the separate Linux-home workflow in
the Docker guide remains available. The native Windows Python instructions
below are optional and apply when you want host notebooks or editor execution.

## Native notebook route: double-click the guided launcher

After downloading or cloning the repository, open its folder in File Explorer
and double-click:

```text
START_DS60.cmd
```

For a ZIP download, use **Extract All** before launching. Do not run from
inside File Explorer's compressed-folder view. A normal user-owned local
folder is preferable to a protected system directory or a folder whose cloud
sync can replace files while they are running.

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
Set-Location "C:\Users\Ada\Documents\ds60sqlpy"
code .
```

Replace the example username and folder with your actual path. Quote paths
with spaces, for example `Set-Location "C:\Users\Ada\Documents\ds60sqlpy"`.

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

#### Let the guided notebook authenticate without a hidden prompt

The native Windows installer normally requires the `postgres` password.
Terminal `psql` can ask for it visibly, but the guided notebook intentionally
uses `--no-password` so a Jupyter cell can never hang at an invisible prompt.
Configure libpq (PostgreSQL's client connection library) once, outside this
repository:

1. In PowerShell, create PostgreSQL's per-user configuration directory and
   open its password file:

   ```powershell
   $PgConfig = Join-Path $env:APPDATA "postgresql"
   New-Item -ItemType Directory -Force $PgConfig | Out-Null
   notepad (Join-Path $PgConfig "pgpass.conf")
   ```

2. Add exactly one line for this local disposable database, replacing the
   final placeholder with the password chosen during PostgreSQL installation:

   ```text
   localhost:5432:advanced_sql_training:postgres:YOUR_LOCAL_POSTGRES_PASSWORD
   ```

   Save and close Notepad. `pgpass.conf` lives under your Windows profile, not
   in the Git repository. Never copy, commit, paste into Codex, or share it.
   If the password contains `:` or `\`, prefix that character with `\` in this
   file.

3. In the PowerShell window that will start the portal, set a password-free
   target. This tells the runner which local role and host should match the
   password-file entry:

   ```powershell
   $env:DS60_DATABASE_URL = "postgresql://postgres@localhost:5432/advanced_sql_training"
   & $CoursePython scripts\course.py doctor
   ```

   Doctor should report `Course database: advanced_sql_training is reachable`.
   The setting lasts only for that PowerShell process. Start the portal from
   this same window so Jupyter inherits it:

   ```powershell
   & $CoursePython scripts\learning_portal.py
   ```

For the repository's Docker Compose service, do not create this native
`postgres` password-file entry. The browser container uses its own limited
`admin` login. Host notebook users explicitly select that Docker connection as
described in [Local PostgreSQL](postgresql.md#route-a-the-course-container).

### Option B: Canonical container environment

Use the [Docker beginner walkthrough](../docker-beginners.md) for the full
browser application and WSL 2 instructions. That route runs Python and
PostgreSQL inside containers and does not need the native setup above.

For a terminal-only SQL workflow, start the local engine and run from the
repository root in PowerShell:

```powershell
docker compose --project-name ds60-learning up -d postgres
docker compose --project-name ds60-learning run --rm sql-runner -c "SELECT current_database(), 2 + 3 AS first_result;"
```

Expect `advanced_sql_training` and `5`. Follow
[Local PostgreSQL](postgresql.md#route-a-the-course-container) for optional seed
setup, verification, the exact host connection URL, ports, and preserving data.

If you later want **host** VS Code/Jupyter notebooks, install the native Python
environment separately. `bootstrap_windows.ps1 -SkipPostgreSql` prepares Python
without requiring a host database. Guided SQL notebooks still need host
PostgreSQL **client** tools because they launch host `psql`; the browser
container and `sql-runner` supply their own clients.

## 6. Verify a lesson

Start the private course dashboard. It saves completion in ignored
`.learning\progress.json` and can open allowlisted VS Code/Jupyter targets:

```powershell
& $CoursePython scripts\learning_portal.py
```

If you chose native PostgreSQL, run this in the same PowerShell window where
you set the password-free `DS60_DATABASE_URL` in section 5. If you chose
Docker Compose, make sure the `postgres` service is running.

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

Finish the [scratch-notebook walkthrough](first-success.md#3-make-a-scratch-notebook-and-run-one-cell)
to verify the `.venv` kernel, run `2 + 3`, and practice restarting before
working through Python Day 1.

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

PowerShell uses the backtick for line continuation, rather than a trailing backslash.

## 8. Continue offline

Run each lesson that has a disclosed first-use download while connected, then follow [Offline use](offline.md). Seaborn data is cached after the first successful load. Pretrained model lessons require separate caches or an offline fallback.

For common failures, see [Troubleshooting](../troubleshooting.md).
