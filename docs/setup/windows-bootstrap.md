# One-command Windows bootstrap

Use this guide when Python or PostgreSQL is installed on Windows but `python`,
`conda`, or `psql` is not available on `PATH`. It is particularly useful for a
machine with Anaconda3 and the native PostgreSQL installer.

The bootstrapper:

1. Finds Python 3.11 or 3.12 through the Python launcher, `PATH`, conda,
   Windows registry entries, and common Anaconda, Miniconda, and Python.org
   locations.
2. Finds PostgreSQL 16 or newer through `PATH`, Windows registry entries, and
   versioned `Program Files\PostgreSQL` directories.
3. Adds the selected tool directories to the current PowerShell process only.
4. Creates or reuses this repository's `.venv`.
5. Installs the selected course dependency profile, including IPython,
   JupyterLab, Notebook, ipykernel, JupySQL, SQLAlchemy, and Psycopg 3.
6. Registers `Python (ds60sqlpy)` as a per-user Jupyter kernel.
7. Verifies the package imports, Jupyter installation, kernel interpreter,
   `psql` version, and course environment doctor.

It does **not** request or display a PostgreSQL password, set
`DS60_DATABASE_URL`, connect to PostgreSQL, create a database, or run a course
schema reset.

## Run the default bootstrap

Open Windows PowerShell in the repository root, where `README.md` and
`pyproject.toml` are visible:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1
```

Running the script with `&` keeps its process-scoped `PATH` additions in this
PowerShell window. Closing the window removes them. The `.venv`, installed
packages, and registered Jupyter kernel remain available.

The default `Core` profile installs:

- Notebook tooling: IPython, JupyterLab, classic Notebook, ipykernel, and
  notebook validators
- Python data and quality dependencies
- Bridge and professional-track dependencies
- PostgreSQL notebook tooling: JupySQL, SQLAlchemy, and Psycopg 3

It does not install the largest deep-learning, NLP, geospatial, production, or
specialized ML profiles.

Activation is optional. Always-safe commands use the environment interpreter
directly:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import IPython, ipykernel, jupyterlab, notebook, psycopg, sql, sqlalchemy; print('Notebook stack imports passed.')"
.\.venv\Scripts\python.exe -m jupyter --version
.\.venv\Scripts\python.exe -m notebook --version
.\.venv\Scripts\python.exe -m jupyter kernelspec list
.\.venv\Scripts\python.exe scripts\course.py doctor
psql --version
.\.venv\Scripts\python.exe -m jupyter lab
```

In VS Code, select `.venv\Scripts\python.exe` as the Python interpreter and
`Python (ds60sqlpy)` as the notebook kernel.

The `psql` command above works in the same PowerShell process used to invoke
the script. In a new terminal it requires `-PersistUserPath` or the full
`psql.exe` path printed by the bootstrapper.

## Install every optional course profile

The advanced profile can be large and may take a long time because it includes
deep-learning, NLP, geospatial, production, and specialized ML packages:

```powershell
& .\scripts\bootstrap_windows.ps1 -Profile Advanced
```

Run it while connected to the internet. The script is idempotent: it reuses a
valid `.venv`, updates declared packages, and safely refreshes the same kernel
registration.

## Preview changes without making them

PowerShell's standard `-WhatIf` switch performs discovery and prints the
planned profile, environment, PATH, kernel, and verification actions without
changing anything:

```powershell
& .\scripts\bootstrap_windows.ps1 -Profile Advanced -PersistUserPath -WhatIf
```

If a missing system tool would require an explicitly authorized install,
combine the switches to preview that install:

```powershell
& .\scripts\bootstrap_windows.ps1 -InstallMissingWithWinget -WhatIf
```

## Choose locked or declarative installation

The default `Auto` dependency mode uses `uv sync --locked` when `uv` is already
available. This verifies and installs from the checked-in `uv.lock` without
changing it. Otherwise it uses
`python -m pip install -e ...` with the optional dependency groups declared in
`pyproject.toml`.

Require the checked-in lock explicitly:

```powershell
& .\scripts\bootstrap_windows.ps1 -DependencyMode Locked
```

Use the project declarations even when `uv` is installed:

```powershell
& .\scripts\bootstrap_windows.ps1 -DependencyMode Project
```

Locked mode stops with remediation instructions if `uv` is unavailable. It
does not silently fall back when you explicitly requested the lock.

## Make selected tools available in future terminals

By default, the bootstrapper does not change the user or machine `PATH`. To
append only narrowly needed executable directories to the current user's
`PATH`:

```powershell
& .\scripts\bootstrap_windows.ps1 -PersistUserPath
```

This never changes the machine-wide `PATH` and does not use `setx`, which can
truncate long values. PostgreSQL's `bin` directory is eligible. A Python.org
interpreter and its `Scripts` directory are eligible, but the bootstrapper
never persists an Anaconda or Miniconda root. Conda's own activation mechanism
is safer because it manages the distribution's interdependent directories.
Open a new terminal after the command to receive the updated user environment.

You do not need persistence for Python course commands because they use
`.\.venv\Scripts\python.exe`. Persistence is convenient for running `psql`
directly in later PowerShell windows.

## Opt in to installing a truly missing system tool

Discovery always runs before installation. Anaconda or PostgreSQL merely being
absent from `PATH` does not cause a reinstall.

If supported Python or PostgreSQL is genuinely missing, the normal run stops
and explains what to install. To explicitly permit `winget` installation:

```powershell
& .\scripts\bootstrap_windows.ps1 -InstallMissingWithWinget
```

That switch may install:

- `Python.Python.3.12`
- `PostgreSQL.PostgreSQL.17`
- `astral-sh.uv`, but only when locked mode was explicitly selected

The PostgreSQL installer may present its own setup UI. The bootstrapper does
not supply, retain, or print its password. If `winget` is unavailable or an
installer requires a restart, complete the official installation, open a new
PowerShell window, and rerun the bootstrapper.

For a Python-only machine, bypass the otherwise-required PostgreSQL check
explicitly:

```powershell
& .\scripts\bootstrap_windows.ps1 -SkipPostgreSql
```

SQL lessons and PostgreSQL-backed notebooks will not be runnable in that mode.

## Continue to PostgreSQL notebooks

After bootstrap, follow
[PostgreSQL in Jupyter](jupyter-postgresql.md) to configure only the disposable
`advanced_sql_training` database. Connection configuration is deliberately
separate from software installation.

Start the professional notebook folder with:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab .\bridge\professional\notebooks
```

Never paste a workplace or valuable database credential into a notebook.

## Troubleshooting

### Anaconda was found, but its Python version is unsupported

The course supports Python 3.11-3.12. A newer base Anaconda environment is not
silently accepted because compiled course dependencies may not support it.
Install a supported Python or conda distribution, then rerun.

### `.venv` exists but is broken or uses the wrong Python

The bootstrapper never deletes an environment automatically. Preserve anything
you need, then rename or remove only this repository's `.venv` and rerun. A
`.venv` is generated machine-local state and should not be copied to another
computer or USB drive.

### `psql` works during bootstrap but not in a new terminal

The default PATH change is intentionally process-scoped. Rerun with
`-PersistUserPath`, or invoke the full `psql.exe` path printed by the script.

### The kernel appears in Jupyter but not VS Code

Restart VS Code, select `.venv\Scripts\python.exe`, then choose
`Python (ds60sqlpy)` from the notebook kernel picker. Confirm its interpreter:

```powershell
.\.venv\Scripts\python.exe -m jupyter kernelspec list
```

### Package installation fails

Stay online for the initial bootstrap, confirm the machine is 64-bit, and
retry the same command. A partial `.venv` can normally be reused. For the
largest optional profiles, start with `Core`, verify it, and add `Advanced`
afterward.

See [Windows setup](windows.md), [VS Code](../vscode.md), and
[Troubleshooting](../troubleshooting.md) for the rest of the learning
environment.
