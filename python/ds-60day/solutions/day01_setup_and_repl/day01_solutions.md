# Day 01 — Solutions: Setup, REPL, Virtual Envs, Package Management

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**execution contexts and a trustworthy course environment**.

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

### Reference pattern 1 — Ask the running interpreter to identify itself

Inspect evidence rather than guessing which Python is active.

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

**Expected observation:** A dictionary is displayed. The exact paths vary by computer; the course kernel should report Python 3.11 or 3.12 and an executable inside this repository's `.venv`.

### Reference pattern 2 — Separate a calculation from presentation

The same Python expressions work in the REPL, a script, and a notebook.

```python
subtotal = 12.50 + 7.25
tax_rate = 0.08
total = subtotal * (1 + tax_rate)
message = f"Total: ${total:.2f}"
message
```

**Expected observation:** `'Total: $21.33'`. Names keep intermediate facts visible, and the f-string controls only presentation.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Run the repository setup, then run `scripts/course.py doctor` with the repository interpreter. **Required evidence:** copy the Python version and interpreter path from the report. **Success:** the version is 3.11 or 3.12, the path belongs to this repository's `.venv`, and the doctor does not report a blocking core failure. **Constraint:** do not install or delete anything while diagnosing. **Verify:** Save the doctor output showing Python 3.11/3.12 and an interpreter path inside this repository's `.venv`; record that no blocking core check failed.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Save the doctor output showing Python 3.11/3.12 and an interpreter path inside this repository's `.venv`; record that no blocking core check failed.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Open the course Python REPL and evaluate `7 * 6`, `' Python '.strip().lower()`, and `type(3.5)`. **Before running:** predict each value and type. **Success:** record the three results and exit cleanly with `exit()`; explain why the string method does not modify the original literal. **Verify:** Record `42`, `'python'`, and `<class 'float'>` beside your predictions, then confirm the REPL exits without terminating the terminal.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Record `42`, `'python'`, and `<class 'float'>` beside your predictions, then confirm the REPL exits without terminating the terminal.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Open this notebook with the `Python (ds60sqlpy)` kernel. Run `import sys; print(sys.executable)` and compare it with the doctor report. **Success:** both point to the same `.venv` layout. **If they differ:** stop and diagnose the kernel rather than reinstalling packages. **Verify:** Resolve both paths and confirm the doctor interpreter and notebook `sys.executable` identify the same `.venv` environment.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Resolve both paths and confirm the doctor interpreter and notebook `sys.executable` identify the same `.venv` environment.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** Create `calc.py` so `python calc.py 12.5 7.25` prints exactly `19.75`. **Inputs:** exactly two numeric command-line arguments. **Constraints:** convert the strings from `sys.argv`, print a friendly usage message for the wrong count, and keep the arithmetic in a small function. **Verify:** test integers, decimals, and one invalid numeric value. Day 15 later replaces this bounded interface with `argparse`.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** test integers, decimals, and one invalid numeric value. Day 15 later replaces this bounded interface with `argparse`.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** Create two temporary virtual environments outside the repository and install NumPy in only one. **Evidence:** use each environment's `python -m pip show numpy` and interpreter path to prove isolation. **Constraint:** do not alter or delete the course `.venv`; remove only the two temporary environments you created after recording the result. **Verify:** Show NumPy succeeds under exactly one temporary interpreter and fails under the other, while the course interpreter/path remains unchanged.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Show NumPy succeeds under exactly one temporary interpreter and fails under the other, while the course interpreter/path remains unchanged.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict what `sys.executable` should contain when the correct course kernel is active, then verify it in both the REPL and this notebook. **Progressive hint:** The important fact is the interpreter path, not merely the word Python. **Verify:** Resolve the REPL and notebook `sys.executable` values and assert both identify the same course `.venv`; record the exact shared path component.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Resolve the REPL and notebook `sys.executable` values and assert both identify the same course `.venv`; record the exact shared path component.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace the difference between `python -m pip --version` and a bare `pip --version`: which interpreter owns each command? **Progressive hint:** Read the Python and site-packages paths printed by pip. **Verify:** Save both pip-version lines, underline the Python/site-packages owner in each, and explain any mismatch instead of assuming the commands are equivalent.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the execution contexts and a trustworthy course environment model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Save both pip-version lines, underline the Python/site-packages owner in each, and explain any mismatch instead of assuming the commands are equivalent.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Write `environment_report()` returning the Python version, executable, platform, and current working directory without shell commands. **Progressive hint:** Use `sys`, `platform`, and `pathlib.Path`. **Verify:** Assert `environment_report()` has exactly the four required fields with string values and that its executable/cwd agree with direct `sys`/`Path` inspection.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Assert `environment_report()` has exactly the four required fields with string values and that its executable/cwd agree with direct `sys`/`Path` inspection.

### Exercise 9 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** A package imports in PowerShell but is missing in Jupyter. Write a three-step diagnosis that proves whether their interpreters differ. **Progressive hint:** Compare executable paths before reinstalling anything. **Verify:** Record `sys.executable`, `python -m pip --version`, and the notebook kernel interpreter; identify the first evidence that differs before changing anything.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** Record `sys.executable`, `python -m pip --version`, and the notebook kernel interpreter; identify the first evidence that differs before changing anything.

### Exercise 10 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Explain how to recover when the `ds60sqlpy` kernel is absent even though `.venv` exists, and state what remains possible offline. **Progressive hint:** Kernel registration and package download are separate operations. **Verify:** After local kernel registration, confirm `jupyter kernelspec list` includes `ds60sqlpy` and run one already-installed offline import without downloading a package.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from execution contexts and a trustworthy course environment.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A one-line REPL experiment is fast; a saved script is reproducible; a notebook is best when prose, code, and observations belong together.

**Edge case:** Paths differ across Windows, macOS, and Linux, so verify meaningful path components instead of hard-coding an entire developer-specific path.

**Solution evidence to inspect:** After local kernel registration, confirm `jupyter kernelspec list` includes `ds60sqlpy` and run one already-installed offline import without downloading a package.
<!-- END BEGINNER SOLUTION REVIEW -->

This solution expands each exercise with exact commands and the reasoning behind them.

Exercise 1: Create two virtual environments under the ignored
`artifacts/day01/` directory. Install `numpy` only in `ds-prod`. Verify import
works only there.

Why: Isolate dependencies to avoid conflicts across projects. Verifying imports ensures the correct environment is active.

Commands (macOS/Linux)
```
python3 -m venv artifacts/day01/ds-play/.venv
python3 -m venv artifacts/day01/ds-prod/.venv

# Activate ds-play and verify numpy is not present
source artifacts/day01/ds-play/.venv/bin/activate
python -c "import sys; print(sys.executable)"  # sanity
python -c "import numpy" || echo "numpy not installed in ds-play (expected)"
deactivate

# Activate ds-prod and install numpy
source artifacts/day01/ds-prod/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy
python -c "import numpy as np; print(np.__version__)"  # should succeed
```
Windows (PowerShell)
```
py -3.12 -m venv artifacts\day01\ds-play\.venv
if ($LASTEXITCODE -ne 0) { throw "ds-play environment creation failed" }
py -3.12 -m venv artifacts\day01\ds-prod\.venv
if ($LASTEXITCODE -ne 0) { throw "ds-prod environment creation failed" }

# ds-play
$playPython = ".\artifacts\day01\ds-play\.venv\Scripts\python.exe"
& $playPython -c "import importlib.util; raise SystemExit(importlib.util.find_spec('numpy') is not None)"
if ($LASTEXITCODE -eq 0) {
    Write-Host "numpy is not installed in ds-play (expected)"
} else {
    throw "numpy unexpectedly exists in ds-play"
}

# ds-prod
$prodPython = ".\artifacts\day01\ds-prod\.venv\Scripts\python.exe"
& $prodPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
& $prodPython -m pip install numpy
if ($LASTEXITCODE -ne 0) { throw "numpy installation failed" }
& $prodPython -c "import numpy as np; print(np.__version__)"
if ($LASTEXITCODE -ne 0) { throw "numpy import failed" }
```

Exercise 2: From the REPL, define a function `gcd(a, b)` (Euclid’s algorithm) and test.

Why: Practice using the REPL for quick feedback. Euclid’s algorithm is a classic example of simple, testable logic.

Code
```python
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

assert gcd(12, 18) == 6
assert gcd(17, 13) == 1
print("gcd tests passed")
```

Exercise 3: Add a kernel for each environment and practice switching in JupyterLab.

Why: Notebooks execute in a kernel process; binding the correct env avoids import errors.

macOS/Linux:
```bash
# In ds-play
artifacts/day01/ds-play/.venv/bin/python -m pip install ipykernel
artifacts/day01/ds-play/.venv/bin/python -m ipykernel install \
  --user --name ds-play --display-name "Python (ds-play)"

# In ds-prod
artifacts/day01/ds-prod/.venv/bin/python -m pip install ipykernel
artifacts/day01/ds-prod/.venv/bin/python -m ipykernel install \
  --user --name ds-prod --display-name "Python (ds-prod)"

# Launch JupyterLab and switch kernels from the Kernel menu
.venv/bin/python -m jupyterlab
```

Windows PowerShell:
```powershell
$playPython = ".\artifacts\day01\ds-play\.venv\Scripts\python.exe"
$prodPython = ".\artifacts\day01\ds-prod\.venv\Scripts\python.exe"

& $playPython -m pip install ipykernel
if ($LASTEXITCODE -ne 0) { throw "ds-play ipykernel installation failed" }
& $playPython -m ipykernel install --user --name ds-play --display-name "Python (ds-play)"
if ($LASTEXITCODE -ne 0) { throw "ds-play kernel registration failed" }

& $prodPython -m pip install ipykernel
if ($LASTEXITCODE -ne 0) { throw "ds-prod ipykernel installation failed" }
& $prodPython -m ipykernel install --user --name ds-prod --display-name "Python (ds-prod)"
if ($LASTEXITCODE -ne 0) { throw "ds-prod kernel registration failed" }

.\.venv\Scripts\python.exe -m jupyterlab
```

Notes
- These commands avoid activation so it is always clear which interpreter runs.
- The course setup already installs JupyterLab in the repository `.venv`.

---

## Expanded mastery lab solutions

Treat the interpreter, package installer, and notebook kernel as one connected system. Record evidence before changing an environment.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practice 1 — Prediction

The correct result is an executable inside this repository's `.venv`
(`.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on POSIX). The
exact prefix varies by clone location, so inspect the path rather than comparing
it with a developer-specific absolute string.

### Practice 2 — Trace

`python -m pip` asks a known interpreter to import its installed `pip` module.
A bare `pip` is whichever executable the shell finds first on `PATH`; it can
belong to Anaconda, the Windows launcher, or another environment.

### Practices 3–5 — Evidence-first environment diagnosis

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
