# Day 1 — Setup, REPL, Virtual Environments, and Packages

**Level:** Beginner

Day 1 builds the environment used by every later lesson. Run commands from the
repository root in VS Code's integrated terminal.

## Learning objectives

By the end of this lesson, you can:

- verify that a supported Python 3.11–3.12 interpreter is installed;
- create the repository's isolated `.venv` environment;
- identify which interpreter and Jupyter kernel are running your code;
- use the REPL for an experiment and a `.py` file for repeatable work; and
- install packages through the selected interpreter.

## Prerequisites

None. Start with the operating-system setup in
[`docs/setup/windows.md`](../../../docs/setup/windows.md) or the corresponding
macOS/Linux guide. Python 3.12 is the canonical version; 3.11 is also supported.

## Vocabulary and mental model

- **Interpreter:** the program that executes Python code.
- **REPL:** a read-evaluate-print loop for short, disposable experiments.
- **Virtual environment:** a project-local interpreter and package directory.
  Think of `.venv` as this repository's private toolbox.
- **Package:** reusable code installed into an environment.
- **Kernel:** the interpreter process backing a notebook. Selecting the wrong
  kernel is like running the right file with the wrong toolbox.

`.venv` and cache directories are local, disposable machine state. They are
ignored by Git; each learner creates their own.

## Create and verify the course environment

Windows PowerShell:

```powershell
py -3.12 --version
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\course.py doctor
.\.venv\Scripts\python.exe -m jupyterlab python\ds-60day\notebooks
```

macOS/Linux:

```bash
python3.12 --version
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
.venv/bin/python -m jupyterlab python/ds-60day/notebooks
```

Activation is optional. Calling the interpreter by its path avoids PowerShell
execution-policy issues and makes the selected environment unambiguous. In VS
Code, select that same `.venv` interpreter and the `Python (ds60sqlpy)` kernel.

## Worked example

Try this in the REPL, then save it as `hello.py` and run the file:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"


print(greet("learner"))
```

The REPL gives fast feedback. The file records exactly what should run again.

## Exercises and progressive hints

1. Run the setup and confirm that `course.py doctor` reports Python 3.11 or
   3.12. **Hint:** read the interpreter path in the report; it should contain
   `.venv`.
2. Start the REPL and evaluate arithmetic, a string method, and `type(...)`.
   **Hint:** exit with `exit()`.
3. In JupyterLab, select `Python (ds60sqlpy)` and print the interpreter path.
   **Hint:** the `sys` module can describe the running interpreter.
4. Create `calc.py` so two numeric command-line arguments produce their sum.
   **Hint:** command-line values in `sys.argv` are strings, so convert them
   deliberately. Day 15 replaces this bounded approach with `argparse`.
5. As deeper environment practice, create two temporary environments and
   install NumPy in only one. **Hint:** always use `python -m pip` from the
   interpreter you intend to modify.

The separate solution notes use the two-environment and REPL exercises to test
the same setup skills without simply copying the notebook cells.

## Self-check

- How can you prove which Python interpreter is executing a command?
- Why can an import work in a terminal but fail in a notebook?
- Which work belongs in the REPL, a script, and a notebook?
- What should be committed: `.venv`, or the files that describe dependencies?

Expected behavior: setup is repeatable, `doctor` identifies `.venv`, and a new
notebook can import the packages installed by `scripts/setup.*`.

## Common pitfalls and diagnosis

- **`py` or `python3.12` is not found:** install Python 3.12, reopen VS Code,
  and rerun the version command.
- **A package is missing only in Jupyter:** inspect the selected kernel; it is
  probably not the repository's `.venv`.
- **PowerShell blocks activation:** do not change policy just for activation;
  use `.\.venv\Scripts\python.exe` directly.
- **`pip` installs to the wrong place:** replace bare `pip` with
  `<venv-python> -m pip`.
- **A path contains spaces:** quote it when typing the path manually.

## Continue

- [Open the learner notebook](../notebooks/day01_setup_and_repl.ipynb)
- [Check the separate solution after attempting the work](../solutions/day01_setup_and_repl/day01_solutions.md)
- [Next: Day 2 — Variables and core types](day02_basics_types.md)
