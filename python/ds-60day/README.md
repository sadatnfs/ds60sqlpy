# Python and data-science track

This track contains 60 ordered lessons covering practical Python, data analysis, statistics, machine learning, and selected production topics. The number is a sequence, not a deadline.

Start at the repository [README](../../README.md), and run all commands from the repository root.

## Set up

Use the guide for your operating system:

- [Windows](../../docs/setup/windows.md)
- [macOS](../../docs/setup/macos.md)
- [Linux](../../docs/setup/linux.md)

The recommended baseline is Python 3.12.

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\course.py doctor
```

macOS/Linux:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
```

Core setup installs the notebook, data, and quality groups. To prepare the later heavy lessons while connected:

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

macOS/Linux:

```bash
bash scripts/setup.sh --advanced
```

Inspect lesson dependencies and first-run downloads before installing everything:

```text
python scripts/course.py catalog --track python
```

## Study a lesson

For each lesson:

1. Read the matching file under [companion-guides](companion-guides/README.md).
2. Open the learner notebook under `notebooks/`.
3. Predict and run the examples.
4. Attempt the exercises.
5. Check the separate solution only after an honest attempt.

Start with:

- [Day 1 guide](companion-guides/day01_setup_and_repl.md)
- [Day 1 notebook](notebooks/day01_setup_and_repl.ipynb)
- [Day 1 solution](solutions/day01_setup_and_repl/day01_solutions.md)

Launch JupyterLab:

Windows:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab .\python\ds-60day\notebooks
```

macOS/Linux:

```bash
.venv/bin/python -m jupyterlab python/ds-60day/notebooks
```

You can also open notebooks directly in VS Code. Select the repository `.venv` as both interpreter and notebook kernel; see [VS Code](../../docs/vscode.md).

## Artifact coverage

- Learner notebooks: Days 1–60
- Companion guides: Days 1–60
- Markdown solutions: Days 1–60
- Runnable solution notebooks: Days 1–60

Use `python scripts/course.py catalog --track python` rather than inferring that every solution format exists.

Learner notebooks and solutions are intentionally separate. Lessons vary in depth; repository validation checks structure, syntax, and a fast execution subset without treating file presence as proof of pedagogical completeness.

## Offline behavior

Most lessons use generated or local data. Several data-analysis lessons call Seaborn’s sample-data loader; the first call downloads and caches the dataset. Pretrained torchvision, Hugging Face, and spaCy exercises require a disclosed cache or their lesson’s offline fallback.

Prepare while connected and read [Offline use](../../docs/setup/offline.md). A package being installed does not guarantee that its model weights or dataset are cached.

## Progress

Local progress is stored under the ignored `.learning/` directory:

```text
python scripts/course.py progress show
python scripts/course.py progress complete python-01 --notes "Created the environment and explained kernels."
```

Use the stable lesson IDs printed by the catalog.

## Connect Python with PostgreSQL

After Python Day 15 and SQL Day 15, the optional
[engineering bridge](../../bridge/README.md) adds typed configuration, safe
Psycopg queries, transaction and retry design, database testing, ETL,
concurrency, and production failure handling.

## Learn with Codex

The repository-local tutor skill can guide the lesson without revealing answers immediately:

```text
Use $guide-ds60sqlpy-learning to guide Python Day 1. Check my setup, quiz prerequisites, and give hints before solutions.
```

See [Learning with Codex](../../docs/learning-with-codex.md).

## Validate

```text
python scripts/course.py validate
```

Structural validation does not mean every notebook was fully executed. See [Validation](../../docs/validation.md) for the evidence labels and full workflow.

## Scope

This is a practical Python-for-data-science path, not a replacement for the complete Python language reference. The high-level sequence remains in [PYTHON_TRAINING.md](../PYTHON_TRAINING.md); `curriculum/catalog.json` is the checked-in generated artifact map, built from lesson filenames and catalog-builder metadata.

For help, see [Troubleshooting](../../docs/troubleshooting.md).
