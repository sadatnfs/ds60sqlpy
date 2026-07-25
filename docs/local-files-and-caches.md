# Local environments, caches, and learner files

The repository contains the instructions and lock files needed to build an
environment. It does not ship another person's environment or machine caches.
Each learner creates local state on their own computer.

## What each local path means

| Path or asset | Needed? | Commit it? | Safe assumption |
| --- | --- | --- | --- |
| `.venv/` | Yes, for the normal local Python workflow | No | Created by the setup script for this clone; recreate it after a Python or dependency change |
| `__pycache__/`, `*.pyc` | No | No | Python bytecode cache; recreated automatically |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | No | No | Tool acceleration only; deleting it makes the next run slower, not different |
| `.ipynb_checkpoints/` | No | No | VS Code/Jupyter recovery state, not an official notebook |
| `.learning/` | Optional | No | Learner-owned progress, not a cache; deleting it loses recorded progress |
| `artifacts/` | Optional | No | Learner-generated models, reports, or outputs; inspect or back up before deleting |
| `mlruns/` | Optional | No | Local MLflow experiments created by Python Day 53; inspect or back up before deleting |
| `uv.lock` | Yes for reproducible validation | Yes | Maintained source artifact, not a cache; do not delete or hand-edit it |
| `.python-version` | Yes for version-manager defaults | Yes | Declares the canonical Python version |
| `.serena/project.yml`, `.serena/memories/` | Useful for Codex/Serena | Yes | Shared repository navigation and handoff guidance |
| `.serena/cache/`, `.serena/logs/`, `.serena/project.local.yml` | No | No | Machine-local Serena index, diagnostics, and overrides |
| `.DS_Store` | No | No | macOS Finder metadata |
| Docker `postgres-data` volume | Yes only for the container SQL environment | No | Local database state; `docker compose down` preserves it |

An ignored path is not automatically disposable. `.learning/`, `artifacts/`, `mlruns/`,
model caches, and a Docker volume can contain work or offline assets that the
learner wants to keep.

## Why `.venv` is local

A virtual environment contains absolute interpreter paths and
platform-specific executables. A macOS environment cannot be reused reliably
on Windows, and even two Windows machines may have different paths or binary
wheels. Committing it would make the repository much larger without producing
a portable installation.

Create it after cloning:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

```bash
bash scripts/setup.sh
```

VS Code should then select the interpreter inside that clone's `.venv`.

## User-level data and model caches

Seaborn sample data, Hugging Face models, and PyTorch weights are normally
cached outside the Git repository under the user's profile. These caches are
not required for source control, but they may be required to repeat a disclosed
first-download lesson offline. Keep them until offline study is complete.

A spaCy pipeline installed with `python -m spacy download en_core_web_sm` is a
package inside the selected `.venv`, not merely a durable user-profile cache.
Recreating `.venv` removes that installed pipeline, so reinstall it while
online before returning to the spaCy lesson.

See [Offline use](setup/offline.md) for preparation and typical locations.

## Check before cleanup

From the repository root:

```text
git status --short
git status --ignored --short
```

The first command shows source changes. The second also shows ignored local
state. Resolve the exact directory before deleting anything, close Jupyter and
Python processes first, and preserve learner progress or artifacts separately.

To reset only recorded course progress, use the guarded command:

```text
python scripts/course.py progress reset --yes
```

For the SQL container, `docker compose down` stops services and preserves the
named database volume. Removing the volume is a separate destructive action
and is not needed for normal study.
