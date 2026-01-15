# 60-Day Intensive Python for Data Science

This folder contains a complete, beginner-friendly curriculum in Jupyter notebooks that follows the 60-day lesson plan in python/PYTHON_TRAINING.md.

How to use

1) Create and activate a virtual environment (recommended)
- macOS/Linux:
  - python3 -m venv .venv
  - source .venv/bin/activate
- Windows (PowerShell):
  - py -3 -m venv .venv
  - .venv\Scripts\Activate.ps1

2) Install requirements
- pip install -r requirements.txt

3) Launch Jupyter
- jupyter lab
  - or: jupyter notebook

4) Open notebooks
- Navigate to notebooks/day01_setup_and_repl.ipynb and work day-by-day.
- Each notebook has: objectives, theory, step-by-step examples, exercises, solutions, and a daily checklist.

Conventions
- Notebooks are safe to run in order; some days refer to small sample datasets loaded via seaborn, sklearn, or generated on the fly.
- Cells marked "Exercise" contain TODOs and hints. Solutions are provided in dedicated cells below each exercise.
- Where meaningful, we use type hints, docstrings, logging, and tests (pytest-style) inside notebooks.

Structure
- requirements.txt — packages for the entire 60-day track
- notebooks/
  - day01_setup_and_repl.ipynb
  - day02_basics_types.ipynb
  - ... up to day60_capstone_presentation.ipynb

Tips
- Keep a daily journal (markdown cell at the end of each notebook)
- If you are brand new to Python, spend extra time on Days 1–7
- Use black/flake8/mypy suggested on Day 14—config samples are included inline in that day’s notebook

Troubleshooting
- If jupyter: command not found, install Jupyter with: pip install jupyterlab
- If kernels don’t show, install ipykernel: python -m ipykernel install --user --name=python3
- If plots don’t render in some environments, ensure %matplotlib inline is present or use JupyterLab 3+
