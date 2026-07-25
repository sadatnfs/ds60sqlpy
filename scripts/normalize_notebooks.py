#!/usr/bin/env python3
"""Normalize and repair every Python-course Jupyter notebook.

The migration is deterministic and idempotent: it repairs the historical Day 55
JSON defect, applies documented compatibility repairs, assigns stable cell IDs,
clears outputs, and writes uniform nbformat 4.5 metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Final

import nbformat
from nbformat import NotebookNode

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
COURSE_ROOT_RELATIVE: Final = Path("python") / "ds-60day"
DAY_PATTERN: Final = re.compile(r"day(?P<day>\d{2})_")

DAY55_BROKEN_PAYLOAD: Final = """-d '{"features": [5.1, 3.5, 1.4, 0.2]}'"""
DAY55_REPAIRED_PAYLOAD: Final = """-d '{\\"features\\": [5.1, 3.5, 1.4, 0.2]}'"""

SOURCE_REPLACEMENTS: Final[dict[str, tuple[tuple[str, str], ...]]] = {
    "python/ds-60day/notebooks/day01_setup_and_repl.ipynb": (
        (
            "- Install Python 3.10+ and Jupyter.\n- Create and activate a virtual environment.",
            "- Install the supported Python 3.11-3.12 environment "
            "(3.12 recommended) and Jupyter.\n"
            "- Create and use a repository-local virtual environment.",
        ),
        (
            "## 1) Creating a virtual environment (reference)\n\n"
            "macOS/Linux:\n"
            "```bash\n"
            "python3 -m venv .venv\n"
            "source .venv/bin/activate\n"
            "python -V\n"
            "```\n"
            "Windows (PowerShell):\n"
            "```ps1\n"
            "py -3 -m venv .venv\n"
            ".venv\\Scripts\\Activate.ps1\n"
            "python -V\n"
            "```\n"
            "Install core tools:\n"
            "```bash\n"
            "pip install --upgrade pip\n"
            "pip install jupyterlab ipykernel\n"
            "python -m ipykernel install --user --name=python3\n"
            "```\n"
            "Launch Jupyter Lab:\n"
            "```bash\n"
            "jupyter lab\n"
            "```",
            "## 1) Create the course environment from the repository root\n\n"
            "Windows PowerShell:\n"
            "```powershell\n"
            "powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1\n"
            ".\\.venv\\Scripts\\python.exe scripts\\course.py doctor\n"
            "```\n"
            "macOS/Linux:\n"
            "```bash\n"
            "bash scripts/setup.sh\n"
            ".venv/bin/python scripts/course.py doctor\n"
            "```\n\n"
            "Activation is optional. In VS Code, select the interpreter inside "
            "`.venv` as both the Python interpreter and notebook kernel.",
        ),
        (
            "- Use pip to install packages.",
            "- Use the repository interpreter to inspect installed packages.",
        ),
        (
            "At the end of this notebook you will be able to create a clean "
            "environment, install dependencies, and run code in Jupyter.",
            "At the end of this notebook you will be able to create a clean "
            "environment, identify its interpreter, and run code in Jupyter.\n\n"
            "A brand-new machine needs a connection for tools and packages. The "
            "lesson itself runs offline after that documented bootstrap.",
        ),
        (
            "## 2) Python REPL basics\n"
            "Type `python` or `python3` in your terminal to open an interactive "
            "shell (REPL). Try some math and string operations.",
            "## 2) Python REPL basics\n"
            "A REPL is an interactive Python prompt. Start the interpreter that "
            "belongs to this repository:\n\n"
            "Windows PowerShell:\n"
            "```powershell\n"
            ".\\.venv\\Scripts\\python.exe\n"
            "```\n"
            "macOS/Linux:\n"
            "```bash\n"
            ".venv/bin/python\n"
            "```\n"
            "At the `>>>` prompt, try the expressions below. Enter `exit()` when "
            "you are finished.",
        ),
        (
            "Run it with `python hello.py`.\n\n"
            "Below we reproduce similar logic in this notebook cell.",
            "Run it with the repository interpreter:\n\n"
            "Windows PowerShell:\n"
            "```powershell\n"
            ".\\.venv\\Scripts\\python.exe hello.py\n"
            "```\n"
            "macOS/Linux:\n"
            "```bash\n"
            ".venv/bin/python hello.py\n"
            "```\n\n"
            "Below we reproduce similar logic in this notebook cell.",
        ),
        (
            "## 4) Installing a package with pip\n"
            "Use pip to install packages into your active environment:\n"
            "```bash\n"
            "pip install numpy pandas\n"
            "```\n"
            "Then you can import them below.",
            "## 4) Inspecting packages in the course environment\n"
            "The setup script already installed NumPy and pandas. Verify them "
            "through the same interpreter instead of using a bare `pip` command:\n\n"
            "Windows PowerShell:\n"
            "```powershell\n"
            ".\\.venv\\Scripts\\python.exe -m pip show numpy pandas\n"
            "```\n"
            "macOS/Linux:\n"
            "```bash\n"
            ".venv/bin/python -m pip show numpy pandas\n"
            "```\n"
            "Maintainers add course dependencies to `pyproject.toml`; learners "
            "normally rerun the setup script rather than installing ad hoc packages.",
        ),
        (
            "import sys, platform\n"
            "print(sys.version)\n"
            "print(platform.platform())\n"
            "\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "np.array([1,2,3])",
            "import platform\n"
            "import sys\n"
            "\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "\n"
            "print(sys.executable)\n"
            "print(sys.version)\n"
            "print(platform.platform())\n"
            "print(pd.__version__)\n"
            "np.array([1, 2, 3])",
        ),
        (
            "def greet(name: str) -> str:\n"
            '    """Return a friendly greeting.\n'
            "    Args:\n"
            "        name: Person's name.\n"
            "    \n"
            "    Returns: greeting string.\n"
            '    """\n'
            "    return f'Hello, {name}!'\n"
            "\n"
            "greet('Data Scientist')",
            "def greet(name: str) -> str:\n"
            '    """Return a friendly greeting for ``name``."""\n'
            "\n"
            '    return f"Hello, {name}!"\n'
            "\n"
            "\n"
            'greet("Data Scientist")',
        ),
        (
            "## Exercises\n"
            "1. Create and activate a virtual environment locally.\n"
            "2. Install `jupyterlab`, `ipykernel`.\n"
            "3. Create a new kernel named `python3` (done by this notebook if you "
            "ran the command).\n"
            "4. Write a script `calc.py` that takes two numbers and prints their sum.\n"
            "\n"
            "## Solutions (sample)\n"
            "See code cells above for references to structure functions and REPL usage.",
            "## Exercises\n"
            "1. Run the setup command for your operating system and explain what "
            "`.venv` isolates.\n"
            "2. In VS Code, select the `.venv` interpreter and notebook kernel. "
            "The setup script registers the `Python (ds60sqlpy)` kernel.\n"
            "3. Start the REPL with the exact `.venv` interpreter path and print "
            "`sys.executable`.\n"
            "4. Write `calc.py` so two numeric command-line arguments produce their sum.\n"
            "\n"
            "## Progressive hints\n"
            "1. First verify that `sys.executable` points inside this repository's `.venv`.\n"
            "2. Command-line values arrive as strings; convert them deliberately.\n"
            "3. Use `sys.argv` for this first bounded exercise; Day 15 introduces "
            "`argparse` for a complete CLI.\n"
            "\n"
            "Keep the implementation in your own file. Open the separate solution "
            "only after an honest attempt.",
        ),
    ),
    "python/ds-60day/notebooks/day08_files_json_csv_context.ipynb": (
        (
            "import json, csv\nfrom pathlib import Path\np = Path('data') / 'people.json'",
            "import csv\nimport json\nfrom pathlib import Path\n\n"
            "data_dir = Path('data')\n"
            "data_dir.mkdir(parents=True, exist_ok=True)\n"
            "p = data_dir / 'people.json'",
        ),
        ("with p.open('w') as f:", "with p.open('w', encoding='utf-8') as f:"),
        ("with p.open() as f:", "with p.open(encoding='utf-8') as f:"),
        ("p2 = Path('data') / 'people.csv'", "p2 = data_dir / 'people.csv'"),
        (
            "with p2.open('w', newline='') as f:",
            "with p2.open('w', encoding='utf-8', newline='') as f:",
        ),
        (
            "p2.read_text().splitlines()[:3]",
            "p2.read_text(encoding='utf-8').splitlines()[:3]",
        ),
    ),
    "python/ds-60day/notebooks/day14_code_quality_tooling.ipynb": (
        (
            "# Day 14 — Code quality: black, flake8, mypy\n"
            "Objectives:\n"
            "- Auto-format with black.\n"
            "- Lint with flake8.\n"
            "- Type-check with mypy.\n"
            "Includes sample configs and commands.",
            "# Day 14 — Code quality with Ruff and mypy\n"
            "Objectives:\n"
            "- Use Ruff to find correctness, import, and style problems.\n"
            "- Use Ruff's formatter to keep layout consistent.\n"
            "- Use mypy to check type contracts before runtime.\n"
            "- Distinguish formatting, linting, type checking, and tests.",
        ),
        (
            "## Sample pyproject.toml\n"
            "```toml\n"
            "[tool.black]\n"
            "line-length = 88\n"
            "target-version = ['py310']\n"
            "\n"
            "[tool.flake8]\n"
            "max-line-length = 88\n"
            "extend-ignore = ['E203']\n"
            "```\n"
            "Run:\n"
            "```bash\n"
            "black .\n"
            "flake8 .\n"
            "mypy .\n"
            "```\n",
            "## Sample `pyproject.toml`\n"
            "```toml\n"
            "[tool.ruff]\n"
            "target-version = 'py311'\n"
            "line-length = 100\n"
            "\n"
            "[tool.ruff.lint]\n"
            "select = ['E', 'F', 'I', 'UP', 'B']\n"
            "\n"
            "[tool.mypy]\n"
            "python_version = '3.11'\n"
            "strict = true\n"
            "```\n"
            "Run from the project root:\n"
            "```text\n"
            "python -m ruff check .\n"
            "python -m ruff format --check .\n"
            "python -m mypy .\n"
            "```\n"
            "A formatter changes layout; a linter finds suspicious code; a type "
            "checker verifies annotated contracts. None replaces tests.",
        ),
        (
            "## Exercise\n"
            "Apply black/flake8/mypy to your utilities from earlier days and fix issues.",
            "## Exercise\n"
            "Run Ruff and mypy on utilities from earlier days. First predict each "
            "warning, then make the smallest behavior-preserving fix. Finish by "
            "running the tests so a clean tool report is not mistaken for correct behavior.",
        ),
    ),
    "python/ds-60day/notebooks/day15_cli_project.ipynb": (
        (
            "- Pass black/flake8/mypy.",
            "- Pass Ruff lint and format checks, mypy, and pytest.",
        ),
        (
            "- Use argparse or click for CLI.",
            "- Use the standard-library `argparse` module for the CLI.",
        ),
    ),
    "python/ds-60day/notebooks/day21_time_series_pandas.ipynb": (
        ("ts.resample('M')", "ts.resample('ME')"),
    ),
    "python/ds-60day/notebooks/day27_geospatial_or_domain_viz.ipynb": (
        (
            "# Example (commented if geopandas not installed)\n"
            "# import geopandas as gpd\n"
            "# world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))\n"
            "# world.plot(figsize=(8,6))\n"
            "# \n"
            "# Alternative: Domain viz placeholder\n"
            "print('Install geopandas for geospatial demo, or implement "
            "domain-specific chart here.')",
            "# This optional example downloads and caches Natural Earth data on first use.\n"
            "try:\n"
            "    import geopandas as gpd\n"
            "    from geodatasets import get_path\n"
            "\n"
            "    world = gpd.read_file(get_path('naturalearth.land'))\n"
            "    world.plot(figsize=(8, 6), edgecolor='black')\n"
            "except ImportError:\n"
            "    print('Install the geo dependency group to run this optional example.')",
        ),
    ),
    "python/ds-60day/notebooks/day29_data_validation_schemas.ipynb": (
        ("import pandera as pa", "import pandera.pandas as pa"),
        ("pa.SchemaModel", "pa.DataFrameModel"),
    ),
    "python/ds-60day/notebooks/day43_model_interpretation_shap_pdp.ipynb": (
        (
            "shap_values = explainer.shap_values(Xte[:200])\n"
            "# Summary plot (may open a window in some envs)\n"
            "shap.summary_plot(shap_values[1], Xte[:200], show=False)",
            "X_sample = Xte[:200]\n"
            "shap_values = explainer.shap_values(X_sample)\n"
            "# SHAP <0.45 returned a list per class; newer SHAP returns a 3-D array.\n"
            "if isinstance(shap_values, list):\n"
            "    positive_class_values = shap_values[1]\n"
            "elif shap_values.ndim == 3:\n"
            "    positive_class_values = shap_values[:, :, 1]\n"
            "else:\n"
            "    positive_class_values = shap_values\n"
            "shap.summary_plot(positive_class_values, X_sample, show=False)",
        ),
    ),
    "python/ds-60day/notebooks/day50_time_series_modeling.ipynb": (
        (
            "# Day 50 — Time series modeling: ARIMA/Prophet/LSTM overview\n"
            "Objectives:\n"
            "- Stationarity and differencing.\n"
            "- Fit a simple ARIMA with pmdarima.\n"
            "- Prophet/LSTM overview (when to use).\n"
            "Note: Prophet and deep nets require additional installs; we'll demo "
            "ARIMA with pmdarima.",
            "# Day 50 — Time-series modeling and forecast evaluation\n"
            "Objectives:\n"
            "- Split time-ordered data without future leakage.\n"
            "- Fit a small ARIMA model with pmdarima.\n"
            "- Compare it with a naive forecast using the same horizon and metric.\n"
            "- Treat more complex forecasting families as hypotheses to validate, "
            "not automatic upgrades.",
        ),
        (
            "## Prophet (overview)\n"
            "- pip install prophet\n"
            "- Works well with multiple seasonality/holidays; additive model.\n"
            "## LSTM (overview)\n"
            "- Sequence models for complex patterns, but heavier and data-hungry.\n"
            "- Use when nonlinear dependencies and long memory present.\n"
            "\n"
            "## Exercises\n"
            "1) Try different seasonality (m=7, m=30) and compare MAE.\n"
            "2) Difference the series manually and visualize autocorrelation (acf/pacf).\n"
            "3) (Optional) Install prophet and fit a baseline forecast.",
            "## Model choice and baselines\n"
            "Seasonal additive models, tree models with lag features, and neural "
            "sequence models can all be useful in the right setting. They also add "
            "assumptions and operational cost. Compare every candidate against a "
            "simple last-value or seasonal-naive forecast on a forward time split.\n"
            "\n"
            "## Exercises\n"
            "1) Try `m=7` and `m=30`; compare mean absolute error on the same test window.\n"
            "2) Create a last-value and a 30-day seasonal-naive forecast, then compare "
            "both with ARIMA.\n"
            "3) Difference the training series and inspect autocorrelation without "
            "using test-period observations.",
        ),
    ),
    "python/ds-60day/notebooks/day52_scalability_dask.ipynb": (
        (
            "df = dd.demo.make_timeseries('2000','2001', freq='1s', "
            "dtypes={'name':str,'id':int,'x':float,'y':float}, partition_freq='1M')",
            "df = dd.demo.make_timeseries(\n"
            "    start='2000-01-01',\n"
            "    end='2000-02-01',\n"
            "    freq='1min',\n"
            "    dtypes={'name': str, 'id': int, 'x': float, 'y': float},\n"
            "    partition_freq='7D',\n"
            ")",
        ),
        (
            "df.npartitions, df = df.repartition(npartitions=8)\ndf = df.persist()\ndf.npartitions",
            "before = df.npartitions\n"
            "df = df.repartition(npartitions=4)\n"
            "# This small demo is safe to persist; do not persist data larger than memory.\n"
            "df = df.persist()\n"
            "before, df.npartitions",
        ),
    ),
    "python/ds-60day/notebooks/day55_apis_containerization_docker.ipynb": (
        ("FROM python:3.11-slim", "FROM python:3.12-slim"),
        (
            "RUN pip install --no-cache-dir -r requirements-api.txt",
            "RUN python -m pip install --no-cache-dir -r requirements-api.txt",
        ),
        (
            "  -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'\n```\n",
            "  -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'\n"
            "```\n"
            "PowerShell:\n"
            "```powershell\n"
            "$body = @{ features = @(5.1, 3.5, 1.4, 0.2) } | ConvertTo-Json\n"
            "Invoke-RestMethod -Method Post -Uri "
            "'http://127.0.0.1:8000/predict' "
            "-ContentType 'application/json' -Body $body\n"
            "```\n",
        ),
    ),
    "python/ds-60day/notebooks/day58_code_review_refactor_tests.ipynb": (
        (
            "- Style & linting: black, flake8, mypy\n"
            "- Tests pass: pytest\n"
            "- Reproducibility: pinned requirements, deterministic seeds",
            "- Style and linting: Ruff; type contracts: mypy\n"
            "- Tests pass: pytest\n"
            "- Reproducibility: reviewed lock file, deterministic seeds",
        ),
        (
            "import pytest, pandas as pd, seaborn as sns\n"
            "from src.model import train_evaluate\n"
            "def test_train_evaluate_runs():\n"
            "    df = sns.load_dataset('titanic').dropna("
            "subset=['survived','sex','class','fare','age'])\n"
            "    res = train_evaluate(df)\n"
            "    assert 0.5 <= res.auc <= 1.0",
            "import pandas as pd\n"
            "from src.model import train_evaluate\n\n"
            "def test_train_evaluate_runs():\n"
            "    df = pd.DataFrame([\n"
            "        {\n"
            "            'survived': i % 2,\n"
            "            'sex': 'female' if i % 2 else 'male',\n"
            "            'class': ('First', 'Second', 'Third')[i % 3],\n"
            "            'fare': 20.0 + i,\n"
            "            'age': 18.0 + (i % 30),\n"
            "        }\n"
            "        for i in range(40)\n"
            "    ])\n"
            "    res = train_evaluate(df)\n"
            "    assert 0.5 <= res.auc <= 1.0",
        ),
    ),
    "python/ds-60day/notebooks/day60_capstone_completion_presentation.ipynb": (
        (
            "- [ ] Saved artifacts (`models/`) and `requirements.txt`.",
            "- [ ] Saved artifacts under `artifacts/`, plus `pyproject.toml` "
            "and a reviewed dependency lock.",
        ),
        (
            "## Reproducibility instructions\n"
            "- Create venv and install requirements.\n"
            "- Run training with provided script/notebook.\n"
            "- Evaluate and reproduce plots.\n"
            "- (Optional) Launch API container with Dockerfile.\n\n"
            "Example:\n"
            "```bash\n"
            "python3 -m venv .venv && source .venv/bin/activate\n"
            "pip install -r requirements.txt\n"
            "python -m src.data.load   # or notebooks/EDA.ipynb\n"
            "python -m src.model.train # or notebooks/train.ipynb\n"
            "python -m src.model.eval  # or notebooks/evaluate.ipynb\n"
            "```\n\n"
            "## Congratulations!\n"
            "Wrap up your learnings: write 3 takeaways and 1 open question below.",
            "## Reproducibility instructions\n"
            "- Create a virtual environment with the documented OS command.\n"
            "- Install the project from `pyproject.toml` and its lock.\n"
            "- Run training, evaluation, and plots from explicit modules.\n"
            "- (Optional) launch the API container from its Dockerfile.\n\n"
            "Windows PowerShell:\n"
            "```powershell\n"
            "py -3.12 -m venv .venv\n"
            ".\\.venv\\Scripts\\python.exe -m pip install -e .\n"
            ".\\.venv\\Scripts\\python.exe -m src.data.load\n"
            ".\\.venv\\Scripts\\python.exe -m src.model.train\n"
            ".\\.venv\\Scripts\\python.exe -m src.model.eval\n"
            "```\n"
            "macOS/Linux:\n"
            "```bash\n"
            "python3.12 -m venv .venv\n"
            ".venv/bin/python -m pip install -e .\n"
            ".venv/bin/python -m src.data.load\n"
            ".venv/bin/python -m src.model.train\n"
            ".venv/bin/python -m src.model.eval\n"
            "```\n\n"
            "## Congratulations!\n"
            "Wrap up your learnings: write 3 takeaways and 1 open question below.",
        ),
    ),
    "python/ds-60day/solutions/day18_pandas_io_cleaning/day18_solutions.ipynb": (
        ("mode.iat(0)", "mode.iat[0]"),
    ),
    "python/ds-60day/solutions/day14_code_quality_tooling/day14_solutions.ipynb": (
        (
            "# Day 14 — Solutions: Code Quality\n"
            "Demonstration of an improved loader with explicit types and safe file handling.",
            "# Day 14 — Solutions: Code Quality with Ruff and mypy\n"
            "This improved loader addresses lint, type-contract, and resource-safety "
            "concerns. Tests are still required to verify behavior.",
        ),
        (
            "from pathlib import Path\n"
            "from typing import Any\n"
            "import json\n"
            "\n"
            "def load(path: str | Path) -> Any:\n"
            "    p = Path(path)\n"
            "    with p.open(encoding='utf-8') as f:\n"
            "        return json.load(f)\n"
            "\n"
            "# This cell illustrates code improved per black/flake8/mypy guidance "
            "from the Markdown file.",
            "import json\n"
            "from pathlib import Path\n"
            "from typing import Any\n"
            "\n"
            "\n"
            "def load(path: str | Path) -> Any:\n"
            "    p = Path(path)\n"
            '    with p.open(encoding="utf-8") as file_handle:\n'
            "        return json.load(file_handle)\n"
            "\n"
            "\n"
            "# Ruff checks imports and suspicious code; mypy checks the annotated contract.",
        ),
    ),
    "python/ds-60day/solutions/day21_time_series_pandas/day21_solutions.ipynb": (
        ("resample('H')", "resample('h')"),
    ),
    "python/ds-60day/solutions/day24_eda_best_practices/day24_solutions.ipynb": (
        ("df.describe(numeric_only=True)", "df.describe(include='number')"),
    ),
    "python/ds-60day/solutions/day27_geospatial_or_domain_viz/day27_solutions.ipynb": (
        (
            "# GeoPandas track (requires geopandas, contextily)\n"
            "# import geopandas as gpd, contextily as cx\n"
            "# world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')).to_crs(3857)",
            "# GeoPandas track (requires geopandas, contextily, geodatasets)\n"
            "# import contextily as cx\n"
            "# import geopandas as gpd\n"
            "# from geodatasets import get_path\n"
            "# world = gpd.read_file(get_path('naturalearth.land')).to_crs(3857)",
        ),
    ),
    "python/ds-60day/solutions/day29_data_validation_schemas/day29_solutions.ipynb": (
        ("import pandera as pa", "import pandera.pandas as pa"),
        ("pa.SchemaModel", "pa.DataFrameModel"),
    ),
    "python/ds-60day/solutions/day30_project_eda_preprocessing/day30_solutions.ipynb": (
        ("import pandera as pa", "import pandera.pandas as pa"),
        ("pa.SchemaModel", "pa.DataFrameModel"),
    ),
    "python/ds-60day/solutions/day43_model_interpretation_shap_pdp/day43_solutions.ipynb": (
        (
            "shap_values = shap_explainer.shap_values(X_sample)\n"
            "shap.summary_plot(shap_values[1], X_sample, show=False)",
            "shap_values = shap_explainer.shap_values(X_sample)\n"
            "if isinstance(shap_values, list):\n"
            "    positive_class_values = shap_values[1]\n"
            "elif shap_values.ndim == 3:\n"
            "    positive_class_values = shap_values[:, :, 1]\n"
            "else:\n"
            "    positive_class_values = shap_values\n"
            "shap.summary_plot(positive_class_values, X_sample, show=False)",
        ),
    ),
    "python/ds-60day/solutions/day44_model_deployment_fastapi/day44_solutions.ipynb": (
        (
            "from pydantic import BaseModel, conlist",
            "from typing import Annotated\n\nfrom pydantic import BaseModel, Field",
        ),
        (
            "features: conlist(float, min_items=4, max_items=4)",
            "features: Annotated[list[float], Field(min_length=4, max_length=4)]",
        ),
    ),
    "python/ds-60day/solutions/day51_advanced_feature_engineering_target_encoding/"
    "day51_solutions.ipynb": (("freq='H'", "freq='h'"),),
}


def _stable_cell_id(relative_path: Path, index: int, cell_type: str) -> str:
    identity = f"{relative_path.as_posix()}:{index}:{cell_type}".encode()
    return f"ds60-{hashlib.sha256(identity).hexdigest()[:16]}"


def _repair_raw_json(path: Path, raw: str) -> tuple[str, bool]:
    if path.name != "day55_apis_containerization_docker.ipynb":
        return raw, False
    if DAY55_BROKEN_PAYLOAD not in raw:
        return raw, False
    return raw.replace(DAY55_BROKEN_PAYLOAD, DAY55_REPAIRED_PAYLOAD), True


def _load_notebook(path: Path) -> tuple[NotebookNode, bool]:
    raw = path.read_text(encoding="utf-8")
    try:
        notebook = nbformat.reads(raw, as_version=4)  # type: ignore[no-untyped-call]
        repaired = False
    except (json.JSONDecodeError, nbformat.reader.NotJSONError):
        raw, repaired = _repair_raw_json(path, raw)
        notebook = nbformat.reads(raw, as_version=4)  # type: ignore[no-untyped-call]
    return notebook, repaired


def _day_and_artifact(path: Path) -> tuple[int, str]:
    match = DAY_PATTERN.search(path.name)
    if match is None:
        raise ValueError(f"Cannot determine course day from {path}")
    artifact = "solution" if "solutions" in path.parts else "learner"
    return int(match.group("day")), artifact


def _apply_source_repairs(
    notebook: NotebookNode,
    relative_path: Path,
) -> int:
    replacements = SOURCE_REPLACEMENTS.get(relative_path.as_posix(), ())
    applied = 0
    for cell in notebook.cells:
        source = str(cell.get("source", ""))
        for old, new in replacements:
            if old in source and new not in source:
                source = source.replace(old, new)
                applied += 1
        cell.source = source
    return applied


def _inferred_tags(day: int, source: str) -> set[str]:
    lowered = source.lower()
    tags: set[str] = set()
    if any(marker in lowered for marker in ("geopandas", "geodatasets", "contextily")):
        tags.update({"geo", "network"})
    if any(
        marker in lowered
        for marker in (
            "from_pretrained(",
            "load_dataset(",
            "pipeline('sentiment-analysis",
            'pipeline("sentiment-analysis',
            "resnet18(weights=",
            "sns.load_dataset(",
            "add_basemap(",
        )
    ):
        tags.add("network")
    if day in {43, 48, 49, 52} and source.strip():
        tags.add("slow")
    if day in {48, 49} and source.strip():
        tags.add("gpu")
    if day == 55 and any(marker in lowered for marker in ("docker", "curl", "container")):
        tags.add("docker")
    return tags


def normalize_notebook(
    notebook: NotebookNode,
    *,
    relative_path: Path,
) -> tuple[NotebookNode, int]:
    day, artifact = _day_and_artifact(relative_path)
    source_repairs = _apply_source_repairs(notebook, relative_path)
    notebook.nbformat = 4
    notebook.nbformat_minor = 5
    if "metadata" not in notebook:
        notebook.metadata = {}
    notebook.metadata["kernelspec"] = {
        "display_name": "Python (ds60sqlpy)",
        "language": "python",
        "name": "ds60sqlpy",
    }
    notebook.metadata["language_info"] = {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.12",
    }

    notebook_tags = {"python", f"day-{day:02d}", artifact}
    for index, cell in enumerate(notebook.cells):
        if "metadata" not in cell:
            cell.metadata = {}
        cell.id = _stable_cell_id(relative_path, index, str(cell.cell_type))
        tags = set(cell.metadata.get("tags", []))
        tags.update(_inferred_tags(day, str(cell.source)))
        if tags:
            cell.metadata["tags"] = sorted(tags)
            notebook_tags.update(tags)
        if cell.cell_type == "code":
            cell.execution_count = None
            cell.outputs = []

    notebook.metadata["course"] = {
        "artifact": artifact,
        "day": day,
        "lesson_id": f"python-{day:02d}",
        "tags": sorted(notebook_tags),
        "track": "python",
    }
    nbformat.validate(notebook)
    return notebook, source_repairs


def notebook_paths(repo_root: Path) -> Iterable[Path]:
    course_root = repo_root / COURSE_ROOT_RELATIVE
    return sorted(course_root.rglob("*.ipynb"))


def normalize_all(*, repo_root: Path, check: bool) -> tuple[int, int, int, int]:
    """Return ``(checked, changed, raw_repairs, source_repairs)``."""

    checked = changed = raw_repairs = source_repairs = 0
    for path in notebook_paths(repo_root):
        relative_path = path.relative_to(repo_root)
        raw_before = path.read_text(encoding="utf-8")
        notebook, repaired_raw = _load_notebook(path)
        notebook, applied = normalize_notebook(notebook, relative_path=relative_path)
        rendered = nbformat.writes(notebook, version=4)  # type: ignore[no-untyped-call]
        checked += 1
        raw_repairs += int(repaired_raw)
        source_repairs += applied
        if rendered == raw_before:
            continue
        changed += 1
        if not check:
            path.write_text(rendered, encoding="utf-8", newline="\n")

    return checked, changed, raw_repairs, source_repairs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report drift without modifying notebooks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checked, changed, raw_repairs, source_repairs = normalize_all(
        repo_root=args.repo_root.resolve(),
        check=args.check,
    )
    action = "would change" if args.check else "changed"
    print(
        f"Notebooks checked: {checked}; {action}: {changed}; "
        f"raw JSON repairs: {raw_repairs}; source repairs: {source_repairs}"
    )
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
