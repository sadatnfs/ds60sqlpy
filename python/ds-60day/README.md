# Python and data-science track

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Python and data science** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


This track preserves 60 ordered lessons covering practical Python, data
analysis, statistics, machine learning, and selected production topics.
Four named foundation checkpoints slow the early learning ramp, and thirteen
named professional modules extend practice beyond the numbered sequence.
Use the catalog's prerequisite order rather than treating 60 as a deadline.

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

Complete the foundation checkpoints after Days 1, 3, 8, and 10 before
continuing into their successor lessons. They add program tracing, evidence-led
debugging, trustworthy text-record cleaning, and a first auditable data project.
Their [guides and learner scripts](../professional/README.md) use the same
separate-solution workflow. They are deliberately smaller conceptual steps,
not additional package installation tasks.

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
- Named learner scripts, guides, executable solutions, and solution
  explanations: four foundation checkpoints and thirteen professional modules

Use `python scripts/course.py catalog --track python` rather than inferring that every solution format exists.

Learner notebooks and solutions are intentionally separate. Lessons vary in depth; repository validation checks structure, syntax, and a fast execution subset without treating file presence as proof of pedagogical completeness.

## Continue into professional Python

After the numbered track, or earlier when you meet a module's catalog
prerequisites, continue with the [professional learning paths](../../docs/professional-paths.md).
The extension covers package builds, reliable HTTP clients, concurrency,
Arrow/DuckDB, generative testing, advanced typing, experiments, reproducible
model delivery, service hardening, measurement-first performance, exact value
and time boundaries, leakage-resistant evaluation, and restartable pipelines.

Use stable lesson IDs rather than inventing Day 61 filenames:

```text
python scripts/course.py catalog --track python
python scripts/course.py progress complete python-pro-01
```

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

## Learn with the AI tutor

The repository-local tutor skill can guide the lesson without revealing answers immediately:

```text
Use $guide-ds60sqlpy-learning to guide Python Day 1. Check my setup, quiz prerequisites, and give hints before solutions.
```

See [Learning with an AI tutor](../../docs/learning-with-an-ai-tutor.md).

## Validate

```text
python scripts/course.py validate
```

Structural validation does not mean every notebook was fully executed. See [Validation](../../docs/validation.md) for the evidence labels and full workflow.

## Scope

This is a practical Python-for-data-science path, not a replacement for the complete Python language reference. The high-level sequence remains in [PYTHON_TRAINING.md](../PYTHON_TRAINING.md); `curriculum/catalog.json` is the checked-in generated artifact map, built from lesson filenames and catalog-builder metadata.

For help, see [Troubleshooting](../../docs/troubleshooting.md).
