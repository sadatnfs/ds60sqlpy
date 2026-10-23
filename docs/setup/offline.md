# Offline use

DS60 is designed for a one-time connected bootstrap followed by offline study. “Offline” describes lesson execution after tools, packages, and disclosed assets have been installed; it does not mean a brand-new computer can install Python, VS Code, PostgreSQL, container images, and packages without installation media.

## What works offline after setup

- Core Python and standard-library lessons
- Generated and repository-tracked data
- Datasets bundled with scikit-learn
- Local Jupyter and VS Code execution
- The PostgreSQL training schema after the server or container image is installed
- Bridge fake-backed exercises and tests; optional live checks work after the
  local PostgreSQL environment is prepared
- PostgreSQL notebook magics after the `sql-notebooks` profile and local
  database are installed; no remote notebook service is required
- Local plots, files, APIs, MLflow, and orchestration examples that do not opt into cloud services
- Tutor-independent course navigation and validation

## First-use downloads

Run these while connected before relying on the corresponding lessons offline:

| Asset | Used by | Offline behavior |
| --- | --- | --- |
| Seaborn sample datasets | Several data-analysis lessons | Accepted first-run download; Seaborn reuses its local cache afterward |
| Python packages and platform wheels | Course environment | Installed once by the setup script |
| PostgreSQL or PostgreSQL container image | SQL track | Runs locally after installation or image pull |
| JupySQL, pandas, SQLAlchemy, and Psycopg wheels | PostgreSQL notebook bridge | Installed by the default Core setup on every OS; queries stay local afterward |
| torchvision pretrained weights | Transfer-learning lesson | Must already be cached, or use the lesson’s non-pretrained fallback |
| Hugging Face model/tokenizer | NLP lesson | Must already be cached, or use the local fallback |
| spaCy language model | NLP lesson | Must be installed while connected, or use `spacy.blank(...)` where the lesson permits |

External “further reading” links are optional and do not form part of the offline execution contract.

## Prepare while connected

1. Run the OS setup script.
2. Run the environment doctor.
3. Inspect the catalog for optional network or heavy requirements.
4. Open and execute any accepted first-download lessons you plan to study.
5. Run repository validation.

Windows:

```powershell
# Recommended: double-click START_DS60.cmd and approve the connected setup.
# Manual equivalent:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
& $CoursePython scripts\course.py catalog
& $CoursePython scripts\course.py validate
```

macOS/Linux:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py catalog
.venv/bin/python scripts/course.py validate
```

Structural validation does not populate or verify every third-party cache. Test each planned network-tagged lesson once while connected, then repeat it disconnected; a missing cache must produce an actionable lesson error or use the documented fallback rather than silently fetching.

## Confirm offline readiness

Disconnect from the network or disable Wi-Fi and start a fresh terminal.

Windows:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
& $CoursePython scripts\course.py validate
```

macOS/Linux:

```bash
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py validate
```

Then open the planned lesson from a fresh notebook kernel. A cached lesson should not attempt a network request.

For Hugging Face tooling, these environment variables make accidental online fallback fail fast:

Windows PowerShell:

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
```

macOS/Linux:

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

These variables do not create a cache; they only require tools to use one.

## Cache notes

Common default locations include:

- Seaborn: `seaborn-data` under the user home directory
- Hugging Face: `.cache/huggingface` under the user home directory
- PyTorch: `.cache/torch` under the user home directory

Locations can vary by operating system and environment configuration. Do not commit machine caches to the repository.

Prepare the Seaborn datasets currently used by the historical lessons in a
scratch notebook while connected:

```python
import seaborn as sns

for name in ("tips", "titanic", "penguins"):
    frame = sns.load_dataset(name)
    print(name, frame.shape)
```

Expect three nonempty shapes. Then disconnect, restart the kernel, and repeat
the cell. A successful connected load alone does not prove the second run
avoids a network lookup. `HF_HUB_OFFLINE` only controls Hugging Face libraries;
it does not disable Seaborn, pip, Docker pulls, or arbitrary HTTP requests.
For downloaded model weights, exercise the exact model identifier and revision
that the lesson uses, or choose its documented local fallback.

## Fully disconnected installation

A completely offline fresh-machine installation requires a separately prepared bundle containing, at minimum:

- Python installer
- Git and VS Code installers
- Required VS Code `.vsix` files
- Platform- and Python-version-specific wheels
- PostgreSQL installer or exported container image
- Course datasets and permitted model assets
- Checksums and licenses

The Git repository alone is not that bundle. If you build one, generate it on a connected machine for a specific operating system, CPU architecture, and Python version, then install wheels with `--no-index --find-links`. Do not claim another platform is supported until that bundle is tested there.

## Optional package-only offline bundle

On a connected machine matching the target OS, CPU, and Python version, create
a course wheel and Core dependency wheels in an ignored folder:

```powershell
# Windows, after resolving $CoursePython as above
& $CoursePython -m pip wheel --wheel-dir artifacts\wheelhouse ".[notebooks,data,quality,bridge,professional,sql-notebooks]"
```

```bash
# macOS/Linux
.venv/bin/python -m pip wheel --wheel-dir artifacts/wheelhouse ".[notebooks,data,quality,bridge,professional,sql-notebooks]"
```

On the offline machine, install Python first, copy the repository and matching
wheelhouse, then create `.venv` and install the built course wheel:

```powershell
# Native Windows Python.org route
py -3.12 -m venv .venv
$CoursePython = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $CoursePython -m pip install --no-index --find-links artifacts\wheelhouse "ds60sqlpy[notebooks,data,quality,bridge,professional,sql-notebooks]"
& $CoursePython -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
& $CoursePython scripts\course.py doctor --no-database
```

```bash
# macOS/Linux; use python3.11 if that is the bundle's interpreter
python3.12 -m venv .venv
.venv/bin/python -m pip install --no-index --find-links artifacts/wheelhouse "ds60sqlpy[notebooks,data,quality,bridge,professional,sql-notebooks]"
.venv/bin/python -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
.venv/bin/python scripts/course.py doctor --no-database
```

Installing the wheel avoids an offline source build. Keep the repository and
installed package versions in sync. This is a package-only bundle, separate
from a standalone application: it omits Python, PostgreSQL, VS Code, extensions,
datasets, and models. Default setup scripts perform a connected installation;
they are not offline bundle installers. Verify the intended workflow on the
actual target OS before distributing it. See [pip wheel](https://pip.pypa.io/en/stable/cli/pip_wheel/)
and [installing local packages](https://pip.pypa.io/en/stable/user_guide/#installing-from-local-packages).

## Adding a lesson

New lesson code must not make a silent network call. Record its network classification in the catalog-builder metadata, regenerate `curriculum/catalog.json`, and choose one:

1. Track or generate the asset locally.
2. Accept a disclosed first-run cache and provide a local fallback.
3. Mark the entire exercise as optional enrichment.

See [Content authoring](../content-authoring.md).
