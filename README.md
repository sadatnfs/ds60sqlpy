# DS60 Python, Data Science, SQL, and Engineering Learning Lab

DS60 is a self-paced repository for learning practical Python, data science, and PostgreSQL from introductory material through substantial projects. The existing tracks are organized as 60 numbered lessons, but the number is a navigation aid rather than a deadline: take the time you need, repeat lessons, and use the curriculum catalog to choose prerequisites.

The repository is designed for:

- A learner working locally in Visual Studio Code
- Windows, macOS, and Linux
- A one-time connected setup followed by offline study
- Optional guidance from Codex without requiring Codex to run the lessons

> [!IMPORTANT]
> The repository runs locally after setup, but a brand-new machine still needs internet access to install Python packages, PostgreSQL or Docker, and VS Code extensions. A few lessons use Seaborn datasets that download on first use and are cached afterward. Pretrained Hugging Face, spaCy, and torchvision exercises can also require a deliberate first download; their lesson notes identify those cases. See [Offline use](docs/setup/offline.md).

## Choose a track

| Track | Start here | What it covers |
| --- | --- | --- |
| Python and data science | [Python track](python/ds-60day/README.md) | Core Python, notebooks, data work, statistics, machine learning, APIs, and production topics |
| PostgreSQL | [SQL track](sql/postgres-60day/README.md) | SQL fundamentals, joins, analytics, performance, transactions, data warehousing, and projects |
| Python + PostgreSQL engineering | [Engineering bridge](bridge/README.md) | Typed configuration, safe database access, transactions, testing, ETL, concurrency, and production operations |
| Both | Start with Python Days 1–15, then alternate tracks | A broader data-practitioner path |

The human-readable overview is [docs/curriculum-map.md](docs/curriculum-map.md). The checked-in `curriculum/catalog.json` is a generated index for tools; lesson artifact filenames and the metadata rules in `src/ds60sqlpy/catalog_builder.py` are its inputs. Inspect the generated view with:

```text
python scripts/course.py catalog
```

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
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\course.py doctor
```

macOS or Linux:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
```

The Windows workflow intentionally does not require activating the virtual environment. In VS Code, select the interpreter inside `.venv`.

Core setup installs notebook, data, and quality tooling. Before later machine-learning and production lessons, install the larger optional groups while connected:

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

macOS or Linux:

```bash
bash scripts/setup.sh --advanced
```

The advanced profile includes machine learning, production, Python/PostgreSQL
bridge, deep-learning, natural-language-processing, and geospatial packages. It
can take substantially longer and may use platform-specific wheels, so install
it when the catalog shows that you need it. Catalog labels are not all literal
package extras; use the
[dependency-label mapping](docs/dependency-profiles.md) before choosing a
targeted install.

### 3. See what is ready

```text
python scripts/course.py catalog
python scripts/course.py validate
```

If `python` does not resolve to the repository environment, use `.venv/bin/python` on macOS/Linux or `.\.venv\Scripts\python.exe` on Windows.

### 4. Start a lesson

Python:

1. Read [Python Day 1 companion guide](python/ds-60day/companion-guides/day01_setup_and_repl.md).
2. Open [Python Day 1 notebook](python/ds-60day/notebooks/day01_setup_and_repl.ipynb) in VS Code.
3. Attempt exercises before opening [the worked solution](python/ds-60day/solutions/day01_setup_and_repl/day01_solutions.md).

SQL:

1. Complete [SQL setup](sql/postgres-60day/README.md).
2. Read [SQL Day 1 companion guide](sql/postgres-60day/companion-guides/day01_select_where_orderby.md).
3. Run the lesson with error-stop behavior:

   ```text
   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
   ```

4. Attempt the exercises before opening [the worked solution](sql/postgres-60day/solutions/day01_solutions.md).

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
sql/
  ADVANCED_SQL_60DAY_PLAN.md
  postgres-60day/
    00_setup.sql
    day*.sql
    companion-guides/
    solutions/
bridge/
  lessons/
  companion-guides/
  solutions/
  tests/
curriculum/catalog.json
scripts/
docs/
.agents/skills/guide-ds60sqlpy-learning/
```

The maintained content has learner artifacts, companion guides, and runnable
solutions for all 60 lessons in both main tracks, plus eight engineering bridge
lessons. The generated catalog and validation command report the exact artifact
paths.

## Documentation

- [Curriculum map](docs/curriculum-map.md)
- [VS Code workflow](docs/vscode.md)
- [Offline use](docs/setup/offline.md)
- [Local environments and caches](docs/local-files-and-caches.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Validation](docs/validation.md)
- [Content authoring](docs/content-authoring.md)
- [Contributing](CONTRIBUTING.md)

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
