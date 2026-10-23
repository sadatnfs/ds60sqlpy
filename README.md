# DS60 Learning Lab: Python, Data Science, SQL, and Engineering

[![Course validation](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml/badge.svg)](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml)

DS60 is a self-paced repository for learning practical Python, data science, and PostgreSQL from introductory material through substantial projects. The existing tracks are organized as 60 numbered lessons, but the number is a navigation aid rather than a deadline: take the time you need, repeat lessons, and use the curriculum catalog to choose prerequisites.

> [!TIP]
> From the course folder, run **`./classroom`** to build locally, start all ten
> ordinary workers, wait for readiness and open the browser. The same entrypoint
> works on macOS, Linux and Windows through WSL 2. It selects available local
> ports and retains learning data in named Docker volumes. Read the
> [one-command setup](docs/one-command-classroom.md) for first-time engine/WSL
> preparation, a smaller starter option, stopping and recovery.
> [START_HERE.html](START_HERE.html) remains the static offline reading library.


The repository is designed for:

- A learner using the browser coding lab, Visual Studio Code, or JupyterLab
- Windows, macOS, and Linux
- A one-time connected setup followed by offline study
- Optional guidance from Codex without requiring Codex to run the lessons

**Learning journeys:** open `/journeys` for C++20, Java, JavaScript/TypeScript,
Kubernetes, Scala and Apache Spark, TensorFlow, PyTorch, NLP, LLM internals,
and applied LLM systems. Each journey shows its authored lessons and any
future extension points. The statistics/ML book is a separate reading route
with explained theory, Python examples, and answered interview discussions.
Its chapters have no exams or solution gate. The [LLM textbook reading route](docs/learning/llm-textbook.md) connects the 48 theory and 24 applied chapters with notation, derivations and a subject-assistant case study. For a connected explanation of how a language model works, read [Inside a Transformer](docs/learning/inside-a-transformer.md), including its runnable numerical forward pass. The [implementation checkpoint](docs/implementation/CHECKPOINT.md)
records current completion and actual runtime evidence. The original Python,
PostgreSQL, and bridge library remains available, with additional NumPy,
pandas, algorithms, and advanced SQL lessons.

Each Python, SQL, and bridge guide is designed to stand on its own: it defines the
mental model and vocabulary, breaks down syntax or query anatomy, provides
runnable examples and visible checks, diagnoses common mistakes, and supplies
a progression of practice. Its final **Ask Codex about this lesson** block is
optional, copy-ready coaching context - not a replacement for the lesson.

> [!IMPORTANT]
> The repository runs locally after setup, but a brand-new machine still needs internet access to install Python packages, PostgreSQL or Docker, and VS Code extensions. A few lessons use Seaborn datasets that download on first use and are cached afterward. Pretrained Hugging Face, spaCy, and torchvision exercises can also require a deliberate first download; their lesson notes identify those cases. See [Offline use](docs/setup/offline.md).

## Current validation

The expanded library has 186 Python/SQL/bridge lessons and 412 module/book
lessons across 11 subjects, with 30 additional PySpark implementations. The
statistics book maps all 1,005 topics in its supplied outline. The grouped
four-worker suite passed 2,011 tests in 127.16 seconds, with 244 explicit optional
host-runtime skips; separate local Docker checks cover all 385 executable
module/book references and all ten ordinary app-to-worker routes. See the
[acceptance checkpoint](docs/implementation/CHECKPOINT.md) for exact scope,
worked examples, browser/cluster evidence and platform limitations.

## New module labs

The workspace at `/journeys` puts the guide, coding pad, notes, compiler
diagnostics, and execution history together. C++ and Java compile in their
Docker workers. JavaScript runs in Node.js; TypeScript passes a strict compiler
check before its emitted JavaScript runs. Python, TensorFlow, PyTorch, and
Spark use their declared worker profiles. A successful example run does not
award automatic mastery; keep your explanation and transfer evidence too.

**Start with the [one-command classroom walkthrough](docs/one-command-classroom.md).**
Run `./classroom` on macOS, Linux or in a Windows WSL 2 terminal. The supplied
Bash launcher uses your local Docker engine and Compose; the language runtimes
are installed inside images, with no host Python or compiler installation. On Windows, `START_DOCKER_CLASSROOM.cmd` invokes the same entrypoint through
WSL 2; the default prepares all ordinary language and framework workers.

The classroom keeps saved work in its own persistent Docker volume. Existing
host-folder `.learning` work stays in the older launcher route; see the guide's
export and transfer instructions before moving between them. Choose only the
language or framework workers needed for your lesson and build each
image with visible foreground logs.

The [implementation checkpoint](docs/implementation/CHECKPOINT.md) records
completed content, actual runtime evidence, limitations, and the next batch.
The [optional host-launcher runtime guide](docs/modules-runtime.md) covers the
existing PowerShell/Bash workflow and the separate owned Kubernetes setup.
Those launchers remain available for learners who want host-folder storage.

## Start the guided coding application

The Docker-managed classroom above is the primary module route. The optional
alternatives below keep learning files in a visible host `.learning` folder.

The course now includes a browser workspace with Python and PostgreSQL coding
pads, a lesson guide beside your code, saved work and evidence, progressive
hints, and a route generated from your goal's prerequisites. It runs locally
and works offline after the required tools, images, and lesson packages have
been prepared.

**Docker browser lab on Windows, macOS, or Linux:** follow the
[beginner walkthrough](docs/docker-beginners.md) to install the engine,
prepare Windows WSL 2 if needed, and extract the course folder. No host Python,
PostgreSQL, or course package installation is required for this route.

**New Windows computer:** download the supplied Windows Starter ZIP (or a
repository ZIP containing the first-run wizard), choose **Extract All**, then
double-click **`START_DOCKER_LAB.cmd`** in the extracted folder. Its
first-run wizard reuses a ready engine or offers prerequisite installation.
No host Python or Git is needed. Windows may request installation approval or
a restart; rerun the same launcher afterward to continue. See the
[Windows first-run walkthrough](docs/docker-beginners.md#windows-start-with-the-first-run-wizard).

With a configured engine, Mac users can double-click
`START_DOCKER_LAB.command`. Runtime-only terminal alternatives, from the folder
containing `compose.yaml`, are:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start
```

```bash
# macOS, Linux, or an integrated WSL 2 terminal
bash scripts/docker_lab.sh start
```

The launcher builds when needed, waits for readiness, and opens
[the local learning lab](http://127.0.0.1:8765/learn). The first build needs
internet; later starts reuse local images. Saved pads, history, evidence, and
progress live in the host `.learning` folder, so replacing a container keeps
them. PostgreSQL has a separate persistent volume and uses the limited local
course login `admin` / password `admin`. Use the same launcher with `stop` to
pause without deleting either store. [Backup, custom folders, ports, and
troubleshooting](docs/docker-beginners.md#6-find-the-host-files-that-preserve-your-work)
are covered step by step.

**Use native backends:** finish your [operating-system setup](docs/setup/first-success.md),
then double-click `START_LEARNING_LAB.cmd` on Windows. On macOS/Linux:

```bash
.venv/bin/python scripts/learning_lab.py
```

**Build an executable:** use `python scripts/build_app.py` after installing the
optional `desktop-build` extra, or `make app PYTHON=.app-build/bin/python`.
Build on each target OS. The application bundles its own UI runtime and the
complete course; coding pads connect to a supported Python environment and
PostgreSQL. See [application and build instructions](docs/offline-app.md).

**Use Codex as your coach:** the optional [stdio MCP tutor](docs/mcp-tutor.md)
provides bounded course search, prerequisite planning, lessons, progressive
hints, and explicitly requested solutions. It is read-only by default and does
not execute pad code. Your Codex connection is separate from offline study.

The static `START_HERE.html` library remains available for reading. For help
choosing a route, use [learning paths and placement](docs/learning-paths.md).

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
named modules. A new SQL learner starts with `sql-start-01`, `sql-start-02`, and
`sql-start-03` before `sql-01`; relational design
(`sql-found-01`) is the milestone between Days 15 and 16, and safe versioned
migrations (`sql-found-02`) sit between Days 39 and 40.

## Quick start

Run commands from the repository root - the directory containing this README.

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
IPython, JupyterLab, Jupyter Notebook, ipykernel, and the course dependency
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

Start with the three `sql-start` labs in catalog order before the historical
Day 1 exercises; each uses a small fixture and a plain-language query model.

1. Complete [SQL setup](sql/postgres-60day/README.md).
2. Open the private course portal with `START_DS60.cmd` on Windows or
   `scripts/learning_portal.py` with the repository interpreter on macOS/Linux.
3. Open [SQL Day 1](lesson-pages/sql-01.html), read its guide, and choose
   **Create/open guided SQL notebook**. The generated learner workspace is
   ignored under `.learning/sql/sql-01/` and preserves your edits.
4. If you prefer the terminal, run the complete lesson with error-stop behavior:

   ```text
   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
   ```

   That command uses the current operating system's PostgreSQL role and
   authentication defaults. A native Windows installation normally needs the
   `-h localhost -U postgres` flags from the
   [Windows setup guide](docs/setup/windows.md#option-a-native-postgresql).
   Before opening a guided notebook against native Windows PostgreSQL, also
   complete the guide's non-interactive local-authentication step; the notebook
   will never stop in a hidden password prompt.

5. Attempt the exercises before opening [the worked solution](sql/postgres-60day/solutions/day01_solutions.md).
6. Follow the generated catalog order: complete
   [relational design](sql/professional/companion-guides/sql_found_01_relational_design.md)
   between Days 15 and 16, then
   [versioned migrations](sql/professional/companion-guides/sql_found_02_versioned_migrations.md)
   between Days 39 and 40.

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

The tutor should adapt commands to your operating system, inspect your actual
work, and avoid opening official solutions until you ask. Every companion
guide ends with a lesson-specific prompt; the same exact prompt is copyable
from its generated reader and from the lesson selector in `START_HERE.html`.
See [Learning with Codex](docs/learning-with-codex.md).

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
lessons, and 40 named foundation/professional/specialization modules. The
generated catalog indexes 186 learning modules and reports their exact artifact
paths.

Every lesson also has a checked exercise-enrichment target. The immutable
historical baseline lives in `curriculum/practice_baseline.json`; new lessons
are registered separately in `curriculum/practice_expansion.json`. The target for each
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
manual job also verifies every optional dependency group on Windows, Ubuntu,
and macOS. See [Validation](docs/validation.md) for the exact local
equivalents and the difference between structural, smoke, and full execution
evidence.

## Scope and expectations

The Python track is strongest as a practical Python-for-data-science path; it
is not a substitute for the complete Python language reference. The SQL track
targets PostgreSQL. The bridge adds focused application-engineering practice,
not a full distributed-systems or database-administration program. Treat lesson
objectives and the generated catalog view - not a promise to teach
“everything” - as the contract.

Progress matters more than the 60-day label. A good session ends with runnable work, an explanation in your own words, and one small note about what to revisit.

## License

See [LICENSE](LICENSE).
