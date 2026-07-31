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





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

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
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day01_setup_and_repl.md`, then open `python/ds-60day/notebooks/day01_setup_and_repl.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 1 — setup, repl, virtual environments, and packages to practice execution contexts and a trustworthy course environment
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

Python code always runs inside a particular **interpreter process**. That
process has a version, a filesystem location, an installed package set,
and a current working directory. A terminal REPL, a script, and a
notebook may look like three different tools, but each eventually asks
an interpreter to execute Python.

A virtual environment gives this repository its own interpreter and
package directory. A Jupyter kernel is the notebook's connection to an
interpreter. If the terminal and notebook point at different
interpreters, a package can import in one place and fail in the other.
Diagnose identity first; reinstalling packages blindly often makes the
mismatch harder to see.

### Vocabulary in plain language

- **interpreter:** the program that reads Python code and executes it.
- **REPL:** Read-Evaluate-Print Loop, an interactive prompt for small experiments.
- **script:** a saved `.py` file executed from top to bottom.
- **virtual environment:** an isolated interpreter/package location owned by one project.
- **kernel:** the long-running interpreter process connected to a notebook.
- **working directory:** the base directory used to resolve relative paths.

### Syntax anatomy

`python -m module` has three parts: `python` chooses the interpreter,
`-m` asks that interpreter to locate an importable module, and `module`
names what to run. Therefore `python -m pip` installs into the same
interpreter selected by `python`. In a notebook, `sys.executable`
reveals the kernel's interpreter and `Path.cwd()` reveals its working
directory.

### Worked example 1 — Ask the running interpreter to identify itself

Inspect evidence rather than guessing which Python is active. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import platform
import sys
from pathlib import Path

identity = {
    "python": platform.python_version(),
    "executable_name": Path(sys.executable).name,
    "working_folder": Path.cwd().name,
}
identity
```

**Expected observation**

```text
A dictionary is displayed. The exact paths vary by computer; the course kernel should report Python 3.11 or 3.12 and an executable inside this repository's `.venv`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Separate a calculation from presentation

The same Python expressions work in the REPL, a script, and a notebook. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
subtotal = 12.50 + 7.25
tax_rate = 0.08
total = subtotal * (1 + tax_rate)
message = f"Total: ${total:.2f}"
message
```

**Expected observation**

```text
`'Total: $21.33'`. Names keep intermediate facts visible, and the f-string controls only presentation.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Print `sys.executable` in both places when an import works in a terminal but not a notebook.
2. Run `python -m pip --version` and confirm its path belongs to the intended `.venv`.
3. Check `Path.cwd()` before blaming a missing relative file.
4. Restart the kernel after changing installed packages so the long-running process sees the new environment.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Boundary to remember:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Run the repository setup, then run `scripts/course.py doctor` with the repository interpreter. **Required evidence:** copy the Python version and interpreter path from the report. **Success:** the version is 3.11 or 3.12, the path belongs to this repository's `.venv`, and the doctor does not report a blocking core failure. **Constraint:** do not install or delete anything while diagnosing.
   **Verify:** Save the doctor output showing Python 3.11/3.12 and an interpreter path inside this repository's `.venv`; record that no blocking core check failed.

2. Open the course Python REPL and evaluate `7 * 6`, `' Python '.strip().lower()`, and `type(3.5)`. **Before running:** predict each value and type. **Success:** record the three results and exit cleanly with `exit()`; explain why the string method does not modify the original literal.
   **Verify:** Record `42`, `'python'`, and `<class 'float'>` beside your predictions, then confirm the REPL exits without terminating the terminal.

3. Open this notebook with the `Python (ds60sqlpy)` kernel. Run `import sys; print(sys.executable)` and compare it with the doctor report. **Success:** both point to the same `.venv` layout. **If they differ:** stop and diagnose the kernel rather than reinstalling packages.
   **Verify:** Resolve both paths and confirm the doctor interpreter and notebook `sys.executable` identify the same `.venv` environment.

4. Create `calc.py` so `python calc.py 12.5 7.25` prints exactly `19.75`. **Inputs:** exactly two numeric command-line arguments. **Constraints:** convert the strings from `sys.argv`, print a friendly usage message for the wrong count, and keep the arithmetic in a small function.
   **Verify:** test integers, decimals, and one invalid numeric value. Day 15 later replaces this bounded interface with `argparse`.

5. Create two temporary virtual environments outside the repository and install NumPy in only one. **Evidence:** use each environment's `python -m pip show numpy` and interpreter path to prove isolation. **Constraint:** do not alter or delete the course `.venv`; remove only the two temporary environments you created after recording the result.
   **Verify:** Show NumPy succeeds under exactly one temporary interpreter and fails under the other, while the course interpreter/path remains unchanged.

### Additional mastery practice

Treat the interpreter, package installer, and notebook kernel as one connected system. Record evidence before changing an environment.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

6. **Prediction:** Predict what `sys.executable` should contain when the correct course kernel is active, then verify it in both the REPL and this notebook.
   **Progressive hint:** The important fact is the interpreter path, not merely the word Python.
   **Verify:** Resolve the REPL and notebook `sys.executable` values and assert both identify the same course `.venv`; record the exact shared path component.
7. **Tracing:** Trace the difference between `python -m pip --version` and a bare `pip --version`: which interpreter owns each command?
   **Progressive hint:** Read the Python and site-packages paths printed by pip.
   **Verify:** Save both pip-version lines, underline the Python/site-packages owner in each, and explain any mismatch instead of assuming the commands are equivalent.
8. **Implementation:** Write `environment_report()` returning the Python version, executable, platform, and current working directory without shell commands.
   **Progressive hint:** Use `sys`, `platform`, and `pathlib.Path`.
   **Verify:** Assert `environment_report()` has exactly the four required fields with string values and that its executable/cwd agree with direct `sys`/`Path` inspection.
9. **Debugging:** A package imports in PowerShell but is missing in Jupyter. Write a three-step diagnosis that proves whether their interpreters differ.
   **Progressive hint:** Compare executable paths before reinstalling anything.
   **Verify:** Record `sys.executable`, `python -m pip --version`, and the notebook kernel interpreter; identify the first evidence that differs before changing anything.
10. **Edge case and explanation:** Explain how to recover when the `ds60sqlpy` kernel is absent even though `.venv` exists, and state what remains possible offline.
   **Progressive hint:** Kernel registration and package download are separate operations.
   **Verify:** After local kernel registration, confirm `jupyter kernelspec list` includes `ds60sqlpy` and run one already-installed offline import without downloading a package.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-01`
(Day 1 — Setup, REPL, Virtual Environments, and Packages). I am a complete beginner. Emphasize execution contexts and a trustworthy course environment.
Read `python/ds-60day/companion-guides/day01_setup_and_repl.md` and use the learner notebook
`python/ds-60day/notebooks/day01_setup_and_repl.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
