# Windows setup

This guide assumes a new Windows 10 or Windows 11 machine and PowerShell. The recommended course baseline is Python 3.12, PostgreSQL 16 or newer, and Visual Studio Code.

Run course commands from the repository root—the directory containing `README.md`.

## 1. Install the base tools

Install:

1. [Git for Windows](https://git-scm.com/download/win)
2. [Python 3.12](https://www.python.org/downloads/windows/)
3. [Visual Studio Code](https://code.visualstudio.com/download)
4. [PostgreSQL 16+](https://www.postgresql.org/download/windows/) or
   [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
   for the SQL track

During Python installation, install the Python launcher (`py`). Adding Python to `PATH` is useful, but the launcher is the important part for these instructions.

If you choose Docker Desktop, use its WSL 2 backend when your machine supports
it and complete Docker's documented virtualization/WSL prerequisites before
running the Compose commands below.

Open a new PowerShell window and verify:

```powershell
git --version
py -3.12 --version
code --version
```

If `code` is not found, open VS Code from the Start menu and use **File → Open Folder** instead.

## 2. Clone and open the repository

Choose a normal user-owned folder. Paths containing spaces are supported.

```powershell
git clone <repository-url> ds60sqlpy
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

Run the repository setup script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

The process-scoped execution-policy flag applies only to this command. It does not change the machine-wide policy.

Verify with the virtual environment’s interpreter:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe scripts\course.py doctor
.\.venv\Scripts\python.exe scripts\course.py catalog
```

Activation is optional. Using the interpreter’s full relative path avoids PowerShell activation-policy issues and guarantees that packages install into the intended environment.

Core setup installs notebook, data, and quality tooling. Before the engineering
bridge, PostgreSQL-in-Jupyter lesson, professional modules, or later
machine-learning, production, deep-learning, natural-language-processing, or
geospatial lessons, install the advanced profile while connected:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

This can take substantially longer and some packages use platform-specific
wheels. You can defer it until the catalog shows that a lesson needs an
optional dependency. Use the
[catalog-label mapping](../dependency-profiles.md): labels such as `core`,
`postgres`, and `advanced` are not literal package extras.

If you prefer activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python scripts\course.py doctor
```

## 4. Configure VS Code

1. Open the repository root.
2. Accept the recommended extensions, or install them from [the VS Code guide](../vscode.md).
3. Open the Command Palette with `Ctrl+Shift+P`.
4. Run **Python: Select Interpreter**.
5. Select `.venv\Scripts\python.exe`.
6. Open a notebook and select the same `.venv` interpreter as its kernel.

The checked-in tasks under **Terminal → Run Task** can run setup, doctor, catalog, validation, and JupyterLab.

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

Python:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab .\python\ds-60day\notebooks
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
