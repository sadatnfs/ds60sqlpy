# Day 1 — Python Setup, REPL, Virtual Envs, and Package Management (Companion Guide)

This guide provides the narrative context for the Day 1 notebook. Use it as a reading resource before and during the hands‑on sections.

## What you’ll learn
- Install Python 3.10+ and verify your installation
- Create and activate isolated environments with `venv`
- Use `pip` to manage packages and why upgrading `pip` first is wise
- Launch and use the Python REPL for quick experiments
- Install and launch JupyterLab; understand kernels

## Why this matters
Professional data science relies on reproducibility and isolation. Virtual environments ensure your project’s dependencies don’t conflict with system or other projects. A solid workflow today prevents hours of debugging in week 4.

## Concepts and mental models
- Environment isolation: Think of each project as a self‑contained lab bench. Mixing chemicals (packages) across benches is risky.
- REPL vs scripts vs notebooks: REPL is fast feedback; scripts are reproducible; notebooks are great for exploratory, narrative workflows.
- Kernels: Jupyter’s kernel is the interpreter process running your code. Match notebooks to the correct environment via kernels.

## Step‑by‑step workflow (recommended)
1) Check Python
   - macOS/Linux: `python3 --version`
   - Windows: `py -3 --version`
2) Create a project folder and environment
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```ps1
     py -3 -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
3) Upgrade `pip` and install core tools
   ```bash
   python -m pip install --upgrade pip
   pip install jupyterlab ipykernel
   python -m ipykernel install --user --name=python3
   ```
4) Launch Lab
   ```bash
   jupyter lab
   ```
5) Use the REPL when needed
   - Run `python` (or `python3`) in terminal for quick arithmetic, small function tests, and import checks.

## Common pitfalls and fixes
- “jupyter: command not found”: You installed Jupyter to a different environment. Activate the right venv and reinstall, or use the full path `python -m jupyterlab`.
- Kernel mismatch: If a notebook can’t find modules you installed, its kernel is likely bound to a different environment. In JupyterLab, change the kernel to your environment’s kernel (installed above as `python3`).
- Spaces and paths: On Windows, prefer PowerShell and avoid paths with spaces where possible.

## Exercises (beyond notebook)
1) Create two virtual environments: `ds‑play` and `ds‑prod`. Install `numpy` only in `ds‑prod`. Verify you can import `numpy` in that env and not the other.
2) From the REPL, define a function `gcd(a, b)` (Euclid’s algorithm) and test with several inputs.
3) Add a kernel for each environment and practice switching kernels in Jupyter.

## Stretch goals
- Install `pipx` and learn when it’s preferable to install CLI tools globally.
- Try `conda` or `uv` (if available) and compare UX to `venv`.

## Check your understanding
- Why do we use virtual environments? Name two practical benefits.
- What is a kernel, and why might a notebook fail to import a package even after you installed it?
- When would you use REPL vs a `.py` script vs a notebook?

## Further reading
- Python venv docs: https://docs.python.org/3/library/venv.html
- Packaging tutorial: https://packaging.python.org/en/latest/tutorials/installing-packages/
- JupyterLab docs: https://jupyterlab.readthedocs.io
