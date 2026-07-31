# DS60 Python, Data Science, SQL, and Engineering Learning Lab

[![Course validation](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml/badge.svg)](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml)

DS60 is a self-paced repository for learning practical Python, data science, and PostgreSQL from introductory material through substantial projects. The existing tracks are organized as 60 numbered lessons, but the number is a navigation aid rather than a deadline: take the time you need, repeat lessons, and use the curriculum catalog to choose prerequisites.

> [!TIP]
> **On Windows, double-click `START_DS60.cmd`.** It checks the machine, guides
> the connected first setup when `.venv` is absent or incomplete, runs the
> course doctor, and opens the private portal that can launch cataloged
> artifacts in VS Code or JupyterLab. On macOS/Linux—or before setup—double-click
> [START_HERE.html](START_HERE.html) for the static offline guide. Static browser
> mode can render lesson pages, but a browser cannot execute Python or SQL;
> use the private launcher for runnable actions.

The repository is designed for:

- A learner working locally in Visual Studio Code
- Windows, macOS, and Linux
- A one-time connected setup followed by offline study
- Optional guidance from Codex without requiring Codex to run the lessons

Each Python, SQL, and bridge guide is designed to stand on its own: it defines the
mental model and vocabulary, breaks down syntax or query anatomy, provides
runnable examples and visible checks, diagnoses common mistakes, and supplies
a progression of practice. Its final **Ask Codex about this lesson** block is
optional, copy-ready coaching context—not a replacement for the lesson.

> [!IMPORTANT]
> The repository runs locally after setup, but a brand-new machine still needs internet access to install Python packages, PostgreSQL or Docker, and VS Code extensions. A few lessons use Seaborn datasets that download on first use and are cached afterward. Pretrained Hugging Face, spaCy, and torchvision exercises can also require a deliberate first download; their lesson notes identify those cases. See [Offline use](docs/setup/offline.md).

## Choose a track

| Track | Start here | What it covers |
| --- | --- | --- |
| Python and data science | [Python track](python/ds-60day/README.md) | Core Python, notebooks, data work, statistics, machine learning, APIs, and production topics |
| PostgreSQL | [SQL track](sql/postgres-60day/README.md) | Relational design, SQL fundamentals, analytics, performance, operations, and projects |
| Python + PostgreSQL engineering | [Engineering bridge](bridge/README.md) | Typed configuration, safe database access, transactions, testing, ETL, concurrency, and production operations |
| Both | Start with Python Days 1–15, then alternate tracks | A broader data-practitioner path |

The human-readable overview is [docs/curriculum-map.md](docs/curriculum-map.md). The checked-in `curriculum/catalog.json` is a generated index for tools; lesson artifact filenames and the metadata rules in `src/ds60sqlpy/catalog_builder.py` are its inputs. Inspect the generated view with:

```text
python scripts/course.py catalog
```

After the shared lessons, use
[professional and specialization paths](docs/professional-paths.md) for the
named modules. New SQL learners start with `sql-found-01` and `sql-found-02`
before SQL Day 1.

## Quick start

Run commands from the repository root—the directory containing this README.

### 1. Install prerequisites

The recommended compatibility baseline is:

- Python 3.12
- PostgreSQL 16 or newer
- PostgreSQL 17 for the canonical automated environment
- Current Visual Studio Code with the recommended extensions

Follow the guide for your operating system:

- [Windows](docs/setup/windows.md)
- [macOS](docs/setup/macos.md)
- [Linux](docs/setup/linux.md)

### 2. Set up the Python environment

Windows PowerShell:

```powershell
# Easiest guided route: double-click START_DS60.cmd in File Explorer.
#
# Recommended on a new Windows machine, including when Anaconda or PostgreSQL
# is installed but not on PATH:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1

$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
```

The discovery bootstrap leaves PATH process-local by default, installs
IPython, JupyterLab, classic Notebook, ipykernel, and the course dependency
profile, registers `Python (ds60sqlpy)`, and verifies `psql` without connecting
to a database. A standard `venv` puts Python under `.venv\Scripts`; the
Anaconda fallback creates a conda prefix whose interpreter is
`.venv\python.exe`. Resolve `$CoursePython` once per PowerShell window and
reuse it for the commands below. See the
[one-command Windows bootstrap guide](docs/setup/windows-bootstrap.md).
Use the smaller historical `scripts\setup.ps1` only when a supported Python is
already discoverable and you specifically want its standard-`venv`
`.venv\Scripts\python.exe` layout; do not run it over a conda-prefix `.venv`.

`START_DS60.cmd` is the day-to-day Windows entry point; the PowerShell command
above is the lower-level setup tool. The launcher reuses a ready environment
without reinstalling packages. Before its first download it clearly labels the
connected setup and asks you to type `SETUP`. It never asks for a database
credential and never creates, drops, or resets database data.

macOS or Linux:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
```

The Windows workflow intentionally does not require activating the virtual environment. In VS Code, select the interpreter inside `.venv`.

Core setup installs notebook, data, and quality tooling. Before later machine-learning and production lessons, install the larger optional groups while connected:

Windows PowerShell:

```powershell
& .\scripts\bootstrap_windows.ps1 -Profile Advanced
```

macOS or Linux:

```bash
bash scripts/setup.sh --advanced
```

The advanced profile includes machine learning, production, Python/PostgreSQL
bridge, professional data tooling, PostgreSQL notebook magics, deep-learning,
natural-language-processing, and geospatial packages. It can take substantially
longer and may use platform-specific wheels, so install it when the catalog
shows that you need it. Catalog labels are not all literal package extras; use the
[dependency-label mapping](docs/dependency-profiles.md) before choosing a
targeted install.

### 3. See what is ready

```text
python scripts/course.py catalog
python scripts/course.py validate
```

If `python` does not resolve to the repository environment, use
`.venv/bin/python` on macOS/Linux or `& $CoursePython` on Windows. In a new
PowerShell window, rerun the resolver from step 2 first.

To use the progress dashboard and launcher:

```powershell
# Windows PowerShell
& $CoursePython scripts\learning_portal.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/learning_portal.py
```

The server binds only to `127.0.0.1`, chooses a free port, uses a per-session
request token, and accepts no arbitrary commands or paths. Use
`--no-launches` for progress synchronization without native launch buttons.

### 4. Start a lesson

Python:

1. Read [Python Day 1 companion guide](python/ds-60day/companion-guides/day01_setup_and_repl.md).
2. Open [Python Day 1 notebook](python/ds-60day/notebooks/day01_setup_and_repl.ipynb) in VS Code.
3. Attempt exercises before opening [the worked solution](python/ds-60day/solutions/day01_setup_and_repl/day01_solutions.md).

SQL:

1. Complete [SQL setup](sql/postgres-60day/README.md).
2. Complete the
   [relational-design foundation](sql/professional/companion-guides/sql_found_01_relational_design.md)
   and
   [versioned-migrations foundation](sql/professional/companion-guides/sql_found_02_versioned_migrations.md).
3. Read [SQL Day 1 companion guide](sql/postgres-60day/companion-guides/day01_select_where_orderby.md).
4. Run the lesson with error-stop behavior:

   ```text
   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
   ```

5. Attempt the exercises before opening [the worked solution](sql/postgres-60day/solutions/day01_solutions.md).

`sql/postgres-60day/00_setup.sql` is a destructive reset of the disposable `training` schema. Never run it against a database that contains data you care about.

Python + PostgreSQL engineering bridge:

1. Complete at least Python Day 15 and SQL Day 15.
2. Read the [bridge guide](bridge/README.md).
3. Open [Bridge Day 1](bridge/lessons/day01_config_logging_cli.py) and its
   [companion guide](bridge/companion-guides/day01_config_logging_cli.md).
4. Run it with the repository interpreter; live-database work is optional and
   uses `DS60_DATABASE_URL`.

## Learn with Codex

Codex is optional. The lessons, examples, and local tools remain usable without it.

This repository includes the repo-local skill `$guide-ds60sqlpy-learning`. Try:

```text
Use $guide-ds60sqlpy-learning to assess my level and guide me through the next Python, SQL, or bridge lesson. Give hints before solutions.
```

The tutor should adapt commands to your operating system, inspect your actual work, and avoid opening official solutions until you ask. See [Learning with Codex](docs/learning-with-codex.md).

## What is in the repository

```text
python/
  PYTHON_TRAINING.md
  ds-60day/
    notebooks/
    companion-guides/
    solutions/
  professional/
sql/
  ADVANCED_SQL_60DAY_PLAN.md
  postgres-60day/
    00_setup.sql
    day*.sql
    companion-guides/
    solutions/
  professional/
bridge/
  lessons/
  companion-guides/
  solutions/
  tests/
  professional/
curriculum/catalog.json
scripts/
docs/
.agents/skills/guide-ds60sqlpy-learning/
```

The maintained content has learner artifacts, companion guides, and runnable
solutions for all 60 lessons in both main tracks, eight engineering bridge
lessons, and 26 named foundation/professional/specialization modules. The
generated catalog indexes 154 learning modules and reports their exact artifact
paths.

Every lesson also has a checked exercise-enrichment target. The immutable
baseline lives in `curriculum/practice_baseline.json`; the target for each
learner artifact, guide, and every explanatory solution artifact is at least
`max(6, 2 × audited baseline)`. Run `python scripts/audit_practice.py` or read
the generated [practice coverage report](docs/practice-coverage.md).
The companion [lesson depth report](docs/lesson-depth-report.md) checks the
self-contained beginner-teaching contract, explanatory solution floor,
historical Python notebook depth, and per-lesson Codex prompts. These automated
checks are minimums; runnable examples and technical explanations still
receive human and execution review.

## Documentation

- [Curriculum map](docs/curriculum-map.md)
- [Portable guided course portal](START_HERE.html)
- [Portal modes, progress, and launcher security](docs/learning-portal.md)
- [Professional and specialization paths](docs/professional-paths.md)
- [VS Code workflow](docs/vscode.md)
- [One-command Windows bootstrap](docs/setup/windows-bootstrap.md)
- [Offline use](docs/setup/offline.md)
- [PostgreSQL in Jupyter](docs/setup/jupyter-postgresql.md)
- [Practice coverage](docs/practice-coverage.md)
- [Lesson depth report](docs/lesson-depth-report.md)
- [Curriculum design references](docs/curriculum-design-references.md)
- [Local environments and caches](docs/local-files-and-caches.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Validation](docs/validation.md)
- [Content authoring](docs/content-authoring.md)
- [Contributing](CONTRIBUTING.md)

## Continuous validation

The badge at the top reflects `.github/workflows/ci.yml`. Every push and pull
request runs locked core checks on Ubuntu (Python 3.11 and 3.12), Windows
(3.12), and macOS (3.12), exercises the learner bootstrap, and executes the
complete learner/solution SQL sequence against PostgreSQL 17. A scheduled or
manual job also verifies every optional dependency group on Windows and
Ubuntu. See [Validation](docs/validation.md) for the exact local equivalents
and the difference between structural, smoke, and full execution evidence.

## Scope and expectations

The Python track is strongest as a practical Python-for-data-science path; it
is not a substitute for the complete Python language reference. The SQL track
targets PostgreSQL. The bridge adds focused application-engineering practice,
not a full distributed-systems or database-administration program. Treat lesson
objectives and the generated catalog view—not a promise to teach
“everything”—as the contract.

Progress matters more than the 60-day label. A good session ends with runnable work, an explanation in your own words, and one small note about what to revisit.

## License

See [LICENSE](LICENSE).
