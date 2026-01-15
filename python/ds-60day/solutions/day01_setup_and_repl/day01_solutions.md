# Day 01 — Solutions: Setup, REPL, Virtual Envs, Package Management

This solution expands each exercise with exact commands and the reasoning behind them.

Exercise 1: Create two virtual environments `ds-play` and `ds-prod`. Install `numpy` only in `ds-prod`. Verify import works only there.

Why: Isolate dependencies to avoid conflicts across projects. Verifying imports ensures the correct environment is active.

Commands (macOS/Linux)
```
python3 -m venv ds-play/.venv
python3 -m venv ds-prod/.venv

# Activate ds-play and verify numpy is not present
source ds-play/.venv/bin/activate
python -c "import sys; print(sys.executable)"  # sanity
python -c "import numpy" || echo "numpy not installed in ds-play (expected)"
deactivate

# Activate ds-prod and install numpy
source ds-prod/.venv/bin/activate
python -m pip install --upgrade pip
pip install numpy
python -c "import numpy as np; print(np.__version__)"  # should succeed
```
Windows (PowerShell)
```
py -3 -m venv ds-play/.venv
py -3 -m venv ds-prod/.venv

# ds-play
./ds-play/.venv/Scripts/Activate.ps1
python -c "import numpy" || echo "numpy not installed in ds-play (expected)"

# ds-prod
./ds-prod/.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
pip install numpy
python -c "import numpy as np; print(np.__version__)"
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

Commands
```
# In ds-play
source ds-play/.venv/bin/activate
python -m pip install ipykernel
python -m ipykernel install --user --name=ds-play --display-name "Python (ds-play)"

# In ds-prod
source ds-prod/.venv/bin/activate
python -m pip install ipykernel
python -m ipykernel install --user --name=ds-prod --display-name "Python (ds-prod)"

# Launch JupyterLab and switch kernels from the Kernel menu
jupyter lab
```

Notes
- If `jupyter` isn’t found, install with `pip install jupyterlab` in the target env.
- On Windows, use the Scripts paths and install ipykernel similarly.
