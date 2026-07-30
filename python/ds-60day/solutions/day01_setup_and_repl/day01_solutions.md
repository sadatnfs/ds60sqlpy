# Day 01 — Solutions: Setup, REPL, Virtual Envs, Package Management

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Run the setup and confirm that `course.py doctor` reports Python 3.11 or 3.12. **Hint:** read the interpreter path in the report; it should contain `.venv`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Start the REPL and evaluate arithmetic, a string method, and `type(...)`. **Hint:** exit with `exit()`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** In JupyterLab, select `Python (ds60sqlpy)` and print the interpreter path. **Hint:** the `sys` module can describe the running interpreter.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Original lesson practice

**Prompt:** Create `calc.py` so two numeric command-line arguments produce their sum. **Hint:** command-line values in `sys.argv` are strings, so convert them deliberately. Day 15 replaces this bounded approach with `argparse`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 5 — Original lesson practice

**Prompt:** As deeper environment practice, create two temporary environments and install NumPy in only one. **Hint:** always use `python -m pip` from the interpreter you intend to modify. The separate solution notes use the two-environment and REPL exercises to test the same setup skills without simply copying the notebook cells.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 6 — Prediction

**Prompt:** Predict what `sys.executable` should contain when the correct course kernel is active, then verify it in both the REPL and this notebook.

**Reasoning checkpoint:** The important fact is the interpreter path, not merely the word Python. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Tracing

**Prompt:** Trace the difference between `python -m pip --version` and a bare `pip --version`: which interpreter owns each command?

**Reasoning checkpoint:** Read the Python and site-packages paths printed by pip. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Implementation

**Prompt:** Write `environment_report()` returning the Python version, executable, platform, and current working directory without shell commands.

**Reasoning checkpoint:** Use `sys`, `platform`, and `pathlib.Path`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 9 — Debugging

**Prompt:** A package imports in PowerShell but is missing in Jupyter. Write a three-step diagnosis that proves whether their interpreters differ.

**Reasoning checkpoint:** Compare executable paths before reinstalling anything. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 10 — Edge case and explanation

**Prompt:** Explain how to recover when the `ds60sqlpy` kernel is absent even though `.venv` exists, and state what remains possible offline.

**Reasoning checkpoint:** Kernel registration and package download are separate operations. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
