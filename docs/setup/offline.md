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
- Codex-independent course navigation and validation

## First-use downloads

Run these while connected before relying on the corresponding lessons offline:

| Asset | Used by | Offline behavior |
| --- | --- | --- |
| Seaborn sample datasets | Several data-analysis lessons | Accepted first-run download; Seaborn reuses its local cache afterward |
| Python packages and platform wheels | Course environment | Installed once by the setup script |
| PostgreSQL or PostgreSQL container image | SQL track | Runs locally after installation or image pull |
| JupySQL, pandas, SQLAlchemy, and Psycopg wheels | PostgreSQL notebook bridge | Installed by advanced setup; queries stay local afterward |
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
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\course.py doctor
.\.venv\Scripts\python.exe scripts\course.py catalog
.\.venv\Scripts\python.exe scripts\course.py validate
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
.\.venv\Scripts\python.exe scripts\course.py doctor
.\.venv\Scripts\python.exe scripts\course.py validate
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

## Adding a lesson

New lesson code must not make a silent network call. Record its network classification in the catalog-builder metadata, regenerate `curriculum/catalog.json`, and choose one:

1. Track or generate the asset locally.
2. Accept a disclosed first-run cache and provide a local fallback.
3. Mark the entire exercise as optional enrichment.

See [Content authoring](../content-authoring.md).
