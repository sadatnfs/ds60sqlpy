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
