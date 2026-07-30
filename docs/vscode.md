# Visual Studio Code workflow

Open the repository root in VS Code. Opening only `python/ds-60day` or `sql/postgres-60day` makes relative commands and agent guidance harder to resolve.

```text
code .
```

## Recommended extensions

The repository recommends:

- Ruff (`charliermarsh.ruff`)
- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)
- Jupyter (`ms-toolsai.jupyter`)
- PostgreSQL (`ms-ossdata.vscode-pgsql`)
- markdownlint (`DavidAnson.vscode-markdownlint`)

VS Code should offer these automatically from `.vscode/extensions.json`. Use **Extensions: Show Recommended Extensions** if it does not.

Extensions are a connected-setup requirement. For a fully offline machine, download their `.vsix` packages in advance.

## Select the Python interpreter

Create the environment first with the OS setup script.

1. Open the Command Palette:
   - Windows/Linux: `Ctrl+Shift+P`
   - macOS: `Cmd+Shift+P`
2. Run **Python: Select Interpreter**.
3. Choose:
   - Windows: the interpreter printed by `bootstrap_windows.ps1`:
     `.venv\Scripts\python.exe` for a standard `venv`, or
     `.venv\python.exe` for the Anaconda conda-prefix fallback
   - macOS/Linux: `.venv/bin/python`
4. Open a new integrated terminal.
5. Run **Terminal → Run Task → Course: Doctor**. If you prefer the terminal,
   use the activation-free command for your operating system:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS or Linux
   .venv/bin/python scripts/course.py doctor
   ```

The status bar should show the selected `.venv` interpreter. Selecting it does
not guarantee that PowerShell execution policy allowed terminal
auto-activation, which is why the command above resolves and invokes either
supported Windows layout directly.

## Select a notebook kernel

Interpreter selection and notebook-kernel selection are related but separate.

1. Open a lesson notebook.
2. Choose **Select Kernel** in the upper-right corner.
3. Choose **Python Environments**.
4. Select the repository `.venv`.

If a package imports in the terminal but not the notebook, the notebook almost always has the wrong kernel. Restart the kernel after installing packages.

Start at **Terminal → Run Task → Course: Learning portal** for the private
progress dashboard and allowlisted VS Code/Jupyter launch buttons. You can also
start JupyterLab directly with **Course: JupyterLab** or work in VS Code's
notebook editor.

The professional PostgreSQL notebook uses the same Python kernel plus the
JupySQL extension. Prepare its process-scoped connection and packages with
[PostgreSQL in Jupyter](setup/jupyter-postgresql.md); do not save a database
password in notebook metadata or VS Code workspace settings.

## Repository tasks

Use **Terminal → Run Task**:

- `Course: Setup`
- `Course: Learning portal`
- `Course: Doctor`
- `Course: Catalog`
- `Course: Validate`
- `Course: JupyterLab`
- `Course: PostgreSQL Notebook`
- `Course: Bridge tests`
- `Course: Professional tests`

Python-backed tasks use the interpreter selected through **Python: Select
Interpreter**, so both supported Windows `.venv` layouts work without editing
the task file. The Windows setup task uses the discovery bootstrap, which can
find supported Anaconda and PostgreSQL installations even when they are absent
from `PATH`.

## PostgreSQL

The PostgreSQL extension is optional; every SQL lesson can run through `psql`.

For a local connection:

- Server: `localhost`
- Port: `5432`
- Database: `advanced_sql_training`
- User: the role created in your OS setup guide

Do not save a real production password in repository settings. Keep this connection limited to the disposable course database.

When running files in the terminal, preserve error-stop behavior:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
```

VS Code query-editor execution does not automatically reproduce every `psql` behavior. Use the terminal command when validating an entire lesson file.

## Working with Codex

Open Codex from the repository root so it discovers:

- Root and nested `AGENTS.md` files
- The `$guide-ds60sqlpy-learning` repo skill
- The curriculum catalog
- The checked-in validation commands

Ask Codex to inspect the learner’s current file before suggesting a fix. See [Learning with Codex](learning-with-codex.md).

## Files generated while learning

Write experiments to `artifacts/` or personal progress to `.learning/`; both are ignored. Do not save generated models, notebook checkpoints, credentials, or large downloads beside course source files.

## Common VS Code fixes

- Wrong interpreter: run **Python: Select Interpreter** again.
- Wrong notebook kernel: use **Select Kernel**, then restart.
- New packages not visible: restart the kernel and verify the selected `.venv`.
- `code` command missing: open VS Code normally and use **File → Open Folder**.
- PostgreSQL extension connects but a lesson behaves differently: validate with the documented `psql` command.

More help: [Troubleshooting](troubleshooting.md).
