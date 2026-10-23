# Your first successful session

> **One classroom:** the browser opens `/classroom`, where Python, PostgreSQL,
> the engineering bridge and every module/book subject share one home and
> individually themed workspaces. Choose any path and set your own pace.
> Start with `./classroom`; see the [classroom guide](../classroom-experience.md) for reading, code,
> saved work and compatibility bookmarks.


You do not need to know programming, SQL, or Git before starting. Set aside a
first session for getting one Python cell and one SQL query to run. Setup is
part of learning. The lesson sequence starts after those two small wins.

## Understand the tools before installing them

| Word | Meaning in this course |
| --- | --- |
| Repository | This course folder and the files inside it |
| Terminal | A window where you type commands and read their output |
| Shell | The program interpreting terminal commands: PowerShell on Windows, Bash or Zsh on macOS/Linux |
| Python interpreter | The program that executes Python code |
| Package | A reusable library installed for one Python interpreter |
| `.venv` | This repository's isolated Python and packages |
| Notebook | A file ending in `.ipynb` with text and runnable cells |
| Kernel | The Python process executing a notebook's cells |
| PostgreSQL server | The local program storing tables and answering SQL queries |
| `psql` | A terminal client that sends SQL to PostgreSQL |
| Docker container | An isolated process used here to run a consistent PostgreSQL server |

VS Code is the editor. JupyterLab is an alternative notebook interface that
opens in your browser. The learning portal helps you navigate lessons and
launch either editor; the browser's static lesson preview is read-only.

## 1. Choose the matching operating-system guide

- [Windows with PowerShell](windows.md)
- [macOS with Terminal](macos.md)
- [Linux with a terminal](linux.md)

Type only the contents of a command block, without its triple-backtick fence.
Run one command at a time and wait for the prompt to return. A command can
succeed without printing anything. Lines beginning with `#` explain the next
command. Do not paste a PowerShell block into a Bash terminal or a SQL prompt.

On Windows, open **Windows PowerShell** from Start. On macOS, open **Terminal**
from Applications → Utilities. On Linux, open your desktop's terminal app.
Commands below assume you have completed the OS guide's package setup and are
in the repository root, the folder containing `README.md` and `pyproject.toml`.

The first setup needs internet access. Python 3.12 is the course baseline;
3.11 is supported too. An installed newer Python can coexist with it. The
course does not require you to replace your operating system's Python.

## 2. Prove the terminal uses the course Python

Windows PowerShell, once in each new terminal:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython -c "import sys; print(sys.executable); print(2 + 3)"
```

macOS/Linux:

```bash
.venv/bin/python -c "import sys; print(sys.executable); print(2 + 3)"
```

Expected: a Python path inside this course's `.venv`, then `5`. Keep using that
interpreter for installations and commands. Environment activation is optional.

Run doctor with the same interpreter:

```powershell
# Windows
& $CoursePython scripts\course.py doctor
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py doctor
```

A missing optional Docker/VS Code command is a warning. A missing course
package requires setup repair. A database warning is expected if you have
chosen to start with Python before installing PostgreSQL. Doctor's package
discovery is not an execution test of every library or lesson.

## 3. Make a scratch notebook and run one cell

Start JupyterLab from this terminal:

```powershell
# Windows
& $CoursePython -m jupyter lab
```

```bash
# macOS/Linux
.venv/bin/python -m jupyter lab
```

Keep the terminal open. If a browser does not open, use the local Jupyter URL
printed there. Treat a URL containing a token as private.

1. In JupyterLab's file browser, create an `artifacts` folder if it does not
   already exist and open it. This ignored folder is for your experiments.
2. Create a notebook with **Python (ds60sqlpy)**. Rename it `first-success.ipynb`.
3. Type the following into a code cell and press `Shift+Enter`:

   ```python
   import sys

   print(sys.executable)
   learner = "Ada"
   study_minutes = 20
   print(f"Hello, {learner}. Today I studied for {study_minutes} minutes.")
   print(2 + 3)
   ```

4. Expect the `.venv` path, the greeting, and `5`.
5. Change the name and minutes, predict the new output, then run it again.
6. Restart the kernel and run all cells. The output should remain correct.
   Restarting removes variables remembered from earlier cell execution.

In VS Code, the same cell works in an `.ipynb` file after **Select Kernel** →
the repository's Python environment. Selecting a terminal interpreter and
selecting a notebook kernel are separate steps. See the
[VS Code notebook documentation](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)
and the [course VS Code guide](../vscode.md).

## 4. Prove SQL works

Follow [Local PostgreSQL, step by step](postgresql.md) using either the native
server or the course's container. That guide includes a query returning `5`,
the disposable database setup, seed verification, and the exact connection
setting needed by the private learning portal.

You can study the Python fundamentals first if database setup must wait.
Creating a Python environment does not install or start a PostgreSQL server.

## 5. Start the first lesson

Start the dashboard from the terminal that has your database setting:

```powershell
# Windows
& $CoursePython scripts\learning_portal.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/learning_portal.py
```

Choose Python Day 1 (`python-01`) or SQL Day 1 (`sql-01`). Read its guide, predict
what the examples will do, run them, and attempt the exercises before reading
solutions. SQL's **Create/open guided SQL notebook** action preserves your
working copy under `.learning/sql/`. Opening a lesson is a navigation step;
being able to explain and reproduce its result is your learning check.

At the end of the session, save your notebook and press `Ctrl+C` in the
terminal to stop a server you started. Closing a browser tab alone does not
stop Jupyter or the portal. Follow any visible confirmation prompt. Next time,
open the repository, resolve the course interpreter, and launch the portal;
you do not need to reinstall packages.

## If the first session fails

Find the first failing step above and use the corresponding section in
[Troubleshooting](../troubleshooting.md). Include the exact command, operating
system, first error, and the interpreter path when seeking help. Remove
passwords and private Jupyter URLs. Your scratch notebook, progress, and SQL
working copies should be preserved during a repair.
