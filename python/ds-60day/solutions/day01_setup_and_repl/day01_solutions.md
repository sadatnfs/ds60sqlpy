# Day 01 — Solutions: Setup, REPL, Virtual Envs, Package Management

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **execution contexts and a trustworthy course environment**. Predict each named
result before comparing your attempt with its matching assertions.

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

### Vocabulary used in the worked answers

- **interpreter:** the program that reads Python code and executes it.
- **REPL:** Read-Evaluate-Print Loop, an interactive prompt for small experiments.
- **script:** a saved `.py` file executed from top to bottom.
- **virtual environment:** an isolated interpreter/package location owned by one project.
- **kernel:** the long-running interpreter process connected to a notebook.
- **working directory:** the base directory used to resolve relative paths.

### How to compare an answer

For this lesson's **execution contexts and a trustworthy course environment** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–5 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Run the repository setup, then run `scripts/course.py doctor` with the repository interpreter. **Required evidence:** copy the Python version and interpreter path from the report. **Success:** the version is 3.11 or 3.12, the path belongs to this repository's `.venv`, and the doctor does not report a blocking core failure. **Constraint:** do not install or delete anything while diagnosing. **Verify:** Save the doctor output showing Python 3.11/3.12 and an interpreter path inside this repository's `.venv`; record that no blocking core check failed.

**Reasoning:** Implement this exact contract as written: Run the repository setup, then run `scripts/course.py doctor` with the repository interpreter. Required evidence: copy the Python version and interpreter path from the report. Success: the version is 3.11 or 3.12, the path belongs to this repository's `.venv`, and the doctor does not report a blocking core failure. Constraint: do not install or delete anything while diagnosing. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Save the doctor output showing Python 3.11/3.12 and an interpreter path inside this repository's `.venv`; record that no blocking core check failed. That connects the answer to execution contexts and a trustworthy course environment.

Run the doctor with the repository interpreter and keep its output as
evidence; no Python implementation is needed for this environment check.

```powershell
# Windows PowerShell, after resolving $CoursePython as shown in the guide
& $CoursePython scripts\course.py doctor
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py doctor
```

Read the reported executable path rather than accepting a successful
command from an unrelated global Python.

**Verification evidence:** Save the doctor output showing Python 3.11/3.12 and an interpreter path inside this repository's `.venv`; record that no blocking core check failed.

### Exercise 2 — worked answer

**Learner contract:** Open the course Python REPL and evaluate `7 * 6`, `' Python '.strip().lower()`, and `type(3.5)`. **Before running:** predict each value and type. **Success:** record the three results and exit cleanly with `exit()`; explain why the string method does not modify the original literal. **Verify:** Record `42`, `'python'`, and `<class 'float'>` beside your predictions, then confirm the REPL exits without terminating the terminal.

**Reasoning:** Predict this named state change before running it: Open the course Python REPL and evaluate `7 * 6`, `' Python '.strip().lower()`, and `type(3.5)`. Before running: predict each value and type. Success: record the three results and exit cleanly with `exit()`; explain why the string method does not modify the original literal. Then compare the prediction with this proof target: Record `42`, `'python'`, and `<class 'float'>` beside your predictions, then confirm the REPL exits without terminating the terminal. This makes execution contexts and a trustworthy course environment observable instead of relying on intuition.

A REPL transcript should look like this:

```pycon
>>> 7 * 6
42
>>> "  Python ".strip().lower()
'python'
>>> type(3.5)
<class 'float'>
>>> exit()
```

`strip()` and `lower()` each return a new string; the literal is not
mutated.

**Verification evidence:** Record `42`, `'python'`, and `<class 'float'>` beside your predictions, then confirm the REPL exits without terminating the terminal.

### Exercise 3 — worked answer

**Learner contract:** Open this notebook with the `Python (ds60sqlpy)` kernel. Run `import sys; print(sys.executable)` and compare it with the doctor report. **Success:** both point to the same `.venv` layout. **If they differ:** stop and diagnose the kernel rather than reinstalling packages. **Verify:** Resolve both paths and confirm the doctor interpreter and notebook `sys.executable` identify the same `.venv` environment.

**Reasoning:** Implement this exact contract as written: Open this notebook with the `Python (ds60sqlpy)` kernel. Run `import sys; print(sys.executable)` and compare it with the doctor report. Success: both point to the same `.venv` layout. If they differ: stop and diagnose the kernel rather than reinstalling packages. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Resolve both paths and confirm the doctor interpreter and notebook `sys.executable` identify the same `.venv` environment. That connects the answer to execution contexts and a trustworthy course environment.

Run this in the selected notebook kernel and compare the resolved path
with the doctor report:

```python
import sys
from pathlib import Path

notebook_python = Path(sys.executable).resolve()
print(notebook_python)
assert notebook_python.exists()
```

Compare the printed path to the doctor's path character for character
after resolving both. In the real course run they must name the same
repository environment. This reusable snippet checks that the
interpreter exists without hard-coding a Windows or POSIX layout.

**Verification evidence:** Resolve both paths and confirm the doctor interpreter and notebook `sys.executable` identify the same `.venv` environment.

### Exercise 4 — worked answer

**Learner contract:** Create `calc.py` so `python calc.py 12.5 7.25` prints exactly `19.75`. **Inputs:** exactly two numeric command-line arguments. **Constraints:** convert the strings from `sys.argv`, print a friendly usage message for the wrong count, and keep the arithmetic in a small function. **Verify:** test integers, decimals, and one invalid numeric value. Day 15 later replaces this bounded interface with `argparse`.

**Reasoning:** Implement this exact contract as written: Create `calc.py` so `python calc.py 12.5 7.25` prints exactly `19.75`. Inputs: exactly two numeric command-line arguments. Constraints: convert the strings from `sys.argv`, print a friendly usage message for the wrong count, and keep the arithmetic in a small function. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test integers, decimals, and one invalid numeric value. Day 15 later replaces this bounded interface with `argparse`. That connects the answer to execution contexts and a trustworthy course environment.

Save this as `calc.py`:

```python
from __future__ import annotations

import sys


def add(left: float, right: float) -> float:
    return left + right


def main(arguments: list[str]) -> int:
    if len(arguments) != 2:
        print("Usage: python calc.py NUMBER NUMBER")
        return 2
    try:
        left, right = (float(value) for value in arguments)
    except ValueError:
        print("Both arguments must be numbers.")
        return 2
    print(add(left, right))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

`python calc.py 12.5 7.25` prints `19.75`; bad count or bad numeric
text returns status 2 without hiding unrelated programming errors.

**Verification evidence:** test integers, decimals, and one invalid numeric value. Day 15 later replaces this bounded interface with `argparse`.

### Exercise 5 — worked answer

**Learner contract:** Create two temporary virtual environments outside the repository and install NumPy in only one. **Evidence:** use each environment's `python -m pip show numpy` and interpreter path to prove isolation. **Constraint:** do not alter or delete the course `.venv`; remove only the two temporary environments you created after recording the result. **Verify:** Show NumPy succeeds under exactly one temporary interpreter and fails under the other, while the course interpreter/path remains unchanged.

**Reasoning:** Implement this exact contract as written: Create two temporary virtual environments outside the repository and install NumPy in only one. Evidence: use each environment's `python -m pip show numpy` and interpreter path to prove isolation. Constraint: do not alter or delete the course `.venv`; remove only the two temporary environments you created after recording the result. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Show NumPy succeeds under exactly one temporary interpreter and fails under the other, while the course interpreter/path remains unchanged. That connects the answer to execution contexts and a trustworthy course environment.

Create temporary environments outside the repository, always invoking
pip through the interpreter that owns the environment:

```powershell
py -3.12 -m venv $env:TEMP\ds60-env-a
py -3.12 -m venv $env:TEMP\ds60-env-b
& $env:TEMP\ds60-env-a\Scripts\python.exe -m pip install numpy
& $env:TEMP\ds60-env-a\Scripts\python.exe -m pip show numpy
& $env:TEMP\ds60-env-b\Scripts\python.exe -m pip show numpy
```

```bash
python3.12 -m venv /tmp/ds60-env-a
python3.12 -m venv /tmp/ds60-env-b
/tmp/ds60-env-a/bin/python -m pip install numpy
/tmp/ds60-env-a/bin/python -m pip show numpy
/tmp/ds60-env-b/bin/python -m pip show numpy
```

The final command should report NumPy absent; neither command targets
the course `.venv`.

**Verification evidence:** Show NumPy succeeds under exactly one temporary interpreter and fails under the other, while the course interpreter/path remains unchanged.

## Exercises 6–10 — Expanded mastery answers

### Exercise 6 — answer contract

**Learner contract:** **Prediction:** Predict what `sys.executable` should contain when the correct course kernel is active, then verify it in both the REPL and this notebook. **Progressive hint:** The important fact is the interpreter path, not merely the word Python. **Verify:** Resolve the REPL and notebook `sys.executable` values and assert both identify the same course `.venv`; record the exact shared path component.

**Reasoning:** Predict this named state change before running it: Prediction: Predict what `sys.executable` should contain when the correct course kernel is active, then verify it in both the REPL and this notebook. Progressive hint: The important fact is the interpreter path, not merely the word Python. Then compare the prediction with this proof target: Resolve the REPL and notebook `sys.executable` values and assert both identify the same course `.venv`; record the exact shared path component. This makes execution contexts and a trustworthy course environment observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Resolve the REPL and notebook `sys.executable` values and assert both identify the same course `.venv`; record the exact shared path component.

### Exercise 7 — answer contract

**Learner contract:** **Tracing:** Trace the difference between `python -m pip --version` and a bare `pip --version`: which interpreter owns each command? **Progressive hint:** Read the Python and site-packages paths printed by pip. **Verify:** Capture both pip-version outputs, underline the Python executable/site-packages owner in each, and assert whether the two paths identify the same environment; explain any mismatch.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace the difference between `python -m pip --version` and a bare `pip --version`: which interpreter owns each command? Progressive hint: Read the Python and site-packages paths printed by pip. Record the named value, shape, label, or iterator position needed to establish: Capture both pip-version outputs, underline the Python executable/site-packages owner in each, and assert whether the two paths identify the same environment; explain any mismatch. The trace exposes execution contexts and a trustworthy course environment directly.

**Evidence to locate in the grouped implementation:** Capture both pip-version outputs, underline the Python executable/site-packages owner in each, and assert whether the two paths identify the same environment; explain any mismatch.

### Exercise 8 — answer contract

**Learner contract:** **Implementation:** Write `environment_report()` returning the Python version, executable, platform, and current working directory without shell commands. **Progressive hint:** Use `sys`, `platform`, and `pathlib.Path`. **Verify:** Assert `environment_report()` has exactly the four required fields with string values and that its executable/cwd agree with direct `sys`/`Path` inspection.

**Reasoning:** Implement this exact contract as written: Implementation: Write `environment_report()` returning the Python version, executable, platform, and current working directory without shell commands. Progressive hint: Use `sys`, `platform`, and `pathlib.Path`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert `environment_report()` has exactly the four required fields with string values and that its executable/cwd agree with direct `sys`/`Path` inspection. That connects the answer to execution contexts and a trustworthy course environment.

**Evidence to locate in the grouped implementation:** Assert `environment_report()` has exactly the four required fields with string values and that its executable/cwd agree with direct `sys`/`Path` inspection.

### Exercise 9 — answer contract

**Learner contract:** **Debugging:** A package imports in PowerShell but is missing in Jupyter. Write a three-step diagnosis that proves whether their interpreters differ. **Progressive hint:** Compare executable paths before reinstalling anything. **Verify:** Record `sys.executable`, `python -m pip --version`, and the notebook kernel interpreter; identify the first evidence that differs before changing anything.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: A package imports in PowerShell but is missing in Jupyter. Write a three-step diagnosis that proves whether their interpreters differ. Progressive hint: Compare executable paths before reinstalling anything. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Record `sys.executable`, `python -m pip --version`, and the notebook kernel interpreter; identify the first evidence that differs before changing anything. The diagnosis depends on execution contexts and a trustworthy course environment.

**Evidence to locate in the grouped implementation:** Record `sys.executable`, `python -m pip --version`, and the notebook kernel interpreter; identify the first evidence that differs before changing anything.

### Exercise 10 — answer contract

**Learner contract:** **Edge case and explanation:** Explain how to recover when the `ds60sqlpy` kernel is absent even though `.venv` exists, and state what remains possible offline. **Progressive hint:** Kernel registration and package download are separate operations. **Verify:** After local kernel registration, assert the `jupyter kernelspec list` output contains `ds60sqlpy`, then run one already-installed offline import and record its successful output without downloading a package.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Explain how to recover when the `ds60sqlpy` kernel is absent even though `.venv` exists, and state what remains possible offline. Progressive hint: Kernel registration and package download are separate operations. Values below, at, and above the named boundary must produce the evidence After local kernel registration, assert the `jupyter kernelspec list` output contains `ds60sqlpy`, then run one already-installed offline import and record its successful output without downloading a package. Those cases show how execution contexts and a trustworthy course environment behaves at its edge.

**Evidence to locate in the grouped implementation:** After local kernel registration, assert the `jupyter kernelspec list` output contains `ds60sqlpy`, then run one already-installed offline import and record its successful output without downloading a package.

## Expanded mastery lab solutions

Treat the interpreter, package installer, and notebook kernel as one connected system. Record evidence before changing an environment.

### Shared implementation for Exercise 6 — Prediction

The correct result is an executable inside this repository's `.venv`
(`.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on POSIX). The
exact prefix varies by clone location, so inspect the path rather than comparing
it with a developer-specific absolute string.

### Shared implementation for Exercise 7 — Trace

`python -m pip` asks a known interpreter to import its installed `pip` module.
A bare `pip` is whichever executable the shell finds first on `PATH`; it can
belong to Anaconda, the Windows launcher, or another environment.

### Shared implementation for Exercises 8–10 — Evidence-first environment diagnosis

```python
from __future__ import annotations

import platform
import sys
from pathlib import Path


def environment_report() -> dict[str, str]:
    """Return portable facts about the interpreter running this code."""

    # resolve() makes relative path segments explicit without assuming a drive.
    executable = Path(sys.executable).resolve()
    return {
        "python": platform.python_version(),
        "executable": str(executable),
        "platform": platform.platform(),
        "working_directory": str(Path.cwd().resolve()),
    }


report = environment_report()
assert report["python"].count(".") == 2
assert Path(report["executable"]).name.lower().startswith("python")

# Debugging order:
# 1. Print sys.executable in PowerShell's Python and in the notebook.
# 2. Run each executable with `-m pip --version`.
# 3. Select/register the kernel that points at the repository interpreter.
#
# If `.venv` already contains ipykernel, registration is local and works
# offline:
#   .\.venv\Scripts\python.exe -m ipykernel install --user \
#       --name ds60sqlpy --display-name "Python (ds60sqlpy)"
# Package installation still requires the downloaded wheel cache or a network.
```

The repair changes kernel metadata; it should not involve copying packages
between interpreters or adding an arbitrary global directory to `PATH`.
